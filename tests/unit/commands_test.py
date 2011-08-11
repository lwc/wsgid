

import unittest
from wsgid.commands.init import CommandInit
from wsgid.commands.config import CommandConfig
import os
import simplejson

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

  '''
   Checks there is no problem if we run "init" on an already
   inited path
  '''
  def test_init_an_already_inited_path(self):
    self.init.run(FakeOptions(app_path="./newapp"))
    os.system("rm -rf newapp/pid")
    self.init.run(FakeOptions(app_path="./newapp"))
    self.assertTrue(os.path.exists("./newapp/app"))
    self.assertTrue(os.path.exists("./newapp/logs"))
    self.assertTrue(os.path.exists("./newapp/pid"))
    self.assertTrue(os.path.exists("./newapp/pid/master"))
    self.assertTrue(os.path.exists("./newapp/pid/worker"))

class CommandConfigTest(unittest.TestCase):


  def setUp(self):
    self.config = CommandConfig()
    self.init = CommandInit()
    self.opt = FakeOptions(app_path="./newapp", wsgi_app="app.frontends.wsgi.application",\
                      debug=True, no_daemon=True, workers=8, keep_alive=True, chroot=True,\
                      recv="tcp://127.0.0.1:7000", send="tcp://127.0.0.1:7001", no_debug=False, no_chroot=False, no_keep_alive=False)

    os.system("rm -rf ./newapp/")
    self.init.run(self.opt)

  '''
   if ${app-path}/wsgid.json does not exists, create
  '''
  def test_create_json_if_not_exist(self):
    self.config.run(self.opt)
    self.assertTrue(os.path.exists("newapp/wsgid.json"))

  '''
   An option passed on the command line, overrides the same option in the
   config file.
  '''
  def test_override_option(self):
    # Write an config file so we can override some options
    f = file("./newapp/wsgid.json", "w+")
    simplejson.dump({"recv": "tcp://127.0.0.1:3000", "debug": "True", "workers": "8", "chroot": "True"}, f)
    f.close()

    # Here we override some options
    self.opt.recv ="tcp://127.0.0.1:4000"
    self.opt.workers = 8
    self.opt.chroot = None

    # Run the config command
    self.config.run(self.opt)
    
    # Check that the options passed on the command line are the new config options
    h = simplejson.loads(file("./newapp/wsgid.json", "r+").read())
    self.assertEquals("tcp://127.0.0.1:4000", h['recv'])
    self.assertEquals("True", h['debug'])
    self.assertEquals("8", h['workers'])
    self.assertEquals("True", h['chroot']) # An option nos passed on the command line should remain on the config file


  def test_create_all_options(self):
    opt = FakeOptions(app_path="./newapp", wsgi_app="app.frontends.wsgi.application",\
                      debug=True, no_daemon=True, workers=8, keep_alive=True, chroot=True,\
                      recv="tcp://127.0.0.1:7000", send="tcp://127.0.0.1:7001", no_debug=False, no_chroot=False, no_keep_alive=False)
    self.config.run(opt)
    h = simplejson.loads(file("./newapp/wsgid.json", "r+").read())
    self.assertEquals("app.frontends.wsgi.application", h['wsgi_app'])
    self.assertEquals("True", h['debug'])
    self.assertEquals("8", h['workers'])
    self.assertEquals("True", h['keep_alive'])
    self.assertEquals("True", h['chroot'])
    self.assertEquals("tcp://127.0.0.1:7000", h['recv'])
    self.assertEquals("tcp://127.0.0.1:7001", h['send'])

  '''
    the no_debug options is an extra option added by the config command
  '''
  def test_disable_boolean_option(self):
    opt = FakeOptions(app_path="./newapp", wsgi_app="app.frontends.wsgi.application",\
                      no_debug=True, debug=True, workers=9, keep_alive=True, chroot=True,\
                      recv="tcp://127.0.0.1:7000", send="tcp://127.0.0.1:7001", no_chroot=False, no_keep_alive=False)
    self.config.run(opt)
    h = simplejson.loads(file("./newapp/wsgid.json", "r+").read())
    self.assertEquals("app.frontends.wsgi.application", h['wsgi_app'])
    self.assertEquals("False", h['debug'])

