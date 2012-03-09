from fabric.api import env, task
from fabric.utils import abort

env.site    = 'example'
env.repository = 'git+ssh://git.hosting.com/drupal/example.git'
env.apptype = 'drupal'
env.local_tmp = '~/tmp'
env.version = 7

"""Assume stage set via rcfile, eg:
stage=dev
"""
'''
if (env.stage == 'dev'):
  env.pre_deploy_tasks = []

  env.deploy_tasks = [
    'build_release',
    'upload_release',
    'extract_release',
  ]

  env.post_deploy_tasks = [
    'drush_backup_database',
    'drush_site_offline',
    'drush_update_database',
    'drush_feature_revert',
    'drush_cache_clear_all',
    'drush_site_online',
  ]

  env.hosts = [
    'user@host.domain'
  ]
else:
  abort('stage not setup in site recipe')

'''
