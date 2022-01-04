import re

PADDINGS = ['30px', '60px', '80px']
COLOR = '#004161'


def style_mappings(text, title=None):
    text = standardize(text)
    text = regexp_style_mappings(text)
    text = format_quotation_marks(text)
    text = align_styles(text)
    text = add_header(text)
    text = add_copyright(text)
    text = format_bible_verses(text, title)
    text = reformat_lists(text)
    assertion_test(text, title)
    return text


def standardize(text):
    # Simple replacements to clean up and standardize html
    for _ in range(5):
        text = text.replace('</h2><', '</h2>\n<')
        text = text.replace('</h3><', '</h3>\n<')
        text = text.replace('</p><', '</p>\n<')
        text = text.replace('</li><', '</li>\n<')

        text = text.replace('<p> ', '<p>')
        text = text.replace('. </p>', '.</p>')
        text = text.replace('. </li>', '.</li>')

        text = text.replace('<strong>', '<b>')
        text = text.replace('</strong>', '</b>')
        text = text.replace('<b>.', '.<b>')
        text = text.replace('<b> ', ' <b>')
        text = text.replace('</b><b> ', '')

        text = text.replace('<em> ', ' <em>')
        text = text.replace(' </em>', '</em> ')

        text = text.replace('<li><ul>', '')
        text = text.replace('</ul></li>', '')

        text = text.replace('  ', ' ')
        text = text.replace('­', '')
    return text


def regexp_style_mappings(text):
    # Regular expressions used for parsing
    text = '<div>\n' + text
    for _ in range(5):
        text = re.sub(r'(<div>)([\r\n]+)(<p>)(.*)(</p>)', r'<h2>\4</h2>', text)
        text = re.sub(r'<div>[\r\n]', r'', text)

        text = re.sub(r'(<p>)(<b>)?(<em>)?([A-Z]\.)(.*)(</b>)(</p>)', r'<h3>\4\5</h3>', text)
        text = re.sub(r'(<p>)(<b>)?(<em>)?([A-Z]\.)(.*)(</p>)', r'<h3>\4\5</h3>', text)

        text = re.sub(r'(<p>)(<b>)([0-9])(\. )(\()(\d{1,3})(.*)(</b>)(</p>)', r'<h4>\3\4\5Vers \6\7</h4>', text)
        text = re.sub(r'(<p>)(<b>)?([0-9])(\. )(\()(\d{1,3})(.*)(</p>)', r'<h4>\3\4\5Vers \6\7</h4>', text)
        text = re.sub(r'(<h4>[0-9]\. )(\(Vers )(\d{1,3})( )(\w)', r'\1\2\3\5', text)
        text = re.sub(r'(<h4>[0-9]\. )(\(Vers )(\d{1,3}\w?)(-\d{1,3}\w?)?(\). )', r'\1\2\3\4) ', text)

        text = re.sub(r'(<h2>)(.*)(<b><em>)(.*)(</em></b>)(.*)(</h2>)', r'\1\2\4\6\7', text)
        text = re.sub(r'(<h2>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h2>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h2>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h2>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h3>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h3>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h3>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h3>)', r'\1\2\4\5', text)

        text = re.sub(r'\.</h', '</h', text)

        text = re.sub(r'(<h4>)(.*)(</h4>)([\r\n]+)(<p>)(.*)(</p>)', fr'\1\2\3\4<p style="font-weight: bold; color:{COLOR};"> \6\7', text)

        pad0 = fr'<p style="padding-left: {PADDINGS[0]};">'
        pad1 = fr'<p style="padding-left: {PADDINGS[1]};">'
        text = re.sub(r'(<p>)(<b>)?([a-hj-n])(\.)', fr'{pad0}\2\3\4', text)
        text = re.sub(r'(<p>)(<b>)?([iv]+)(\.)', fr'{pad1}\2\3\4', text)

        text = re.sub(fr'({pad1})([iv]+)(\.)(.*)(</p>)([\r\n]+)({pad1})(i\.)', fr'\1\2\3\4\5\6{pad0}\8', text)

        text = re.sub(r'<p>&middot; (.*)</p>', fr'<p style="margin-top:-10; padding-left: {PADDINGS[2]};">&bull; \1</p>', text)
        text = re.sub(r'(<li>)(.*)(</li>)', fr'<p style="margin-top:-10; padding-left: {PADDINGS[2]};">&bull; \2</p>', text)

        text = re.sub(r'<ul>', r'', text)
        text = re.sub(r'</ul>', r'', text)

        text = re.sub(r'([\r\n]+)([\r\n][\r\n]+)', r'\1', text)
        text = re.sub(r'([\r\n]+)([\r\n]+)', r'\1', text)

        text = re.sub(r'<b>', r'<b style="color:#004161;">', text)

        text = re.sub(r'(>[A-za-z0-9]\.)([^\s])', r'\1 \2', text)
        text = re.sub(r'<[^/>]+>[ \n\r\t]*</[^>]+>', r'', text)
        text = re.sub(r'\n(\w|\&)', r' \1', text)
        text = re.sub(r'([^\s])(\()', r'\1 \2', text)

    return text


