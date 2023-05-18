"""CLI for running the server."""

import time
import traceback
import rich
import typer

cmd = typer.Typer()

@cmd.command()
def run_waitress(port: int=7771):
    """Run the server using waitress."""

    import waitress
    import app

    waitress.serve(app.app, host='0.0.0.0', port=port)

@cmd.command()
def run_debug(port: int=7771):
    """Run the server in debug mode."""

    while True:
        try:
            import app
            app.app.run(host='0.0.0.0', port=port, debug=True, use_evalex=False, threaded=True)
        except Exception:
            traceback.print_exc()

        rich.print('[bold red]Restarting...[/bold red]')
        time.sleep(3)

cmd()
