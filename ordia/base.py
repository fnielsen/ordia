"""base."""

from collections import defaultdict

from .api import wb_get_entities


class Base(object):
    """Database of lexemes from Wikidata."""

    def __init__(self):
        """Initialize attributes."""
        self.entities = {}
        self.keyword_index = defaultdict(list)
        self.language_index = defaultdict(list)
        self.grammatical_feature_index = defaultdict(list)

        self.initialize_entities_from_api()
        self.build_indices()

    def initialize_entities_from_api(self):
        """Initialize entities attributes from Wikidata API."""
        ids = ['L{}'.format(id_) for id_ in range(1, 20000)]

        self.entities = wb_get_entities(ids)

    def build_indices(self):
        """Build indices."""
        for id_, entity in self.entities.items():

            # Index lemmas
            for lemma in entity.get('lemmas', {}).values():
                self.language_index[lemma['language']].append(id_)
                self.keyword_index[lemma['value']].append(id_)

            # Forms
            for form in entity['forms']:
                for grammatical_feature in form['grammaticalFeatures']:
                    self.grammatical_feature_index[grammatical_feature] \
                        = id_

                for representation in form['representations'].values():
                    self.keyword_index[representation['value']].append(
                        form['id'])
                    self.language_index[representation['language']].append(
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
