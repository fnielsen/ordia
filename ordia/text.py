"""text."""


# Import of regex instead of re to get better Unicode matching support
import regex


sentence_split_pattern = regex.compile(
    r"(?<=[\.!?:])\s",
    flags=regex.UNICODE | regex.DOTALL)
word_pattern = regex.compile(
    r"((?:\p{L}\p{M}*)+(?:-(?:\p{L}\p{M}*)+)*)",
    flags=regex.UNICODE)


def lowercase_first_sentence_letters(text):
    """Lowercase the first letter in sentences.

    Parameters
    ----------
    text : str
        Text to be lower cased for the first letter.

    Result
    ------
    lowercased_text : str
        Text with first letter in sentences lower cased.

    Examples
    --------
    >>> text = "Hi, there. How are you? Well?"
    >>> lowercased_text = lowercase_first_sentence_letters(text)
    >>> lowercased_text == "hi, there. how are you? well?"
    True

    """
    sentences = text_to_sentences(text)
    lowercased_text = ''
    for sentence in sentences:
        sentence = sentence.strip()
        if not lowercased_text == '':
            lowercased_text += ' '
        if len(sentence) > 0:
            lowercased_text += sentence[0].lower()
            if len(sentence) >= 2:
                lowercased_text += sentence[1:]
    return lowercased_text


def text_to_sentences(text):
    """Split text to sentences.

    Return sentences in a text as a list of strings splitting at punctuations.

    Parameters
    ----------
    text : str
        Text to be sentence tokenized.

    Result
    ------
    sentences : list of str
        List with sentences as strings.

    See Also
    --------
    text_to_words : Split text to words.

    Examples
    --------
    >>> text = "Hi, there. How are you? Well?"
    >>> len(text_to_sentences(text))
    3

    """
    sentences = sentence_split_pattern.split(text)
    return sentences


def text_to_words(text):
    """Split text to words.

    Split a text into words with a word defined as a sequence of letters and
    markings followed by one or more groups of dash and letter and markings.

    Parameters
    ----------
    text : str
        Text to be tokenized.

    Result
    ------
    tokens : list of str
        List with tokens.

    Notes
    -----
    Words are defined as Unicode letters and markings followed by zero or more
    groups, each consisting of a dash `-` and one or more letters and markings.
    Markings are added to accommodate, e.g., Hindi words.

    Examples
    --------
    >>> text = 'Hi there!'
    >>> words = text_to_words(text)
    >>> words[0] == 'Hi'
    True
    >>> words[1] == 'there'
    True

    >>> text = "Scholia creates on-the-fly profiles"
    >>> len(text_to_words(text))
    4

    """
    words = word_pattern.findall(text)
    return words


def word_list_to_everygrams(word_list, max_n_gram=3):
    """Convert a word list to a everygram list.

    Convert a list of strings to a list of strings that contain, unigrams,
    bigram, trigram, ...

    Parameters
    ----------
    word_list : list of str
        List of strings with words.
    max_n_gram : int
        Maximum n-gram, e.g., if `max_n_gram=2` then the list consists of
        unigrams and bigrams.

    Returns
    -------
    everygrams : list of str
        List of strings with words within an n-gram joined by space.

    Examples
    --------
    >>> word_list = ['nuclear', 'magnetic', 'resonance']
    >>> everygrams = word_list_to_everygrams(word_list, max_n_gram=3)
    >>> everygrams[:4]
    ['nuclear', 'nuclear magnetic', 'nuclear magnetic resonance', 'magnetic']

    """
    everygrams = [" ".join(word_list[i:i + n + 1])
                  for i in range(len(word_list))
                  for n in range(max_n_gram) if len(word_list) >= i + n + 1]
    return everygrams
