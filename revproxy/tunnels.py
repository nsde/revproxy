"""Tunnel management."""

import config

def get_url(path: str) -> str:
    """Get the actual URL for the given path."""

    original_path = path
    path = '/' + path

    if not path.endswith('/'):
        path += '/'

    for tunnel in reversed(config.read()['tunnels']):
        if path.startswith(tunnel['from']):
            domain = tunnel['to']
            url = f'{domain}{path[len(tunnel["from"]):]}'

            if url.endswith('/') and not original_path.endswith('/'):
                url = url[:-1]
            return url

    raise ValueError('No tunnel found for path: ' + path)
