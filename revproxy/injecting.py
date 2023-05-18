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
    # TODO

    netloc = urllib.parse.urlparse(target_url).netloc
    injection_folder = f'inject/{netloc}'

    if os.path.exists(injection_folder):
        for file in os.listdir(injection_folder):
            if file.endswith('.js'):
                script = soup.new_tag('script')
                with open(f'{injection_folder}/{file}', 'r', encoding='utf8') as f:
                    script.string = f.read()
                soup.body.append(script)

            if file.endswith('.css'):
                style = soup.new_tag('style')
                with open(f'{injection_folder}/{file}', 'r', encoding='utf8') as f:
                    style.string = f.read()
                soup.head.append(style)

    injected_html = str(soup)
    injected_html = f'<!-- Target: {target_url} -->\n{injected_html}'
    injected_html = f'<!-- PROXY INJECTION SUCCEEDED -->\n{injected_html}'

    return injected_html
