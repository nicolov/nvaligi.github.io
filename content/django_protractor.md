Title: Continous integration with Django and Protractor
Date: 2015-06-10
Category: Web Backend Django

Continous integration is a catchy term to refer to the software engineering practice of frequently committing to the `master` branch and running automated tests. Failing builds are tagged so that developers can (in theory) immediately drop everything they are doing to fix them.

Besides the criticisms one could raise from an organizational perspective (a nice analysis is [here](http://www.yegor256.com/2014/10/08/continuous-integration-is-dead.html)), doing CI right means having a reliable set of automated tests that run with appropriate database-backed data. This is somewhat of a challenge with the modern SPA + REST API setup, since the backend and frontend will each have a different set of unit and integration tests expecting certain rows in the database.

In this article we are going to look at the popular Django+Angular configuration and lay down an architecture to easily integrate both testing suites (and run them on CircleCI).

## The problem with Protractor

Protractor is the de-facto solution for end-to-end testing of Angular.JS applications. Specifications ("specs") for application behaviour can be written following the Jasmine API and easily run from the command line:

    protractor protractor.conf.js --specs="specs/my_spec.js"

The problem with this setup is that each spec may potentially require a different set of data in the database. Django and DRF (as usual) brilliantly solve the issue by allowing the user to declare a fixture when defining the `TestCase`:

    class ExampleTests(APITestCase):
        fixtures = [...]

        def setUp(self):
            ...

Looking at the problem, we see two potential solutions:

- script the automated testing so that Django management commands `flush` and `loaddata` are run before each Protractor spec, creating a new database and loading the necessary data.
- wrap Protractor tests inside a Django management command that sets up a new database, loads the appropriate fixtures, and spawns a Protractor process.

We will be looking at the second approach, for its DRY awesomeness.

## A Django management command

There's an interesting [project on GitHub](https://github.com/jpulec/django-protractor) offering a tidy Mixin to Django's unit testing classes that spawns a Protractor process with given fixtures. While neat, this is no solution for us because it only ever uses Django's development (and static file) server. I tend to believe that integration tests should be run with as close a configuration to production as possible. In our case, this means that protractor should load the pages through the *gunicorn/nginx* stack.

On the other hand, not having access to Django's testing classes (that automatically set up and tear down new databases) means handling these jobs ourselves. What came out is a management command that takes command line arguments for both django fixtures and protractor specs:

    python manage.py protractor
        --protractor-conf="protractor/conf.js"
        --fixture="protractor/fixture_a.json"
        --fixture="protractor/fixture_b.json"
        --specs="protractor/spec_1.spec.js"

## Running everything on CircleCI

Now that all work has been delegated to the management command, all that needs to be done to run protractor tests in CircleCI is to add lines similar to the one above to the `test: override: ` array in the circle.yml file. As noted below, please keep in mind that the command does *not* support parallel testing, since each process shares the same, single, database (unlike normal Django tests that set up their own databases).

## Conclusions

Thorough testing requires not only a fair number of test cases, but a variety of different situations as well. To solve this issue, we have shown code for a Django management command that wraps protractor processes to load appropriate database fixtures.

## The code

The management command below **flushes** the database before loading the fixtures requested on the command line. So be careful not to run this on databases with valuable data. The CircleCI VM is obviously fine.


```
import os, sys, subprocess
from multiprocessing import Process
from optparse import make_option

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
from django.test.runner import setup_databases

from south.management.commands import patch_for_test_db_setup

class Command(BaseCommand):
    args = '[--protractor-conf] [--runserver-command] [--specs] [--suite]'

    option_list = BaseCommand.option_list + (
        make_option('--protractor-conf',
            action='store',
            dest='protractor_conf',
            default='protractor.conf.js',
            help='Specify a destination for your protractor configuration'
        ),
        make_option('--specs',
            action='store',
            dest='specs',
            help='Specify which specs to run'
        ),
        make_option('--suite',
            action='store',
            dest='suite',
            help='Specify which suite to run'
        ),
        make_option('--fixture',
            action='append',
            dest='fixtures',
            help='Specify fixture to load initial data to the database'
        ),
    )

    def handle(self, *args, **options):
        options['verbosity'] = int(options.get('verbosity'))

        if not os.path.exists(options['protractor_conf']):
            raise IOError("Could not find '{}'"
                .format(options['protractor_conf']))

        # flush the database
        call_command('flush', verbosity=1, interactive=False)

        fixtures = options['fixtures']
        if fixtures:
            for fixture in fixtures:
                call_command('loaddata', fixture,
                             **{'verbosity': options['verbosity']})

        protractor_command = 'protractor {}'.format(options['protractor_conf'])
        if options['specs']:
            protractor_command += ' --specs {}'.format(options['specs'])
        if options['suite']:
            protractor_command += ' --suite {}'.format(options['suite'])

        self.stdout.write("Running protractor..\n" + protractor_command + "\n")
        return_code = subprocess.call(protractor_command.split())
        sys.exit(return_code)

```
