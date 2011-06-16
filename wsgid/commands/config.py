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
    f = self._open_config_file(config_file)
    s = f.read()
    cfg_values = {}
    if s:
      cfg_values = simplejson.loads(s)

    # Copy the values
    cfg_values['wsgi_app'] = options.wsgi_app
    cfg_values['debug'] = options.debug
    cfg_values['no_daemon'] = options.no_daemon
    cfg_values['workers'] = options.workers
    cfg_values['keep_alive'] = options.keep_alive
    cfg_values['chroot'] = options.chroot
    cfg_values['recv'] = options.recv
    cfg_values['send'] = options.send
    
    # Rewrite the config file
    f.seek(0)
    f.truncate()
    simplejson.dump(cfg_values, f)
    f.close()

  def _open_config_file(self, path):
    if os.path.exists(path):
      return file(path, "r+")
    return file(path, "w+")
