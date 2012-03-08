from fabric.api import env, task
from fabric.utils import abort

env.site    = 'example'
env.repository = 'git+ssh://git.hosting.com/drupal/example.git'
env.apptype = 'drupal'

"""Assume stage set via rcfile, eg:
stage=dev
"""
'''
if (env.stage == 'dev'):
  env.install_tasks = [
    'build_release',
    'upload_release',
    'extract_release',
  ]
  env.hosts = [
    'user@33.33.33.21'
  ]
else:
  abort('stage not setup in site recipe')

'''
