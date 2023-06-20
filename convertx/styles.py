import re
import os
import random
from copy import copy
import pycld2
import zipfile
from lxml import etree
from .book_ids import BOOK_DICT

ooXMLns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
BOOKS = re.sub(r'([1-5]\s)', r'', '|'.join(list(BOOK_DICT.values())))
BOOKS_NT = re.sub(r'([1-5]\s)', r'', '|'.join(list(BOOK_DICT.values())[-27:]))
PADDINGS = ['30px', '60px', '80px']
COLOR = '#004161'


"""Utilies"""

def detect_language(text):
    raw_text = re.sub(r'(<[^>]*>)', r' ', text)
    raw_text = re.sub(r'[^a-zA-Z\säöüß]', r'', raw_text)
    raw_text = re.sub(r'( \w )', r' ', raw_text)
    raw_text = ' '.join(random.sample(raw_text.split(),100))   # pick randomly 100 words
    reliable, index, top_3_choices = pycld2.detect(raw_text, bestEffort=False)
    if not reliable:
        reliable, index, top_3_choices = pycld2.detect(raw_text, bestEffort=True)
    return top_3_choices[0][1]


"""HTML mappings"""

def style_mappings(text, title=None, wordpress=True, copyright=True):
    text_raw = copy(text)

    text = standardize(text)
    text = regexp_style_mappings(text)
    text = align_styles(text)
    text = add_body(text)
    if not wordpress:
        text = add_header(text)
    if copyright:
        text = add_copyright(text)
    text = add_closing(text)

    text = format_quotation_marks(text)
    text = format_bible_verses(text, title)
    text = format_lists(text)
    text = format_quotes(text)

    assertion_test(text, text_raw, title)

    lang = 'de' if True else detect_language(text_raw)  # seems to not work with Mac M1 processors
    text = format_language(text, lang)

    if lang == 'de':
        bible_check(text, title)
    if wordpress:
        text = format_wordpress(text, title)
    text = final_cut(text)
    #text = format_ascii(text)  # Do we need this?

    # code efficiency: styles ~0.1s, tests ~0.1s, lang ~0.15s, bible ~0.2s
    return text


def standardize(text):
    # Simple replacements to clean up and standardize html
    for _ in range(5):
        text = text.replace('<div>', '')
        text = text.replace('</div>', '')

        text = text.replace('</h2><', '</h2>\n<')
        text = text.replace('</h3><', '</h3>\n<')
        text = text.replace('</p><', '</p>\n<')
        text = text.replace('</li><', '</li>\n<')
        text = text.replace('</table><', '</table>\n<')

        text = text.replace('<p> ', '<p>')
        text = text.replace('. </p>', '.</p>')
        text = text.replace('. </li>', '.</li>')

        text = text.replace('<p><br />', '<p>')
        text = text.replace('<br /></p>', '</p>')

        text = text.replace('<strong>', '<b>')
        text = text.replace('</strong>', '</b>')
        text = text.replace('<b> ', ' <b>')
        text = text.replace(' </b>', '</b> ')
        text = text.replace('<b>.</b>', '.')
        text = text.replace('</b><b> ', '')
        text = text.replace('<b>.', '.<b>')

        text = text.replace('<em> ', ' <em>')
        text = text.replace(' </em>', '</em> ')
        text = text.replace('<em>.</em>', '.')

        text = text.replace('<li><ul>', '')
        text = text.replace('</ul></li>', '')

        text = text.replace('  ', ' ')
        text = text.replace('\t', '')
        text = text.replace(' - ', ' &ndash; ')
        text = text.replace('...', '&hellip;')

        text = text.replace('??', '?')
        text = text.replace('!!', '!')

        try:  # not compatible with py27 due to non-ascii characters
            text = text.replace(' ', ' ')
            text = text.replace('­', '')
            text = text.replace('…', '&hellip;')
        except:
            pass
    return text