def format_quotation_marks(text):
    text = re.sub(fr' \'(<em>)([^\']*)(</em>)\'', r' &sbquo;\1\2\3&lsquo;', text)
    text = re.sub(fr' \'(<b>)([^\']*)(</b>)\'', r' &sbquo;\1\2\3&lsquo;', text)
    text = re.sub(fr' \'([^\']*)\'', r' &sbquo;\1&lsquo;', text)

    text = re.sub(r'(\s|\(|>)&quot;(<b>)([^&quot;]*)(</b>)&quot;', r'\1&bdquo;\2\3\4&ldquo;', text)
    text = re.sub(r'(\s|\(|>)&quot;(<em>)([^&quot;]*)(</em>)&quot;', r'\1&bdquo;\2\3\4&ldquo;', text)
    text = re.sub(r'(\s|\(|>)&quot;([^&quot;]*)&quot;', r'\1&bdquo;\2&ldquo;', text)

    text = re.sub(r'„', r'&bdquo;', text)
    text = re.sub(r' “([^\s])', r' &bdquo;\1', text)

    text = re.sub(r'(“|”)([\s\:\.\;\,])', r'&ldquo;\2', text)
    text = re.sub(r'([^\s])(</b>|</em>)?(“|”)', r'\1\2&ldquo;', text)

    text = re.sub(r'(\s|\(|>)&quot;([^\s\:\.\;\,])', r'\1&bdquo;\2', text)
    text = re.sub(r'([^\s])&quot;', r'\1&ldquo;', text)
    text = re.sub(r'(&ldquo;)([\w])', r'\1 \2', text)
    text = re.sub(r'(&bdquo;.*?)([^$ldquo;][\.]|[\.][^$ldquo;])( \(.*?\))', r'\1\2&ldquo;\3', text)

    single_term = '\w+|[^\s]+\-[^\s]+|[^\s]+\s[^\s]+|[^\s]+\s[^\s]+\s[^\s]+'
    text = re.sub(fr'(&bdquo;)({single_term})(&bdquo;|&ldquo;)', r'&sbquo;\2&lsquo;', text)
    text = re.sub(fr'(&bdquo;)(<b>)({single_term})(</b>)(&bdquo;|&ldquo;)', r'&sbquo;\2\3\4&lsquo;', text)
    text = re.sub(fr'(&bdquo;)(<em>)({single_term})(</em>)(&bdquo;|&ldquo;)', r'&sbquo;\2\3\4&lsquo;', text)
    return text


def align_styles(text):
    # Style unformatted html lines by applying style from preceding line
    for _ in range(5):
        for pad in PADDINGS:
            text = re.sub(fr'(<p style="padding-left: {pad};">)(.*)(</p>\n)(<p>)([^\d])', r'\1\2<br />\5', text)
        text = re.sub(fr'(<p style="font-weight: bold; color:{COLOR};">)(.*)(</p>\n)(<p>)([^\d])', fr'\1\2<br />\5', text)
        text = re.sub(fr'(<p style="margin-top:-10; font-weight: bold; color:{COLOR};">)(.*)(</p>\n)(<p>)([^\d])', r'\1\2\3\1\5', text)

    return text


def reformat_lists(text):
    text = re.sub(r'(<p style="padding-left: 30px;">a. )', r'<ol>\n\1', text)
    text = re.sub(r'(<p style="padding-left: 60px;">i. )', r'  <ol class="i">\n\1', text)
    text = re.sub(r'(<p style="padding-left: 30px;">)([a-z])(\. )(.*)(</p>)', r' <li>\4</li>', text)
    text = re.sub(r'(<p style="padding-left: 60px;">)([iv]+)(\. )(.*)(</p>)', r'   <li>\4</li>', text)
    text = re.sub(r'(<p style="margin-top:-10; padding-left: 80px;">&bull; )(.*)(</p>)', r'     <li>\2</li>', text)
    text = re.sub(r'([\r\n]<p>)(.*)(</p>[\r\n])(     <li>)', r'\1\2\3<ol>\n  <ol>\n    <ol class="bull">\n\4', text)
    text = re.sub(r'([\r\n] <li>)(.*)(</li>[\r\n])(     <li>)', r'\1\2\3  <ol>\n    <ol class="bull">\n\4', text)
    text = re.sub(r'([\r\n]   <li>)(.*)(</li>[\r\n])(     <li>)', r'\1\2\3    <ol class="bull">\n\4', text)

    for _ in range(2):
        text = re.sub(r'([\r\n]\s)(<li>)(.*)(</li>[\r\n])(<h|<p)', r'\1\2\3\4</ol>\n\5', text)
        text = re.sub(r'([\r\n]\s)(\s[\s]+)(<li>)(.*)(</li>[\r\n])([\s]?<)', r'\1\2\3\4\5\2</ol>\n\6', text)
        text = re.sub(r'([\r\n]\s\s\s\s\s)(<li>)(.*)(</li>[\r\n])(\s[\s]?[\s]?<)', r'\1\2\3\4    </ol>\n\5', text)

        text = re.sub(r'([\r\n]\s\s\s\s)(</ol>)(.*)([\r\n])([\s]?<|\s\s<ol)', r'\1\2\3\4  </ol>\n\5', text)
        text = re.sub(r'([\r\n]\s\s)(</ol>)(.*)([\r\n])(<h|<p)', r'\1\2\3\4</ol>\n\5', text)
    return text


