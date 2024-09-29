"""views."""


import re

from flask import (Blueprint, redirect, render_template, request, url_for)
from werkzeug.routing import BaseConverter

from six import u

from ..api import wb_search_lexeme_entities
from ..query import (escape_string, form_to_representation_and_iso639,
                     get_wikidata_language_codes_cached, iso639_to_q)
from ..text import (lowercase_first_sentence_letters, text_to_words,
                    word_list_to_everygrams)


ALLOWED_LANGUAGES = [
    'aa', 'ab', 'ady', 'af', 'am', 'an', 'ang', 'ar', 'ar-x-q775724',
    'arc', 'arz', 'as', 'ase', 'ase-x-q22001375', 'ast', 'atj', 'av',
    'ay', 'az', 'az-x-q1828555', 'az-x-q8209', 'ba', 'bar', 'bcl',
    'be', 'be-tarask', 'bg', 'bho', 'bi', 'bjn', 'bm', 'bn', 'bo',
    'br', 'br-x-q2924576', 'br-x-q54555486', 'br-x-q54555509', 'bxr',
    'ca', 'ca-x-q32641', 'ce', 'ceb', 'ch', 'chr', 'chy', 'ckb', 'co',
    'cr', 'crh', 'crh-latn', 'crh-x-q38893333', 'crh-x-q39132363',
    'cs', 'cs-x-q28861', 'cs-x-q9995', 'csb', 'cu', 'cu-x-q145625',
    'cu-x-q8209', 'cv', 'cy', 'da', 'de', 'de-x-q306626',
    'de-x-q35218', 'de-x-q837985', 'diq', 'dsb', 'dtp', 'dty', 'dv',
    'egl', 'el', 'en', 'en-ca', 'en-gb', 'en-x-q1337', 'en-x-q44679',
    'en-x-q7976', 'eo', 'eo-x-q3497763', 'eo-x-q3505590', 'es',
    'es-419', 'es-x-q2034', 'es-x-q957764', 'et', 'eu',
    'eu-x-q3125314', 'eu-x-q749166', 'ext', 'fa', 'ff', 'fi', 'fo',
    'fr', 'fr-x-q35222', 'fr-x-q39', 'fr-x-q535', 'frr', 'fur', 'fy',
    'ga', 'gag', 'gd', 'gl', 'gn', 'gom-deva', 'gom-latn', 'got',
    'grc', 'gsw', 'gu', 'gv', 'ha', 'haw', 'he', 'he-x-q21283070',
    'he-x-q2975864', 'he-x-q67200702', 'hi', 'hif', 'hr', 'hsb', 'ht',
    'hu', 'hy', 'ia', 'id', 'id-x-q57549853', 'ie', 'ig', 'ii', 'ilo',
    'inh', 'io', 'is', 'it', 'it-x-q672147', 'iu', 'iu-x-q2479183',
    'iu-x-q8229', 'ja', 'ja-x-q10997505', 'ja-x-q53979341',
    'ja-x-q53979348', 'ja-x-q82772', 'ja-x-q82946', 'jam', 'jbo',
    'jv', 'jv-x-q879704', 'ka', 'kaa', 'kaa-x-q8209', 'kab', 'kbp',
    'kg', 'ki', 'kk', 'kk-x-q64362991', 'kk-x-q64362992',
    'kk-x-q64362993', 'kl', 'km', 'kn', 'ko', 'ko-x-q485619', 'koi',
    'krc', 'ku', 'kv', 'kw', 'ky', 'la', 'la-x-q179230', 'lad',
    'lad-x-q33513', 'lad-x-q8229', 'lb', 'lbe', 'lez', 'lfn', 'lg',
    'li', 'lij', 'liv', 'lmo', 'ln', 'lo', 'lt', 'ltg', 'lv', 'mdf',
    'mg', 'mhr', 'mi', 'min', 'mis', 'mis-x-q149838',
    'mis-x-q16315466', 'mis-x-q179230', 'mis-x-q181074',
    'mis-x-q208503', 'mis-x-q21117', 'mis-x-q21146257',
    'mis-x-q2270532', 'mis-x-q2482781', 'mis-x-q27567',
    'mis-x-q27969', 'mis-x-q3199353', 'mis-x-q33060', 'mis-x-q33161',
    'mis-x-q33170', 'mis-x-q33537', 'mis-x-q33624', 'mis-x-q33690',
    'mis-x-q33759', 'mis-x-q35222', 'mis-x-q35228', 'mis-x-q35241',
    'mis-x-q35505', 'mis-x-q35527', 'mis-x-q3558112', 'mis-x-q35668',
    'mis-x-q35726', 'mis-x-q36155', 'mis-x-q36395', 'mis-x-q36730',
    'mis-x-q36741', 'mis-x-q36790', 'mis-x-q36819', 'mis-x-q36822',
    'mis-x-Q36846',
    'mis-x-q37178', 'mis-x-q3938', 'mis-x-q401', 'mis-x-q44679',
    'mis-x-q47091826', 'mis-x-q505674', 'mis-x-q50868',
    'mis-x-q533109', 'mis-x-q56384', 'mis-x-q56430', 'mis-x-q56485',
    'mis-x-q56627865', 'mis-x-q56743290', 'mis-x-q666027',
    'mis-x-q7249970', 'mis-x-q7251862', 'mis-x-q747537',
    'mis-x-q787610', 'mis-x-q837985', 'mk', 'ml', 'mn',
    'mn-x-q1055705', 'mr', 'ms', 'ms-x-q83942', 'mt', 'mwl', 'my',
    'myv', 'mzn', 'na', 'nah', 'nan', 'nap', 'nb', 'nds', 'ne', 'new',
    'nl', 'nn', 'no', 'nv', 'nys', 'oc', 'om', 'or', 'os', 'ota',
    'pa', 'pam', 'pap', 'pdc', 'pl', 'pl-x-q101244', 'pl-x-q180309',
    'pl-x-q98912', 'pms', 'pnb', 'prg', 'ps', 'pt', 'pt-br', 'qu',
    'rm', 'rm-sursilv', 'rm-sutsilv', 'rm-vallader', 'rmy', 'ro',
    'ru', 'ru-x-q2442696', 'rue', 'sa', 'sah', 'sc', 'scn', 'sco',
    'sd', 'se', 'se-x-q56681944', 'se-x-q56681946', 'sgs', 'sh',
    'sh-x-q8229', 'shy-latn', 'si', 'sk', 'sl', 'sm', 'sma', 'smj',
    'smn', 'sms', 'sn', 'so', 'sq', 'sr', 'sr-ec', 'sr-el', 'srn',
    'st', 'st-x-q1013', 'st-x-q258', 'stq', 'su', 'sv', 'sw', 'szl',
    'ta', 'tcy', 'te', 'tet', 'tg', 'th', 'tk', 'tk-x-q8209',
    'tk-x-q8229', 'tl', 'tly-x-q8209', 'tly-x-q8229', 'tr', 'ts',
    'tt', 'tw', 'tyv', 'udm', 'ug', 'ug-latn', 'ug-x-q11084133',
    'ug-x-q6672247', 'ug-x-q986283', 'uk', 'ur', 'uz',
    'uz-x-q64363006', 'uz-x-q64363007', 'vec', 'vep', 'vi', 'vls',
    'vo', 'vo-x-q12712', 'vot', 'vro', 'wa', 'war', 'wo', 'xal', 'xh',
    'xmf', 'yi', 'yi-x-q188725', 'yo', 'yue', 'za', 'za-x-q58349204',
    'zh', 'zh-cn', 'zh-hans', 'zh-hant', 'zh-tw', 'zh-x-q178528',
    'zu']


