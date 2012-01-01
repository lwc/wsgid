from wsgid.core import Plugin
from wsgid.core.command import ICommand
from wsgid.core.parser import CommandLineOption, BOOL
import os
import simplejson

class CommandConfig(Plugin):

  implements = [ICommand]

  def command_name(self):
    return 'config'

  def name_matches(self, cname):
    return "config" == cname

  def run(self, options, **kwargs):
    config_file = os.path.join(options.app_path, 'wsgid.json')
    f = self._open_config_file(config_file)
    s = f.read()
    cfg_values = {}
    if s:
      cfg_values = simplejson.loads(s)

    # Copy the values
    self._override_if_not_none('wsgi_app', cfg_values, options.wsgi_app)
    self._override_if_not_none('debug', cfg_values, options.debug)
    if options.workers > 1:
      self._override_if_not_none('workers', cfg_values, options.workers, convert_func=int)
    self._override_if_not_none('keep_alive', cfg_values, options.keep_alive)
    self._override_if_not_none('chroot', cfg_values, options.chroot)
    self._override_if_not_none('no_daemon', cfg_values, options.no_daemon)
    self._override_if_not_none('recv', cfg_values, options.recv)
    self._override_if_not_none('send', cfg_values, options.send)
    self._override_if_not_none('mongrel2_chroot', cfg_values, options.mongrel2_chroot)

    # Custom config command options
    cfg_values['debug'] = str((not options.no_debug))

    # Rewrite the config file
    f.seek(0)
    f.truncate()
    simplejson.dump(cfg_values, f, indent="  ")
    f.close()

  def extra_options(self):
    return [CommandLineOption(name='no-debug', help = 'Turns off debug option', type=BOOL),
           CommandLineOption(name='no-keep-alive', help = 'Turns off Keep alive option', type=BOOL),
           CommandLineOption(name='no-chroot', help = 'Turns off Chroot option', type=BOOL)]

  def _open_config_file(self, path):
    if os.path.exists(path):
      return open(path, "r+")
    return open(path, "w+")

  def _override_if_not_none(self, opt_name, dest, value, convert_func=str):
    if value:
      dest[opt_name] = convert_func(value)
