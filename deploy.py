from fabric.api import *
from fabric.colors import green, red, yellow
import os, sys, time

env.user = 'drupaldeploy'
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
  'create_release_files_symlink',
  'create_release_settings_symlink',
  'drush_site_offline',
  'drush_backup_database',
  'symlink_current_release',
  'drush_update_database',
  #'drush_feature_revert',
  'drush_cache_clear_all',
  'drush_site_online',
]

@task
def list_deploy_tasks():
  """List your deployment tasks
  Run load_config task first to see what tasks your site would run
  """
  print yellow("\n".join(env.deploy_tasks))

@task
def deploy(tag):
  """Deploy your site
  Calls load_config(), then proceeds to run through the defined deployment tasks.
  """
  load_config()
  env.scm_build_dir = '%(local_tmp)s/%(apptype)s-site-%(site)s' % env
  set_sitetag(env.site, tag)

  print(green("=> Beginning deploy"))
  list_deploy_tasks()

  for task in env.deploy_tasks:
    if ('feature_revert' in task or 'update_database' in task):
      execute(task, prompt=False)
    else:
      execute(task)

@task
def load_config():
  """Load site config.
  Assume config file is called siteconfig.py and resides in the current directory.
  Can be overridden by setting the siteconfig_dir env variable, eg.: --set siteconfig_dir=/path/to/your/siteconfig
  """
  print green("===> Loading site recipe...")
  try:
    env.siteconfig_dir
  except AttributeError:
    env.siteconfig_dir = None

  if (env.siteconfig_dir == None):
    directory = os.getcwd()
  else:
    directory = env.siteconfig_dir
  sys.path.append(directory)
  import siteconfig

def set_sitetag(site=None, tag=None):
  if (not site is None):
    env.site = site
  if (not tag is None):
    env.tag = tag

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
def build_release(tag=None, site=None):
  """Build your release tarball
  Keyword arguments: tag, site
  Standalone Usage: load_config build_release:tag='mytag'
  Required environment variables: apptype, local_tmp, repository, tag, site
  - tag, site can be set during build_release call
  """
  set_sitetag(site, tag)

  print green("===> Building the release...")
  env.release_archive = '%(apptype)s-site-%(site)s_%(tag)s.tar.gz' % env
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
def upload_release(site=None, tag=None):
  set_sitetag(site, tag)

  print green("===> Uploading the release archive...")
  env.release_archive = '%(apptype)s-site-%(site)s_%(tag)s.tar.gz' % env
  with settings(warn_only=True):
    if run("test -f %(remote_tmp)s/%(release_archive)s" % env).failed:
      put('%(local_tmp)s/%(release_archive)s' % env, '/tmp/')

@task
@serial
@roles('web')
def extract_release(site=None, tag=None):
  set_sitetag(site, tag)

  print green("===> Extracting the release...")
  env.release_archive = '%(apptype)s-site-%(site)s_%(tag)s.tar.gz' % env
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
def create_release_files_symlink(site=None, tag=None):
  set_sitetag(site, tag)

  print green("===> Symlink shared files to current release...")
  run('ln -nfs /var/lib/sitedata/%(apptype)s/%(site)s/files /var/www/%(apptype)s/%(site)s/releases/%(tag)s/sites/default/files' % env)

@task
@serial
@roles('web')
def create_release_settings_symlink(site=None, tag=None):
  set_sitetag(site, tag)

  print green("===> Symlink settings.php to current release...")
  run('ln -nfs /var/www/%(apptype)s/%(site)s/settings.php /var/www/%(apptype)s/%(site)s/releases/%(tag)s/sites/default/settings.php' % env)

@task
@serial
@roles('web')
def symlink_current_release(site=None, tag=None):
  set_sitetag(site, tag)

  print green("===> Symlinking current release...")
  env.site_symlink = '/var/www/%(apptype)s/%(site)s/current' % env
  env.previous_site_symlink = '/var/www/%(apptype)s/%(site)s/previous' % env
  env.new_previous = ''
  with settings(warn_only=True):
    env.new_previous = run('readlink %(site_symlink)s' % env)

  env.new_current = '/var/www/%(apptype)s/%(site)s/releases/%(tag)s' % env

  # If targets are different, set target of current -> previous, and new release -> current
  if (env.new_previous != env.new_current):
    if run("test -d %(new_current)s" % env).succeeded:
      run('ln -fns %(new_current)s %(site_symlink)s' % env)
    with settings(warn_only=True):
      if run("test -d %(new_previous)s" % env).succeeded:
        run('ln -fns %(new_previous)s %(previous_site_symlink)s' % env)

@task
@serial
@roles('web')
def rollback_symlink(site=None, tag=None):
  set_sitetag(site, tag)

  print green("===> Settings current release symlink to the value of previous symlink...")
  env.site_symlink = '/var/www/%(apptype)s/%(site)s/current' % env
  env.previous_site_symlink = '/var/www/%(apptype)s/%(site)s/previous' % env
  env.previous = run('readlink %(previous_site_symlink)s' % env)
  run('ln -fns %(previous)s %(site_symlink)s' % env)
  run("rm %(previous_site_symlink)s" % env)

@task
@runs_once
@roles('web')
def drush_backup_database(site=None, tag=None):
  """
  Backup database to deploy user's home directory with drush
  """
  set_sitetag(site, tag)

  print green("===> Quick and dirty database backup...")
  env.backup_time = time.strftime('%Y.%m.%d-%H.%M')
  run('drush -u 1 -r /var/www/%(apptype)s/%(site)s/current sql-dump --result-file=~/%(site)s_%(stage)s_%(backup_time)s.sql --gzip' % env)

