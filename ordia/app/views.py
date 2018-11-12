"""views."""


import re

from flask import (Blueprint, redirect, render_template, request, url_for)
from werkzeug.routing import BaseConverter

from six import u

from ..api import wb_search_lexeme_entities
from ..query import iso639_to_q
from ..text import lowercase_first_sentence_letters, text_to_words


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
s_pattern = '<regex("S[1-9]\d*"):s>'
p_pattern = '<regex("P[1-9]\d*"):p>'
iso_language_pattern = """\
<regex("[a-z]{2,3}"):language>"""
q_language_pattern = """\
<regex("(Q[1-9]\d*)|([a-z]{2,3}((-[a-z]{2})|(-x-Q[1-9]\d*)))"):q>"""

Q_PATTERN = re.compile(r'Q[1-9]\d*')
L_PATTERN = re.compile(r'L[1-9]\d*')
S_PATTERN = re.compile(r'S[1-9]\d*')
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
        Wikidata lexeme item identifier.

    """
    return render_template("l.html", l=l)


@main.route("/grammatical-feature/")
def show_grammatical_feature_index():
    """Render webpage for grammatical feature index page."""
    return render_template("grammatical_feature_index.html")


@main.route("/grammatical-feature/" + q_pattern)
def show_grammatical_feature(q):
    """Render webpage for grammatical feature.

    Parameters
    ----------
    q : str
        Wikidata item representing a grammatical feature.

    """
    return render_template("grammatical_feature.html", q=q)


@main.route("/language/" + iso_language_pattern)
def redirect_language(language):
    """Redirect from ISO language code.

    Parameters
    ----------
    language : str
        ISO language identifier as a string

    Returns
    -------
    reponse : werkzeug.wrappers.Response
        Redirect

    """
    q = iso639_to_q(language)
    if q:
        return redirect(url_for('app.show_language', q=q), code=302)
    return render_template('404.html')


@main.route("/language/" + q_language_pattern)
def show_language(q):
    """Render webpage for language.

    Parameters
    ----------
    q : str
        Wikidata item for the language.

    """
    if q.startswith('Q'):
        return render_template("language.html", q=q)
    else:
        q = q.split('-')[-1]
        return redirect(url_for('app.show_language', q=q), code=302)


@main.route("/language/")
def show_language_index():
    """Render index webpage for language."""
    return render_template("language_index.html")


@main.route("/lexical-category/" + q_pattern)
def show_lexical_category(q):
    """Render webpage for lexical category item.

    Parameters
    ----------
    q : str
        Wikidata item identifier

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template("lexical_category.html", q=q)


@main.route("/lexical-category/")
def show_lexical_category_index():
    """Render webpage for lexical_category index page."""
    return render_template("lexical_category_index.html")


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
    return render_template("lf.html", l=l, f=f)


@main.route("/" + l_pattern + "-" + s_pattern)
def show_ls(l, s):
    """Render webpage for l-s Wikidata item.

    Parameters
    ----------
    l : str
        Wikidata lexeme form item identifier
    s : str
        Wikidata lexeme sense identifier

    """
    return render_template("ls.html", l=l, s=s)


@main.route("/property/" + p_pattern)
def show_property(p):
    """Render webpage for a property.

    Parameters
    ----------
    p : str
        Wikidata item for the language.

    """
    return render_template("property.html", p=p)


@main.route("/property/")
def show_property_index():
    """Render index webpage for property."""
    return render_template("property_index.html")


@main.route("/" + q_pattern)
def show_q(q):
    """Render webpage for q Wikidata item.

    Parameters
    ----------
    q : str
        Wikidata item identifier

    """
    return render_template("q.html", q=q)


@main.route("/reference")
def show_reference_index():
    """Render webpage for reference index page."""
    return render_template("reference_index.html")


@main.route("/reference/" + q_pattern)
def show_reference(q):
    """Render webpage for reference Wikidata item.

    Parameters
    ----------
    q : str
        Wikidata item identifier for reference

    """
    return render_template("reference.html", q=q)


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
        search_results = wb_search_lexeme_entities(query)
    else:
        search_results = []
    return render_template("search.html",
                           query=query, search_results=search_results)


@main.route('/text-to-lexemes', methods=['POST', 'GET'])
def show_text_to_lexemes():
    """Return HTML page for text-to-lexemes query.

    Return HTML page with form for text-to-lexemes query or if the text field
    is set, extract Wikidata identifiers.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    if request.method == 'GET':
        text = request.args.get('text')
        text_language = request.args.get('text-language')
    elif request.method == 'POST':
        text = request.form.get('text')
        text_language = request.form.get('text-language')
    else:
        assert False

    # Sanitize language
    if text_language not in ['da', 'br', 'de', 'fr', 'en', 'nl', 'pl', 'sv']:
        text_language = 'da'

    if not text:
        return render_template('text_to_lexemes.html',
                               text_language=text_language)

    lowercased_text = lowercase_first_sentence_letters(text.strip())
    list_of_words = text_to_words(lowercased_text)

    # Make the list only consists of unique words
    list_of_words = list(set(list_of_words))

    # Build list of monolingual strings
    words = ''
    for word in list_of_words:
        if words != '':
            words += ' '
        words += u('"{word}"@{language}').format(
            word=word, language=text_language)

    return render_template('text_to_lexemes.html', text=text, words=words,
                           text_language=text_language)
