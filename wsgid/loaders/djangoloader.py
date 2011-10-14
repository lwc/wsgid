


from wsgid.loaders import IAppLoader
from wsgid.core import Plugin, get_main_logger

import os
import sys

log = get_main_logger()

class DjangoAppLoader(Plugin):
  implements = [IAppLoader]

  def _not_hidden_folder(self, name):
    return not name.startswith('.')

  def _valid_dirs(self, app_path):
    return sorted(filter(self._not_hidden_folder, os.listdir(app_path)))

  def _first_djangoproject_dir(self, app_path):
    dirs = self._valid_dirs(app_path)
    log.debug("{0} Possible valid djangoapp folders: {1}".format(len(dirs), dirs))
    for d in dirs:
      settings_path = os.path.join(app_path, d, 'settings.py')
      if os.path.exists(settings_path):
        return d
    return None

  def can_load(self, app_path):
    return self._first_djangoproject_dir(app_path) is not None


  def load_app(self, app_path, app_full_name):
    logger = get_main_logger()
    
    site_name = self._first_djangoproject_dir(app_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % site_name
    logger.debug("Using DJANGO_SETTINGS_MODULE = %s" % os.environ['DJANGO_SETTINGS_MODULE'])
    
    new_sys_path = os.path.join(app_path, site_name)
    logger.debug("Adding %s to sys.path" % new_sys_path)
    sys.path.insert(0, new_sys_path)

    import django.core.handlers.wsgi
    return django.core.handlers.wsgi.WSGIHandler()
     
