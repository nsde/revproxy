"""Config reader."""

import yaml

def read() -> dict:
    """Read the config.yml file."""

    with open('config.yml', 'r', encoding='utf8') as file:
        return yaml.load(file, Loader=yaml.FullLoader)
