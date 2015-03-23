# -*- coding: utf-8 -*-

import yaml
import os

from fabric.api import env, task
from dockermap.map.container import ContainerMap
from dockermap.map.config import ClientConfiguration
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

    if 'host' in environment:
        for volume, path in environment['host'].items():
            environment['host'][volume] = os.path.abspath(path)

    env.container_dict = environment
    env.container_prefix = prefix
    env.container_map = ContainerMap(prefix, environment,
                                     check_integrity=True)
    env.container_config = ClientConfiguration(base_url=env.docker.base_url,
                                               version=env.docker._version,
                                               timeout=env.docker.timeout,
                                               client=env.docker)


def bootstrap_environment(name):
    return load_environment(name)
