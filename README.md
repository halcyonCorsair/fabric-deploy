Quick start:
* Copy exampleconfig.py to siteconfig.py in a handy location.
* Update siteconfig.py as required.
* Update copy examplerc to say 'devrc' and update as required

Handy hints:
* Alias 'deploy'
'''
alias deploy="fab -f /path/to/deploy.py"
'''

See the fabric documentation at: http://docs.fabfile.org

Example usage:
  fab -f /path/to/deploy.py -c devrc load_config test:'mytag-20120307-1'

  Deploy to an arbitrary server (as long as env.hosts isn't getting overridden):
  fab -f /path/to/deploy.py -c devrc -H user@hostname.com load_config test:'mytag-20120307-1'