def regexp_style_mappings(text):
    # Regular expressions used for parsing
    text = '<div>\n' + text

    # header2 = first paragraph
    text = re.sub(r'([^<div>]*[\r\n])(<h2>)(.*)(</h2>)', r'\1<p>\3</p>', text)
    text = re.sub(r'(<div>)([\r\n]+)(<p>)(.*)(</p>)', r'<h2>\4</h2>', text)
    text = re.sub(r'<div>[\r\n]', r'', text)

    for _ in range(5):
        # header3 = starts with [A-Z] item
        text = re.sub(r'<h3>(\d{1,2}\. )(.*)</h3>', r'<p>\1\2></p>', text)
        text = re.sub(r'(<p>)(|<b>)(|<em>)([A-Z]\.)(.*)(</b>)(</p>)', r'<h3>\4\5</h3>', text)
        text = re.sub(r'(<p>)(|<b>)(|<em>)([A-Z]\.)(.*)(</p>)', r'<h3>\4\5</h3>', text)

        # header4 = starts with [0-9] item
        text = re.sub(r'(<p>)(<b>)(\d{1,3})(\. )(\()(\d{1,3})(.*)(</b>)(</p>)', r'<h4>\3\4\5Vers \6\7</h4>', text)
        text = re.sub(r'(<p>)(|<b>|<em>)(\d{1,3})(\. )(\()(\d{1,3})(.*)(</p>)', r'<h4>\3\4\5Vers \6\7</h4>', text)

        # header4 -> add 'Vers'
        text = re.sub(r'(<h4>\d{1,3}\. )(\(Vers )(\d{1,3})( )(\w)', r'\1\2\3\5', text)
        text = re.sub(r'(<h4>\d{1,3}\. )(\(Vers )(\d{1,3}\w?)(|-\d{1,3}\w?)(\). )', r'\1\2\3\4) ', text)

        # header2/3 -> remove all bold and italic
        text = re.sub(r'(<h2>)(.*)(<b><em>)(.*)(</em></b>)(.*)(</h2>)', r'\1\2\4\6\7', text)
        text = re.sub(r'(<h2>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h2>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h2>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h2>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h3>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h3>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h3>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h3>)', r'\1\2\4\5', text)

        # headers -> no end of header punctuation
        text = re.sub(r'\.</h', '</h', text)

        # bible verse -> bold colored, comes right after header4
        verse_style = '<p style="font-weight: bold; color:{};">'.format(COLOR)
        text = re.sub(r'(<h4>)(.*)(</h4>)([\r\n]+)(<p>)(.*)(</p>)', r'\1\2\3\4{} \6\7'.format(verse_style), text)

        # try to handle word-specific <ol>
        vals = ['v', 'iv', 'iii', 'ii', 'i']
        for i in range(len(vals)-1):
            text = re.sub(r'(<ol><li>)(.*)(</li>[\r\n]</ol>)(<p>)({}\.)'.format(vals[i]), r'<p>{}.\2</p>\n\4\5'.format(vals[i+1]), text)

        vals = ['g', 'f', 'e', 'd', 'c', 'b', 'a']
        for i in range(len(vals) - 1):
            text = re.sub(r'(<ol><li>)(.*)(</li>[\r\n]</ol>)(<p>)({}\.)'.format(vals[i]), r'<p>{}.\2</p>\n\4\5'.format(vals[i + 1]), text)

        # ordered lists -> add paddings to [a-n], [ivx]
        pad0 = r'<p style="padding-left: {};">'.format(PADDINGS[0])
        pad1 = r'<p style="padding-left: {};">'.format(PADDINGS[1])

        text = re.sub(r'(<p>)(|<b>)([a-hj-u])(\.)', r'{}\2\3\4'.format(pad0), text)
        text = re.sub(r'(<p>)(|<b>)([a-hj-u])( )', r'{}\2\3.\4'.format(pad0), text)
        text = re.sub(r'({}h\. )(.*)(</p>[\r\n])(<p>)(i\. )(.*)(</p>[\r\n]<p>ii\.)'.format(pad0), r'\1\2\3{}\5\6\7'.format(pad1), text)
        text = re.sub(r'({}h\. )(.*)(</p>[\r\n])(<p>)(i\. <b>)'.format(pad0), r'\1\2\3{}\5'.format(pad0), text)
        text = re.sub(r'({}h\. )(.*)(</p>[\r\n])({})(i\. )(.*)(</p>[\r\n])({})(i\. )(.*)(</p>[\r\n])({})(i\. )'.format(pad0, pad1, pad1, pad1), r'\1\2\3{}\5\6\7{}\9\10\11{}\13'.format(pad1, pad0, pad1), text)
        text = re.sub(r'({}[ivx]+\. )(.*)(</p>[\r\n])({})(i\. )(.*)(</p>[\r\n])({})(i\. )(.*)(</p>[\r\n])({})(ii\. )'.format(pad1, pad1, pad1, pad1), r'\1\2\3{}\5\6\7\8\9\10\11\12\13'.format(pad0), text)

        text = re.sub(r'(<p>)(|<b>)([ivx]+)(\.)', r'{}\2\3\4'.format(pad1), text)
        text = re.sub(r'(<p>)(|<b>)([ivx]+)( )', r'{}\2\3.\4'.format(pad1), text)

        # fix list item i. if it belongs to [a-n] hierarchy
        text = re.sub(r'({}[ivx]+\. )(.*)(</p>[\r\n])({})(i\. <b>)'.format(pad1, pad1), r'\1\2\3{}\5'.format(pad0), text)

        # fix -> replace ii. with i. if it comes right after [a-z]\.
        text = re.sub(r'({}[a-hj-u]\. )(.*)(</p>\n{})(ii. )'.format(pad0, pad1), r'\1\2\3i. ', text)

        # unordered lists -> add paddings to &middot;
        pad2 = r'<p style="margin-top:-10; padding-left: {};">&bull;'.format(PADDINGS[2])
        text = re.sub(r'<p>&middot; (.*)</p>', r'{} \1</p>'.format(pad2), text)
        text = re.sub(r'(<li>)(.*)(</li>)', r'{} \2</p>'.format(pad2), text)  # how to detect <ol><li>?

        #for pad in [pad0, pad1, pad2]:
        #    text = re.sub(fr'(<ol>)({pad})(.*)(</p>[\r\n]?)(</ol>)', fr'\2\3\4', text)

        # remove remaining unordered lists
        text = re.sub(r'<ul>', r'', text)
        text = re.sub(r'</ul>', r'', text)

        # remove multiple line breaks
        text = re.sub(r'([\r\n]+)([\r\n][\r\n]+)', r'\1', text)
        text = re.sub(r'([\r\n]+)([\r\n]+)', r'\1', text)

        # add color to bold text
        text = re.sub(r'<b>', r'<b style="color:{};">'.format(COLOR), text)

        # add space after >[A-za-z0-9]\.
        text = re.sub(r'(>[A-za-z0-9]\.)([^\s])', r'\1 \2', text)

        # remove empty tags
        text = re.sub(r'<[^/>]+>[ \n\r\t]*</[^>]+>', r'', text)

        # start newline with tag and not with valid word
        text = re.sub(r'\n(\w|\&)', r' \1', text)

        # add space before '('
        text = re.sub(r'([^\s])(\()', r'\1 \2', text)

    # header 4 in preface
    text = re.sub(r'(<p>)(|<b>|<em>)(\d{1,3}\. )(.*)(</p>)', r'<h4>\3\4</h4>', text)
    text = re.sub(r'\.</h', '</h', text)

    # make sure ... is surrounded by spaces
    text = re.sub(r'([^\s>])(&hellip;)', r'\1 \2', text)
    text = re.sub(r'(&hellip;)([^\s<])', r'\1 \2', text)

    return text


