"""app."""


from __future__ import absolute_import, division, print_function

from os.path import join

from flask import Flask
from flask_jsonlocale import Locales


class OrdiaLocales(Locales):
    def get_message(self, message_code, language=None):
        message = super(OrdiaLocales, self).get_message(message_code, language)
        if message is None:
            message = message_code
        return message


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
    OrdiaLocales(app)
    
    from .views import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
