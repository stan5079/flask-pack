import difflib
import os
from typing import Callable

from flask import Flask
from flask.templating import Environment

from flask_pack.exceptions import FileNotFound


def get_find_static(app: Flask) -> Callable:
    def find_static(path: str = None) -> str:
        for rule in app.url_map.iter_rules():

            if '.' in rule.endpoint:
                blueprint_name = rule.endpoint.rsplit('.', 1)[0]
                blueprint = app.blueprints[blueprint_name]
            else:
                blueprint = None

            if blueprint and blueprint.static_folder:
                static_folder = blueprint.static_folder
            else:
                static_folder = app.static_folder

            abs_path = join_overlapping_path(static_folder, path)
            if os.path.isfile(abs_path):
                return abs_path

        raise FileNotFound

    return find_static


def join_overlapping_path(p1: str, p2: str) -> str:
    sm = difflib.SequenceMatcher(None, p1, p2)
    _, p2i, size = sm.get_matching_blocks()[0]
    p1, p2 = (p1, p2) if p2i == 0 else (p2, p1)
    size = sm.get_matching_blocks()[0].size
    return p1 + p2[size:]


def get_env_vars(environment: Environment) -> dict:
    configs = {}
    for key in dir(environment):
        if key.startswith('pack_'):
            configs[key] = getattr(environment, key)
    return configs