class RegexConverter(BaseConverter):
    """Converter for regular expression routes.

    References
    ----------
    https://stackoverflow.com/questions/5870188

    """

    def __init__(self, url_map, *items):
        """Set up regular expression matcher."""
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


def add_app_url_map_converter(self, func, name=None):
    """Register a custom URL map converters, available application wide.

    References
    ----------
    https://coderwall.com/p/gnafxa/adding-custom-url-map-converters-to-flask-blueprint-objects

    """
    def register_converter(state):
        state.app.url_map.converters[name or func.__name__] = func

    self.record_once(register_converter)


Blueprint.add_app_url_map_converter = add_app_url_map_converter
main = Blueprint('app', __name__)
main.add_app_url_map_converter(RegexConverter, 'regex')


# Wikidata item identifier matcher
q_pattern = r'<regex("Q[1-9]\d*"):q>'
q1_pattern = r'<regex("Q[1-9]\d*"):q1>'
q2_pattern = r'<regex("Q[1-9]\d*"):q2>'
l_pattern = r'<regex("L[1-9]\d*"):lexeme>'
f_pattern = r'<regex("F[1-9]\d*"):f>'
s_pattern = r'<regex("S[1-9]\d*"):s>'
p_pattern = r'<regex("P[1-9]\d*"):p>'
iso_language_pattern = """\
<regex(r"[a-z]{2,3}"):language>"""
q_language_pattern = (r'<regex("(Q[1-9]\d*)|([a-z]{2,3}((-[a-z]{2})|'
                      r'(-x-Q[1-9]\d*)))"):q>')
