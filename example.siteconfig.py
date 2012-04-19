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
"""

# <Sitename> Overrides:
env.site    = 'example'
env.repository = 'git+ssh://git.hosting.com/drupal/example.git'
env.apptype = 'drupal'
env.remote_tmp = '/tmp'
env.local_tmp = '/tmp'
env.version = 7

if (env.stage == 'dev'):
  # A little dirty, but may desirable until convenience method exists?
  # Uncomment if you want features automatically reverted on deploy
  #fr_index = env.deploy_tasks.index('drush_cache_clear_all')
  #env.deploy_tasks.append('drush_feature_revert')
  #env.deploy_tasks.remove('drush_feature_revert')

  """
  Server uri's should be specified as fqdn
  """
  #env.roledefs = {
  #    'web': ['web1.server.net', 'web2.server.net'],
  #    'db': ['db.server.net'],
  #    'files': ['files.server.net'],
  #}
elif (env.stage == 'staging'):
  pass
else:
  abort('stage not setup in site recipe')