def add_header(text):
    header = '<head>\n <style type="text/css">\n'
    header += '  body {\n' \
              '      background-color: #fcfaf0;\n' \
              '      margin: 30px; margin-left: 4%; margin-right: 4%;\n' \
              '     }\n'
    header += '  br {display: grid; margin-top: 2px; content: " ";}\n'
    header += '  ol {display: grid; list-style: lower-latin; gap: 10px; padding-left: 25px;}\n'
    header += '  ol.i {list-style: lower-roman; gap: 8px;}\n'
    header += '  ol.bull {list-style: square; gap: 5px;}\n'
    header += '  li {position: relative; padding-left: 2px;}\n'
    header += '  p.verse {font-weight: bold; font-family: Georgia; color:#004161;}\n'
    header += '  b {color: #004161;}\n'
    header += '  hr {margin: -2px;}\n'
    header += '  small {display: inline-block;}\n'
    header += ' </style>\n</head>\n<body>\n'
    text = header + str(text)

    text = re.sub(r'<b style="color:#004161;">', r'<b>', text)
    text = re.sub(r'<p style="font-weight: bold; color:#004161;">', r'<p class="verse">', text)
    return text


def add_copyright(text):
    copyright = '\n<p><br /><em>&copy; 2022 The <a href="https://enduringword.com/">Enduring Word</a> '
    copyright += 'Bible Commentary by David Guzik.</em></p>\n<body>'
    text = re.sub(r'([\n\r])([\n\r])', r'\1', text + copyright)
    return text


def format_bible_verses(text, title=None):
    h4 = '(<h4>[0-9]\. )(\(Vers )(\d{1,3}\s?\w?)(\-\d{1,3}\s?\w?)?(\) )(.*</h4>[\r\n])'
    h4_verse = fr'{h4}(<p class="verse"> )(.*)(</p>)'
    if title[-1].isdigit():
        text = re.sub(h4_verse, fr'\1\6<hr>\7&bdquo;\8&ldquo;  <small>({title},&thinsp;\3\4)</small>\9<hr>', text)
    else:
        text = re.sub(h4_verse, fr'\1\6<hr>\7&bdquo;\8&ldquo;  <small>({title} \3\4)</small>\9<hr>', text)
    return text


def assertion_test(text, title):
    for item in ['h2', 'h3', 'h4', 'p', 'ol', 'li']:
        assert text.count(f'<{item}') == text.count(f'</{item}')
    assert text.count('(Vers ') == 0

    b_count, l_count = text.count(f'&bdquo;'), text.count(f'&ldquo;')
    if b_count != l_count:
        title_eng = re.sub(r'[^a-zA-Z0-9\s]', r'', title)
        print(title, ' '*(15-len(title_eng)), f'Unbalanced quotation marks: {b_count} <> {l_count}')


def spell_check(text):
    from spellchecker import SpellChecker

    text_raw = re.sub(r'<head>.*?</head>', r' ', text)
    text_raw = re.sub(r'<.*?>|\(.*?\)', r' ', text_raw)
    text_raw = re.sub(r'&bdquo;|&ldquo;|&copy;', r' ', text_raw)
    text_raw = re.sub(r'[ ]?[iv]+\.', r' ', text_raw)
    text_raw = re.sub(r',|\.|\?|\!|\;|\:|\(|\)', r'', text_raw)
    text_raw = re.sub(r'  |   ', r' ', text_raw)

    spell = SpellChecker(language='de', distance=1)
    misspelled = spell.unknown(text_raw.split(' '))
    for word in misspelled:
        word_corrected = spell.correction(word)
        if word != word_corrected:
            print(word, spell.correction(word))