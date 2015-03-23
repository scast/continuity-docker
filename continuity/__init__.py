# -*- coding: utf-8 -*-

import yaml

from fabric.api import env, task
from dockermap.map.container import ContainerMap
from .utils import ImageManager

__author__ = 'Simon Castillo'
__email__ = 'scastb@gmail.com'
__version__ = '0.1.0'

def load_environment(environment_name):
    # Load up the images definitions
    images_file = env.get('images_file', './docker/images.yaml')
    with open(images_file, 'r') as f:
        env.images = yaml.safe_load(f)
        env.manager = ImageManager(env.images)

    # Load up the maps definitions and store the one in `name`
    map_file = env.get('map_file', './docker/map.yaml')
    with open(map_file, 'r') as f:
        data = yaml.safe_load(f)
        prefix = data['name']
        repo = data.get('repository', None)
        environment = data[environment_name]

    env.update(environment.pop('settings', {}))
    if repo is not None:
        environment['repository'] = repo

    env.environment = environment_name
    env.container_dict = environment
    env.container_prefix = prefix
    env.container_map = ContainerMap(prefix, environment,
                                     check_integrity=True)




def bootstrap_environment(name):
    '''Returns a decorator that is in charge of setting up the `env`
    global variable with the environment in `name`.'''



    def decorator(task):
        def func():
            # Load the environment and then run the original task
            load_environment(name)
            task()

        return func

    return decorator
