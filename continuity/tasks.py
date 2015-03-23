from fabric.api import (cd, env, execute, hide, local, prefix, prompt, puts,
                        roles, run, sudo, task)
from fabric.utils import abort
from fabric.colors import cyan, green, red, yellow
from fabric.contrib.console import confirm
from fabric.contrib.files import exists

@task
def build_image(image='production'):
    if env.docker.build(**env.images[image]['build']) is None:
        abort('Failed to build image {image}'.format(image=image))

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
