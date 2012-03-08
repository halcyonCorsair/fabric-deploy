from fabric.api import *
from fabric.colors import green, red, yellow

def create_config_symlink():
  with cd('%s' % env.release_dir):
    # create config symlink
    with settings(warn_only=True):
      if run("test -d %s/config" % env.release_dir).succeeded:
        sudo("cp -v %s/global.ini.php %s" % (env.release_dir + '/config', env.site_shared_config_dir))
        sudo("cp -v %s/config.ini.sample.php %s" % (env.release_dir + '/config', env.site_shared_config_dir))
        sudo("rm -vrf %s/config" % env.release_dir)
      if run("test -L %s/config" % env.release_dir).failed:
        sudo("ln -s %s %s/config" % (env.site_shared_config_dir, env.release_dir))

def create_tmp_symlink():
  with cd('%s' % env.release_dir):
    # create tmp symlink
    with settings(warn_only=True):
      if run("test -d %s/tmp" % env.release_dir).succeeded:
        sudo("rm -vrf %s/tmp" % env.release_dir)
      if run("test -L %s/tmp" % env.release_dir).failed:
        sudo("ln -s %s %s/tmp" % (env.site_shared_tmp_dir, env.release_dir))

## disable piwik tracking and user interface
def site_offline():
  config_file = env.site_symlink + '/config/config.ini.php'

  # Turn on maintenance mode
  if (not contains(config_file, '\[General\]')):
    append(config_file, '[General]\nmaintenance_mode = 1', use_sudo=True)
  elif (not contains(config_file, 'maintenance_mode = 1')):
    sed(config_file, '\[General\]', '[General]\\nmaintenance_mode = 1', use_sudo=True)
  else:
    uncomment(config_file, 'maintenance_mode = 1', use_sudo=True, char=';')

  # Stop recording statistics
  if (not contains(config_file, '\[Tracker\]')):
    append(config_file, '[Tracker]\nrecord_statistics = 0', use_sudo=True)
  elif (not contains(config_file, 'record_statistics = 0')):
    sed(config_file, '\[Tracker\]', '[Tracker]\\nrecord_statistics = 0', use_sudo=True)
  else:
    uncomment(config_file, 'record_statistics = 0', use_sudo=True, char=';')

## enable piwik tracking and user interface
def site_online():
  config_file = env.site_symlink + '/config/config.ini.php'
  # Turn off maintenance mode; [General] section
  comment(config_file, 'maintenance_mode = 1', use_sudo=True, char=';')
  # Restart recording statistics; [Tracker] section
  comment(config_file, 'record_statistics = 0', use_sudo=True, char=';')

def db_update():
  sudo('php %s/index.php -- "module=CoreUpdater"' % env.site_symlink, user='piwik-site-mohpub')
  # this doesn't return an error on error!

def switch_symlinks():
  new_previous = run('readlink %s' % env.site_symlink)
  new_current = env.release_dir

def check_dirs():
    # Create application specific directories
    print(green("Checking required directories are in place"))
    mkdir(env.releases_dir)
    mkdir(env.shared_config_dir)
    mkdir(env.shared_tmp_dir)
    #mkdir(env.app_log_dir)
