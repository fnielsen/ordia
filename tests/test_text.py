"""Test ordia text module."""


from ordia.text import text_to_sentences, text_to_words


def test_text_to_sentences():
    assert text_to_sentences('Hallo') == ['Hallo']
    assert text_to_sentences('Hallo. World') == ['Hallo.', 'World']
    assert text_to_sentences('Hallo.\nWorld') == ['Hallo.', 'World']
    assert text_to_sentences('Hallo.\tWorld') == ['Hallo.', 'World']
    assert text_to_sentences('and, e.g., hallo') == ['and, e.g., hallo']


def test_text_to_words():
    assert text_to_words('e-mail to send') == ['e-mail', 'to', 'send']
