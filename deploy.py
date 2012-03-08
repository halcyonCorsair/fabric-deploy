from fabric.api import *
from fabric.colors import green, red, yellow
import os, sys, time


env.user = 'autodeploy'
env.shell = '/bin/bash -c'
env.web_root = '/var/www'
env.release_time = time.strftime('%Y.%m.%d-%H.%M')

env.install_tasks = [
  'build_release',
  'upload_release',
  'extract_release',
]

def deploy(tag):
  load_config()
  for task in env.install_tasks:
    execute(task, env.site, tag)

def load_config():
  """Load site config.
  Assume config file is called siteconfig.py and resides in the current directory.
  """
  print green("===> Loading site recipe...")
  directory = os.getcwd()
  sys.path.append(directory)
  import siteconfig
  env.scm_build_dir = '/tmp/%s-site-%s' % (env.apptype, env.site)

def tag_release(site, tag, commit, message=''):
  print green("===> Building the release...")
  tag = 'site-%s-' % (env.release_time)

  # Ensure code directory exists
  with settings(warn_only=True):
    if local('test -d %s' % env.scm_build_dir).failed:
      local('git clone %s %s' % (env.scm_uri, env.scm_build_dir))

  with lcd(env.scm_build_dir):
    # TODO: put git status check here
    if (local("git pull", capture=True)).succeeded:
      if (message == ''):
        local('git tag %s %s' % (tag, commit))
      else:
        local('git tag -m "%s" %s %s' % (message, tag, commit))
  return tag

def build_release(site, tag):
  print green("===> Building the release...")
  release_archive = '%s-site-%s.tar.gz' % (env.apptype, tag)
  env.scm_build_dir = '/tmp/%s-site-%s' % (env.apptype, site)

  # Ensure code directory exists
  with settings(warn_only=True):
    if local('test -d %s' % env.scm_build_dir).failed:
      local('git clone %s %s' % (env.scm_uri, env.scm_build_dir))

  with lcd(env.scm_build_dir):
    # put git status check here
    if (local("git pull", capture=True)).succeeded:
      release_tree = local('git show -s --format=%%h %s' % tag, True)
      local('git archive --format tar %s | gzip > /tmp/%s' % (release_tree, release_archive))

def upload_release(site, tag):
  print green("===> Uploading the release archive...")
  release_archive = '%s-site-%s.tar.gz' % (env.apptype, tag)
  with settings(warn_only=True):
    #if run("test -f /tmp/%s" % release_archive).failed:
    if run("test -f ~/tmp/%s" % release_archive).failed:
      #put('/tmp/%s' % release_archive, '/tmp/')
      put('~/tmp/%s' % release_archive, '/tmp/')
    else:
      abort(red("Release archive doesn't exist, please run build_release again"))

def extract_release(site, tag):
  print green("===> Extracting the release...")
  env.site = site
  env.tag = tag
  release_archive = '%s-site-%s.tar.gz' % (env.apptype, tag)
  with settings(warn_only=True):
    if run("test -f /tmp/%s" % release_archive).failed:
      abort(red("Release archive doesn't exist, please run build_release again"))
    if run('test -d /var/www/%(apptype)s/%(site)s/releases/%(tag)s' % env).succeeded:
      abort(red("Release directory already exists"))
  if run('test -d /var/www/%(apptype)s/%(site)s/releases' % env).succeeded:
    with cd('/var/www/%s/%s/releases' % (env.apptype, site)):
      run('mkdir -p /var/www/%s/%s/releases/%s' % (env.apptype, site, tag))
      run('tar -zxf /tmp/%s -C /var/www/%s/%s/releases/%s' % (release_archive, env.apptype, site, tag))

def create_release_files_symlink(site, tag):
  run('ln -nfs /var/lib/sitedata/%s/%s/files /var/www/%s/%s/releases/%s/sites/default/files' % (env.apptype, site, env.apptype, site, tag))

def create_release_settings_symlink(site, tag):
  run('ln -nfs /var/www/%s/%s/settings.php /var/www/%s/%s/releases/%s/sites/default/settings.php' % (env.apptype, site, env.apptype, site, tag))

def symlink_current_release(site, tag):
  print green("===> Symlinking current release...")
  site_symlink = '/var/www/%s/%s/current' % (env.apptype, site)
  previous_site_symlink = '/var/www/%s/%s/previous' % (env.apptype, site)
  new_previous = ''
  with settings(warn_only=True):
    new_previous = run('readlink %s' % site_symlink)
  new_current = '/var/www/%s/%s/releases/%s' % (env.apptype, site, tag)

  if (new_previous != new_current):
    if run("test -d %s" % new_current).succeeded:
      run('ln -fns %s %s' % (new_current, site_symlink))
    with settings(warn_only=True):
      if run("test -d %s" % new_previous).succeeded:
        run('ln -fns %s %s' % (new_previous, previous_site_symlink))

def backup_database(site):
  print green("===> Quick and dirty database backup...")
  run('drush -r /var/www/%s/%s/current sql-dump --result-file=~/%s-`date +%Y.%m.%d-%H.%M`.sql --gzip' % (env.apptype, site, site))

def site_offline(site):
  print green("===> Set site offline...")
  run("drush -r /var/www/%s/%s/current -y vset maintenance_mode 1" % (env.apptype, site))

def site_online(site):
  print green("===> Set site online...")
  run("drush -r /var/www/%s/%s/current -y vset maintenance_mode 0" % (env.apptype, site))

def drush_revert_features(site):
  print green("===> Reverting site features...")
  run("drush -r /var/www/%s/%s/current fra -y" % (env.apptype, site))

def drush_update_database(site):
  print green("===> Running database updates...")
  run("drush -r /var/www/%s/%s/current updb" % (env.apptype, site))

def drush_clear_cache_all(site):
  print green("===> Running drush cc all...")
  run("drush -r /var/www/%s/%s/current cc all" % (env.apptype, site))

