

from wsgid.core import Plugin, get_main_logger as logger
from wsgid.core.command import ICommand
import os
import signal
from glob import glob

class CommandRestart(Plugin):

  implements = [ICommand]

  def command_name(self):
    return 'restart'

  def name_matches(self, cname):
    return 'restart' == cname

  def run(self, options):
    logger().info("Restarting worker processes at {0}...\n".format(options.app_path))
    final_path = os.path.join(options.app_path, 'pid/worker/*.pid') 
    pids = glob(final_path)
    for pid in pids:
      pidnumber = os.path.basename(pid).split('.')[0]
      logger().debug("Sending signal {0} to worker pid={1}".format(signal.SIGTERM, pidnumber))
      os.kill(int(pidnumber), signal.SIGTERM)

  def extra_options(self):
    return []
