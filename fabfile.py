from fabric.api import *
import os
import sys
import time

env.user = 'autodeploy'
env.shell = '/bin/bash -c'
env.release_time = time.strftime('%Y.%m.%d-%H.%M')

def test(tag):
  #env.hosts = env.web_hosts
  #execute('build_release', env.site, tag)
  #execute('upload_release', env.site, tag)
  execute('extract_release', env.site, tag)

def load_config(config_name, stage='dev'):
  env.stage = stage
  directory = os.getcwd()
  sys.path.append(directory)
  __import__(config_name)

def tag_release(site, tag, commit):
  pass

# TODO: needs appropriate gitconfig, etc
# TODO: ensure files directory and settings.php are excluded by git archive
def build_release(site, tag):
  print "===> Building the release..."
  release_archive = 'drupal-site-%s.tar.gz' % tag
  scm_build_dir = '/tmp/drupal-site-%s' % site

  # Ensure code directory exists
  with settings(warn_only=True):
    if local('test -d %s' % scm_build_dir).failed:
      local('git clone %s %s' % (env.scm_uri, scm_build_dir))

  with lcd(scm_build_dir):
    # put git status check here
    if (local("git pull", capture=True)).succeeded:
      release_tree = local('git show -s --format=%%h %s' % tag, True)
      local('git archive --remote="%s" --format tar %s | gzip > /tmp/%s' % (env.scm_uri, release_tree, release_archive))

def upload_release(site, tag):
  print "===> Installing the site for the first time..."
  release_archive = 'drupal-site-%s.tar.gz' % tag
  with settings(warn_only=True):
    if run("test -f /tmp/%s" % release_archive).failed:
      put('/tmp/%s' % release_archive, '/tmp/')
    else:
      abort(red("Release archive doesn't exist, please run build_release again"))

def extract_release(site, tag):
  print "===> Extracting the release..."
  release_archive = 'drupal-site-%s.tar.gz' % tag
  with settings(warn_only=True):
    if run("test -f /tmp/%s" % release_archive).failed:
      abort(red("Release archive doesn't exist, please run build_release again"))
  with cd('/var/www/drupal/%s/releases' % site):
    run('mkdir -p /var/www/drupal/%s/releases/%s' % (site, tag))
    run('tar -zxf /tmp/%s -C /var/www/drupal/%s/releases/%s' % (release_archive, site, tag))

def create_release_files_symlink(site, tag):
  run('ln -nfs /var/lib/sitedata/drupal/%s/files /var/www/drupal/%s/releases/%s/sites/default/files' % (site, site, tag))

def create_release_settings_symlink(site, tag):
  run('ln -nfs /var/www/drupal/%s/settings.php /var/www/drupal/%s/releases/%s/sites/default/settings.php' % (site, site, tag))

def symlinks_current_release(site, tag):
  print "===> Symlinking current release..."
  site_symlink = '/var/www/drupal/%s/current' % site
  previous_site_symlink = '/var/www/drupal/%s/previous' % site
  new_previous = run('readlink %s' % site_symlink)
  new_current = '/var/www/drupal/%s/releases/%s' % (site, tag)

  if (new_previous != new_current):
    if run("test -d %s" % new_current).succeeded:
      run('ln -fns %s %s' % (new_current, site_symlink))
    if run("test -d %s" % new_previous).succeeded:
      run('ln -fns %s %s' % (new_previous, previous_site_symlink))

def backup_database(site):
  print "===> Quick and dirty database backup..."
  run('drush -r /var/www/drupal/%s/current sql-dump --result-file=~/%s-`date +%Y.%m.%d-%H.%M`.sql --gzip' % (site, site))

def site_offline(site):
  print "===> Set site offline..."
  run("drush -r /var/www/drupal/%s/current -y vset maintenance_mode 1" % site)

def site_online(site):
  print "===> Set site online..."
  run("drush -r /var/www/drupal/%s/current -y vset maintenance_mode 0" % site)

def drush_revert_features(site):
  print "===> Reverting site features..."
  run("drush -r /var/www/drupal/%s/current fra -y" % site)

def drush_update_database(site):
  print "===> Running database updates..."
  run("drush -r /var/www/drupal/%s/current updb" % site)

def drush_clear_cache_all(site):
  print "===> Running drush cc all..."
  run("drush -r /var/www/drupal/%s/current cc all" % site)

