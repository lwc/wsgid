
from wsgid.core import Plugin, get_main_logger as logger
from wsgid.core.command import ICommand
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
    return []

  def _stop(self, options):
    logger().info("Stopping master processes at {0}...\n".format(options.app_path))
    pids = self._get_pids(options.app_path, 'pid/master')
    for pidnumber in pids:
      logger().debug("Sending signal {0} to master pid={1}".format(signal.SIGTERM, pidnumber))
      self._sigkill(pidnumber)

  def _restart(self, options):
    logger().info("Restarting worker processes at {0}...\n".format(options.app_path))
    pids = self._get_pids(options.app_path, 'pid/worker')
    for pidnumber in pids:
      logger().debug("Sending signal {0} to worker pid={1}".format(signal.SIGTERM, pidnumber))
      self._sigkill(pidnumber)

  def _get_pids(self, base_path, pids_path):
    final_path = os.path.join(base_path, pids_path, '*.pid')
    pid_files = glob(final_path)
    pids = [int(os.path.basename(pid_file).split('.')[0]) for pid_file in pid_files if self._is_pidfile(pid_file)]
    return pids

  def _is_pidfile(self, fileame):
    return self.REGEX_PIDFILE.match(os.path.basename(fileame)) 

  def _sigkill(self, pid):
    try:
      os.kill(pid, signal.SIGTERM)
    except:
      logger().debug("Non existant pid {0}".format(pid))


