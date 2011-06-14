from wsgid.core import Plugin
from wsgid.core.command import ICommand
import os
import simplejson

class CommandConfig(Plugin):

  implements = [ICommand]

  def name_matches(self, cname):
    return "config" == cname

  def run(self, options):
    config_file = os.path.join(options.app_path, 'wsgid.json')
    f = file(config_file, "r+")
    s = f.read()
    cfg_values = simplejson.loads(s)

    cfg_values['recv'] = options.recv
    f.seek(0)
    f.truncate()
    simplejson.dump(cfg_values, f)
    f.close()

