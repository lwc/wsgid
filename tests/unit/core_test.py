


import unittest
from wsgid.core import run_command
from wsgid.commands import *
import plugnplay
import sys

from mock import Mock

class CoreTest(unittest.TestCase):


  def test_ICommand_must_receive_command_name(self):
      mock_command = Mock(wraps=CommandManage())

      # Very dirty hack to replace CommandManage implementation inside plugnplay
      saved = plugnplay.man.iface_implementors[ICommand]
      plugnplay.man.iface_implementors[ICommand] = [mock_command]
      sys.argv[:] = ['wsgid', 'stop', '--app-path=/tmp/app-path']

      found_implementor = run_command()
      
      plugnplay.man.iface_implementors[ICommand] = saved

      self.assertTrue(found_implementor, "Did not find any ICommand implementing stop command")
      self.assertTrue(mock_command.run.called, "ManageCommand.run() not called")
      print mock_command.run.call_args
      self.assertEquals({'command_name': 'stop'}, mock_command.run.call_args[1])
