import flask
import urllib
import requests

import pages
import config
import privacy
import blocking
import injecting

def generate(response: requests.Response) -> bytes:
    """Generate streamed response."""

    for chunk in response.iter_content(chunk_size=1024 * 1024 * 1):
        yield chunk

def respond(url: str) -> flask.Response:
    """Respond to the request."""

    if blocking.should_block(url):
        return pages.show_error(f'The website `{url}` is blocked.', None, 403)

    timeout = config.read()['timeout']

    headers = {key: value for (key, value) in flask.request.headers if key != 'Host'}

    headers['Host'] = privacy.apply_privacy('target-ip', urllib.parse.urlparse(url).netloc)

    try:
        resp = requests.request(
            method=flask.request.method,
            url=url,
            headers=headers,
            data=flask.request.get_data(),
            cookies=flask.request.cookies,
            allow_redirects=False,
            timeout=float(timeout),
            stream=True
        )

    except requests.exceptions.Timeout as err:
        return pages.show_error(f'The website took longer than the specified `timeout` of **{timeout}ms** to respond.', err, 504)

    except requests.exceptions.TooManyRedirects as err:
        return pages.show_error(f"""
This [website]({url}) tried to redirect too many times.

Your `Referer`: `{flask.request.headers.get('Referer')}`        
""", err, 504)
    
    except requests.exceptions.ConnectionError as err:
        return pages.show_error(f'`{url}` could not be reached.', err, 502)

    except requests.exceptions.RequestException as err:
        raise err
        return pages.show_error('The website could not be requested.', err, 502)

    content_type = \
        resp.headers.get('Content-Type',
        resp.headers.get('content-type', 'text/html ; charset=utf-8'))

    # check if response is html:
    if 'text/html' in content_type:
        html = resp.content.decode('utf-8')
        html = injecting.inject(html, url)
        resp._content = html.encode('utf-8')

    # ! WARNING: content-length breaks some websites. That's why we removed it.

    headers = {
        'content-type': content_type,
        'cache-control': resp.headers.get('cache-control'),
        'expires': resp.headers.get('expires'),
        'last-modified': resp.headers.get('last-modified')
    }

    return flask.Response(
        generate(resp),
        resp.status_code,
        headers=headers
    )
