#encoding: utf-8

from .. import __version__, __progname__, __description__
import os

from command import ICommand

BOOL, STRING, LIST, INT = range(4)

TYPES = {INT: 'int'}

def _parse_args():
  import platform
  pyversion = platform.python_version()
  if pyversion < '2.7':
    optparser = _create_optparse(prog=__progname__, description=__description__,\
                                      version= __version__)
    (opts, args) = optparser.parse_args()
    return opts
  else:
    import argparse
    parser = argparse.ArgumentParser(prog=__progname__, description=__description__, version=__version__, conflict_handler='resolve' )
    commands = ICommand.implementors()
    for command in commands:
      name = command.command_name()
      option_group = parser.add_argument_group(description="Options added by the {0} subcommand".format(name))
      # Add the custom command aditional options
      for opt in command.extra_options():
        print "Adding option {0}".format(opt.name)
        option_group.add_argument(opt.name, help = opt.help, dest = opt.dest, action = opt.action, default = opt.default_value)
    
    # Add wsgid core options
    for opt in _create_core_options():
      print "Adding option {0}".format(opt.name)
      parser.add_argument(opt.name, help = opt.help, dest = opt.dest, action = opt.action, default = opt.default_value)
    return parser.parse_args()

def _create_optparse(prog, description, version):
    import optparse
    optparser = optparse.OptionParser(prog=prog, description=description, version=version)
    commands = ICommand.implementors()
    for command in commands:
      name = command.command_name()
      option_group = optparse.OptionGroup(optparser, "Options added by the {0} subcommand".format(name))
      
      # Add the custom command aditional options
      for opt in command.extra_options():
        print "Adding option {0}".format(opt.name)
        option_group.add_option(opt.name, help = opt.help, dest = opt.dest, action = opt.action, default = opt.default_value)

    for opt in _create_core_options():
      optparser.add_option(opt.name, help = opt.help, \
                           type = opt.type, action = opt.action, \
                           dest = opt.dest, default = opt.default_value)
    return optparser

class CommandLineOption(object):

  def __init__(self, name = None, shortname = None, help = None, type = 'string', dest = None, default_value = None):
    self.name = "--{0}".format(name)
    self.shortname = shortname
    self.help = help
    self.action = 'store'
    self.type = None
    
    if type is BOOL and default_value is False:
      self.action = 'store_false'
    elif type is BOOL:
      self.action = 'store_true'

    if type is LIST:
      self.action = 'append'

    if TYPES.has_key(type):
      self.type = TYPES[type]

    self.dest = dest
    if not dest:
      self.dest = name.replace('-', '_')
    self.default_value = default_value


  def __str__(self):
    return "{name}".format(name=self.name)

def add_option(name = None, shortname = None, help = None, type = None, dest = None, default_value = None, namespace = 'core'):
  if name:
    return CommandLineOption(name, shortname, help, type, dest, default_value)

'''
  Create the list of main CLI options
'''
def _create_core_options():

  return [
  add_option('app-path', help="Path to the WSGI application",\
      dest="app_path"),

  add_option('wsgi-app', help="Full qualified name for the WSGI application object",\
      dest="wsgi_app"),

  add_option('loader-dir', help="Aditional dir for custom Application Loaders",\
      dest="loader_dir"),

  add_option('debug', help="Runs wsgid in debug mode. Lots of logging.",\
      dest="debug", type = BOOL),

  add_option('no-daemon', help="Runs wsgid in the foreground, printing all logs to stderr",\
      type=BOOL, dest="nodaemon"),

  add_option('workers', help="Starts a fixed number of wsgid processes. Defaults to 1",\
      type=INT, dest="workers"),

  add_option('keep-alive', help="Automatically respawn any dead worker. Killink the master process kills any pending worker",\
      type = BOOL, dest="keep_alive"),

  add_option('chroot', help="Chroot to the value of --app-path, before loading the app.",\
      type = BOOL, dest="chroot"),

  add_option('recv', \
      help="TCP socket used to receive data from mongrel2. Format is IP:Port or *:Port to listen on any local IP",\
      dest="recv"),

  add_option(name='send', \
      help="TCP socket used to return data to mongrel2. Format is IP:Port",\
    dest="send")]

def parse_options(use_config = True):
  options = _parse_args()
  options.app_path = _full_path(options.app_path)
  options.envs = {}

  if options.app_path:
    # Check the existence of app-path/wsgid.json, if yes use it
    # instead of command line options
    filepath = os.path.join(options.app_path, 'wsgid.json')
    if os.path.exists(filepath) and use_config:
      try:
        import simplejson as json
      except:
        # Fallback to python's built-in
        import json
      json_cfg = json.loads(file(filepath).read())

      options.send = _return_str(json_cfg.setdefault('send', options.send))
      options.recv = _return_str(json_cfg.setdefault('recv', options.recv))
      options.debug = _return_bool(json_cfg.setdefault('debug', options.debug))
      options.workers = int(json_cfg.setdefault('workers', options.workers or 1))
      options.keep_alive = _return_bool(json_cfg.setdefault('keep_alive', options.keep_alive))
      options.wsgi_app = _return_str(json_cfg.setdefault('wsgi_app', options.wsgi_app))
      options.nodaemon = _return_str(json_cfg.setdefault('nodaemon', options.nodaemon))
      options.chroot = _return_bool(json_cfg.setdefault('chroot', options.chroot))
      options.envs = json_cfg.setdefault('envs', {})

  return options

def _return_bool(option):
  if option and str(option).lower() == 'true':
    return True
  return False

def _return_str(option):
  if option:
    return str(option)
  return option

def _full_path(path=None):
  if path:
    return os.path.abspath(os.path.expanduser(path))
  return path