representation_pattern = r'<regex("[\w\-\']+"):representation>'

Q_PATTERN = re.compile(r'Q[1-9]\d*')
L_PATTERN = re.compile(r'L[1-9]\d*')
S_PATTERN = re.compile(r'S[1-9]\d*')
P_PATTERN = re.compile(r'P[1-9]\d*')


@main.route("/")
def index():
    """Return rendered index page.

    Returns
    -------
    html : str
        Rederende HTML for index page.

    """
    return render_template('index.html')


@main.route("/" + l_pattern)
def show_l(lexeme):
    """Render webpage for l Wikidata item.

    Parameters
    ----------
    lexeme : str
        Wikidata lexeme item identifier.

    """
    return render_template("l.html", l=lexeme)


@main.route("/grammatical-feature/")
def show_grammatical_feature_index():
    """Render webpage for grammatical feature index page."""
    return render_template("grammatical_feature_index.html")


@main.route("/grammatical-feature/" + q_pattern)
def show_grammatical_feature(q):
    """Render webpage for grammatical feature.

    Parameters
    ----------
    q : str
        Wikidata item representing a grammatical feature.

    """
    return render_template("grammatical_feature.html", q=q)


@main.route("/guess-the-gender/")
def show_guess_the_gender():
    """Render webpage for Guess the Gender.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template("guess-the-gender.html")


@main.route("/guess-word-from-image/")
def show_guess_word_from_image():
    """Render webpage for Guess word from image.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template("guess-word-from-image.html")


@main.route("/hyphenation/")
def show_hyphenation_index():
    """Render index webpage for hyphenation."""
    return render_template("hyphenation_index.html")


@main.route("/language/" + iso_language_pattern)
def redirect_language(language):
    """Redirect from ISO language code.

    Parameters
    ----------
    language : str
        ISO language identifier as a string

    Returns
    -------
    reponse : werkzeug.wrappers.Response
        Redirect

    """
    q = iso639_to_q(language)
    if q:
        return redirect(url_for('app.show_language', q=q), code=302)
    return render_template('404.html')


@main.route("/language/" + q_language_pattern)
def show_language(q):
    """Render webpage for language.

    Parameters
    ----------
    q : str
        Wikidata item for the language.

    """
    if q.startswith('Q'):
        return render_template("language.html", q=q)
    else:
        q = q.split('-')[-1]
        return redirect(url_for('app.show_language', q=q), code=302)


@main.route("/language/")
def show_language_index():
    """Render index webpage for language."""
    return render_template("language_index.html")


@main.route("/lexical-category/" + q_pattern)
def show_lexical_category(q):
    """Render webpage for lexical category item.

    Parameters
    ----------
    q : str
        Wikidata item identifier

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template("lexical_category.html", q=q)


@main.route("/lexical-category/")
def show_lexical_category_index():
    """Render webpage for lexical_category index page."""
    return render_template("lexical_category_index.html")


@main.route("/lexical-category/" + q1_pattern + "/language/" + q2_pattern)
def show_lexical_category_language(q1, q2):
    """Render webpage for lexical category and language item.

    Parameters
    ----------
    q1 : str
        Wikidata item identifier for lexical category.
    q2 : str
        Wikidata item identifier for language.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template("lexical_category_language.html", q1=q1, q2=q2)


