



import unittest
from wsgid.core import parser
import sys
import signal

from wsgid.commands import *

class ParserTest(unittest.TestCase):

  '''
    Test if we correctly parse options added by sub-commands 
    --no-daemon is added by the config command
  '''
  def test_parse_aditional_options(self):
    sys.argv[1:] = ['--no-debug', '--app-path=/tmp']
    opts = parser.parse_options()
    self.assertTrue(opts.no_debug)

  def test_parse_aditional_options_py26(self):
    import platform
    original_version = platform.python_version
    def py26():
      return '2.6'
    platform.python_version = py26
    # Call the parser
    sys.argv[1:] = ['--no-debug', '--app-path=/tmp']
    opts = parser.parse_options()
    self.assertTrue(opts.no_debug)

  '''
   Tests that the default signal os 15 (SIGTERM)
  '''
  def test_default_signal(self):
    sys.argv[1:] = ['--app-path=/tmp']
    opts = parser.parse_options()
    self.assertEquals(signal.SIGTERM, opts.send_signal)
