

import unittest
from wsgid.commands import *
from wsgid.test import FakeOptions, fullpath
import os
import simplejson

from mock import patch, Mock
import signal


ROOT_PATH = fullpath(__file__)
FIXTURES_PATH = os.path.join(ROOT_PATH, 'fixtures')
APP_PATH = os.path.join(FIXTURES_PATH, "newapp")

#Generates a fresh full path for the given app_name
def new_app_path(app_name):
  return os.path.join(FIXTURES_PATH, app_name)

class CommandInitTest(unittest.TestCase):

  def setUp(self):
    self.init = CommandInit()
    self.opt = FakeOptions(app_path=APP_PATH)

  '''
   If the the --app-path does not exist, create.
  '''
  @patch('sys.stderr')
  def test_create_root_folter_if_not_exists(self, *args):
    self.init.run(self.opt)
    self.assertTrue(os.path.exists(APP_PATH), "Did not create the app root folder")

  @patch('sys.stderr')
  def test_create_pid_structure(self, *args):
    self.init.run(self.opt)
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "pid")), "Did not create pid folder")
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "pid/master")), "Did not create master pid folder")
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "pid/worker")), "Did not create workers pid folder")

  @patch('sys.stderr')
  def test_create_log_dir(self, *args):
    self.init.run(self.opt)
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "logs")), "Did not create logs folder")

  @patch('sys.stderr')
  def test_create_app_dir(self, *args):
    self.init.run(self.opt)
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "app")), "Did not create app folder")

  '''
   Checks there is no problem if we run "init" on an already
   inited path
  '''
  @patch('sys.stderr')
  def test_init_an_already_inited_path(self, *args):
    self.init.run(FakeOptions(app_path=APP_PATH))
    os.system("rm -rf {0}".format(os.path.join(APP_PATH, 'pid')))
    self.init.run(FakeOptions(app_path=APP_PATH))
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "app")))
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "logs")))
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "pid")))
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "pid/master")))
    self.assertTrue(os.path.exists(os.path.join(APP_PATH, "pid/worker")))

class CommandConfigTest(unittest.TestCase):

  @patch('sys.stderr')
  def setUp(self, *args):
    self.config = CommandConfig()
    self.init = CommandInit()
    self.CLEAN_PATH = os.path.join(FIXTURES_PATH, 'clean-path')
    self.opt = FakeOptions(app_path=self.CLEAN_PATH, wsgi_app="app.frontends.wsgi.application",\
                      debug=True, no_daemon=True, workers=8, keep_alive=True, chroot=True,\
                      recv="tcp://127.0.0.1:7000", send="tcp://127.0.0.1:7001", no_debug=False, no_chroot=False, no_keep_alive=False)

    self.init.run(self.opt)

  '''
   if ${app-path}/wsgid.json does not exists, create
  '''
  def test_create_json_if_not_exist(self):
    self.config.run(self.opt)
    self.assertTrue(os.path.exists(os.path.join(self.CLEAN_PATH, "wsgid.json")))

  '''
   An option passed on the command line, overrides the same option in the
   config file.
  '''
  def test_override_option(self):
    # Write an config file so we can override some options
    f = file(os.path.join(self.CLEAN_PATH, "wsgid.json"), "w+")
    simplejson.dump({"recv": "tcp://127.0.0.1:3000", "debug": "True", "workers": 8, "chroot": "True"}, f)
    f.close()

    # Here we override some options
    self.opt.recv ="tcp://127.0.0.1:4000"
    self.opt.workers = 8
    self.opt.chroot = None

    # Run the config command
    self.config.run(self.opt)
    
    # Check that the options passed on the command line are the new config options
    h = simplejson.loads(file(os.path.join(self.CLEAN_PATH, "wsgid.json"), "r+").read())
    self.assertEquals("tcp://127.0.0.1:4000", h['recv'])
    self.assertEquals("True", h['debug'])
    self.assertEquals(8, h['workers'])
    self.assertEquals("True", h['chroot']) # An option nos passed on the command line should remain on the config file


  def test_create_all_options(self):
    open(os.path.join(self.CLEAN_PATH, 'wsgid.json'), 'w+') #Clean any old config file created by other tests
    opt = FakeOptions(app_path=self.CLEAN_PATH, wsgi_app="app.frontends.wsgi.application",\
                      debug=True, no_daemon=True, workers=8, keep_alive=True, chroot=True,\
                      recv="tcp://127.0.0.1:7000", send="tcp://127.0.0.1:7001", no_debug=False, no_chroot=False, no_keep_alive=False)
    self.config.run(opt)
    h = simplejson.loads(file(os.path.join(self.CLEAN_PATH, "wsgid.json"), "r+").read())
    self.assertEquals("app.frontends.wsgi.application", h['wsgi_app'])
    self.assertEquals("True", h['debug'])
    self.assertEquals(8, h['workers'])
    self.assertEquals("True", h['keep_alive'])
    self.assertEquals("True", h['chroot'])
    self.assertEquals("tcp://127.0.0.1:7000", h['recv'])
    self.assertEquals("tcp://127.0.0.1:7001", h['send'])

  '''
    the no_debug options is an extra option added by the config command
  '''
  def test_disable_boolean_option(self):
    opt = FakeOptions(app_path=self.CLEAN_PATH, wsgi_app="app.frontends.wsgi.application",\
                      no_debug=True, debug=True, workers=9, keep_alive=True, chroot=True,\
                      recv="tcp://127.0.0.1:7000", send="tcp://127.0.0.1:7001", 
                      no_chroot=False, no_keep_alive=False)
    self.config.run(opt)
    h = simplejson.loads(file(os.path.join(self.CLEAN_PATH, "wsgid.json"), "r+").read())
    self.assertEquals("app.frontends.wsgi.application", h['wsgi_app'])
    self.assertEquals("False", h['debug'])


