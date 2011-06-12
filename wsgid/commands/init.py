

from wsgid.core import Plugin
from wsgid.core.command import ICommand
import os

class CommandInit(Plugin):

  implements = [ICommand]

  def name_matches(self, cname):
    return "init" == cname

  def run(self, options):
    print "Initializing wsgid app folder in {0}...".format(options.app_path)
    os.mkdir(options.app_path)
    os.mkdir(os.path.join(options.app_path, 'pid'))
    os.mkdir(os.path.join(options.app_path, 'pid/master'))
    os.mkdir(os.path.join(options.app_path, 'pid/worker'))
    os.mkdir(os.path.join(options.app_path, 'app'))
    os.mkdir(os.path.join(options.app_path, 'logs'))
