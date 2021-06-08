import dash
import dash_bootstrap_components as dbc

from .layout import create_layout
from .callbacks import create_callbacks


EXTERNAL_STYLESHEETS = [
    # Dash CSS
    "https://codepen.io/chriddyp/pen/bWLwgP.css",

    # Loading screen CSS
    "https://codepen.io/chriddyp/pen/brPBPO.css",

    # Bootstrap theme CSS
    dbc.themes.BOOTSTRAP,

    # CodeMirror stylesheets: https://cdnjs.com/libraries/codemirror
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/codemirror.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.59.1/theme/twilight.min.css",
]


EXTERNAL_SCRIPTS = [
    # CodeMirror scripts: https://cdnjs.com/libraries/codemirror
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.32.0/codemirror.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.59.1/mode/python/python.min.js",
]


def create_app():
    app = dash.Dash(
        __name__,
        title="mlinspect",
        external_stylesheets=EXTERNAL_STYLESHEETS,
        external_scripts=EXTERNAL_SCRIPTS,
    )

    app.config.suppress_callback_exceptions = True

    app.layout = create_layout()

    create_callbacks(app)

    return app
