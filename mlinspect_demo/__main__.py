import os

from . import create_app


if __name__ == "__main__":
    create_app().run_server(
        host="0.0.0.0",
        debug="DEBUG" in os.environ,
    )
