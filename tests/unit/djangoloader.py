

import unittest
import os
import sys

from wsgid.loaders.djangoloader import DjangoAppLoader
from wsgid.test import fullpath
from mock import patch
from django.conf import settings
import django

FIXTURE = fullpath(__file__)
WSGID_APP_NAME = 'django-wsgid-app'
DJANGOAPP_NO_INIT = 'djangonoinit'

class DjangoLoaderTest(unittest.TestCase):

  def setUp(self):
    dirname = os.path.dirname(__file__)
    self.abs_app_path = os.path.join(FIXTURE, WSGID_APP_NAME)
    self.wsgid_appfolder_fullpath = os.path.join(self.abs_app_path, 'app/')
    self.app_loader = DjangoAppLoader()

#  def tearDown(self):
#    setattr(settings, '_wrapped', None) #So django thinks we are not configured yet

  '''
   Ensure we can load a djangoapp even with hidden folders
   inside the wsgi-app folder.
  '''
  def test_can_load_with_hidden_folder(self):

    self.assertTrue(self.app_loader.can_load(self.wsgid_appfolder_fullpath))

    with patch('os.listdir'):
      os.listdir.return_value = ['.git', '.hg', 'mydjangoapp']

      app = self.app_loader.load_app(self.wsgid_appfolder_fullpath, 'app')
      self.assertEquals(django.core.handlers.wsgi.WSGIHandler, app.__class__)
      self.assertEquals("mydjangoapp.settings", os.environ['DJANGO_SETTINGS_MODULE'])

  '''
   Check that we can recognize a simple wsgid app with a django app inside
  '''
  def test_can_load_django_app(self, *args):
      self.assertTrue(self.app_loader.can_load(self.wsgid_appfolder_fullpath))

  '''
   A valid django folder must be importable, so we have to check
   that __init__.py exists.
  '''
  def test_django_folder_must_have_init(self):
      djangoapp_path = os.path.join(FIXTURE, 'wsgidapp-noinit/app')
      self.assertFalse(self.app_loader.can_load(djangoapp_path))

  '''
   Check if we return False for a non-django app folder
  '''
  def test_not_django_wsgid_app_folder(self):
    with patch('os.listdir'):
      os.listdir.return_value  = []
      self.assertFalse(self.app_loader.can_load(self.wsgid_appfolder_fullpath))

  '''
    Since os.list returns the result in a random order, DjangoAppLoader can return True for can_load()
    but get a different result on the second call to os.listdir (inside load_app())
    We should consistently load the django app from the same folder we said we could load it.
  '''
  def test_prepared_for_os_listdir_random(self):
    with patch('os.listdir'):
      dirs = ['mydjangoapp', 'otherdjangoapp']
      os.listdir.return_value = dirs
      self.assertTrue(self.app_loader.can_load(self.wsgid_appfolder_fullpath))

      os.listdir.return_value = list(reversed(dirs))
      self.app_loader.load_app(self.wsgid_appfolder_fullpath, 'appname')
      self.assertEquals("mydjangoapp.settings", os.environ['DJANGO_SETTINGS_MODULE'])

  '''
   Check that we can load a django app that is not the first one (in alphabetical order)
  '''
  def test_can_load_the_second_folder(self):
    with patch('os.listdir'):
      os.listdir.return_value = ['anotherfolder', 'mydjangoapp']
      self.assertTrue(self.app_loader.can_load(self.wsgid_appfolder_fullpath))
      self.app_loader.load_app(self.wsgid_appfolder_fullpath, None)
      self.assertEquals("mydjangoapp.settings", os.environ['DJANGO_SETTINGS_MODULE'])

  '''
   Any setting inside settngs.py that are *not* mentioned on django.json must
   remain available when we do:
       from django.conf settings
       settings.MY_NON_OVERRIDEN_OPTION
  '''
  def test_custom_options_must_remain(self):
      app_path = os.path.join(FIXTURE, WSGID_APP_NAME, 'app')
      self.app_loader.load_app(app_path)
      self.assertEquals('still-the-same-value', settings.MY_OTHER_CUSTOM_SETTING)


  '''
   If we have a setting in django.json that does not exist in settings,
   we must create it
  '''
  def test_create_new_setting(self):
      app_path = os.path.join(FIXTURE, WSGID_APP_NAME, 'app')
      self.app_loader.load_app(app_path)
      self.assertEquals('a new value', settings.NEW_SETTING)

  '''
   If we have a TEST_OPT inside settings.py and this same
   options inside wsgidappfolder/django.json, the JSON version
   must be available at:
       from django.conf import settings
       settings.TEST_OPT
   after DjangoAppLodare loads this app.
  '''
  def test_override_existing_settings_option(self):
      app_path = os.path.join(FIXTURE, WSGID_APP_NAME, 'app')
      self.app_loader.load_app(app_path)
      self.assertEquals('other-value', settings.MY_CUSTOM_SETTING)

  '''
   If django.json contains a setting that is a dict we must "join" this
   dict from django.json with the dict loaded from app's settings.py
  '''
  def test_join_hash_setting(self):
      app_path = os.path.join(FIXTURE, WSGID_APP_NAME, 'app')
      self.app_loader.load_app(app_path)
      self.assertTrue(isinstance(settings.DATABASES, dict))
      self.assertEquals(2, len(settings.DATABASES))

      self.assertEquals("django.db.backends.postgresql", settings.DATABASES['default']['ENGINE'])
      self.assertEquals("pgdb", settings.DATABASES['default']['NAME'])
      self.assertEquals("postgres", settings.DATABASES['default']['USER'])
      self.assertEquals("pgpasswd", settings.DATABASES['default']['PASSWORD'])
      self.assertEquals("localhost", settings.DATABASES['default']['HOST'])
      self.assertEquals("5432", settings.DATABASES['default']['PORT'])

      self.assertEquals("mysql", settings.DATABASES['myotherdb']['ENGINE'])
      self.assertEquals("mydb", settings.DATABASES['myotherdb']['NAME'])
      self.assertEquals("user", settings.DATABASES['myotherdb']['USER'])
      self.assertEquals("passwd", settings.DATABASES['myotherdb']['PASSWORD'])
      self.assertEquals("localhost", settings.DATABASES['myotherdb']['HOST'])
      self.assertEquals("3598", settings.DATABASES['myotherdb']['PORT'])

  def test_override_hash_setting(self):
      app_path = os.path.join(FIXTURE, WSGID_APP_NAME, 'app')
      self.app_loader.load_app(app_path)
      self.assertTrue(isinstance(settings.MY_HASH, dict))
      self.assertEquals(1, len(settings.MY_HASH))

      self.assertEquals("new-v1", settings.MY_HASH['subhash']['k1'])
      self.assertEquals("new-v2", settings.MY_HASH['subhash']['k2'])
      self.assertEquals("new-v3", settings.MY_HASH['subhash']['k3'])


  '''
   Whataver is on django.json, overrides settings.py, even if
   settings are of different types
   This does not apply if original settings is dict or tuple
  '''
  def test_django_json_overrides_settings(self):
      app_path = os.path.join(FIXTURE, WSGID_APP_NAME, 'app')
      self.app_loader.load_app(app_path)
      self.assertTrue(isinstance(settings.GENERIC_SETTING, dict))
      self.assertEquals(1, len(settings.GENERIC_SETTING))
      self.assertEquals("v", settings.GENERIC_SETTING['k'])


  '''
   If we find a list settings we must append the extra values at the
   end of the found list
  '''
  def test_list_setting(self):
      setattr(settings, 'MY_LIST_SETTING', ['some value', 'another one'])
      app_path = os.path.join(FIXTURE, WSGID_APP_NAME, 'app')
      self.app_loader.load_app(app_path)
      self.assertTrue(isinstance(settings.MY_LIST_SETTING, list))
      #self.assertEquals(3, len(settings.MY_LIST_SETTING))
      self.assertEquals(['some value', 'another one', 'one more'], settings.MY_LIST_SETTING)

  '''
    If we have a setting on django.json (that is a list) with the same name of another
    setting (that is a tuple), the list must be converted to tuple.
  '''
  def test_convert_list_to_tuple(self):
      self.fail()

  '''
   We must log any parse error that we may find when reading django.json
  '''
  def test_log_error_when_parsing_django_json(self):
      self.fail()





