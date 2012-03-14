TODO:

* Write documentation around overall process: cfgmgr -> puppet, then deploy
* Write puppet modules
* Rollback
* Add more comments/documentation
** Change exampleconfig to use ReSTructured text with the first string as a comment, per discussion with Tom

* Check, re: drush status return codes
* Check, re: enabled modules before running drush fr for example

* Turn site and tag into kwargs?
* Add checkargs or getargs type function

* Test parallel execution
* healthchecks, load balancers?
* Git checkout bare?
* Hiding/show relevant output
* Log in parallel with console
* Put release_archive in env
* After loading, print config?
* Mention git attributes for git archive
* For drupal: ensure files directory and settings.php are excluded by git archive
* Omit cache tables from database backup
* Import more selectively
* Logging
* Look at yyuus fabric_deploy (yyuu.fabric_deploy)
* Add more verbose output, eg. zxvf vs zxf

* Parallel execution - capture output, display once where required, eg. puppet runs
* Kick other services?

Recipe future possibilities:

* Turn into xml / validate against xsd, show what variables / overrides are available, etc
* Store in database - manage via admin app, eg. elearning

BUGS:

