# Copyright (c) 2020 Software AG,
# Darmstadt, Germany and/or Software AG USA Inc., Reston, VA, USA,
# and/or its subsidiaries and/or its affiliates and/or their licensors.
# Use, reproduction, transfer, publication or disclosure is prohibited except
# as specifically provided for in your License Agreement with Software AG.

from get_version import get_version
from invoke import task

import microservice_util as ms_util


@task
def show_version(_):
    """Print the module version.

    This version string is inferred from the last Git tag. A tagged HEAD
    should resolve to a clean x.y.z version string.
    """
    print(get_version(__file__))


@task(help={
    'scope': ("Which source directory to check, can be one of 'c8y_api', "
              "'tests', 'integration_tests' or 'all'. Default: 'all'")
})
def lint(c, scope='all'):
    """Run PyLint."""
    if scope == 'all':
        scope = 'c8y_api c8y_tk tests integration_tests samples'
    c.run(f'pylint {scope}')


@task
def build(c):
    """Build the module.

    This will create a distributable wheel (.whl) file.
    """
    c.run('python -m build')


@task(help={
    'name': "Microservice name. Defaults to 'python-ms'.",
    "version": "Microservice version. Defaults to '1.0.0'.",
})
def build_ms(c, name='python-ms', version='1.0.0'):
    """Build a Cumulocity microservice binary for upload.

    This will build a ready to deploy Cumulocity microservice from the
    sources.
    """
    c.run(f'./build.sh {name} {version}')


@task(help={
    'name': "Microservice name. Defaults to 'python-ms'.",
})
def register_ms(_, name='python-ms'):
    """Register a microservice at Cumulocity."""
    try:
        ms_util.register_microservice(name)
    except ValueError:
        print(f"Microservice '{name}' appears to be already registered at Cumulocity.")


@task(help={
    'name': "Microservice name. Defaults to 'python-ms'.",
})
def deregister_ms(_, name='python-ms'):
    """Deregister a microservice from Cumulocity."""
    try:
        ms_util.unregister_microservice(name)
    except LookupError:
        print(f"Microservice '{name}' appears not to be registered at Cumulocity.")


@task(help={
    'name': "Microservice name. Defaults to 'python-ms'.",
})
def update_ms(_, name='python-ms'):
    """Update microservice at Cumulocity."""
    try:
        ms_util.update_microservice(name)
    except LookupError:
        print(f"Microservice '{name}' appears not to be registered at Cumulocity.")


@task(help={
    'name': "Microservice name. Defaults to 'python-ms'.",
})
def get_credentials(_, name='python-ms'):
    """Read and print credentials of registered microservice."""
    _, tenant, user, password = ms_util.get_bootstrap_credentials(name)
    print(f"Tenant:    {tenant}\n"
          f"Username:  {user}\n"
          f"Password:  {password}")


@task(help={
    'name': "Microservice name. Defaults to 'python-ms'.",
})
def create_env(_, name='python-ms'):
    """Create a sample specific .env-{sample_name} file using the
    credentials of a corresponding microservice registered at Cumulocity."""
    base_url, tenant, user, password = ms_util.get_bootstrap_credentials(name)
    with open(f'.env-ms', 'w', encoding='UTF-8') as f:
        f.write(f'C8Y_BASEURL={base_url}\n'
                f'C8Y_BOOTSTRAP_TENANT={tenant}\n'
                f'C8Y_BOOTSTRAP_USER={user}\n'
                f'C8Y_BOOTSTRAP_PASSWORD={password}\n')
