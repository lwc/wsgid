#encoding: utf-8

import plugnplay
import os
from ..core import Plugin, get_main_logger
import sys
import logging
import glob

log = get_main_logger()

class IAppLoader(plugnplay.Interface):

  '''
    Return True/False if a custom load is able to load
    the WSGI app that is in tha path passed as a parameter.
  '''
  def can_load(self, app_path):
    pass

  '''
    Return the WSGI application object for tha app in app_path
    @ap_path: Path on disk where the app is located. Already inserted into sys.path. This is --app-path + 'app/' 
    @app_full_name: Full qualified name for the WSGI application object
  '''
  def load_app(self, app_path, app_full_name):
    pass


def load_app(app_path, wsgi_app_full_name):

  if app_path:
    absolute_path = os.path.abspath(os.path.expanduser(app_path))
    log.debug("Adding %s to sys.path" % absolute_path)
    sys.path.append(absolute_path)

  if wsgi_app_full_name:
    log.info("Loading WSGI application object: %s" % wsgi_app_full_name)
    return import_object(wsgi_app_full_name)

  app_loaders = IAppLoader.implementors()
  log.debug("Found {0} loaders: {1}".format(len(app_loaders), app_loaders))
  for loader in app_loaders:
    if loader.can_load(app_path):
      log.info("Using AppLoader: %s" % loader.__class__.__name__)
      return loader.load_app(absolute_path, wsgi_app_full_name)

  raise Exception("No Loader found for app %s and no --wsgi-app option found\n" % app_path)


'''
 Imports an object from a full qualified name.
 ex: app.module.submodule.objectname, returns an instance of objectname
'''
def import_object(full_object_name):
  parts = full_object_name.strip().split('.')
  mod = '.'.join(parts[:-1])
  obj_name = parts[-1]
  imported = __import__(mod, fromlist=obj_name)
  return getattr(imported, obj_name)

# Loaders implementation

class PyRoutesLoader(Plugin):
  implements = [IAppLoader]

  def can_load(self, app_path):
    settings = os.path.join(app_path, 'pyroutes_settings.py')
    return os.path.exists(settings)

  def load_app(self, app_path, app_full_name):
    if app_full_name:
      return import_object(app_full_name)

    dirs = [d for d in os.listdir(app_path) if os.path.isdir(os.path.join(app_path, d))]

    # A normal pyroutes application should have only 3 folders: templates/ tests/ <app-name>/
    # Here we do: "import <app-name>"
    app_dir = filter(lambda d: d not in ('templates', 'tests'), dirs)
    __import__(app_dir[0]) # This should import all @routes from the app
    __import__(app_dir[0], fromlist='pyroutes_settings')
    import pyroutes
    return pyroutes.application


class PasteLoader(Plugin):
  implements = [IAppLoader]

  def can_load(self, app_path):
    return bool(glob.glob(os.path.join(app_path, '../*.ini')))

  def load_app(self, app_path, app_full_name):
    from paste.deploy import loadapp
    logger = get_main_logger()
    logger.debug("Using ini "+str(os.getenv('PASTE_INI_PATH')))
    return loadapp('config:'+os.getenv('PASTE_INI_PATH'))


import djangoloader
