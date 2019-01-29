"""text."""


# Import of regex instead of re to get better Unicode matching support
import regex


sentence_split_pattern = regex.compile("(?<=[\.!?:]) ", flags=regex.UNICODE)
word_pattern = regex.compile(r"((?:\p{L}\p{M}?)+(?:-(?:\p{L}\p{M}?)+)*)",
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
        if not lowercased_text == '':
            lowercased_text += ' '
        if len(sentence) > 0:
            lowercased_text += sentence[0].lower()
            if len(sentence) > 2:
                lowercased_text += sentence[1:]
    return lowercased_text


def text_to_sentences(text):
    """Split text to sentences.

    Parameters
    ----------
    text : str
        Text to be sentence tokenized.

    Result
    ------
    sentences : list of str
        List with sentences as strings.

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

    Parameters
    ----------
    text : str
        Text to be tokenized.

    Result
    ------
    tokens : list of str
        List with tokens.

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
