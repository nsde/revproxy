"""Tunnel management."""

import urllib

import config

def get_tunnel(path: str) -> str:
    """Get the tunnel for the given path."""

    path = urllib.parse.urlparse(path).path

    if not path.startswith('/'):
        path = '/' + path

    if not path.endswith('/'):
        path += '/'

    for tunnel in reversed(config.read()['tunnels']):
        if path.startswith(tunnel['from']):
            return tunnel

    raise ValueError('No tunnel found for path: ' + path)

def get_target(path: str) -> str:
    """Get the target for the given path."""
    
    target = get_tunnel(path)['to']

    return target

def get_url(path: str):
    """Get the URL for the given path."""

    original_path = path

    tunnel = get_tunnel(path)
    target = tunnel['to']

    url = '{target}/{path}'.format(
        target=target,
        path=path[len(tunnel['from']):]
    )

    if url.endswith('/') and not original_path.endswith('/'):
        url = url[:-1]

    return url

def add_tunnel_list(md: str) -> str:
    for tunnel in config.read()['tunnels']:
        url = tunnel["from"]
        md += f'- [{url}]({url})\n'

    return md
