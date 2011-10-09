#encoding: utf-8
import unittest
from wsgid.test import fullpath, FakeOptions
from wsgid.commands import CommandInit
from wsgid.core import WsgidApp
import os

from mock import patch

FIXTURE = os.path.join(fullpath(__file__), 'fixtures')

class WsgidAppTest(unittest.TestCase):

  @patch('sys.stderr')
  def setUp(self, *args):
    self.init = CommandInit()
    self.empty_apppath = os.path.join(FIXTURE, 'empty-app')
    self.init.run(FakeOptions(app_path=self.empty_apppath))
    self.empty_wsgidapp = WsgidApp(self.empty_apppath)

  def test_check_valid_wsgid_app_folder(self):
    self.assertTrue(self.empty_wsgidapp.is_valid(), "Did not recognize as a valid wsgid app folder")

  def test_return_empty_master_pids(self):
    self.assertEquals([], self.empty_wsgidapp.master_pids())

  def test_return_empty_worker_pids(self):
    self.assertEquals([], self.empty_wsgidapp.worker_pids())

  @patch('sys.stderr')
  def test_return_pids(self, *args):
    app = os.path.join(FIXTURE, 'app-with-pids')
    self.init.run(FakeOptions(app_path=app))
    open(os.path.join(app, 'pid/master/3345.pid'), 'w')
    open(os.path.join(app, 'pid/master/2938.pid'), 'w')
    open(os.path.join(app, 'pid/master/no-pid.pid'), 'w')
    
    open(os.path.join(app, 'pid/worker/8756.pid'), 'w')
    open(os.path.join(app, 'pid/worker/3948.pid'), 'w')
    open(os.path.join(app, 'pid/worker/invalid.pid'), 'w')

    wsgidapp = WsgidApp(app)
    # Invalid pidfiles must be ignored
    self.assertEquals([2938, 3345], wsgidapp.master_pids())
    self.assertEquals([3948, 8756], wsgidapp.worker_pids())


