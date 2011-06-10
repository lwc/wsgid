from plugnplay import Interface
import sys

from ..options import parser

class ICommand(Interface):


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
 Extract the first command line argument (if it exists)
 and tries to find a ICommand implementor for it.
 If found, run it. If not does nothing.
'''
def run_command():
  command_implementors = ICommand.implementors()
  if command_implementors and len(sys.argv) > 1:
    cname = sys.argv[1] # get the command name
    for command in command_implementors:
      if command.name_matches(cname):
        # Remove the command name, since it's not defined
        # in the parser options
        sys.argv.remove(cname)
        command.run(parser.parse_options())
        return True
  return False


