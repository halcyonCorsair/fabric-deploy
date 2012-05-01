from fabric.api import env, task
from fabric.utils import abort

"""Possible overrides
env.user = 'drupaldeploy'
env.shell = '/bin/bash -c'
env.web_root = '/var/www'
env.release_archive = None
env.release_time = time.strftime('%Y.%m.%d-%H.%M')
env.local_tmp = '/tmp'
env.remote_tmp = '/tmp'

To see all available tasks, run:
  fab -f /path/to/deploy.py -l

To see the default deployment tasks, run:
  fab -f /path/to/deploy.py list_deploy_tasks

See http://docs.python.org/tutorial/datastructures.html for list methods (eg, remove, insert, etc).

# Reverting Features #:

You can revert individual features by creating a list (env.revertable_features), and then adding drush_feature_revert to your list of tasks. eg.

env.revertable_features = [
  'feature_one',
  'feature_two',
]
env.deploy_tasks.insert(position, 'drush_cron')


"""

# <Sitename> Overrides:
env.site    = 'example'
env.repository = 'git+ssh://git.hosting.com/drupal/example.git'
env.apptype = 'drupal'
env.remote_tmp = '/tmp'
env.local_tmp = '/tmp'
env.version = 7

if (env.stage == 'dev'):
  # Append a task
  env.deploy_tasks.append('drush_feature_revert_all')

  # Remove a task
  env.deploy_tasks.remove('drush_cache_clear_all')

  # Insert a task
  #   Unfortunately you need to know the position in the list, so...
  #   eg. Insert drush_cron before drush_site_online:
  position = env.deploy_tasks.index('drush_site_online')
  env.deploy_tasks.insert(position, 'drush_cron')

  """
  Server uri's should be specified as fqdn
  """
  env.roledefs = {
      'web': ['web1.server.net', 'web2.server.net'],
  #    'db': ['db.server.net'],
  #    'files': ['files.server.net'],
  }
elif (env.stage == 'staging'):
  pass
else:
  abort('stage not setup in site recipe')

