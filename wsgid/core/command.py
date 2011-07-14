from plugnplay import Interface
import sys

class ICommand(Interface):


  '''
    Returns the command name. This name will be used to show aditional
    options when calling wsgid --help
  '''
  def command_name(self):
    pass

  '''
    Returns True if this command implementor
    can run the command passed as {command_name} parameter
    Returns False otherwise
  '''
  def name_matches(self, command_name):
    pass

  '''
    Officially runs the command and receive the same options that
    was passed on the command line
    Retuns nothing
  '''
  def run(self, options):
    pass

  
  '''
   Return a list of wsgid.options.parser.CommandLineOption instances
  '''
  def extra_options(self):
    pass




