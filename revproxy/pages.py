import flask

def show_error(message: str, code: int = 500) -> flask.Response:
    """Show an error page."""

    with open('revproxy/pages/style.css', encoding='utf8') as f:
        css = f.read()

    with open('revproxy/pages/index.js', encoding='utf8') as f:
        js = f.read()

    return flask.render_template('error.html', message=message, code=code, css=css, js=js), code
