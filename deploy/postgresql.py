from fabric.api import *
from fabric.colors import green, red, yellow

def database_backup(environment='prod'):
  sudo("pgdump -Fc -O -x -p %(port)d -H %(host)s -U %(user)s -d %(database)s %(result_file)s" % env.database)
  sudo("gzip %s" % env.database.result_file)

