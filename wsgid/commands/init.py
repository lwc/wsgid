

from wsgid.core import Plugin
from wsgid.core.command import ICommand
import os

class CommandInit(Plugin):

  implements = [ICommand]

  def name_matches(self, cname):
    return "init" == cname

  def run(self, options):
    print "Initializing wsgid app folder in {0}...".format(options.app_path)
    self._create_if_not_exist(options.app_path)
    self._create_if_not_exist(os.path.join(options.app_path, 'pid'))
    self._create_if_not_exist(os.path.join(options.app_path, 'pid/master'))
    self._create_if_not_exist(os.path.join(options.app_path, 'pid/worker'))
    self._create_if_not_exist(os.path.join(options.app_path, 'app'))
    self._create_if_not_exist(os.path.join(options.app_path, 'logs'))

  def _create_if_not_exist(self, path):
    if not os.path.exists(path):
      os.mkdir(path)
