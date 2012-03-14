from fabric.api import *
from fabric.colors import green, red, yellow
import os, sys, time

env.user = 'deploy'
env.shell = '/bin/bash -c'
env.web_root = '/var/www'
env.release_archive = None
env.release_time = time.strftime('%Y.%m.%d-%H.%M')
env.local_tmp = '/tmp'
env.remote_tmp = '/tmp'

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

@task
def deploy(tag):
  load_config()

  for task in env.pre_deploy_tasks:
    execute(task, env.site, tag)

  for task in env.deploy_tasks:
    execute(task, env.site, tag)

  for task in env.post_deploy_tasks:
    if ('feature_revert' in task or 'update_database' in task):
      execute(task, env.site, tag, prompt=False)
    else:
      execute(task, env.site, tag)

@task
def load_config():
  """Load site config.
  Assume config file is called siteconfig.py and resides in the current directory.
  """
  print green("===> Loading site recipe...")
  directory = os.getcwd()
  sys.path.append(directory)
  import siteconfig
  env.scm_build_dir = '%(local_tmp)s/%(apptype)s-site-%(site)s' % env

@task
def tag_release(site, tag, commit, message=''):
  print green("===> Building the release...")
  tag = 'site-%(release_time)s-' % env

  # Ensure code directory exists
  with settings(warn_only=True):
    if local('test -d %(scm_build_dir)s' % env).failed:
      local('git clone %(repository)s %(scm_build_dir)s' % env)

  with lcd(env.scm_build_dir):
    # TODO: put git status check here
    if (local("git pull", capture=True)).succeeded:
      if (message == ''):
        local('git tag %s %s' % (tag, commit))
      else:
        local('git tag -m "%s" %s %s' % (message, tag, commit))
  return tag

@task
@runs_once
def build_release(site, tag):
  print green("===> Building the release...")
  release_archive = '%(apptype)s-site-%(site)s_%(tag)s.tar.gz' % env
  env.scm_build_dir = '%(local_tmp)s/%(apptype)s-site-%(site)s' % env

  # Ensure code directory exists
  with settings(warn_only=True):
    if local('test -d %(scm_build_dir)s' % env).failed:
      local('git clone %(repository)s %(scm_build_dir)s' % env)

  with lcd(env.scm_build_dir):
    # put git status check here
    if (local("git pull", capture=True)).succeeded:
      env.release_tree = local('git show-ref --tags -s "%(tag)s"' % env, True)
      local('git archive --format tar %(release_tree)s | gzip > %(local_tmp)s/%(release_archive)s' % env)

@task
@serial
@roles('web')
def upload_release(site, tag):
  print green("===> Uploading the release archive...")
  release_archive = '%(apptype)s-site-%(site)s_%(tag)s.tar.gz' % env
  with settings(warn_only=True):
    if run("test -f %(remote_tmp)s/%(release_archive)s" % env).failed:
      put('%(local_tmp)s/%(release_archive)s' % env, '/tmp/')

@task
@serial
@roles('web')
def extract_release(site, tag):
  print green("===> Extracting the release...")
  env.site = site
  env.tag = tag
  release_archive = '%(apptype)s-site-%(site)s_%(tag)s.tar.gz' % env
  with settings(warn_only=True):
    if run("test -f %(remote_tmp)s/%(release_archive)s" % env).failed:
      abort(red("Release archive doesn't exist, please run build_release again"))
    if run('test -d /var/www/%(apptype)s/%(site)s/releases/%(tag)s' % env).succeeded:
      abort(red("Release directory already exists"))
  if run('test -d /var/www/%(apptype)s/%(site)s/releases' % env).succeeded:
    with cd('/var/www/%(apptype)s/%(site)s/releases' % env):
      run('mkdir -p /var/www/%(apptype)s/%(site)s/releases/%(tag)s' % env)
      env.extraction_flags = 'zxf'
      run('tar -%(extraction_flags)s %(remote_tmp)s/%(release_archive)s -C /var/www/%(apptype)s/%(site)s/releases/%(tag)s' % env)

@task
@serial
@roles('web')
def create_release_files_symlink(site, tag):
  print green("===> Symlink shared files to current release...")
  run('ln -nfs /var/lib/sitedata/%(apptype)s/%(site)s/files /var/www/%(apptype)s/%(site)s/releases/%(tag)s/sites/default/files' % env)

