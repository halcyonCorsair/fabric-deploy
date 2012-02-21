from fabric.api import env, task
from fabric.utils import abort

env.site    = 'example'
env.scm_uri = 'git+ssh://git.catalyst.net.nz/git/private/drupal/example.git'

if (env.stage == 'dev'):
  env.install_tasks = [
    'build_release',
    'upload_release',
    'extract_release',
  ]
  env.web_hosts = [
    'user@33.33.33.21'
  ]
else:
  abort('stage not setup in site recipe')

