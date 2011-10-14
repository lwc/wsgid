


import unittest
import os

from wsgid.loaders.djangoloader import DjangoAppLoader
from wsgid.test import fullpath
import django.core.handlers.wsgi
from mock import patch

FIXTURE = fullpath(__file__)
WSGID_APP_NAME = 'django-wsgid-app'

class DjangoLoaderTest(unittest.TestCase):

  def setUp(self):
    dirname = os.path.dirname(__file__)
    self.abs_app_path = os.path.join(FIXTURE, WSGID_APP_NAME)
    self.wsgid_appfolder_fullpath = os.path.join(self.abs_app_path, 'app/')
    self.app_loader = DjangoAppLoader()

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
  def test_can_load_django_app(self):
      self.assertTrue(self.app_loader.can_load(self.wsgid_appfolder_fullpath))

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