def format_quotation_marks(text):
    # remove redundant character formatting
    text = re.sub(r'<em>(\&[\w]+;)</em>', r'\1', text)
    text = re.sub(r'<b>(\&[\w]+;)</b>', r'\1', text)

    # two single quotes to double quote
    text = re.sub(r'‘\'|\'‘|‘‘|\'\'', '“', text)

    # single quotes
    text = re.sub(r' \'(<em>)([^\']*)(</em>)\'', r' &sbquo;\1\2\3&lsquo;', text)
    text = re.sub(r' \'(<b>)([^\']*)(</b>)\'', r' &sbquo;\1\2\3&lsquo;', text)
    text = re.sub(r' \'([^\']*)\'', r' &sbquo;\1&lsquo;', text)

    # double quotes
    text = re.sub(r'(&quot;|“)(|</em></b>)( \()', r'&ldquo;\2\3', text)
    text = re.sub(r'(&quot;|“)(\))', r'&ldquo;\2)', text)
    text = re.sub(r'( \()(|</em></b>)(&quot;|“)', r'\1\2&bdquo;', text)
    text = re.sub(r'&quot;(\s?</p>)', r'&ldquo;\1', text)
    text = re.sub(r'(\s|\(|>)&quot;(<b>)([^&\r\n]+)(</b>)&quot;', r'\1&bdquo;\2\3\4&ldquo;', text)
    text = re.sub(r'(\s|\(|>)&quot;(<em>)([^&\r\n]+)(</em>)&quot;', r'\1&bdquo;\2\3\4&ldquo;', text)
    #text = re.sub(r'(\s|\()&quot;([^&]*)&quot;', r'\1&bdquo;\2&ldquo;', text)

    # double quotes from word-specific symbols
    text = re.sub(r'„', r'&bdquo;', text)
    text = re.sub(r' “([^\s])', r' &bdquo;\1', text)
    text = re.sub(r'(“|”)([\s\:\.\;\,])', r'&ldquo;\2', text)
    text = re.sub(r'([^\s])(|</b>|</em>)(“|”)', r'\1\2&ldquo;', text)

    # double quotes edge cases
    text = re.sub(r'(\s|\(|>)&quot;([^\s\:\.\;\,])', r'\1&bdquo;\2', text)
    text = re.sub(r'([^\s])&quot;', r'\1&ldquo;', text)
    text = re.sub(r'(&ldquo;)([\w])', r'\1 \2', text)
    text = re.sub(r': &quot;|: „', r': &bdquo;', text)
    #text = re.sub(r'(&bdquo;.*?)([^&ldquo;][\.]|[\.][^&ldquo;])( \(.*?\))', r'\1\2&ldquo;\3', text)

    # quotation marks in standard font
    text = re.sub(r'(<em>)(&bdquo;|&sbquo;)', r'\2\1', text)
    text = re.sub(r'(<b>)(&bdquo;|&sbquo;)', r'\2\1', text)

    text = re.sub(r'(&ldquo;|&lsquo;)(</em>)', r'\2\1', text)
    text = re.sub(r'(&ldquo;|&lsquo;)(</b>)', r'\2\1', text)

    # single quotes if no more than 3 words
    single_term = ['\w+|[^\s<>&]+\-[^\s<>&]+', '[^\s<>&]+\s[^\s<>&]+', '[^\s<>&]+\s[^\s<>&]+\s[^\s<>&]+']
    for term in single_term:
        text = re.sub(r'(&bdquo;)(<em>|<b>|)({})(</em>|</b>|)(&bdquo;|&ldquo;)'.format(term), r'&sbquo;\2\3\4&lsquo;', text)

    # remove redundant character formatting
    text = re.sub(r'<em>(\&[\w]+;)</em>', r'\1', text)
    text = re.sub(r'<b>(\&[\w]+;)</b>', r'\1', text)

    return text


