import flask
import markdown

import config

with open('revproxy/pages/style.css', encoding='utf8') as f:
    css = f.read()

with open('revproxy/pages/index.js', encoding='utf8') as f:
    js = f.read()

def show_error(message: str, error: Exception, status_code: int) -> flask.Response:
    """Show an error page."""
    pretty = config.read()['pretty-error-pages']

    if pretty:
        return flask.render_template('error.html', message=markdown.markdown(message), code=status_code, css=css, js=js), status_code 
    return f"""<h1>{status_code} - {str(error)}</h1>
{markdown.markdown(message)}
""", status_code

def show_info(message: str) -> flask.Response:
    """Show an info page."""
    return flask.render_template('info.html', message=markdown.markdown(message), css=css, js=js), 200
