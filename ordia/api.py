"""api."""


import requests


HEADERS = {
    'User-Agent': 'Ordia',
}


def wb_get_entities(ids):
    """Get entities from Wikidata.

    Query the Wikidata webservice via is API.

    Parameters
    ----------
    is : list of str
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
