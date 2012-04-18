Conventions / Assumptions:

* user/group deploy exist and have correct ssh/key setup
* /var/lib/sitedata/\<apptype\> exists
* /var/lib/sitedata/\<apptype\>/\<sitename\> exists
* /var/lib/sitedata/\<apptype\>/\<sitename\>/files exists and is writable by deploy
* /var/www/\<apptype\> exists
* /var/www/\<apptype\>/\<sitename\> exists and is writable by deploy
* /var/www/\<apptype\>/\<sitename\>/settings.php exists
* /var/www/\<apptype\>/\<sitename\>/releases exists and is writable by deploy
* Git tags do NOT contain slashes

Getting started:

See the fabric documentation at: http://docs.fabfile.org

Install fabric:

```bash
$ sudo pip install fabric
```

Copy exampleconfig.py to siteconfig.py in a handy location.

Update siteconfig.py as required.

Alias fabric call, add to your ~/.bashrc:

```bash
  alias deploy="fab -f /path/to/deploy.py"
```

Example usage:

```bash
  deploy --set stage=dev deploy:'mytag-20120307-1'
```

  Deploy to an arbitrary server (as long as env.hosts isn&#39;t getting overridden):

```bash
  deploy --set stage=dev -H user@hostname.com deploy:'mytag-20120307-1'
```

  To run an arbitrary command you must first load config:

```bash
  deploy --set stage=dev load_config build_release:'mytag-20120307-1'
```

  Get information about the available commands:

```bash
  deploy -l
```

  Get information about a command:

```bash
  deploy -d load_config
```

  To show debugging information (see fabric&#39;s documentation on output levels):

```bash
  deploy --show=debug
```
