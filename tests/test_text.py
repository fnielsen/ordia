"""Test ordia text module."""


from ordia.text import text_to_words


def test_text_to_words():
    assert text_to_words('e-mail to send') == ['e-mail', 'to', 'send']
