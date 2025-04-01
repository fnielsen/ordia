"""ordia.query.

Usage:
  ordia.query iso639-to-q <iso639>
  ordia.query get-wikidata-language-codes [options]
  ordia.query form-to-iso639 <form>

Options:
  --min-count=<min-count>   Minimum count [default: 0]

Description:
  Functions in this module query the Wikidata Query Service and
  thus requires Internet access.

Examples
--------
  $ python -m ordia.query iso639-to-q en
  Q1860

"""


from __future__ import absolute_import, division, print_function

from re import compile

from six import string_types


try:
    from functools import lru_cache
except ImportError:
    # For Python 2.
    from functools32 import lru_cache

import requests


USER_AGENT = 'Ordia'

HEADERS = {'User-Agent': USER_AGENT}

FORM_PATTERN = compile(r'L[1-9]\d*-F[1-9]\d*')


def escape_string(string):
    r"""Escape string to be used in SPARQL query.

    Parameters
    ----------
    string : str
        String to be escaped.

    Returns
    -------
    escaped_string : str
        Excaped string.

    Examples
    --------
    >>> escape_string('"hello"')
    '\\"hello\\"'

    >>> escape_string(r'\"hello"')
    '\\\\\\"hello\\"'

    """
    return string.replace('\\', '\\\\').replace('"', r'\"')


def form_to_representation_and_iso639(form):
    """Return representation and iso639 for a form.

    Parameters
    ----------
    form : str
        String for the form identifier.

    Returns
    -------
    representation_and_form : tuple with str or None
        Tuple with two strings or None if not found

    Raises
    ------
    ValueError
        If the `form` input argument does not matches the
        form identifier.

    Examples
    --------
    >>> result = form_to_representation_and_iso639('L33930-F1')
    >>> result == ("fyr", "da")
    True

    """
    # Validate input
    if not isinstance(form, string_types):
        raise ValueError('`form` input should be a string')
    if not FORM_PATTERN.match(form):
        raise ValueError(('`form` input should be a form identifier, '
                          'e.g., "L33930-F1"'))

    lexeme = form.split('-')[0]
    url = "https://www.wikidata.org/wiki/Special:EntityData/{}.json".format(
        lexeme)
    response = requests.get(url, headers=HEADERS)

    # Handle response
    if not response.ok:
        return None
    data = response.json()
    if 'entities' in data and lexeme in data['entities']:
        entities = data['entities'][lexeme]
        for entity_form in entities['forms']:
            if form == entity_form['id']:
                break
        else:
            return None
        if 'representations' in entity_form:
            representations = entity_form['representations']
            if len(representations) > 0:
                first_representation = next(iter(representations.values()))
                representation = first_representation['value']
                iso639 = first_representation['language']
                return (representation, iso639)
    return None


def get_wikidata_language_codes(min_count=0):
    """Get all Wikidata language codes.

    Query the Wikidata Query Service to get language codes that
    Wikidata uses for the lemmas.

    Parameters
    ----------
    min_count : int, optional
        Minimum count of lexemes for a particular language. The default is 0
        meaning that all language will be returned.

    Returns
    -------
    codes : list of str
        List of strings with language codes, e.g., ['ru', 'en', ...].

    Examples
    --------
    >>> codes = get_wikidata_language_codes()
    >>> 'da' in codes
    True

    """
    query = """
        # tool: Ordia
        SELECT (COUNT(?lexeme) AS ?count) ?language
        {
          ?lexeme wikibase:lemma ?lemma .
          BIND(LANG(?lemma) AS ?language) .
        }
        GROUP BY ?language
        """
    if min_count:
        try:
            min_count_value = int(min_count)
            if min_count_value < 0:
                raise ValueError('min_count should be non-negative')
        except ValueError:
            raise ValueError('min_count should be an integer.')
        query += "\nHAVING (?count > {})".format(min_count_value)

    query += "\nORDER BY DESC(?count)"

    url = 'https://query-main.wikidata.org/sparql'
    params = {'query': query, 'format': 'json'}
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()

    bindings = data['results']['bindings']
    if bindings:
        return [binding['language']['value'] for binding in bindings]
    else:
        return []