@main.route("/" + l_pattern + "-" + f_pattern)
def show_lf(lexeme, f):
    """Render webpage for l-f Wikidata item.

    Parameters
    ----------
    lexeme : str
        Wikidata lexeme form item identifier
    f : str
        Wikidata lexeme form identifier

    """
    form = lexeme + "-" + f

    # Server-side query to get the representation and language
    result = form_to_representation_and_iso639(form)
    if result is None:
        representation = ""
        iso639 = 'en'
    else:
        representation = result[0]
        iso639 = result[1]

    return render_template("lf.html", l=lexeme, f=f,
                           representation=escape_string(representation),
                           iso639=iso639)


@main.route("/" + l_pattern + "-" + s_pattern)
def show_ls(lexeme, s):
    """Render webpage for l-s Wikidata item.

    Parameters
    ----------
    lexeme : str
        Wikidata lexeme form item identifier
    s : str
        Wikidata lexeme sense identifier

    """
    return render_template("ls.html", l=lexeme, s=s)


@main.route("/numeral")
def show_numeral_index():
    """Render webpage for numeral index page."""
    return render_template("numeral_index.html")


@main.route("/property/" + p_pattern)
def show_property(p):
    """Render webpage for a property.

    Parameters
    ----------
    p : str
        Wikidata property.

    """
    return render_template("property.html", p=p)


@main.route("/property/")
def show_property_index():
    """Render index webpage for property."""
    return render_template("property_index.html")


@main.route("/property/" + p_pattern + "/value/" + q_pattern)
def show_property_value(p, q):
    """Render webpage for a property.

    Parameters
    ----------
    p : str
        Wikidata property
    q : str
        Wikidata item

    Returns
    -------
    html : str
        Rederende HTML for index page.

    """
    return render_template("property_value.html", p=p, q=q)


@main.route("/" + q_pattern)
def show_q(q):
    """Render webpage for q Wikidata item.

    Parameters
    ----------
    q : str
        Wikidata item identifier

    """
    return render_template("q.html", q=q)


@main.route("/reference")
def show_reference_index():
    """Render webpage for reference index page."""
    return render_template("reference_index.html")


@main.route("/reference/" + q_pattern)
def show_reference(q):
    """Render webpage for reference Wikidata item.

    Parameters
    ----------
    q : str
        Wikidata item identifier for reference

    """
    return render_template("reference.html", q=q)


@main.route("/representation/" + representation_pattern)
def show_representation(representation):
    """Render webpage for representation."""
    return render_template("representation.html",
                           representation=representation,
                           languages=ALLOWED_LANGUAGES)


@main.route("/search")
def show_search():
    """Render webpage for q Wikidata item.

    Show search interface and search results if anything has been typed in.
    Redirect of search string matches a Q identifier.

    Notes
    -----
    The function expects two URL arguments: `q` as a Wikidata item identifier
    or search string and `language` as the ISO language code.

    """
    query = request.args.get('q', '').strip()
    language = request.args.get('language', '').strip()

    if len(query) == 0:
        return redirect(url_for("app.index"), code=302)

    if Q_PATTERN.match(query):
        q = Q_PATTERN.findall(query)[0]
        return redirect(url_for("app.show_q", q=q), code=302)

    if query:
        try:
            search_results = wb_search_lexeme_entities(query)
        except Exception as exception:
            return render_template("error.html",
                                   message=str(exception))
    else:
        search_results = []
    return render_template("search.html", language=language,
                           query=query, search_results=search_results)


@main.route("/statistics/")
def show_statistics():
    """Render webpage for statistics.

    Returns
    -------
    html : str
        Rendered HTML.

    """
    return render_template("statistics.html")


