"""views."""


import re

from flask import (Blueprint, current_app, render_template, request)
from werkzeug.routing import BaseConverter


class RegexConverter(BaseConverter):
    """Converter for regular expression routes.

    References
    ----------
    https://stackoverflow.com/questions/5870188

    """

    def __init__(self, url_map, *items):
        """Set up regular expression matcher."""
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def add_app_url_map_converter(self, func, name=None):
    """Register a custom URL map converters, available application wide.

    References
    ----------
    https://coderwall.com/p/gnafxa/adding-custom-url-map-converters-to-flask-blueprint-objects

    """
    def register_converter(state):
        state.app.url_map.converters[name or func.__name__] = func

    self.record_once(register_converter)


Blueprint.add_app_url_map_converter = add_app_url_map_converter
main = Blueprint('app', __name__)
main.add_app_url_map_converter(RegexConverter, 'regex')


# Wikidata item identifier matcher
q_pattern = '<regex("Q[1-9]\d*"):q>'
l_pattern = '<regex("L[1-9]\d*"):l>'
f_pattern = '<regex("F[1-9]\d*"):f>'
Q_PATTERN = re.compile(r'Q[1-9]\d*')
L_PATTERN = re.compile(r'L[1-9]\d*')

p_pattern = '<regex("P[1-9]\d*"):p>'
P_PATTERN = re.compile(r'P[1-9]\d*')


@main.route("/")
def index():
    """Return rendered index page.

    Returns
    -------
    html : str
        Rederende HTML for index page.

    """
    return render_template('index.html')


@main.route("/" + l_pattern)
def show_l(l):
    """Render webpage for l Wikidata item.

    Parameters
    ----------
    l : str
        Wikidata lexeme item identifier

    """
    print(l)
    entity = current_app.base.entities.get(l)
    print(entity)
    return render_template("l.html", l=l, entity=entity)


@main.route("/" + l_pattern + "-" + f_pattern)
def show_lf(l, f):
    """Render webpage for l-f Wikidata item.

    Parameters
    ----------
    l : str
        Wikidata lexeme form item identifier
    f : str
        Wikidata lexeme form identifier

    """
    entity = current_app.base.entities.get(l)
    for form in entity['forms']:
        if form['id'] == l + '-' + f:
            break
        else:
            form = {}
    return render_template("lf.html", l=l, f=f, form=form)


@main.route("/" + q_pattern)
def show_q(q):
    """Render webpage for q Wikidata item.

    Parameters
    ----------
    q : str
        Wikidata item identifier

    """
    return render_template("q.html", q=q)


@main.route("/search")
def show_search():
    """Render webpage for q Wikidata item.

    Parameters
    ----------
    q : str
        Wikidata item identifier

    """
    query = request.args.get('q', '')
    if query:
        search_results = current_app.base.search(query)
    else:
        search_results = []
    return render_template("search.html",
                           query=query, search_results=search_results)