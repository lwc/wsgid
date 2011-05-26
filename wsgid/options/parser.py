#encoding: utf-8

from wsgid import __version__, __progname__


options = []
BOOL, STRING, LIST, INT = range(4)

TYPES = {INT: 'int'}

def parse_args():
  import platform
  pyversion = platform.python_version()
  if pyversion < '2.7':
    import optparse

    optparser = optparse.OptionParser(prog=__progname__, description='A complete WSGI environment for mongrel2 handlers',\
                                      version="%s" % __version__)
    for opt in options:
      optparser.add_option(opt.name, help = opt.help, \
                           type = opt.type, action = opt.action, \
                           dest = opt.dest, default = opt.default_value)

    (opts, args) = optparser.parse_args()
    return opts

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
    self.default_value = default_value


  def __str__(self):
    return "{name}".format(name=self.name)

def add_option(name = None, shortname = None, help = None, type = None, dest = None, default_value = None):
  if name:
    op = CommandLineOption(name, shortname, help, type, dest, default_value)
    options.append(op)



#optparser.add_option('--app-path', help="Path to the WSGI application",\
#    action="store", dest="app_path")
add_option('app-path', help="Path to the WSGI application",\
    dest="app_path")

#optparser.add_option('--wsgi-app', help="Full qualified name for the WSGI application object",\
#    action="store", dest="wsgi_app")
add_option('wsgi-app', help="Full qualified name for the WSGI application object",\
    dest="wsgi_app")

#optparser.add_option('--loader-dir', help="Aditional dir for custom Application Loaders",\
#    action="append", dest="loader_dir")
add_option('loader-dir', help="Aditional dir for custom Application Loaders",\
    dest="loader_dir")

#optparser.add_option('--debug', help="Runs wsgid in debug mode. Lots of logging.",\
#    action="store_true", dest="debug")
add_option('debug', help="Runs wsgid in debug mode. Lots of logging.",\
    dest="debug", type = BOOL)

#optparser.add_option('--no-daemon', help="Runs wsgid in the foreground, printing all logs to stderr",\
#    action="store_true", dest="nodaemon")
add_option('no-daemon', help="Runs wsgid in the foreground, printing all logs to stderr",\
    type=BOOL, dest="nodaemon")

#optparser.add_option('--workers', help="Starts a fixed number of wsgid processes. Defaults to 1",\
#    action="store", default="1", type="int", dest="workers")
add_option('workers', help="Starts a fixed number of wsgid processes. Defaults to 1",\
    default_value="1", type=INT, dest="workers")

#optparser.add_option('--keep-alive', help="Automatically respawn any dead worker. Killink the master process kills any pending worker",\
#    action="store_true", dest="keep_alive")
add_option('keep-alive', help="Automatically respawn any dead worker. Killink the master process kills any pending worker",\
    type = BOOL, dest="keep_alive")

#optparser.add_option('--chroot', help="Chroot to the value of --app-path, before loading the app.",\
#    action="store_true", dest="chroot")
add_option('chroot', help="Chroot to the value of --app-path, before loading the app.",\
    type = BOOL, dest="chroot")

#optparser.add_option('--recv', help="TCP socket used to receive data from mongrel2. Format is IP:Port or *:Port to listen on any local IP",\
#    action="store", dest="recv")
add_option('recv', \
    help="TCP socket used to receive data from mongrel2. Format is IP:Port or *:Port to listen on any local IP",\
    dest="recv")

#optparser.add_option('--send', help="TCP socket used to return data to mongrel2. Format is IP:Port",\
#    action="store", dest="send")
add_option(name='send', \
    help="TCP socket used to return data to mongrel2. Format is IP:Port",\
    dest="send")


