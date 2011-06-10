

from wsgid.core import Plugin
from wsgid.core.command import ICommand

class CommandInit(Plugin):

  implements = [ICommand]

  def name_matches(self, cname):
    return "init" == cname

  def run(self, options):
    print "Initializing wsgid app folder in {0}...".format(options.app_path)