@task
@runs_once
@roles('web')
def drush_site_offline(site=None, tag=None, version=7):
  """
  Put drupal in maintenance mode
  """
  set_sitetag(site, tag)

  print green("===> Set site offline...")
  if (env.version == 7):
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current -y vset maintenance_mode 1" % env)
  elif (env.version == 6):
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current -y vset site_offline 1" % env)

@task
@runs_once
@roles('web')
def drush_site_online(site=None, tag=None, version=7):
  """
  Take drupal out of maintenance mode
  """
  set_sitetag(site, tag)

  print green("===> Set site online...")
  if (env.version == 7):
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current -y vset maintenance_mode 0" % env)
  elif (env.version == 6):
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current -y vset site_offline 0" % env)

@task
@runs_once
@roles('web')
def drush_features(site=None):
  """
  List the available site features, and their state
  """
  set_sitetag(site)
  run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current features" % env)

@task
@runs_once
@roles('web')
def drush_feature_diff(feature, site=None):
  """Show drupal feature differences
  Keyword arguments: feature, site, prompt, force
  - feature: The feature to check (required)
  """
  set_sitetag(site)

  print green("===> Running feature-diff...")
  env.drupal_feature = feature
  run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current fd %(drupal_feature)s" % env)

@task
@runs_once
@roles('web')
def drush_feature_revert(feature=None, site=None, prompt=True, force=False):
  """Revert drupal feature via drush
  Keyword arguments: feature, site, prompt, force
  - feature: None; If set, revert that feature.  Otherwise, loop through env.revertable_features (if it exists)
  - prompt: True; Set to false to use -y for drush
  - force: False; See drush help feature-revert
  """
  set_sitetag(site)

  env.force_revert_string = ''
  if (force == True or force == 'True'):
    env.force_revert_string = '--force'

  env.prompt_string = ''
  if (prompt == False or prompt == 'False'):
    env.prompt_string = '-y'

  print green("===> Reverting site feature(s)...")
  if (not feature == None):
    env.drupal_feature = feature
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current %(prompt_string)s fr %(force_revert_string)s %(drupal_feature)s" % env)
  else:
    try:
      env.revertable_features
    except AttributeError:
      env.revertable_features = None

    if (not env.revertable_features == None):
      for feature in env.revertable_features:
        env.drupal_feature = feature
        run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current %(prompt_string)s fr %(force_revert_string)s %(drupal_feature)s" % env)
    else:
      print(yellow('[warning]: ') + 'Nothing to revert, no argument, and env.revertable_features was empty.')

@task
@runs_once
@roles('web')
def drush_feature_revert_all(site=None, prompt=True, force=False):
  """
  Revert ALL drupal feature via drush
  """
  # TODO: Add the ability to exclude features (per: drush help fra)
  set_sitetag(site)

  env.force_revert_string = ''
  if (force == True or force == 'True'):
    env.force_revert_string = '--force'

  env.prompt_string = ''
  if (prompt == False or prompt == 'False'):
    env.prompt_string = '-y'

  print green("===> Reverting site feature(s)...")
  if (prompt == True or prompt == 'True'):
    """
    Show list of changed features prior to revert
    """
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current features" % env)

  run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current %(prompt_string)s fra %(force_revert_string)s" % env)

@task
@runs_once
@roles('web')
def drush_cron(site=None, tag=None, prompt=True):
  """
  Use drush to enable cron
  """
  set_sitetag(site, tag)

  print green("===> Running cron via drush...")
  run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current cron" % env)

@task
@runs_once
@roles('web')
def drush_enable_module(drupal_module, site=None, tag=None, prompt=True):
  """
  Enable drupal module via drush
  """
  set_sitetag(site, tag)

  env.drupal_module = drupal_module

  print green("===> Enabling drupal module...")
  if (prompt == True or prompt == 'True'):
    """
    Show list of changed features, and then have drush ask whether to continue.
    """
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current en %(drupal_module)s" % env)
  else:
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current -y en %(drupal_module)s" % env)

@task
@runs_once
@roles('web')
def drush_disable_module(drupal_module, site=None, tag=None, prompt=True):
  """
  Enable drupal module via drush
  """
  set_sitetag(site, tag)

  env.drupal_module = drupal_module

  print green("===> Enabling drupal module...")
  if (prompt == True or prompt == 'True'):
    """
    Show list of changed features, and then have drush ask whether to continue.
    """
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current dis %(drupal_module)s" % env)
  else:
    run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current -y dis %(drupal_module)s" % env)

@task
@runs_once
@roles('web')
def drush_update_database(site=None, tag=None, prompt=True):
  """
  Run drupal database updates via: drush updb
  """
  set_sitetag(site, tag)

  print green("===> Running database updates...")
  command = 'drush -u 1 -r /var/www/%(apptype)s/%(site)s/current updb' % env
  if (prompt != True):
    command += ' -y'
  run(command)

@task
@runs_once
@roles('web')
def drush_cache_clear_all(site=None, tag=None):
  """
  Run drupal cache clear via: drush cc all
  """
  set_sitetag(site, tag)

  print green("===> Running drush cache clear all...")
  run("drush -u 1 -r /var/www/%(apptype)s/%(site)s/current cc all" % env)

def mkdir(dir, use_sudo=False):
  """
  Helper function to create directories
  """
  command = 'if [ ! -d %s ]; then mkdir -p %s; fi;' % (dir, dir)
  if (use_sudo == True):
    sudo(command)
  else:
    run(command)

