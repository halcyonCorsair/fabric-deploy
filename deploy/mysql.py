from fabric.api import *
from fabric.colors import green, red, yellow

def database_backup(environment='prod'):
  sudo(
    "mysqldump --single-transaction --opt -Q --host=%s  --user=%s --result-file=%s %s --password=%s" %
    (env.db_host, env.db_user, env.db_result_file, env.db_name, env.db_pass)
  )
  sudo("gzip %s" % env.db_result_file)

# TODO: should this be run on the db server
#@roles('db')
#@task
def create_current_database_symlink():
  sudo("gzip %s" % (env.current_db_backup))
  # set the new previous backup
  with settings(warn_only=True):
    if run("test -L %s/current" % env.db_backup_dir).succeeded:
      new_previous = run('readlink %s/current' % env.site_symlink)
      sudo("ln -fns %s/%s %s/previous" % (env.db_backup_dir, new_previous, env.db_backup_dir))
  # set the new current backup
  sudo("ln -fns %s.gz %s/current" % (env.current_db_backup, env.db_backup_dir))
