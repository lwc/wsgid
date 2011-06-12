

import unittest
from wsgid.commands.init import CommandInit
import os

class FakeOptions(object):
  def __init__(self, **kwargs):
    for k, v in kwargs.items():
      setattr(self, k, v)


class CommandInitTest(unittest.TestCase):

  def setUp(self):
    self.init = CommandInit()
    os.system("rm -rf newapp/")
    self.opt = FakeOptions(app_path="./newapp")

  '''
   If the the --app-path does not exist, create.
  '''
  def test_create_root_folter_if_not_exists(self):
    self.init.run(self.opt)
    self.assertTrue(os.path.exists("./newapp"), "Did not create the app root folder")

  def test_create_pid_structure(self):
    self.init.run(self.opt)
    self.assertTrue(os.path.exists("./newapp/pid"), "Did not create pid folder")
    self.assertTrue(os.path.exists("./newapp/pid/master"), "Did not create master pid folder")
    self.assertTrue(os.path.exists("./newapp/pid/worker"), "Did not create workers pid folder")

  def test_create_log_dir(self):
    self.init.run(self.opt)
    self.assertTrue(os.path.exists("./newapp/logs"), "Did not create logs folder")

  def test_create_app_dir(self):
    self.init.run(self.opt)
    self.assertTrue(os.path.exists("./newapp/app"), "Did not create app folder")


class CommandConfigTest(unittest.TestCase):


  def setUp(self):
    self.config = CommandConfig()

  '''
   if ${app-path}/wsgid.json does not exists, create
  '''
  def test_create_json_if_not_exist(self):
    self.fail()

  '''
   If an options already exists in the json config file
   and is passed on the command line, it must be overwritten
  '''
  def test_override_option(self):
    self.fail()
