"""text."""


# Import of regex instead of re to get better Unicode matching support
import regex


SENTENCE_SPLIT_PATTERN = regex.compile(
    r"(?<=[\.!?:])\s",
    flags=regex.DOTALL)


LETTER = r"(?:\p{L}\p{M}*)"
BRETON_CH = r"(?:[cC][’']h)"
UNIT_BR = rf"(?:{BRETON_CH}|{LETTER})"

WORD_PATTERN_DEFAULT = regex.compile(rf"{LETTER}+(?:-{LETTER}+)*")

WORD_PATTERN_BR = regex.compile(rf"({UNIT_BR}+(?:-{UNIT_BR}+)*)")


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
    sentences = SENTENCE_SPLIT_PATTERN.split(text)
    return sentences


def text_to_words(text: str, language=None) -> list[str]:
    r"""Split text to words.

    Split a text into words, where a word is defined as a sequence of Unicode
    letters and combining marks, optionally followed by one or more groups
    consisting of a dash `-` and another such sequence.

    Parameters
    ----------
    text : str
        Text to be tokenized.
    language : str or None, optional
        Language code or Wikidata Q-identifier controlling language-specific
        tokenization rules. If `None` (default), language-agnostic rules are
        used. Currently supported values are:

        - `"br"` or `"Q12107"`: Breton, where `c'h` / `c’h` is treated as
          part of a word.

    Result
    ------
    tokens : list of str
        List with tokens.

    Notes
    -----
    Words are primarily defined as Unicode letters (`\p{L}`) and combining
    marks (`\p{M}`). Combining marks are included to support scripts such as
    Devanagari.

    For some languages, the definition of what constitutes a word can be
    extended. Currently, Breton supports treating the digraph `c'h` (including
    the typographic variant `c’h`) as an internal part of a word.

    The function does not perform automatic language detection; the caller is
    responsible for supplying the appropriate language identifier when
    language-specific behavior is desired.

    Examples
    --------
    >>> text = 'Hi there!'
    >>> words = text_to_words(text)
    >>> words[0] == 'Hi'
    True
    >>> words[1] == 'there'
    True

    With a dash:

    >>> text = "Scholia creates on-the-fly profiles"
    >>> len(text_to_words(text))
    4

    With Breton's c'h:

    >>> text_to_words("c'hwezhioù bras", language="br")
    ["c'hwezhioù", 'bras']

    """
    if language in {"br", "Q12107"}:
        # Breton
        return WORD_PATTERN_BR.findall(text)
    return WORD_PATTERN_DEFAULT.findall(text)


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
