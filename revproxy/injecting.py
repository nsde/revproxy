import os
import flask
import urllib

from rich import print
from html import escape
from bs4 import BeautifulSoup

import tunnels

PROTOCOL_RELATIVE_URLS = ['data:', 'javascript:', 'mailto:', 'tel:', 'sms:', 'callto:', 'skype:', 'facetime:']

def inject(html: str, target_url: str) -> str:
    """Inject the given HTML."""

    soup = BeautifulSoup(html, 'html.parser')

    # now we replace all links with our own
    # this includes: a, link, script, img, form, iframe, video, audio, source, embed, track, input
    tags = ['a', 'link', 'script', 'img', 'form', 'iframe', 'video', 'audio', 'source', 'embed',
'track', 'input']

    attrs = ['href', 'src', 'action']

    for tag in soup.find_all(tags):
        for attr in attrs:
            if attr in tag.attrs:
                path = tag[attr]

                # Don't inject protocol-relative URLs
                for url in PROTOCOL_RELATIVE_URLS:
                    if path.startswith(url):
                        break

                else:
                    try:
                        target = tunnels.get_target(flask.request.path)

                    except ValueError:
                        referer = flask.request.headers.get('Referer', '')

                        if referer:
                            args = urllib.parse.parse_qs(urllib.parse.urlparse(referer).query)

                            if '__path' in args:
                                target = args['__path'][0]
                            else:
                                target = tunnels.get_target(referer)
                        else:
                            target = flask.request.url.split('__path=')[1]
                            target = tunnels.get_target(target)

                    new_url = urllib.parse.urljoin(target, path)

                    # e.g. https://beta.awesome-project.app -> /awesome-project/beta
                    website_name = urllib.parse.urlparse(new_url).netloc.split('.')
                    website_name = '/'.join(website_name[::-1][1:][::-1])

                    new_path = f'/{website_name}/?__path={new_url}'
                    tag[attr] = urllib.parse.urljoin(flask.request.url_root, new_path)

    # we also have to search JavaScript code for links.
    # we have to check inline scripts, and scripts loaded from external sources

    # inline scripts
    for script in soup.find_all('script'):
        if script.string:
            script.string = inject_js(script.string, target_url)

    netloc = urllib.parse.urlparse(target_url).netloc
    injection_folder = f'inject/{netloc}'

    if os.path.exists(injection_folder):
        for file in os.listdir(injection_folder):
            for ext, tag in {'.js': 'script', '.css': 'style'}.items():
                if file.endswith(ext):
                    ele = soup.new_tag(tag)

                    with open(f'{injection_folder}/{file}', 'r', encoding='utf8') as f:
                        ele.string = f.read()

                    soup.body.append(ele)

    injected_html = str(soup)
    injected_html = f'<!-- Target: {target_url} -->\n{injected_html}'
    injected_html = f'<!-- PROXY INJECTION SUCCEEDED -->\n{injected_html}'

    return injected_html


def inject_js(js_code: str, target_url: str) -> str:
    """Inject the given JS code and replace all links."""

    replacements = {
        'window.location.href': 'window.location.href.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.href))',
        'window.location.replace': 'window.location.replace.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.replace))',
        'window.location.assign': 'window.location.assign.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.assign))',
        'window.location.search': 'window.location.search.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.search))',
        'window.location.pathname': 'window.location.pathname.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.pathname))',
        'window.location.hash': 'window.location.hash.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.hash))',
        'window.location.host': 'window.location.host.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.host))',
        'window.location.hostname': 'window.location.hostname.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.hostname))',
        'window.location.port': 'window.location.port.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.port))',
        'window.location.protocol': 'window.location.protocol.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.protocol))',
        'window.location.origin': 'window.location.origin.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.origin))',
        'window.location.reload': 'window.location.reload.replace(/__path=(.*)/, "__path=" + encodeURIComponent(window.location.reload))',
    }

    for old, new in replacements.items():
        js_code = js_code.replace(old, new)

    return js_code
