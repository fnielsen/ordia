"""app."""


from __future__ import absolute_import, division, print_function

from flask import Flask


def create_app():
    """Create webapp.

    Factory for webapp.

    Returns
    -------
    app : flask.app.Flask
        Flask app object.

    """
    app = Flask(__name__)

    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
