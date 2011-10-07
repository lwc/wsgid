
from wsgid.core import Plugin, get_main_logger as logger, WsgidApp
from wsgid.core.command import ICommand
from wsgid.core.parser import INT, CommandLineOption
import os
import signal
from glob import glob
import re

'''
Includes both stop and restart commands
'''
class CommandManage(Plugin):
  REGEX_PIDFILE = re.compile("[0-9]+\.pid")

  SUPPORTED_COMMANDS = ['restart', 'stop']
  implements = [ICommand]

  def command_name(self):
    return ', '.join(self.SUPPORTED_COMMANDS)

  def name_matches(self, cname):
    return cname in self.SUPPORTED_COMMANDS

  def run(self, options, command_name = None):
    if command_name:
      method = getattr(self, "_{0}".format(command_name))
      method(options)

  def extra_options(self):
    return [CommandLineOption(name='send-signal', \
                              help = 'Choose a custom signal to send to master/workers processes. Default signal is SIGTERM.',\
                              type=INT, default_value = signal.SIGTERM)]

  def _stop(self, options):
    wsgidapp = WsgidApp(options.app_path)
    logger().info("Stopping master processes at {0}...".format(options.app_path))
    pids = wsgidapp.master_pids()
    self._kill_pids(pids, options.send_signal, 'master')

  def _restart(self, options):
    wsgidapp = WsgidApp(options.app_path)
    logger().info("Restarting worker processes at {0}...".format(options.app_path))
    pids = wsgidapp.worker_pids()
    self._kill_pids(pids, options.send_signal, 'worker')
  
  def _kill_pids(self, pids, signum, pidtype):
    for pidnumber in pids:
      logger().debug("Sending signal {sig} to {pidtype} pid={pid}".format(pid=pidnumber, sig=signum, pidtype=pidtype))
      self._sigkill(pidnumber, signum)

  def _sigkill(self, pid, signum):
    try:
      os.kill(pid, signum)
    except:
      logger().debug("Non existant pid {0}".format(pid))


