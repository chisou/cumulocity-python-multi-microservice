# Copyright (c) 2020 Software AG,
# Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA,
# and/or its subsidiaries and/or its affiliates and/or their licensors.
# Use, reproduction, transfer, publication or disclosure is prohibited except
# as specifically provided for in your License Agreement with Software AG.
import sys
from datetime import datetime
from dunamai import Version
from invoke import task
import re

import microservice_util as ms_util

# CHANGE THE MICROSERVICE/APPLICATION NAME HERE
MICROSERVICE_NAME = 'python-ms'


def resolve_version():
    """Resolve a formatted version string based on the latest VCS tag.

    The VCS tag must have a look like `vx.y.z`, the formatted version string
    will be `<base>[-c<num commits>][-r<date><time>]`. The number of commits
    will be omitted if the tag is on the current HEAD. The date and time will
    be omitted if the local copy is not dirty (i.e. everything is committed).
    """
    version = Version.from_any_vcs()
    result = version.base
    if version.distance:
        result = result + '-c' + str(version.distance).rjust(2, '0')
    if version.dirty:
        result = result + datetime.now().strftime('-r%y%m%d%H%M')
    return result


@task(help={
    'name': "New name of the microservice. Needs to conform to Cumulocity"
            " naming rules.",
})
def init(c, name, env=False):
    """Init the microservice project.

    This sets a default microservice name as it should be represented in
    Cumulocity.
    """
    # (1) Check name pattern (start with a letter followed by any number of
    #     letters, digits and dashes, no underscores)
    if not re.match(r'[a-zA-Z]+[a-zA-Z0-9\-]+', name):
        print(f"Provided name ({name}) does not conform to Cumulocity naming standards.", file=sys.stderr)
        exit(2)
    c.run(f'sed -i "s/^MICROSERVICE_NAME = .\\+/MICROSERVICE_NAME = \'{name}\'/" tasks.py')
    print(f'New microservice name written: {name}')


@task
def show_version(_):
    """Print the module version.

    This version string is inferred from the last Git tag. A tagged HEAD
    should resolve to a clean semver (vX.Y.Z) version string.
    """
    print(resolve_version())


@task(help={
    'scope': ("Which source directory to check, can be one of 'c8y_api', "
              "'tests', 'integration_tests' or 'all'. Default: 'all'")
})
def lint(c, scope='all'):
    """Run PyLint."""
    if scope == 'all':
        scope = 'c8y_api c8y_tk tests integration_tests samples'
    c.run(f'pylint {scope}')


@task(help={
    'name': f"Microservice name. Defaults to '{MICROSERVICE_NAME}'.",
    "version": "Microservice version. If not provided, defaults to a "
               "generated value based on the last Git tag.",
})
def build_ms(c, name=MICROSERVICE_NAME, version=None):
    """Build a Cumulocity microservice binary for upload.

    This will build a ready to deploy Cumulocity microservice from the
    sources.
    """
    c.run(f'./build.sh {name} {version or resolve_version()}')


@task(help={
    'name': f"Microservice name. Defaults to '{MICROSERVICE_NAME}'.",
})
def register_ms(_, name=MICROSERVICE_NAME):
    """Register a microservice at Cumulocity."""
    try:
        ms_util.register_microservice(name)
    except ValueError:
        print(f"Microservice '{name}' appears to be already registered at Cumulocity.")


@task(help={
    'name': f"Microservice name. Defaults to '{MICROSERVICE_NAME}'.",
})
def deregister_ms(_, name=MICROSERVICE_NAME):
    """Deregister a microservice from Cumulocity."""
    try:
        ms_util.unregister_microservice(name)
    except LookupError:
        print(f"Microservice '{name}' appears not to be registered at Cumulocity.")


@task(help={
    'name': f"Microservice name. Defaults to '{MICROSERVICE_NAME}'.",
})
def update_ms(_, name=MICROSERVICE_NAME):
    """Update microservice at Cumulocity."""
    try:
        ms_util.update_microservice(name)
    except LookupError:
        print(f"Microservice '{name}' appears not to be registered at Cumulocity.")


@task(help={
    'name': f"Microservice name. Defaults to '{MICROSERVICE_NAME}'.",
})
def get_credentials(_, name=MICROSERVICE_NAME):
    """Read and print credentials of registered microservice."""
    _, tenant, user, password = ms_util.get_bootstrap_credentials(name)
    print(f"Tenant:    {tenant}\n"
          f"Username:  {user}\n"
          f"Password:  {password}")


@task(help={
    'name': f"Microservice name. Defaults to '{MICROSERVICE_NAME}'.",
})
def create_env(_, name=MICROSERVICE_NAME):
    """Create a .env-ms file to hold the credentials of the microservice
    registered at Cumulocity."""
    base_url, tenant, user, password = ms_util.get_bootstrap_credentials(name)
    with open(f'.env-ms', 'w', encoding='UTF-8') as f:
        f.write(f'C8Y_BASEURL={base_url}\n'
                f'C8Y_BOOTSTRAP_TENANT={tenant}\n'
                f'C8Y_BOOTSTRAP_USER={user}\n'
                f'C8Y_BOOTSTRAP_PASSWORD={password}\n')
