Quick start:

* Copy exampleconfig.py to siteconfig.py in a handy location.
* Update siteconfig.py as required.
* Update copy examplerc to say 'devrc' and update as required

Handy hints:

* Alias fabric call, eg.

```bash
alias deploy="fab -f /path/to/deploy.py"
```

See the fabric documentation at: http://docs.fabfile.org

Example usage:

```bash
  fab -f /path/to/deploy.py -c devrc load_config deploy:'mytag-20120307-1'
```

  Deploy to an arbitrary server (as long as env.hosts isn't getting overridden):

```bash
  fab -f /path/to/deploy.py -c devrc -H user@hostname.com deploy:'mytag-20120307-1'
```
