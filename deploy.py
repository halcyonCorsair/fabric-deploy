from fabric.api import *
from fabric.colors import green, red, yellow
import os, sys, time

env.user = 'autodeploy'
env.shell = '/bin/bash -c'
env.web_root = '/var/www'
env.release_time = time.strftime('%Y.%m.%d-%H.%M')
env.local_tmp = '/tmp'
env.remote_tmp = '/tmp'

env.pre_deploy_tasks = [
]

env.deploy_tasks = [
  'build_release',
  'upload_release',
  'extract_release',
  'symlink_current_release',
  'create_release_files_symlink',
  'create_release_settings_symlink',
]

env.post_deploy_tasks = [
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
  env.scm_build_dir = '%s/%s-site-%s' % (env.local_tmp, env.apptype, env.site)

@task
def tag_release(site, tag, commit, message=''):
  print green("===> Building the release...")
  tag = 'site-%s-' % (env.release_time)

  # Ensure code directory exists
  with settings(warn_only=True):
    if local('test -d %s' % env.scm_build_dir).failed:
      local('git clone %s %s' % (env.repository, env.scm_build_dir))

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
  release_archive = '%s-site-%s_%s.tar.gz' % (env.apptype, site, tag)
  env.scm_build_dir = '%s/%s-site-%s' % (env.local_tmp, env.apptype, site)

  # Ensure code directory exists
  with settings(warn_only=True):
    if local('test -d %s' % env.scm_build_dir).failed:
      local('git clone %s %s' % (env.repository, env.scm_build_dir))

  with lcd(env.scm_build_dir):
    # put git status check here
    if (local("git pull", capture=True)).succeeded:
      release_tree = local('git show-ref --tags -s "%s"' % tag, True)
      local('git archive --format tar %s | gzip > %s/%s' % (release_tree, env.local_tmp, release_archive))

@task
def upload_release(site, tag):
  print green("===> Uploading the release archive...")
  release_archive = '%s-site-%s_%s.tar.gz' % (env.apptype, site, tag)
  with settings(warn_only=True):
    if run("test -f %s/%s" % (env.remote_tmp, release_archive)).failed:
      put('%s/%s' % (env.local_tmp, release_archive), '/tmp/')

@task
def extract_release(site, tag):
  print green("===> Extracting the release...")
  env.site = site
  env.tag = tag
  release_archive = '%s-site-%s_%s.tar.gz' % (env.apptype, site, tag)
  with settings(warn_only=True):
    if run("test -f %s/%s" % (env.remote_tmp, release_archive)).failed:
      abort(red("Release archive doesn't exist, please run build_release again"))
    if run('test -d /var/www/%(apptype)s/%(site)s/releases/%(tag)s' % env).succeeded:
      abort(red("Release directory already exists"))
  if run('test -d /var/www/%(apptype)s/%(site)s/releases' % env).succeeded:
    with cd('/var/www/%s/%s/releases' % (env.apptype, site)):
      run('mkdir -p /var/www/%s/%s/releases/%s' % (env.apptype, site, tag))
      flags = 'zxf'
      run('tar -%s %s/%s -C /var/www/%s/%s/releases/%s' % (flags, env.remote_tmp, release_archive, env.apptype, site, tag))

@task
def create_release_files_symlink(site, tag):
  print green("===> Symlink shared files to current release...")
  run('ln -nfs /var/lib/sitedata/%s/%s/files /var/www/%s/%s/releases/%s/sites/default/files' % (env.apptype, site, env.apptype, site, tag))

@task
def create_release_settings_symlink(site, tag):
  print green("===> Symlink settings.php to current release...")
  run('ln -nfs /var/www/%s/%s/settings.php /var/www/%s/%s/releases/%s/sites/default/settings.php' % (env.apptype, site, env.apptype, site, tag))

@task
def symlink_current_release(site, tag):
  print green("===> Symlinking current release...")
  site_symlink = '/var/www/%s/%s/current' % (env.apptype, site)
  previous_site_symlink = '/var/www/%s/%s/previous' % (env.apptype, site)
  new_previous = ''
  with settings(warn_only=True):
    new_previous = run('readlink %s' % site_symlink)
  new_current = '/var/www/%s/%s/releases/%s' % (env.apptype, site, tag)

  """
  If targets are different, set target of current -> previous, and new release -> current
  """
  if (new_previous != new_current):
    if run("test -d %s" % new_current).succeeded:
      run('ln -fns %s %s' % (new_current, site_symlink))
    with settings(warn_only=True):
      if run("test -d %s" % new_previous).succeeded:
        run('ln -fns %s %s' % (new_previous, previous_site_symlink))

@task
def rollback_symlink(site, tag):
  print green("===> Settings current release symlink to the value of previous symlink...")
  site_symlink = '/var/www/%s/%s/current' % (env.apptype, site)
  previous_site_symlink = '/var/www/%s/%s/previous' % (env.apptype, site)
  previous = run('readlink %s' % previous_site_symlink)
  run('ln -fns %s %s' % previous, site_symlink)
  run("rm %s" % previous_site_symlink)

@task
@runs_once
def drush_backup_database(site, tag):
  print green("===> Quick and dirty database backup...")
  import time
  backup_time = time.strftime('%Y.%m.%d-%H.%M')
  run('drush -r /var/www/%s/%s/current sql-dump --result-file=~/%s_%s_%s.sql --gzip' % (env.apptype, site, site, env.stage, backup_time))

@task
@runs_once
def drush_site_offline(site, tag, version=7):
  print green("===> Set site offline...")
  if (env.version == 7):
    run("drush -r /var/www/%s/%s/current -y vset maintenance_mode 1" % (env.apptype, site))
  elif (env.version == 6):
    run("drush -r /var/www/%s/%s/current -y vset site_offline 1" % (env.apptype, site))

@task
@runs_once
def drush_site_online(site, tag, version=7):
  print green("===> Set site online...")
  if (env.version == 7):
    run("drush -r /var/www/%s/%s/current -y vset maintenance_mode 0" % (env.apptype, site))
  elif (env.version == 6):
    run("drush -r /var/www/%s/%s/current -y vset site_offline 1" % (env.apptype, site))

@task
@runs_once
def drush_feature_revert(site, tag, prompt=True):
  print green("===> Reverting site features...")
  if (prompt == True):
    """
    Show list of changed features, and then have drush ask whether to continue.
    """
    run("drush -r /var/www/%s/%s/current features" % (env.apptype, site))
    run("drush -r /var/www/%s/%s/current fra" % (env.apptype, site))
  else:
    run("drush -r /var/www/%s/%s/current -y fra" % (env.apptype, site))

@task
@runs_once
def drush_update_database(site, tag, prompt=True):
  print green("===> Running database updates...")
  if (prompt == True):
    run("drush -r /var/www/%s/%s/current updb" % (env.apptype, site))
  else:
    run("drush -r /var/www/%s/%s/current -y updb" % (env.apptype, site))

@task
@runs_once
def drush_cache_clear_all(site, tag):
  print green("===> Running drush cc all...")
  run("drush -r /var/www/%s/%s/current cc all" % (env.apptype, site))

def mkdir(dir, use_sudo=False):
    # Create a directory if it doesn't exist
    if (use_sudo == True):
      run('if [ ! -d %s ]; then mkdir -p %s; fi;' % (dir, dir))
    else:
      sudo('if [ ! -d %s ]; then mkdir -p %s; fi;' % (dir, dir))

