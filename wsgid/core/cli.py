#encoding: utf-8

import sys
import logging
import os

from . import get_main_logger, set_main_logger, run_command
from ..commands import *
import parser

import plugnplay
import daemon
import signal

class Cli(object):
  # PID types we may create
  MASTER, WORKER = range(2)

  def __init__(self):
    self.log = get_main_logger()

  '''
   Command Line interface for wsgid
  '''

  def validate_input_params(self, app_path, recv, send, wsgi_app):
    if not app_path and not wsgi_app:
      raise Exception("--app-path is mandatory when --wsgi-app is not passed\n")
    if app_path and not os.path.exists(app_path):
      raise Exception("path {0} does not exist.\n".format(app_path))
    if not recv:
      raise Exception("Recv socket is mandatory\n")
    if not send:
      raise Exception("Send socker is mandatory\n")

  def run(self):
    if run_command():
      sys.exit(0)

    options = parser.parse_options()
    self.validate_input_params(app_path=options.app_path,\
        recv=options.recv, send=options.send,\
        wsgi_app=options.wsgi_app)


    self.options = options # Will be used by the signal handlers
    try:
      daemon_options = self._create_daemon_options(options)
      ctx = daemon.DaemonContext(**daemon_options)

      with ctx:
        # Now that we are chrooted (if desired) we should correct
        # the paths
        options.app_path = self._normalize_path(options)
        self._set_loggers(options)

        self.log.debug("Using configs values {cfg}".format(cfg=options))
        self.log.debug("Dropping privileges to: uid={uid}, gid={gid}".format(uid=daemon_options['uid'], gid=daemon_options['gid']))
        self.log.info("Master process started")
        self.log.debug("Creating master pid file at {0}".format(self._return_pid_file_path(os.getpid(), self.MASTER)))
        self._write_pid(os.getpid(), self.MASTER)
        self._load_plugins(options)

        self.workers = []
        for worker in range(options.workers):
          pid = self._create_worker(options)
          self.workers.append(pid)
        #Now we can register the master process SIGTERM handler
        signal.signal(signal.SIGTERM, self._sigterm_handler)
        self._wait_workers()
    except Exception, e:
      import traceback
      exc = sys.exc_info()
      self.log.info("".join(traceback.format_exception(exc[0], exc[1], exc[2])))
      self._remove_pid(os.getpid(), self.MASTER)
      sys.exit(1)

  def _write_pid(self, pid, pid_type):
    # Create the base pid folder
    self._mkdir_if_not_exist(os.path.join(self.options.app_path, 'pid'))

    pid_folder = self._return_pid_folder(pid_type)
    self._mkdir_if_not_exist(pid_folder)

    pid_file_path = self._return_pid_file_path(pid, pid_type)
    pid_file = open(pid_file_path, 'w')
    self.log.debug("Creating pid file at {0}".format(pid_file_path))
    pid_file.write(str(pid))
    pid_file.close()

  def _return_pid_file_path(self, pid, pid_type):
    return os.path.join(self._return_pid_folder(pid_type), '{0}.pid'.format(pid))

  def _remove_pid(self, pid, pid_type):
    pid_file = self._return_pid_file_path(pid, pid_type)
    self.log.debug("Removing pid file at {0}".format(pid_file))
    if os.path.isfile(pid_file):
      os.unlink(pid_file)

  def _return_pid_folder(self, pid_type):

    pid_folders = {
        self.MASTER: os.path.join(self.options.app_path, 'pid/master'),
        self.WORKER: os.path.join(self.options.app_path, 'pid/worker')
        }
    return pid_folders[pid_type]

  def _mkdir_if_not_exist(self, path):
    if not os.path.exists(path):
      os.mkdir(path, 0700)



  '''
    This is the SIGTERM handler of the master process.
    This method kills any worker left when master process is killed
  '''
  def _sigterm_handler(self, sig, stack):
    self.log.debug("SIGTERM received, killing any pending worker")
    for p in self.workers:
      self.log.debug("Killing worker pid={pid}".format(pid=p))
      os.kill(p, signal.SIGTERM)
      self._remove_pid(p, self.WORKER)
    self.log.info("Exiting...")
    self._remove_pid(os.getpid(), self.MASTER)
    sys.exit(0)

  def _wait_workers(self):
    while True:
      try:
        dead_worker = os.wait()
        self.workers.remove(dead_worker[0])
        self.log.info("Worker finished, pid={pid} retval={retval}".format(pid=dead_worker[0], retval=dead_worker[1]))
        self._remove_pid(dead_worker[0], self.WORKER)

        if self.options.keep_alive:
          new_worker = self._create_worker(self.options)
          self.workers.append(new_worker)
          self.log.debug("Current active workers={workers}".format(workers=self.workers))
        if not self.workers:
          self.log.debug("No more workers to wait for and no keep alive requested, exiting...")
          self._remove_pid(os.getpid(), self.MASTER)
          sys.exit(0)
      except KeyboardInterrupt, k:
        for worker in self.workers:
          self._remove_pid(worker, self.WORKER)
        self._remove_pid(os.getpid(), self.MASTER)
        return

  def _load_plugins(self, options):
    if options.loader_dir:
      plugnplay.set_plugin_dirs(*options.loader_dir)
      plugnplay.load_plugins()

  def _create_daemon_options(self, options):
    daemon = {'detach_process': not options.nodaemon}
    daemon.update({ 'stdin': sys.stdin, 
                   'stdout': sys.stdout, 
                   'stderr': sys.stderr})
    if options.nodaemon:
      # If we are not a daemon we must maintain the basic signal handlers
      daemon.update({'signal_map': {
          signal.SIGTTIN: signal.getsignal(signal.SIGTTIN),
          signal.SIGTTOU: signal.getsignal(signal.SIGTTOU),
          signal.SIGTSTP: signal.getsignal(signal.SIGTSTP),
          signal.SIGTERM: signal.getsignal(signal.SIGTERM)
        }})
    else:
      daemon.update({'signal_map':
                      {signal.SIGTERM: signal.getsignal(signal.SIGTERM)}
        })

    daemon.update({'uid': os.getuid(), 'gid': os.getgid()})

    if options.app_path:
      full_path = options.app_path
      stat = os.stat(full_path)
      daemon.update({'uid': stat.st_uid,
                     'gid': stat.st_gid})

      if options.chroot:
        full_path = options.app_path
        stat = os.stat(full_path)
        daemon.update({'chroot_directory': full_path,
                       'uid': stat.st_uid,
                       'gid': stat.st_gid})
    return daemon


  def _normalize_path(self, options):
    if options.chroot:
      return '/'
    return options.app_path

  '''
   Forks a new wsgid worker, return the pid of this worker
  '''
  def _create_worker(self, options):
    pid = os.fork()
    if pid == 0:
      self.workers = []
      self.log = logging.getLogger('wsgid')
      signal.signal(signal.SIGTERM, signal.SIG_DFL)
      self._call_wsgid(options)

    self.log.info("New wsgid worker created pid={pid}".format(pid=pid))
    self._write_pid(pid, self.WORKER)
    return pid

  def _call_wsgid(self, options):
    from wsgid import Wsgid
    from ..loaders import load_app

    # Create the env vars
    if options.envs:
      for k, v in options.envs.iteritems():
        os.environ[k] = v

    # The app source-code is inside an "app" folder, so we join this part
    # here and pass it to the AppLoaders.
    wsgi_app = load_app(os.path.join(options.app_path, 'app'), options.wsgi_app)
    wsgid = Wsgid(wsgi_app, options.recv, options.send)
    wsgid.serve()

  def _set_loggers(self, options):
    level = logging.INFO if not options.debug else logging.DEBUG
    logger = get_main_logger()
    logger.setLevel(level)


    if options.chroot:
      log_path = os.path.join('/', 'logs/wsgid.log')
    
    if options.nodaemon and options.stdout:
      console = logging.StreamHandler()
    else:
      log_path = os.path.join(options.app_path or '/tmp', 'logs/wsgid.log')
      console = logging.FileHandler(log_path)

    console.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s [pid=%(process)d] - %(levelname)s - %(message)s")
    console.setFormatter(formatter)

    logger.addHandler(console)
    self.log = logger
    set_main_logger(logger)