class CommandManageTest(unittest.TestCase):

  @patch('sys.stderr')
  def setUp(self, *args):
     self.init = CommandInit() 
     self.manage = CommandManage()
     self.opt = FakeOptions(app_path=APP_PATH, send_signal=signal.SIGTERM)
     self.init.run(self.opt)

  def test_match_command_names_matches(self):
    self.assertTrue(self.manage.name_matches('stop'))
    self.assertTrue(self.manage.name_matches('restart'))
    self.assertFalse(self.manage.name_matches('start'))

  def test_command_name(self):
    self.assertEquals('restart, stop', self.manage.command_name())

  def test_run_stop_command(self):
    open(os.path.join(APP_PATH, "pid/master/2968.pid"), "w")
    open(os.path.join(APP_PATH, "pid/master/9847.pid"), "w")

    with patch('os.kill'):
      self.manage.run(self.opt, command_name = 'stop')
      self.assertEquals(2, os.kill.call_count)
      self.assertTrue(((9847, 15), {}) in os.kill.call_args_list)
      self.assertTrue(((2968, 15), {}) in os.kill.call_args_list)

  def test_run_restart_command(self):
    open(os.path.join(APP_PATH, "pid/worker/3847.pid"), "w")
    open(os.path.join(APP_PATH, "pid/worker/4857.pid"), "w")

    with patch('os.kill'):
      self.manage.run(self.opt, command_name = 'restart')
      self.assertEquals(2, os.kill.call_count)
      self.assertTrue(((3847, 15), {}) in os.kill.call_args_list)
      self.assertTrue(((4857, 15), {}) in os.kill.call_args_list)

  @patch('sys.stderr')
  def test_send_custom_signal(self, *args):
    apppath = new_app_path('custom-signal')
    opts = FakeOptions(app_path=apppath, send_signal=9)
    self.init.run(opts)
    open(os.path.join(apppath, "pid/master/3847.pid"), "w")
    open(os.path.join(apppath, "pid/worker/3690.pid"), "w")

    with patch('os.kill'):
      self.manage.run(opts, command_name = 'stop')
      self.manage.run(opts, command_name = 'restart')
      self.assertEquals(2, os.kill.call_count)
      #Check that we sent SIGKILL
      self.assertEquals( [((3847, 9), {}), ((3690, 9), {})], os.kill.call_args_list)


  def test_kill_already_dead_pid(self):
    open(os.path.join(APP_PATH, "pid/worker/3847.pid"), "w")
    open(os.path.join(APP_PATH, "pid/worker/4857.pid"), "w")

    with patch('os.kill'):
      os.kill = Mock(side_effect=OSError("No such process"))
      self.manage.run(self.opt, command_name = 'restart')
      self.assertEquals(2, os.kill.call_count)
      self.assertTrue(((3847, 15), {}) in os.kill.call_args_list)
      self.assertTrue(((4857, 15), {}) in os.kill.call_args_list)

  '''
   Check that wsgid does not crash if we have invalid pid files
  '''
  @patch('sys.stderr')
  def test_invalid_pid_files(self, *args):
    new_path = os.path.join(FIXTURES_PATH, 'crash-app')
    opts = FakeOptions(app_path=new_path, send_signal=signal.SIGTERM)
    self.init.run(opts)
    open(os.path.join(new_path, "pid/worker/crash.pid"), "w")

    with patch('os.kill'):
      self.manage.run(opts, command_name = 'restart')
      self.assertEquals(0, os.kill.call_count)
    

