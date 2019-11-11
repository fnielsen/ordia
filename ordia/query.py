"""ordia.query.

Usage:
  ordia.query iso639-to-q <iso639>

Description:
  Functions in this module query the Wikidata Query Service and
  thus requires Internet access.

Examples
--------
  $ python -m ordia.query iso639-to-q en
  Q1860

"""


from __future__ import absolute_import, division, print_function


import requests


USER_AGENT = 'Ordia'

HEADERS = {'User-Agent': USER_AGENT}


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


def get_wikidata_language_codes():
    """Get all Wikidata language codes.

    Query the Wikidata Query Service to get language codes that
    Wikidata uses for the lemmas.

    Returns
    -------
    codes : list of str
        List of strings with language codes, e.g., ['ru', 'en', ...].

    Examples
    --------
    >>> codes = get_wikidata_language_codes()
    >>> 'ja-x-q53979341' in codes
    True

    """
    query = """
        SELECT (COUNT(?lexeme) AS ?count) ?language
        {
          ?lexeme wikibase:lemma ?lemma .
          BIND(LANG(?lemma) AS ?language) .
        }
        GROUP BY ?language
        ORDER BY DESC(?count)
        """

    url = 'https://query.wikidata.org/sparql'
    params = {'query': query, 'format': 'json'}
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()

    bindings = data['results']['bindings']
    if bindings:
        return [binding['language']['value'] for binding in bindings]
    else:
        return []


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

    url = 'https://query.wikidata.org/sparql'
    params = {'query': query, 'format': 'json'}
    response = requests.get(url, params=params, headers=HEADERS)
    data = response.json()

    bindings = data['results']['bindings']
    if bindings:
        return bindings[0]['code']['value'][31:]
    else:
        return ""


def main():
    """Handle command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['iso639-to-q']:
        q = iso639_to_q(arguments['<iso639>'])
        print(q)


if __name__ == '__main__':
    main()
