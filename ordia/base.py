"""base."""

from collections import defaultdict

from .api import wb_get_entities


class Base(object):
    """Database of lexemes from Wikidata."""

    def __init__(self):
        """Initialize attributes."""
        self.entities = {}
        self.keyword_index = defaultdict(list)

        self.initialize_entities_from_api()
        self.build_keyword_index()

    def initialize_entities_from_api(self):
        """Initialize entities attributes from Wikidata API."""
        ids = ['L{}'.format(id_) for id_ in range(1, 10000)]

        self.entities = wb_get_entities(ids)

    def build_keyword_index(self):
        """Build keyword index."""
        for id_, entity in self.entities.items():

            # Index lemmas
            for lemma in entity.get('lemmas', {}).values():
                self.keyword_index[lemma['value']].append(id_)

            # Forms
            for form in entity['forms']:
                for representation in form['representations'].values():
                    self.keyword_index[representation['value']].append(
                        form['id'])

    def search(self, query):
        """Search for keyword in index.

        Parameters
        ----------
        query : str
            Query string, e.g., a word

        Returns
        -------
        search_results : list of dict
            Search results in list of dict with id and label.

        """
        ids = self.keyword_index.get(query, [])
        search_results = [
            {
                'id': id_,
                'label': query,
            } for id_ in ids]
        return search_results