def align_styles(text):
    # Style unformatted lines by applying style from preceding line
    for _ in range(20):
        for pad in PADDINGS:
            text = re.sub(r'(<p style="padding-left: {};">)(.*)(</p>\n)(<p>)([^\d])'.format(pad), r'\1\2<br />\5', text)
            text = re.sub(r'(<p style="margin-top:-10; padding-left: {};">)(.*)(</p>\n)(<p>)([^\d])'.format(pad), r'\1\2<br />\5', text)
        text = re.sub(r'(<p style="font-weight: bold; color:{};">)(.*)(</p>\n)(<p>)([^\d])'.format(COLOR), r'\1\2<br />\5', text)
        text = re.sub(r'(<p style="margin-top:-10; font-weight: bold; color:{};">)(.*)(</p>\n)(<p>)([^\d])'.format(COLOR), r'\1\2\3\1\5', text)
    return text


def format_quotes(text):
    # change &amps for a moment
    amps = ['&sbquo;', '&lsquo;', '&hellip;', '&ndash;', '&thinsp;']
    for amp in amps:
        text = text.replace(amp, amp.replace('&', '$'))

    # missing closing quotation marks
    quote_tag = '[^&\r\n]+'  # how to better define this as "anything but &ldquo;"
    text = re.sub(r'(<li.*&bdquo;)({})( \(\w+\))(|</em>|</b>|\s)(\s?</li>)'.format(quote_tag), r'\1\2&ldquo;\3\4\5', text)
    text = re.sub(r'(<li.*)(&bdquo;)({})(|</em>|</b>)(\.)(|</em>|</b>|\s)(</li>)'.format(quote_tag), r'\1\2\3\4\5&ldquo;\6\7', text)

    # missing opening quotation marks
    text = re.sub(r'(<li>)(|<em>|<b>|\s)({})(&ldquo; \(\w+\))(</li>)'.format(quote_tag), r'\1\2&bdquo;\3\4\5', text)
    text = re.sub(r'(<li>)(|<em>|<b>|\s)({})(\.&ldquo;)(</li>)'.format(quote_tag), r'\1\2&bdquo;\3\4\5', text)

    # change &amps back..
    for amp in amps:
        text = text.replace(amp.replace('&', '$'), amp)

    # Finally handle these:
    # &bdquo;\s, \s&ldquo;, &ldquo;. -> .&ldquo;
    return text


