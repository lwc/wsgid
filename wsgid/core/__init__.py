#encoding: utf-8

__all__ = ['StartResponse', 'StartResponseCalledTwice', 'Plugin', 'run_command', 'get_main_logger']

import sys
import logging
import plugnplay
from command import ICommand
import parser

from wsgidapp import WsgidApp

Plugin = plugnplay.Plugin

class StartResponse(object):

  def __init__(self):
    self.headers = []
    self.status = ''
    self.body = ''
    self.called = False
    self.body_written = False

  def __call__(self, status, response_headers, exec_info=None):
    if self.called and not exec_info:
      raise StartResponseCalledTwice()

    if exec_info and self.body_written:
      try:
        raise exec_info[0], exec_info[1], exec_info[2]
      finally:
        exec_info = None # Avoid circular reference (PEP-333)

    self.headers = response_headers
    self.status = status

    self.called = True
    return self._write

  def _write(self, body):
    self.body_written = True
    self.body += body


class StartResponseCalledTwice(Exception):
  pass


log = logging.getLogger('wsgid')

def get_main_logger():
  return log

def set_main_logger(logger):
  log = logger

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
        command.run(parser.parse_options(use_config = False), command_name = cname)
        return True
  return False