@task
@serial
@roles('web')
def create_release_settings_symlink(site, tag):
  print green("===> Symlink settings.php to current release...")
  run('ln -nfs /var/www/%(apptype)s/%(site)s/settings.php /var/www/%(apptype)s/%(site)s/releases/%(tag)s/sites/default/settings.php' % env)

@task
@serial
@roles('web')
def symlink_current_release(site, tag):
  print green("===> Symlinking current release...")
  env.site_symlink = '/var/www/%(apptype)s/%(site)s/current' % env
  env.previous_site_symlink = '/var/www/%(apptype)s/%(site)s/previous' % env
  env.new_previous = ''
  with settings(warn_only=True):
    env.new_previous = run('readlink %(site_symlink)s' % env)
  env.new_current = '/var/www/%(apptype)s/%(site)s/releases/%(tag)s' % env

  """
  If targets are different, set target of current -> previous, and new release -> current
  """
  if (new_previous != new_current):
    if run("test -d %(new_current)s" % env).succeeded:
      run('ln -fns %(new_current)s %(site_symlink)s' % env)
    with settings(warn_only=True):
      if run("test -d %(new_previous)s" % env).succeeded:
        run('ln -fns %(new_previous)s %(previous_site_symlink)s' % env)

@task
@serial
@roles('web')
def rollback_symlink(site, tag):
  print green("===> Settings current release symlink to the value of previous symlink...")
  env.site_symlink = '/var/www/%(apptype)s/%(site)s/current' % env
  env.previous_site_symlink = '/var/www/%(apptype)s/%(site)s/previous' % env
  env.previous = run('readlink %(previous_site_symlink)s' % env)
  run('ln -fns %(previous)s %(site_symlink)s' % env)
  run("rm %(previous_site_symlink)s" % env)

@task
@runs_once
def drush_backup_database(site, tag):
  """
  Backup database to deploy user's home directory with drush
  """
  print green("===> Quick and dirty database backup...")
  backup_time = time.strftime('%Y.%m.%d-%H.%M')
  run('drush -r /var/www/%(apptype)s/%(site)s/current sql-dump --result-file=~/%(site)s_%(stage)s_%(backup_time)s.sql --gzip' % env)

@task
@runs_once
def drush_site_offline(site, tag, version=7):
  """
  Put drupal in maintenance mode
  """
  print green("===> Set site offline...")
  if (env.version == 7):
    run("drush -r /var/www/%(apptype)s/%(site)s/current -y vset maintenance_mode 1" % env)
  elif (env.version == 6):
    run("drush -r /var/www/%(apptype)s/%(site)s/current -y vset site_offline 1" % env)

@task
@runs_once
def drush_site_online(site, tag, version=7):
  """
  Take drupal out of maintenance mode
  """
  print green("===> Set site online...")
  if (env.version == 7):
    run("drush -r /var/www/%(apptype)s/%(site)s/current -y vset maintenance_mode 0" % env)
  elif (env.version == 6):
    run("drush -r /var/www/%(apptype)s/%(site)s/current -y vset site_offline 1" % env)

@task
@runs_once
def drush_feature_revert(site, tag, prompt=True):
  """
  Revert drupal feature via drush
  """
  print green("===> Reverting site features...")
  if (prompt == True):
    """
    Show list of changed features, and then have drush ask whether to continue.
    """
    run("drush -r /var/www/%(apptype)s/%(site)s/current features" % env)
    run("drush -r /var/www/%(apptype)s/%(site)s/current fra" % env)
  else:
    run("drush -r /var/www/%(apptype)s/%(site)s/current -y fra" % env)

@task
@runs_once
def drush_update_database(site, tag, prompt=True):
  """
  Run drupal database updates
  """
  print green("===> Running database updates...")
  command = 'drush -r /var/www/%(apptype)s/%(site)s/current updb' % env
  if (prompt != True):
    command += ' -y'
  run(command))

@task
@runs_once
def drush_cache_clear_all(site, tag):
  print green("===> Running drush cc all...")
  run("drush -r /var/www/%(apptype)s/%(site)s/current cc all" % env)

def mkdir(dir, use_sudo=False):
    """
    Helper function to create directories
    """
    command = 'if [ ! -d %s ]; then mkdir -p %s; fi;' % (dir, dir)
    if (use_sudo == True):
      run(command)
    else:
      sudo(command)

