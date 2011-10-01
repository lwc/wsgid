

from wsgid.core import Plugin, get_main_logger as logger
from wsgid.core.command import ICommand
import os
import signal
from glob import glob

class CommandStop(Plugin):

  implements = [ICommand]
  COMMAND = 'stop'

  def command_name(self):
    return self.COMMAND

  def name_matches(self, cname):
    return self.COMMAND == cname

  def run(self, options):
    logger().info("Stopping master processes at {0}...\n".format(options.app_path))
    final_path = os.path.join(options.app_path, 'pid/master/*.pid') 
    pids = glob(final_path)
    for pid in pids:
      pidnumber = os.path.basename(pid).split('.')[0]
      logger().debug("Sending signal {0} to master pid={1}".format(signal.SIGTERM, pidnumber))
      os.kill(int(pidnumber), signal.SIGTERM)

  def extra_options(self):
    return []