def format_lists(text):
    pad0 = r'<p style="padding-left: {};">'.format(PADDINGS[0])
    pad1 = r'<p style="padding-left: {};">'.format(PADDINGS[1])
    pad2 = r'<p style="margin-top:-10; padding-left: {};">&bull;'.format(PADDINGS[2])

    # list -> 'a.' to '<ol><li>...</li>', 'i.' to '  <ol class="i"><li>...</li>', bullets to '<li>...</li>'
    text = re.sub(r'({}a. )'.format(pad0), r'<ol class="a">\n\1', text)
    text = re.sub(r'({}i. )'.format(pad1), r'  <ol class="i">\n\1', text)
    text = re.sub(r'({})([a-z])(\. )(.*)(</p>)'.format(pad0), r' <li>\4</li>', text)
    text = re.sub(r'({})([ivx]+)(\. )(.*)(</p>)'.format(pad1), r'   <li>\4</li>', text)
    text = re.sub(r'({} )(.*)(</p>)'.format(pad2), r'     <li>\2</li>', text)

    # move table up if part of list
    for space in [' ', '   ', '     ']:
        text = re.sub(r'({}<li>.*</li>[\r\n])(<table>)([\s\S]+)(</table>)([\r\n]{}<li>)'.format(space, space), r'\1{}<table>\3</table>\5'.format(space), text)

    # list -> closings detected by spaces set before <li>
    text = re.sub(r'([\r\n]<h4>)(.*)(</h4>[\r\n])(     <li>)', r'\1\2\3<ol>\n  <ol>\n    <ol class="bull">\n\4', text)
    text = re.sub(r'([\r\n]<p>)(.*)(</p>[\r\n])(     <li>)', r'\1\2\3<ol>\n  <ol>\n    <ol class="bull">\n\4', text)
    text = re.sub(r'([\r\n] <li>)(.*)(</li>[\r\n])(     <li>)', r'\1\2\3  <ol>\n    <ol class="bull">\n\4', text)
    text = re.sub(r'([\r\n]   <li>)(.*)(</li>[\r\n])(     <li>)', r'\1\2\3    <ol class="bull">\n\4', text)

    for _ in range(2):
        # list -> remaining closings detected by spaces
        text = re.sub(r'([\r\n]\s)(<li>)(.*)(</li>[\r\n])(<h|<p)', r'\1\2\3\4</ol>\n\5', text)
        text = re.sub(r'([\r\n]\s)(\s[\s]+)(<li>)(.*)(</li>[\r\n])([\s]?<)', r'\1\2\3\4\5\2</ol>\n\6', text)
        text = re.sub(r'([\r\n]\s\s\s\s\s)(<li>)(.*)(</li>[\r\n])(\s[\s]?[\s]?<)', r'\1\2\3\4    </ol>\n\5', text)

        text = re.sub(r'([\r\n]\s\s\s\s)(</ol>)(.*)([\r\n])([\s]?<|\s\s<ol)', r'\1\2\3\4  </ol>\n\5', text)
        text = re.sub(r'([\r\n]\s\s)(</ol>)(.*)([\r\n])(<h|<p|<t)', r'\1\2\3\4</ol>\n\5', text)

    # start every list item with capital letter
    callback = lambda pat: pat.group(1) + pat.group(2) + pat.group(3).upper()
    text = re.sub(r'(<li>)(|<b>|<em>)([a-z])', callback, text)

    return text


def add_body(text):
    text = '<body>\n<div class="bible-comment">\n' + text

    text = re.sub(r'<b style="color:#004161;">', r'<b>', text)
    text = re.sub(r'<p style="font-weight: bold; color:#004161;">', r'<p class="verse">', text)
    return text


def add_header(text):
    header = '<head>\n <style type="text/css">\n'
    header += '  body {\n' \
              '      background-color: #fcfaf0;\n' \
              '      margin: 30px; margin-left: 4%; margin-right: 4%;\n' \
              '     }\n'
    header += '  br {display: grid; margin-top: 5px; content: " ";}\n'
    header += '  ol.a {display: grid; list-style: lower-latin; gap: 10px; padding-left: 25px;}\n'
    header += '  ol.i {list-style: lower-roman; gap: 8px;}\n'
    header += '  ol.bull {list-style: square; gap: 5px;}\n'
    header += '  li {position: relative; padding-left: 2px;}\n'
    header += '  p.verse {font-weight: bold; font-family: Georgia; color:#004161;}\n'
    header += '  b {color: #004161;}\n'
    header += '  hr {margin: -2px;}\n'
    header += '  small {display: inline-block;}\n'
    header += ' </style>\n</head>\n'
    return header + text


