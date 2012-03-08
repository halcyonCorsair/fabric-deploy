from fabric.api import *
from fabric.colors import green, red, yellow

def backup_database(site):
  print green("===> Quick and dirty database backup...")
  run('drush -r /var/www/%s/%s/current sql-dump --result-file=~/%s-`date +%Y.%m.%d-%H.%M`.sql --gzip' % (env.apptype, site, site))

def site_offline(site, version=7):
  print green("===> Set site offline...")
  if (version == 7):
    run("drush -r /var/www/%s/%s/current -y vset maintenance_mode 1" % (env.apptype, site))
  elif (version == 6):
    run("drush -r /var/www/%s/%s/current -y vset site_offline 1" % (env.apptype, site))

def site_online(site, version=7):
  print green("===> Set site online...")
  if (version == 7):
    run("drush -r /var/www/%s/%s/current -y vset maintenance_mode 0" % (env.apptype, site))
  elif (version == 6):
    run("drush -r /var/www/%s/%s/current -y vset site_offline 1" % (env.apptype, site))

def revert_features(site, prompt=True):
  print green("===> Reverting site features...")
  if (prompt):
    """
    Show list of changed features, and then have drush ask whether to continue.
    """
    run("drush -r /var/www/%s/%s/current features" % (env.apptype, site))
    run("drush -r /var/www/%s/%s/current fra" % (env.apptype, site))
  else:
    run("drush -r /var/www/%s/%s/current -y fra" % (env.apptype, site))

def update_database(site, prompt=True):
  print green("===> Running database updates...")
  if (prompt):
    run("drush -r /var/www/%s/%s/current updb" % (env.apptype, site))
  else:
    run("drush -r /var/www/%s/%s/current -y updb" % (env.apptype, site))

def cache_clear_all(site):
  print green("===> Running drush cc all...")
  run("drush -r /var/www/%s/%s/current cc all" % (env.apptype, site))


