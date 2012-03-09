Conventions / Assumptions:

* user/group deploy exist and have correct ssh/key setup
* /var/lib/sitedata/%lt;apptype&gt; exists
* /var/lib/sitedata/%lt;apptype&gt;/&lt;sitename&gt; exists
* /var/lib/sitedata/%lt;apptype&gt;/&lt;sitename&gt;/files exists and is writable by deploy
* /var/lib/sitedata/%lt;apptype&gt;/&lt;sitename&gt;/settings.php exists
* /var/www/&lt;apptype&gt; exists
* /var/www/&lt;apptype&gt;/&lt;sitename&gt; exists and is writable by deploy
* /var/www/&lt;apptype&gt;/&lt;sitename&gt;/releases exists and is writable by deploy
* Git tags do NOT contain slashes

Getting started:

See the fabric documentation at: http://docs.fabfile.org

Install fabric:

```bash
$ sudo pip install fabric
```

Copy exampleconfig.py to siteconfig.py in a handy location.

Update siteconfig.py as required.

Copy examplerc to '&lt;environment&rt;rc' and update as required.

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

  To run an arbitrary command you must first load config:

```bash
  deploy -c devrc load_config build_release:'mytag-20120307-1'
```