def add_copyright(text):
    copyright = '\n<p><br /><em>&copy; 2023 The <a href="https://enduringword.com/">Enduring ' \
                'Word</a> Bible Commentary by David Guzik.</em></p>'
    return text + copyright

def add_closing(text):
    text = re.sub(r'([\n\r])([\n\r])', r'\1', text + '\n</div>\n</body>')
    return text


def format_bible_verses(text, title=None):
    h4_1 = '(<h4>\d{1,3}\. )(\(Vers )(\d{1,3}\s?\w?)(|,\d{1,2})(|\-\d{1,3}\s?\w?)(\) )(.*</h4>[\r\n])'
    h4_2 = '(<h4>\d{1,3}\. )(\(Vers )(\d{1,3}\s?\w?)(|,\d{1,2})(\-\d{1,3}\s?\w?,\d{1,2})(\) )(.*</h4>[\r\n])'
    for h4 in [h4_1, h4_2]:
        h4_verse = r'{}(<p class="verse"> )(.*)(</p>)'.format(h4)
        if title[-1].isdigit():
            #text = re.sub(h4_verse, r'\1\7<hr>\8&bdquo;\9&ldquo;  <small>({},&thinsp;\3\4\5)</small>\10<hr>'.format(title), text)
            text = re.sub(h4_verse, r'\1\7<hr>\8\9  <small>({},&thinsp;\3\4\5)</small>\10<hr>'.format(title), text)
            #text = re.sub(h4_verse, r'\1\7<h5>{} \3\4\5</h5>\8<small>{},&thinsp;\3\4\5</small><br />\9  \10'.format(title, title), text)
        else:
            #text = re.sub(h4_verse, r'\1\7<hr>\8&bdquo;\9&ldquo;  <small>({} \3\4\5)</small>\10<hr>'.format(title), text)
            text = re.sub(h4_verse, r'\1\7<hr>\8\9  <small>({} \3\4\5)</small>\10<hr>'.format(title), text)
            #text = re.sub(h4_verse, r'\1\7<h5>{} \3\4\5</h5>\8<small>{} \3\4\5</small><br />\9  \10'.format(title, title), text)
    text = re.sub('(\d{1,3}),(\d{1,3})', r'\1,&thinsp;\2', text)

    # Use << ... >> quotation marks for Schlachter
    for _ in range(10):
        text = re.sub(r'(<p class="verse"> )(.*)(&bdquo;)(.*)(  <small>)', r'\1\2&raquo;\4\5', text)
        text = re.sub(r'(<p class="verse"> )(.*)(&ldquo;)(.*)(  <small>)', r'\1\2&laquo;\4\5', text)

    # Vers should not be surrounded with quotation mark
    text = re.sub(r'(<p class="verse"> )(&raquo;)([^&])(  <small>)', r'\1\3\4', text)
    text = re.sub(r',(&ldquo;)', r'\1,', text)

    # tender abbreviations
    for abbr, name in BOOK_DICT.items():
        text = re.sub(r'({})\.'.format(abbr), r'{}'.format(name), text)

    # change '1 Korinther' to '1. Korinther'
    text = re.sub(r'([1-5])(|\s|&thinsp;)({})'.format(BOOKS), r'\1.&thinsp;\3', text)
    return text


def format_ascii(text):
    non_ascii = ['Ä', 'Ö', 'Ü', 'ä', 'ö', 'ü', 'ß', '–']
    replace_with = ['&Auml;', '&Ouml;', '&Uuml;', '&auml;', '&ouml;', '&uuml;', '&szlig;', '&ndash;']
    for x, y in zip(non_ascii, replace_with):
        try:
            text.replace(x, y)
        except:
            pass
    return text


def format_language(text, lang=None):
    if lang is None:
        lang = detect_language(text)
    if lang == 'en':
        text = text.replace('&ldquo;', '&rdquo;')
        text = text.replace('&lsquo;', '&rsquo;')

        text = text.replace('&bdquo;', '&ldquo;')
        text = text.replace('&sbquo;', '&lsquo;')
    return text


def final_cut(text):
    text = text.replace('<h2>', '<h1>')
    text = text.replace('</h2>', '</h1>')
    return text


