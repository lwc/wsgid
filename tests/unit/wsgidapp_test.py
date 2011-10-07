#encoding: utf-8
import unittest
from wsgid.test import fullpath, FakeOptions
from wsgid.commands import CommandInit
from wsgid.core import WsgidApp
import os

FIXTURE = os.path.join(fullpath(__file__), 'fixtures')

class WsgidAppTest(unittest.TestCase):

  def setUp(self):
    self.init = CommandInit()
    self.empty_apppath = os.path.join(FIXTURE, 'check-app')
    self.init.run(FakeOptions(app_path=self.empty_apppath))
    self.empty_wsgidapp = WsgidApp(self.empty_apppath)

  def test_check_valid_wsgid_app_folder(self):
    self.assertTrue(self.empty_wsgidapp.is_valid(), "Did not recognize as a valid wsgid app folder")

  def test_return_empty_master_pids(self):
    self.assertEquals([], self.empty_wsgidapp.master_pids())

  def test_return_empty_worker_pids(self):
    self.assertEquals([], self.empty_wsgidapp.worker_pids())


