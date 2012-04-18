TODO:

* Unsymlink settings.php from old releases to prevent execution of old code
* Git checkout bare?
* Write documentation around overall process: cfgmgr -> puppet, then deploy
* Add db and files backup functions
* Add drush run as user
* Rollback
* Add more comments/documentation
* Change exampleconfig to use ReSTructured text with the first string as a comment, per discussion with Tom
* Check, re: drush status return codes
* Check, re: enabled modules before running drush fr for example
* Write some tests
* healthchecks, load balancers?
* Hiding/show relevant output
* Log in parallel with console
* After loading, print config?
* Mention git attributes for git archive
* Omit cache tables from database backup
* Import more selectively
* Logging
* Add more verbose output, eg. zxvf vs zxf

* For drupal: ensure files directory and settings.php are excluded by git archive
* Parallel execution - capture output, display once where required, eg. puppet runs
* Kick other services?

Recipe future possibilities:
* Store in database - manage via admin app, eg. elearning

BUGS:

