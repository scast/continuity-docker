from dockermap.map.config import ClientConfiguration
from dockermap.api import MappingDockerClient

from fabric.api import (cd, env, execute, hide, local, prefix, prompt, puts,
                        roles, run, sudo, task)
from fabric.utils import abort
from fabric.colors import cyan, green, red, yellow
from fabric.contrib.console import confirm
from fabric.contrib.files import exists

@task
def build_image(image='production'):
    if env.docker.build(**env.images[image]['build']) is None:
        abort(red('Failed to build image {image}'.format(image=image)))

    else:
        print green('Successfully built image {image}'.format(image=image))

@task
def build(action='check'):
    '''Step 1. Build artifacts (docker images) for all environments.'''

    force = action == 'force'
    check_changed = action == 'check'

    with cd(env.project_path):
        remote, dest_branch = env.remote_ref.split('/', 1)

        changed_files = []

        if check_changed:
            with hide('running', 'stdout'):
                changed_files = env.run('git diff-index --cached --name-only '
                                        '{working_ref}'.format(**env),
                                        capture=True).splitlines()

        with open('images_rebuilt', 'w') as f:
            for environment in env.manager.get_rebuild_steps('common',
                                                             changed_files,
                                                             force=force):

                build_image(environment)
                f.write('{}\n'.format(environment))

@task
def run_tests():
    '''Step 2. Run tests and keep it real.'''
    # Start the testing runner
    container_map = env.container_map
    map_client = env.map_client
    info = map_client.startup('runner')
    container_id = info[0][1]['Id']

    # Wait on it to return
    exit_status = env.docker.wait(container=container_id,
                                  timeout=600)

    # Clean up
    logs = env.docker.logs(container=container_id)


    for container in container_map.containers:
        map_client.shutdown(container)

    # Abort or succeed.
    print logs
    if exit_status == 0:
        print green('All tests passed.')

    else:
        abort(red('Some tests failed!'))

@task
def push():
    '''Step 3. Merge and push artifacts.'''
    # TODO: push to registry

    # Perform clean up
    env.run('rm -rf images_rebuilt')

@task
def deploy():
    '''Step 4. Deploy artifacts.'''
    for cname in env.containers:
        env.map_client.shutdown(cname)
        env.map_client.startup(cname)
