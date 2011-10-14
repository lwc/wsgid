import os
from glob import glob
import re


class WsgidApp(object):

  REGEX_PIDFILE = re.compile("[0-9]+\.pid")

  def __init__(self, fullpath):
    self.fullpath = fullpath


  def is_valid(self):
    return os.path.exists(os.path.join(self.fullpath, 'app')) \
            and os.path.exists(os.path.join(self.fullpath, 'logs')) \
            and os.path.exists(os.path.join(self.fullpath, 'pid')) \
            and os.path.exists(os.path.join(self.fullpath, 'pid/master')) \
            and os.path.exists(os.path.join(self.fullpath, 'pid/worker'))

  def master_pids(self):
    return sorted(self._get_pids(self.fullpath, 'pid/master/'))

  def worker_pids(self):
    return sorted(self._get_pids(self.fullpath, 'pid/worker/'))


  def _get_pids(self, base_path, pids_path):
    final_path = os.path.join(base_path, pids_path, '*.pid')
    pid_files = glob(final_path)
    pids = [int(os.path.basename(pid_file).split('.')[0]) for pid_file in pid_files if self._is_pidfile(pid_file)]
    return pids

  def _is_pidfile(self, filename):
    return self.REGEX_PIDFILE.match(os.path.basename(filename)) 


