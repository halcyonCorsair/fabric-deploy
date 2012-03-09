Quick start:

* Copy exampleconfig.py to siteconfig.py in a handy location.
* Update siteconfig.py as required.
* Update copy examplerc to say 'devrc' and update as required

Conventions / Assumptions:

* user/group deploy exist and have correct ssh/key setup
* /var/lib/sitedata/<apptype> exists and is writable by deploy
* /var/lib/sitedata/<apptype>/<sitename> exists and is writable by deploy
* /var/www/<apptype> exists and is writable by deploy
* /var/www/<apptype>/<sitename> exists and is writable by deploy

Getting started:

See the fabric documentation at: http://docs.fabfile.org

Install fabric:

```bash
$ sudo pip install fabric
```


Alias fabric call, add to your ~/.bashrc:

```bash
alias deploy="fab -f /path/to/deploy.py"
```

Example usage:

```bash
  deploy -c devrc deploy:'mytag-20120307-1'
```

  Deploy to an arbitrary server (as long as env.hosts isn't getting overridden):

```bash
  deploy -c devrc -H user@hostname.com deploy:'mytag-20120307-1'
```
