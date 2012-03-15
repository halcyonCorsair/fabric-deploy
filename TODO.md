TODO:

* Write documentation around overall process: cfgmgr -> puppet, then deploy
* Add db and files backup functions
* Add drush run as user
* Rollback
* Add more comments/documentation
** Change exampleconfig to use ReSTructured text with the first string as a comment, per discussion with Tom
* Check, re: drush status return codes
* Check, re: enabled modules before running drush fr for example
* Write some tests
* Add checkargs or getargs type function
* Test parallel execution
* healthchecks, load balancers?
* Git checkout bare?
* Hiding/show relevant output
* Log in parallel with console
* After loading, print config?
* Mention git attributes for git archive
* Omit cache tables from database backup
* Import more selectively
* Logging
* Add more verbose output, eg. zxvf vs zxf
* Look at yyuus fabric_deploy (yyuu.fabric_deploy)
* For drupal: ensure files directory and settings.php are excluded by git archive
* Parallel execution - capture output, display once where required, eg. puppet runs
* Kick other services?

Recipe future possibilities:
* Store in database - manage via admin app, eg. elearning

BUGS:

