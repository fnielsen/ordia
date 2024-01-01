"""api.

Usage:
  ordia.api wb-search-lexeme-entities [options] <query>

Options:
  -h | --help      Help message
  -l | --language  Language [default: en]

"""


import requests

try:
    from functools import lru_cache
except ImportError:
    # For Python 2.
    from functools32 import lru_cache

HEADERS = {
    'User-Agent': 'Ordia',
}


class WikidataAPIException(Exception):
    """Exception for Wikidata API."""

    pass


def wb_get_entities(ids):
    """Get entities from Wikidata.

    Query the Wikidata webservice via its API.

    Parameters
    ----------
    ids : list of str
        List of strings, each with a Wikidata item identifier.

    Returns
    -------
    data : dict of dict
        Dictionary of dictionaries.

    """
    if not ids:
        return {}

    # HTTP parameters
    params = {
        'action': 'wbgetentities',
        'format': 'json',
    }

    offset, items_per_batch = 0, 50
    batches = ((len(ids) + 1) // items_per_batch) + 1
    entities = {}
    for batch in range(batches):
        ids50 = ids[offset:offset + items_per_batch]
        offset += items_per_batch
        params["ids"] = "|".join(ids50)

        response_data = requests.get(
            'https://www.wikidata.org/w/api.php',
            headers=HEADERS, params=params).json()

        # TODO: Make informative/better error handling
        if 'error' in response_data:
            message = response_data['error'].get('info', '')
            message += ", id=" + response_data['error'].get('id', '')
            raise Exception(message)

        if 'entities' in response_data:
            non_missing_entities = {
                id_: entity
                for id_, entity in response_data['entities'].items()
                if 'missing' not in entity}
            entities.update(non_missing_entities)

            if len(non_missing_entities) == 0:
                break

    return entities


def wb_content_languages():
    params = {
        'action': 'query',
        'format': 'json',
        'meta': 'wbcontentlanguages',
        'wbclcontext': 'term-lexicographical',
        'wbclprop': 'code|name|autonym',
    }

    response = requests.get(
        'https://www.wikidata.org/w/api.php',
        headers=HEADERS, params=params)

    response_data = response.json()
    return response_data['query']['wbcontentlanguages']


@lru_cache(maxsize=None)
def wb_content_languages_cached():
	return wb_content_languages()


def wb_search_lexeme_entities(query, language='en'):
    """Search lexeme entities on Wikidata.

    Search the Wikidata API for content in the lexeme items.

    Parameters
    ----------
    query : str
        Query string
    language : en | da | sv, optional
        Language. Not clear if that affects the search.

    Returns
    -------
    search_results : list of dicts.
        List of individual search results, that is represented as a dict.
        The format of the dicts are the same as the output from the
        Wikidata API.

    Raises
    ------
    WikidataAPIException
        If an error occurs while communicating with the Wikidata API
        and conversion of the result.

    Notes
    -----
    The MediaWiki API of Wikidata.org is searched over the Internet with the
    `wbsearchentities` action method with the `type` set to `lexeme`. This
    method will search both labels and forms, but it will only return the
    lexeme pages, - not individual form identifiers.

    """
    params = {
        'action': 'wbsearchentities',
        'format': 'json',
        'search': query,
        'language': language,
        'type': 'lexeme',
        }

    response = requests.get(
        'https://www.wikidata.org/w/api.php',
        headers=HEADERS, params=params)

    # The search interface may return status code 500. In that case
    # it might be better to return an error code.
    # For now, an empty result is returned...
    if not response.ok:
        raise WikidataAPIException((
            "Response from Wikidata API returned with status code "
            "{status_code} with reason '{reason}'"
        ).format(
            status_code=response.status_code,
            reason=response.reason))

    response_data = response.json()

    if 'search' in response_data:
        search_results = response_data['search']
    else:
        search_results = []
    return search_results


def main():
    """Handle command-line input."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['wb-search-lexeme-entities']:
        results = wb_search_lexeme_entities(
            arguments['<query>'],
            language=arguments['--language'],
        )
        print(results)


if __name__ == '__main__':
    main()
