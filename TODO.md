TODO:

* Put release_archive in env
* -y for updb? prompt?
* Add notes, re: pre-requisites (eg. deployment directory structure)
** Assumptions, eg. /var/lib/sitedata/<sitename>, /var/www/<appname>/releases
* Fix up .md files
* After loading, print config?
* Mention git attributes for git archive
* For drupal: ensure files directory and settings.php are excluded by git archive
* ! Test for, and handle failure of tasks, eg. symlinking
* site online/offline for d6
* Drush defaults: assume human, or automated? eg. prompt, or not?
* Omit cache tables from database backup
* Import more selectively
* Logging
* Look at yyuus fabric_deploy (yyuu.fabric_deploy)

Recipe future possibilities:

* Turn into xml / validate against xsd, show what variables / overrides are available, etc
* Store in database - manage via admin app, eg. elearning
