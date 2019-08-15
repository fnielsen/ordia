"""app."""


from __future__ import absolute_import, division, print_function

from os.path import join

from flask import Flask
from flask_jsonlocale import Locales


def create_app():
    """Create webapp.

    Factory for webapp.

    Returns
    -------
    app : flask.app.Flask
        Flask app object.

    """
    app = Flask(__name__)

    app.config.setdefault("MESSAGES_DIR", join('ordia', 'app', 'messages'))
    
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
