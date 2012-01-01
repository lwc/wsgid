#encoding: utf-8

import sys
import signal
import os
import logging

import unittest
from wsgid.core.cli import Cli
from wsgid.core import parser, WsgidApp
from wsgid.commands import CommandInit
from wsgid.test import fullpath, FakeOptions
import wsgid.conf

import daemon

from mock import patch, Mock, MagicMock

ROOT_PATH = fullpath(__file__)
FIXTURES_PATH = os.path.join(ROOT_PATH, 'fixtures')

class CliTest(unittest.TestCase):

  @patch('sys.stderr')
  def setUp(self, *args):
    self.cli = Cli()
    # As we are dealing with a command line test, we have do clean the passed arguments
    # so the tested applications does not try to use them
    sys.argv[1:] = []
    self.fake_app_path = os.path.join(fullpath(__file__), 'app-path')

    # Ok, not pretty but better than re-implementing this in python
    os.system("rm -rf {0}".format(os.path.join(self.fake_app_path, 'pid/')))
    self.cli.options = parser._parse_args()
    self.cli.options.app_path = self.fake_app_path

    CommandInit().run(FakeOptions(app_path=self.fake_app_path))

  def tearDown(self):
      wsgid.conf.settings = None

  def test_nodaemon(self):
    opts = self._parse()
    self.assertTrue(opts['detach_process'])

  def test_daemon_keep_sigterm_handler(self):
    opt = self._parse()
    self.assertTrue(opt['detach_process'])
    handler = signal.getsignal(signal.SIGTERM)
    self.assertEquals(opt['signal_map'][signal.SIGTERM], handler)

  '''
   When not a daemon we must keep std{in, out, err}
  '''
  def test_nodaemon_keep_basic_fds(self):
    opt = self._parse('--no-daemon')
    self.assertFalse(opt['detach_process'])
    self.assertEquals(opt['stdin'], sys.stdin)
    self.assertEquals(opt['stdout'], sys.stdout)
    self.assertEquals(opt['stderr'], sys.stderr)

  '''
    We should not try to chroot if --app-path was not passed
  '''
  def test_no_chroot_if_no_app_path(self):
    opt = self._parse('--chroot')
    self.assertFalse(opt.has_key('chroot_directory'))

  '''
    We shoud not chroot if --chroot is not passed.
  '''
  def test_no_chroot(self):
    opt = self._parse('--app-path=./')
    self.assertFalse(opt.has_key('chroot_directory'))

  '''
    If we are chrooting we must drop privileges.
  '''
  def test_drop_priv(self):
    opt = self._parse('--app-path=./', '--chroot')
    stat = os.stat('./')
    self.assertEquals(opt['uid'], stat.st_uid)
    self.assertEquals(opt['gid'], stat.st_gid)

  '''
   chroot_diretocry should have the absolute path of --app-path
  '''
  def test_chroot_has_absolute_app_path(self):
    opt = self._parse('--chroot', '--app-path=./')
    abspath = os.path.abspath(os.getcwd())
    self.assertEquals(opt['chroot_directory'], abspath)

  def test_parse_workers_as_integer(self):
    sys.argv[1:] = ['--workers=3']
    opts = parser._parse_args()
    self.assertTrue(type(int), opts.workers)

  def _parse(self, *opts):
    sys.argv[1:] = opts
    return self.cli._create_daemon_options(parser.parse_options())

  '''
    We must generate all logs inside <app-path>/logs
  '''
  def test_ajust_log_path_app_path(self):
    app_path = os.path.join('../', os.path.dirname(__file__), 'app-path')
    sys.argv[1:] = ['--app-path=%s' % app_path]
    opt = parser._parse_args()
    self.cli._set_loggers(opt)
    handlers = self.cli.log.handlers
    self.assertTrue(isinstance(handlers[0], logging.FileHandler))
    self.assertEquals(os.path.join(app_path, 'logs/wsgid.log'), handlers[0].baseFilename)

  def test_full_path_empty_path(self):
    self.assertEquals(parser._full_path(None), None)

  '''
    Even if we do not chroot, we must drop priv.
  '''
  def test_should_droppriv_if_app_path_is_passed(self):
    app_path = os.path.join('../', os.path.dirname(__file__), 'app-path')
    argv = ['--app-path=%s' % app_path]
    stat = os.stat(parser._full_path(app_path))
    opts = self._parse(*argv)
    self.assertEquals(opts['uid'], stat.st_uid)
    self.assertEquals(opts['gid'], stat.st_gid)

  '''
    If we have a wsgid.json file inside app-path, so we must use it.
  '''
  def test_load_wsgid_json_file(self):
    app_path = os.path.join('../', os.path.dirname(__file__), 'app-path')
    # All we have to do is pass --app-path, so wsgfid ca find ${app-path}/wsgid.json
    sys.argv[1:] = ['--app-path=%s' % app_path]
    options = parser.parse_options()
    self.assertEquals('tcp://127.0.0.1:5000', options.recv)
    self.assertEquals('tcp://127.0.0.1:5001', options.send)
    self.assertEquals(4, options.workers)
    self.assertEquals(True, options.debug)
    self.assertEquals(True, options.keep_alive) #If one option does now exist in the config file, we get the default value
    self.assertEquals(False, options.chroot)
    self.assertEquals(True, options.stdout)

    self.assertEquals({'ENV1': 'VALUE1', 'ENV2': 'VALUE2'}, options.envs)

  def test_wsgid_json_overwrites_command_line(self):
    app_path = os.path.join('../', os.path.dirname(__file__), 'app-path')
    sys.argv[1:] = ['--app-path={0}'.format(app_path), '--workers=8']
    options = parser.parse_options()
    self.assertEquals(4, options.workers)


  def test_autocreate_pid_folder_structure(self):

    os.system("rm -rf {0}".format(os.path.join(self.fake_app_path, 'pid/')))
    pid_folder = os.path.join(self.fake_app_path, 'pid')
    master_pid_folder = os.path.join(pid_folder, 'master')
    worker_pid_folder = os.path.join(pid_folder, 'worker')
    master_pid_file = os.path.join(master_pid_folder, '42.pid')
    worker_pid_file = os.path.join(worker_pid_folder, '43.pid')

    self.assertFalse(os.path.exists(pid_folder))
    self.assertFalse(os.path.exists(master_pid_folder))
    self.assertFalse(os.path.exists(worker_pid_folder))

    self.cli._write_pid(42, self.cli.MASTER)
    self.cli._write_pid(43, self.cli.WORKER)

    # Check we created all necessary paths
    self.assertTrue(os.path.exists(pid_folder))
    self.assertTrue(os.path.exists(master_pid_folder))
    self.assertTrue(os.path.exists(worker_pid_folder))

    self.assertTrue(os.path.exists(os.path.join(master_pid_folder, '42.pid')))
    self.assertTrue(os.path.exists(os.path.join(worker_pid_folder, '43.pid')))

    self.assertEquals("42", file(master_pid_file).read())
    self.assertEquals("43", file(worker_pid_file).read())


  def test_remove_pid(self):
    self.cli._write_pid(42, self.cli.MASTER)
    pid_file = os.path.join(self.fake_app_path, 'pid/master/42.pid')

    self.cli._remove_pid(42, self.cli.MASTER)
    self.assertFalse(os.path.exists(pid_file))

  '''
   Doing this wsgid is able to run with a process supervisor.
   See: issue/20 at github
  '''
  @patch('sys.stderr')
  def test_start_workers_when_nodaemon(self, *args):
    path = os.path.join(FIXTURES_PATH, 'nodaemon-app')
    initcmd = CommandInit()
    initcmd.run(FakeOptions(app_path=path))
    with patch('daemon.DaemonContext', new=MagicMock()):
      with patch.object(Cli, '_create_worker'):
        with patch.object(Cli, 'validate_input_params'):
          with patch.object(Cli, '_wait_workers'):
            daemon.DaemonContext.__enter__ = Mock()
            daemon.DaemonContext.__exit__ = Mock()
            sys.argv[1:] = ['--workers=3', '--no-daemon', '--app-path={0}'.format(path)]
            cli = Cli()
            cli.run()
            self.assertEquals(3, cli._create_worker.call_count)
            self.assertEquals(1, cli._wait_workers.call_count)

  '''
   When using only --do-daemon (without --stdout) logs must be
   redirected to log file.
  '''
  def test_daemon_should_create_normal_logs(self):
    opts = FakeOptions(app_path="/some/path", no_daemon=True, stdout=False, debug=None, chroot=None)
    with patch('logging.FileHandler'):
      cli = Cli()
      cli._set_loggers(opts)
      self.assertEquals(1, logging.FileHandler.call_count)
      self.assertEquals((("/some/path/logs/wsgid.log",), {}), logging.FileHandler.call_args)

  '''
   When we pass --stdout all logs must be pointed to stdout.
  '''
  def test_create_log_for_stdout(self):
    opts = FakeOptions(app_path="/some/path", no_daemon=True, stdout=True, debug=None, chroot=None)
    with patch('logging.StreamHandler'):
      cli = Cli()
      cli._set_loggers(opts)
      self.assertEquals(1, logging.StreamHandler.call_count)

  def test_clean_pid_files_on_keyboard_interrupt(self):
    path = os.path.join(FIXTURES_PATH, 'clean-pids-app')
    initcmd = CommandInit()
    opts = FakeOptions(app_path=path)
    initcmd.run(opts)
    open(os.path.join(path, 'pid/master/3340.pid'), 'w')
    open(os.path.join(path, 'pid/worker/2736.pid'), 'w')
    open(os.path.join(path, 'pid/worker/3847.pid'), 'w')
    with patch('os.wait'):
      with patch('os.getpid'):
          os.getpid.side_effect = lambda: 3340
          os.wait.side_effect = KeyboardInterrupt()
          cli = Cli()
          cli.options = opts
          cli.log = Mock()
          cli.workers = [2736, 3847]
          cli._wait_workers()
          app = WsgidApp(path)
          self.assertEquals([], app.master_pids())
          self.assertEquals([], app.worker_pids())