def print_msg(title, msg, style='bold'):
    title_with_space = title + ' ' * (15 - len(re.sub(r'[^a-zA-Z0-9\s]', r'', title)))
    start = ''  #'\x1B[3m' if style == 'italic' else '\033[1m' if style == 'bold' else ''
    end = re.sub(r'(\[)\d{1}m', r'[0m', start)

    print('{}{} {}{}'.format(start, title_with_space, msg, end))


def print_check(sample):
    if isinstance(sample, str):
        sample = [sample]
    for s in sample:
        print('Check:          \"{}...\"'.format(s[:43]))
    print()


def assertion_test(text, text_orig, title):

    # unbalanced opening/closing element for <p>
    if text.count('<p') != text.count('</p'):
        print_msg(title, 'some text is not identifable')

    # unbalanced opening/closing element for <li>
    if text.count('<li') != text.count('</li'):
        print_msg(title, 'incorrect list item (e.g., i. followed by i.)')

    # missing verse formatting
    char = '. (Vers '
    if text.count(char) > 0:
        print_msg(title, 'unidentified bible verses')
        print_check(re.findall(r'\. (\(Vers .*) [\r\n]', text))

    # missing list item formatting
    if text.count('style="padding-left') > 0:
        print_msg(title, 'unidentified list item formats')
        text_samples = re.findall(r'style="padding-left (.*) [\r\n]', text)
        if len(text_samples) > 0:
            print_check(re.findall(r'style="padding-left (.*) [\r\n]', text)[0])

    ## The following two (list items, quotation marks) are the most common format errors

    # unbalanced list opening/closing items
    if (text_orig.count('<ol>') > 0) or (text_orig.count('</ol>') > 0):
        text_samples = [t for t in re.findall(r'<ol>(.*)</ol>', text_orig)]
        text_samples = [re.sub(r'  ', r' ', re.sub(r'(<[^>]*>|&\w+;)', r'', t)) for t in text_samples]
        print_msg(title, 'unidentified list items')
        print_check(text_samples)

    # incorrect quotation marks
    all_parts = re.findall(r'<p class="verse"> (.*)  <small>', text) + re.findall(r'<li>(.*)</li>', text)
    text_samples = [t for t in all_parts if t.count("&bdquo;") + t.count("&raquo;") != t.count("&ldquo;") + t.count("&laquo;")]
    if len(text_samples)>0:
        text_samples = [re.sub(r'(<[^>]*>|&\w+;)', r' ', t) for t in text_samples]
        text_samples = [re.sub(r'  ', r' ', t) for t in text_samples]
        print_msg(title, 'unidentified quotation marks')
        print_check(text_samples)


"""Markdown mappings"""

def style_mappings_md(text):
    text = re.sub(r'[\r\n](\w)', r'\1', text)
    text = re.sub(r'([\r\n])(\#\#\# [A-Z]\.)', r'\1\n\2', text)
    text = re.sub(r'([\r\n])(\#\#\#\# \d{1,3})', r'\1\n\2', text)

    text = re.sub(r'([\r\n])  \d{1,3}\. (\*\*)', r'\1\n\n\2', text)
    text = re.sub(r'([\r\n])    \d{1,3}\.', r'\1*', text)
    text = re.sub(r'([\r\n])      \d{1,3}\.', r'\1   *', text)
    text = re.sub(r'([\r\n])([\r\n])', r'\1', text)

    text = re.sub(r'(\* \* \*[\r\n]„)(.*)(")', r'\1**\2**\3', text)
    text = re.sub(r'(\*\*) (\:)', r'\1\2', text)

    text = re.sub(r'( .) (\*\*)([^*]*)(\*\*) (. )', r'\1\2\3\4\5', text)
    text = re.sub(r'( .) (\_)([^_]*)(\_) (. )', r'\1\2\3\4\5', text)

    text = re.sub(r'( .) (\*\*)([^*]*)(\*\*) (.[.,\n])', r'\1\2\3\4\5', text)
    text = re.sub(r'( .) (\_)([^_]*)(\_) (.[.,\n])', r'\1\2\3\4\5', text)

    text = re.sub(r'(\() (\*\*)([^*]*)(\*\*) (\))', r'\1\2\3\4\5', text)
    text = re.sub(r'(\() (\_)([^_]*)(\_) (\))', r'\1\2\3\4\5', text)

    text = re.sub(r'(\*\*)([^*]*)(\*\*) (\, )', r'\1\2\3\4', text)
    text = re.sub(r'(\_)([^_]*)(\_) (\, )', r'\1\2\3\4', text)
    return text


