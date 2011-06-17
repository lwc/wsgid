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
    self._override_if_not_none('wsgi_app', cfg_values, options.wsgi_app)
    self._override_if_not_none('debug', cfg_values, options.debug)
    self._override_if_not_none('workers', cfg_values, options.workers)
    self._override_if_not_none('keep_alive', cfg_values, options.keep_alive)
    self._override_if_not_none('chroot', cfg_values, options.chroot)
    self._override_if_not_none('recv', cfg_values, options.recv)
    self._override_if_not_none('send', cfg_values, options.send)
    
    # Rewrite the config file
    f.seek(0)
    f.truncate()
    simplejson.dump(cfg_values, f)
    f.close()

  def _open_config_file(self, path):
    if os.path.exists(path):
      return file(path, "r+")
    return file(path, "w+")

  def _override_if_not_none(self, opt_name, dest, value):
    if value:
      dest[opt_name] = value
