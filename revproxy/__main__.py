import app
import waitress

waitress.serve(app.app, host='0.0.0.0', port=7771)
