"""base."""

from collections import defaultdict

from .api import wb_get_entities


class Entities(dict):
    """Store for lexeme entities."""

    def __getitem__(self, id_):
        """Handle indexing with [].

        Parameters
        ----------
        id_ : str
            Identifier for Wikidata lexeme.

        Returns
        -------
        entity : dictionary
            Entity from Wikidata represented in a dict.

        """
        try:
            entity = dict.__getitem__(self, id_)
        except KeyError:
            if id_.startswith('L'):
                entities = wb_get_entities([id_])
                if len(entities) == 1:
                    entity = list(entities.values())[0]
                    dict.__setitem__(self, id_, entity)
                else:
                    raise KeyError
            else:
                raise KeyError
        return entity

    def get(self, id_, default=None):
        """Handle indexing with get.

        Parameters
        ----------
        id_ : str
            Identifier for Wikidata lexeme.
        default :
            Default return argument

        Returns
        -------
        entity : dictionary
            Entity from Wikidata represented in a dict.

        """
        try:
            entity = dict.__getitem__(self, id_)
        except KeyError:
            try:
                if id_.startswith('L'):
                    entities = wb_get_entities([id_])
                    if len(entities) == 1:
                        entity = list(entities.values())[0]
                    else:
                        return default
                else:
                    return default
            except IndexError:
                return default
            dict.__setitem__(self, id_, entity)
        return entity


class Base(object):
    """Database of lexemes from Wikidata.

    Attributes
    ----------
    entities : Entities
        Structure to save/cache entities from Wikidata.
    form_index : defaultdict of defaultdict of list
        Dictionary by language.
    grammatical_feature_index : defaultdict of list
        Dictionary of grammatical features.
    keyword_index : defaultdict of list
        Dictionary of the lemmas and forms.
    language_index : defaultdict of list
        Dictionary of languages
    lexical_category_counts : defaultdict of int
        Dictionary with counts.

    """

    def __init__(self, max_ids=None):
        """Initialize attributes.

        Parameters
        ----------
        max_ids : int or None
            Maximum identifier to set up. To load the entire lexical data or
            Wikidata this should be set to None. For quick set up during
            development and debugging `max_ids` can be set to, e.g., 200.
            This variable is passed on to the setup method.

        """
        self.entities = Entities()
        self.form_index = defaultdict(lambda: defaultdict(list))
        self.grammatical_feature_index = defaultdict(list)
        self.keyword_index = defaultdict(list)
        self.language_index = defaultdict(list)
        self.lexical_category_counts = defaultdict(int)

        self.initialize_entities_from_api(max_ids=max_ids)
        self.build_indices()

    def initialize_entities_from_api(self, max_ids=None):
        """Initialize entities attributes from Wikidata API.

        Parameters
        ----------
        max_ids : int or None
            Maximum identifier to set up. To load the entire lexical data or
            Wikidata this should be set to None. For quick set up during
            development and debugging `max_ids` can be set to, e.g., 200.

        """
        if max_ids is None:
            max_ids = 20000
        ids = ['L{}'.format(id_) for id_ in range(1, max_ids + 1)]

        self.entities = Entities(wb_get_entities(ids))

    def build_indices(self):
        """Build indices."""
        for id_, entity in self.entities.items():

            self.lexical_category_counts[entity['lexicalCategory']] += 1

            # Index lemmas
            for lemma in entity.get('lemmas', {}).values():
                self.language_index[lemma['language']].append(id_)
                self.keyword_index[lemma['value']].append(id_)

            # Forms
            for form in entity['forms']:
                for grammatical_feature in form['grammaticalFeatures']:
                    self.grammatical_feature_index[
                        grammatical_feature].append(form['id'])
                for representation in form['representations'].values():
                    self.form_index[representation['language']][
                        representation['value']].append(
                            form['id'])
                    self.keyword_index[representation['value']].append(
                        form['id'])
                    self.language_index[representation['language']].append(
                        form['id'])

    def id_to_lemmas(self, id_):
        """Return lemmas for a Wikidata identifier.

        Parameters
        ----------
        id_ : str
            Wikidata lexeme or form identifier.

        Returns
        -------
        lemmas : list of str
            List of strings.

        Examples
        --------
        >>> base = Base(max_ids=20)
        >>> 'describe' in base.id_to_lemmas('L10')
        True

        """
        entity = self.entities.get(id_)
        if entity:
            lemmas = [value['value']
                      for value in entity.get('lemmas', {}).values()]
            return lemmas
        else:
            return []

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

    def word_to_form_ids(self, word, language):
        """Search for word and return word identifier.

        Parameters
        ----------
        word : str
           Word to query.

        Returns
        -------
        ids : list of str
            List of strings representing lexeme forms.

        Examples
        --------
        >>> base = Base(max_ids=20)
        >>> 'L10-F4' in base.word_to_form_ids('describe', 'en')
        True

        """
        return self.form_index[language][word]

    def words_to_form_ids(self, words, language):
        """Search for words and return word identifier.

        Parameters
        ----------
        word : lists of str
           Word to query.

        Returns
        -------
        ids : list of str
            List of strings representing lexeme forms.

        """
        ids = [self.word_to_form_ids(word, language) for word in words]
        return ids