@main.route('/text-to-languages', methods=['POST', 'GET'])
def show_text_to_languages():
    """Return HTML page for text-to-languages query.

    Return HTML page with form for text-to-languages query or if the text field
    is set, extract Wikidata identifiers.

    Returns
    -------
    html : str
        Rendered HTML.

    Notes
    -----
    This function looks at the `text`, `text-language` and `casing` URI
    parameters.

    """
    if request.method == 'GET':
        text = request.args.get('text')
        casing = request.args.get('casing')
    elif request.method == 'POST':
        text = request.form.get('text')
        casing = request.form.get('casing')
    else:
        assert False

    # Sanitize casing
    if casing not in ['none', 'lowercase', 'uppercase',
                      'lowercase-first-sentence-letters',
                      'uppercase-first-word-letters']:
        casing = 'lowercase_first_sentence_letters'
    casing = casing.replace('-', '_')

    if not text:
        return render_template('text_to_languages.html',
                               casing=casing)

    # Casing processing
    cased_text = text.strip()
    if casing == 'none':
        pass
    elif casing == 'lowercase':
        cased_text = cased_text.lower()
    elif casing == 'uppercase':
        cased_text = cased_text.upper()
    elif casing == 'lowercase_first_sentence_letters':
        cased_text = lowercase_first_sentence_letters(cased_text)
    elif casing == 'uppercase_first_word_letters':
        cased_text = cased_text.title()
    else:
        assert False
    list_of_words = text_to_words(cased_text)

    # Make the list only consists of unique words
    list_of_words = list(set(list_of_words))

    # Only match languages with more than 100 lexemes
    language_codes = get_wikidata_language_codes_cached(100)

    # Build list of monolingual strings
    words = ''
    for word in list_of_words:
        for language_code in language_codes:
            if words != '':
                words += ' '
            words += u('"{word}"@{language_code}').format(
                word=word, language_code=language_code)

    return render_template('text_to_languages.html', text=text, words=words,
                           casing=casing)


@main.route('/text-to-lexemes', methods=['POST', 'GET'])
def show_text_to_lexemes():
    """Return HTML page for text-to-lexemes query.

    Return HTML page with form for text-to-lexemes query or if the text field
    is set, extract Wikidata identifiers.

    Returns
    -------
    html : str
        Rendered HTML.

    Notes
    -----
    This function looks at the `text`, `text-language` and `casing` URI
    parameters.

    """
    if request.method == 'GET':
        text = request.args.get('text')
        text_language = request.args.get('text-language')
        casing = request.args.get('casing')
        max_n_gram = request.args.get('max-n-gram')
    elif request.method == 'POST':
        text = request.form.get('text')
        text_language = request.form.get('text-language')
        casing = request.form.get('casing')
        max_n_gram = request.form.get('max-n-gram')
    else:
        assert False

    # Sanitize language
    if text_language not in ALLOWED_LANGUAGES:
        text_language = 'da'

    # Sanitize casing
    if casing not in ['none', 'lowercase', 'uppercase',
                      'lowercase-first-sentence-letters',
                      'uppercase-first-word-letters']:
        casing = 'lowercase_first_sentence_letters'
    casing = casing.replace('-', '_')

    # Convert and sanitize max_n_gram
    try:
        max_n_gram = int(max_n_gram)
    except Exception:
        max_n_gram = 1

    # Currently confined to between 1 and 3
    max_n_gram = min(3, max(1, max_n_gram))

    if not text:
        return render_template('text_to_lexemes.html',
                               text_language=text_language,
                               casing=casing,
                               max_n_gram=max_n_gram)

    # Casing processing
    cased_text = text.strip()
    if casing == 'none':
        pass
    elif casing == 'lowercase':
        cased_text = cased_text.lower()
    elif casing == 'uppercase':
        cased_text = cased_text.upper()
    elif casing == 'lowercase_first_sentence_letters':
        cased_text = lowercase_first_sentence_letters(cased_text)
    elif casing == 'uppercase_first_word_letters':
        cased_text = cased_text.title()
    else:
        assert False
    list_of_words = text_to_words(cased_text)

    if max_n_gram > 1:
        list_of_words = word_list_to_everygrams(list_of_words,
                                                max_n_gram=max_n_gram)
        # list_of_words is now a list of everygrams

    # Make the list only consists of unique words
    list_of_words = list(set(list_of_words))

    # Build list of monolingual strings
    words = ''
    for word in list_of_words:
        if words != '':
            words += ' '
        words += u('"{word}"@{language}').format(
            word=word, language=text_language)

    return render_template('text_to_lexemes.html', text=text, words=words,
                           text_language=text_language, casing=casing,
                           max_n_gram=max_n_gram)