"""Compare text with Schlachter bible text"""

def load_bible(title=None):
    path = os.path.dirname(__file__)
    file = os.path.join(path, 'Schlachter.txt')

    if title is not None:
        book_name = re.sub(r'([aeiou]|)[^a-zA-Z\|]|\d{1,3}| ', r'', title)
        books_nt = re.sub(r'([aeiou]|)[^a-zA-Z\|]|\d{1,3}| ', r'', BOOKS_NT)
        if book_name not in books_nt:
            file = os.path.join(path, 'Schlachter_AT.txt')

    bible = open(file, 'rb').read().decode('ISO-8859-1')
    bible = re.sub(r'[^a-zA-Z0-9\s]', r'', bible)
    bible = re.sub(r'([\r\n])', r' ', bible)
    bible = re.sub(r' \d{1,3} ', r' ', bible)
    bible = re.sub(r'  ', r' ', bible)
    return bible


def bible_check(text, title):

    bible = load_bible(title).lower()
    verses = re.findall(r'<p class="verse"> (.*)  <small>', text.lower())
    verse_nums = re.findall(r'<p class="verse"> .*  <small>\((.*)\)</small>', text.lower())

    n = 0
    for vers, vers_num in zip(verses, verse_nums):
        vers = copy(re.sub(r'<br />|<small>|<small>|&bdquo;|&ldquo;|&raquo;|&laquo;', r'', vers))
        vers = re.sub(r'[^a-zA-Z0-9\s]', r'', vers)
        vers = re.sub(r'[\r\n]', r' ', vers)
        vers = re.sub(r' \d{1,3} ', r' ', vers)
        vers = re.sub(r'  ', r' ', vers)
        valid = (vers[:30] in bible) or (vers[-30:] in bible)
        n += valid

        # for debugging:
        #if not valid:
        #    print(vers_num + '   ' + vers)

    if len(verses) > 0:
        perc_covered = int(n / len(verses) * 100)
        if perc_covered < 60:
            print_msg(title, 'only {}% of verses covered by Schlachter'.format(perc_covered), style='italic')

    #verses = re.findall(r'<p class="verse"> (.*)  <small>', text)
    text_samples = [v for v in verses if v.startswith('&raquo;') and v.endswith('&laquo;')]
    if len(text_samples) > 0:
        print_msg(title, 'verses surrounded by quotation marks')
        print_check([sample.replace('&raquo;', '').replace('&laquo;', '') for sample in text_samples])

    return bible


"""Wordpress-specific formatting"""

def format_wordpress(text, title=None):
    h4_verse = '(<hr><p class="verse">)(.*)(<small>)\((.*)\)(</small>)(</p><hr>[\r\n])'
    text = re.sub(h4_verse, r'<h5 id="\4">\4</h5>\n\1\3\4\5<br />\2\6', text)
    text = re.sub('(<h5 id=".*)(\s)(.*)(,&thinsp;)(.*">.*</h5>)', r'\1_\3_\5', text)
    text = re.sub('(<h5 id=".*)(.&thinsp;)(.*">.*</h5>)', r'\1_\3', text)
    text = text.replace('<hr>', '')
    return text


"""Spell Checker (currently not being used)"""

def spell_check(text):
    from spellchecker import SpellChecker

    text_raw = re.sub(r'<head>.*?</head>', r' ', text)
    text_raw = re.sub(r'<.*?>|\(.*?\)', r' ', text_raw)
    text_raw = re.sub(r'&bdquo;|&ldquo;|&copy;', r' ', text_raw)
    text_raw = re.sub(r'[ ]?[ivx]+\.', r' ', text_raw)
    text_raw = re.sub(r',|\.|\?|\!|\;|\:|\(|\)', r'', text_raw)
    text_raw = re.sub(r'  |   ', r' ', text_raw)

    spell = SpellChecker(language='de', distance=1)
    misspelled = spell.unknown(text_raw.split(' '))
    for word in misspelled:
        word_corrected = spell.correction(word)
        if word != word_corrected:
            print(word, spell.correction(word))


"""Check for open comments in docx file"""
def check_comments(docx_filename, title):

    docx_zip = zipfile.ZipFile(docx_filename)
    try:  # errors if file contains no more comments
        commentsXML = docx_zip.read('word/comments.xml')
        comments = etree.XML(commentsXML).xpath('//w:comment',namespaces=ooXMLns)
        print_msg(title, 'has {} unresolved comments left'.format(len(comments)), style='italic')

    except:
        pass