@lru_cache(maxsize=128)
def get_wikidata_language_codes_cached(*args, **kwargs):
    """Get unique language codes from Wikidata's lexemes.

    Cached version of `get_wikidata_language_codes`.

    Parameters
    ----------
    min_count : int, optional
        Minimum count of lexemes for a particular language. The default is 0
        meaning that all language will be returned.

    Returns
    -------
    codes : list of str
        List of strings with language codes, e.g., ['ru', 'en', ...].

    """
    return get_wikidata_language_codes(*args, **kwargs)


def iso639_to_q(iso639):
    """Convert ISO 639 to Wikidata ID.

    Convert an ISO 639-1 or ISO 639-2 identifier to the associated Q
    identifier by a lookup with the Wikidata Query Service.

    Parameters
    ----------
    iso639 : str
        ISO 639 identifier as a string.

    Returns
    -------
    q : str
        String with Wikidata ID. It is empty if the code is not found.

    Examples
    --------
    >>> iso639_to_q('en') == 'Q1860'
    True

    >>> iso639_to_q('xnx') == ''
    True

    >>> iso639_to_q('dan') == 'Q9035'
    True

    """
    if len(iso639) == 2:
        property = "wdt:P218"
    elif len(iso639) == 3:
        property = "wdt:P219"
    else:
        raise ValueError('Wrong length of `iso639`')

    query = 'SELECT ?code WHERE {{ ?code {property} "{iso639}" }}'.format(
        property=property, iso639=escape_string(iso639))

    url = 'https://query-main.wikidata.org/sparql'
    params = {'query': query, 'format': 'json'}
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()

    bindings = data['results']['bindings']
    if bindings:
        return bindings[0]['code']['value'][31:]
    else:
        return ""


@lru_cache(maxsize=1048)
def spacy_token_to_lexemes(token):
    """Identify Wikidata lexeme from spaCy token.

    Parameters
    ----------
    token : spacy.tokens.token.Token
        Token object from processing with SpaCy.

    Returns
    -------
    lexemes : list of strings

    Examples
    --------
    >>> class Token(object):
    ...     pass
    >>> token = Token()
    >>> setattr(token, 'lang_', 'da')
    >>> setattr(token, 'norm_', 'biler')
    >>> setattr(token, 'pos_', 'NOUN')
    >>> spacy_token_to_lexemes(token)
    ['L36385']

    """
    POSTAG_TO_Q = {
        "ADJ": "Q34698",
        "ADV": "Q380057",
        "INTJ": "Q83034",
        "NOUN": "Q1084",
        "PROPB": "Q147276",
        "VERB": "Q24905",

        "ADP": "Q134316",
        "AUX": "Q24905",
        "CCONJ": "Q36484",
        "DET": "Q576271",
        "NUM": "Q63116",
        "PART": "Q184943",
        "PRON": "Q36224",
        "SCONJ": "Q36484",
    }

    if token.pos_ in ['PUNCT', 'SYM', 'X']:
        return []

    iso639 = token.lang_
    language = iso639_to_q(iso639)
    representation = token.norm_
    if token.pos_ not in POSTAG_TO_Q:
        return []
    lexical_category = POSTAG_TO_Q[token.pos_]

    query = '''
       SELECT DISTINCT ?lexeme {{
           ?lexeme dct:language wd:{language} ;
            wikibase:lexicalCategory / wdt:P279* wd:{lexical_category} ;
            ontolex:lexicalForm / ontolex:representation
                "{representation}"@{iso639} .
    }}'''.format(language=language, lexical_category=lexical_category,
                 representation=representation, iso639=iso639)

    url = 'https://query-main.wikidata.org/sparql'
    params = {'query': query, 'format': 'json'}
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()

    bindings = data['results']['bindings']
    if bindings:
        lexemes = [binding['lexeme']['value'][31:] for binding in bindings]
        return lexemes
    else:
        return []


def main():
    """Handle command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['form-to-iso639']:
        result = form_to_representation_and_iso639(arguments['<form>'])
        if result is not None:
            print(result[1])

    elif arguments['iso639-to-q']:
        q = iso639_to_q(arguments['<iso639>'])
        print(q)

    elif arguments['get-wikidata-language-codes']:
        if arguments['--min-count']:
            try:
                min_count = int(arguments['--min-count'])
            except ValueError:
                raise ValueError('min-count parameter should be an integer')
            language_codes = get_wikidata_language_codes(min_count=min_count)
        else:
            language_codes = get_wikidata_language_codes()

        for language_code in language_codes:
            print(language_code)


if __name__ == '__main__':
    main()
