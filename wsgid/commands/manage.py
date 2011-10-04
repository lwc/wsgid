
from wsgid.core import Plugin, get_main_logger as logger
from wsgid.core.command import ICommand
import os
import signal
from glob import glob

'''
Includes both stop and restart commands
'''
class CommandManage(Plugin):

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
    final_path = os.path.join(options.app_path, 'pid/master/*.pid') 
    pids = glob(final_path)
    for pid in pids:
      pidnumber = os.path.basename(pid).split('.')[0]
      logger().debug("Sending signal {0} to master pid={1}".format(signal.SIGTERM, pidnumber))
      os.kill(int(pidnumber), signal.SIGTERM)

  def _restart(self, options):
    logger().info("Restarting worker processes at {0}...\n".format(options.app_path))
    final_path = os.path.join(options.app_path, 'pid/worker/*.pid') 
    pids = glob(final_path)
    for pid in pids:
      pidnumber = os.path.basename(pid).split('.')[0]
      logger().debug("Sending signal {0} to worker pid={1}".format(signal.SIGTERM, pidnumber))
      os.kill(int(pidnumber), signal.SIGTERM)

