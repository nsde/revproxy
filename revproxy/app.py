"""A simple reverse proxy built using Flask."""

import flask
import requests
import flask_limiter

from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter.util import get_remote_address

import pages
import config
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

allowed_methods = config.read()['allowed-methods']

# for all requests
@app.route('/', defaults={'path': ''}, methods=allowed_methods)
@app.route('/<path:path>', methods=allowed_methods)
def proxy(path):
    """Proxy the request."""

    try:
        url = tunnels.get_url(path)
    except ValueError:
        return pages.show_error('No tunnel found for the given path. ', 404)

    print(url)

    resp = requests.request(
        method=flask.request.method,
        url=url,
        headers={key: value for (key, value) in flask.request.headers if key != 'Host'},
        data=flask.request.get_data(),
        cookies=flask.request.cookies,
        allow_redirects=True,
        timeout=config.read()['timeout'],
    )

    return flask.Response(
        resp.content,
        resp.status_code,
        headers=resp.raw.headers.items()
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7771, debug=True, use_evalex=False)
