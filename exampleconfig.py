from fabric.api import env, task
from fabric.utils import abort

"""Possible overrides
env.user = 'deploy'
env.shell = '/bin/bash -c'
env.web_root = '/var/www'
env.release_archive = None
env.release_time = time.strftime('%Y.%m.%d-%H.%M')
env.local_tmp = '/tmp'
env.remote_tmp = '/tmp'

Possible tasks:
env.deploy_tasks = [
  'build_release',
  'upload_release',
  'extract_release',
  'symlink_current_release',
  'create_release_files_symlink',
  'create_release_settings_symlink',
  'drush_backup_database',
  'drush_site_offline',
  'drush_update_database',
  'drush_feature_revert',
  'drush_cache_clear_all',
  'drush_site_online',
]

See http://docs.python.org/tutorial/datastructures.html for list methods (eg, remove, insert, etc).
"""

env.site    = 'example'
env.repository = 'git+ssh://git.hosting.com/drupal/example.git'
env.apptype = 'drupal'
env.remote_tmp = '/tmp'
env.local_tmp = '/tmp'
env.version = 7

if (env.stage == 'dev'):
  #env.deploy_tasks.remove('drush_feature_revert')

  #env.user = 'deployuser'
  #env.roledefs = {
  #    'web': ['web1.server.net', 'web2.server.net'],
  #    'db': ['db.server.net'],
  #    'files': ['files.server.net'],
  #}
else:
  abort('stage not setup in site recipe')

