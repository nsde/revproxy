"""A simple reverse proxy built using Flask."""

import flask
import flask_limiter

from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter.util import get_remote_address

import pages
import config
import system
import tunnels

app = flask.Flask(__name__, template_folder='pages')
app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

limiter = flask_limiter.Limiter(
    get_remote_address,
    app=app,
    default_limits=config.read()['rate-limits']
)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

allowed_methods = config.read()['allowed-methods']

@cache.cached(timeout=60)
@app.route('/', defaults={'path': ''}, methods=allowed_methods)
@app.route('/<path:path>', methods=allowed_methods)
def proxy(path):
    """Proxy the request."""

    arg = flask.request.args.get

    ext_url = arg('__path')

    if not ext_url: # direct request
        try:
            url = tunnels.get_url(path)

        except ValueError as err:
            if not path:
                md = """Welcome!
The following routes are available:

"""
                return pages.show_info(tunnels.add_tunnel_list(md))
            else:
                md = f"""There is no tunnel with **`/{path}`** as its origin path.

The following routes are available:

"""
                return pages.show_error(tunnels.add_tunnel_list(md), err, 404)
    else:
        url = ext_url

    return system.respond(url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7771, use_reloader=True, use_evalex=False)
