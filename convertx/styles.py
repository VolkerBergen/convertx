# -*- coding: utf-8 -*-

import re
import os
import random
from copy import copy
import pycld2

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

def style_mappings(text, title=None):
    text_raw = copy(text)

    text = standardize(text)
    text = regexp_style_mappings(text)
    text = format_quotation_marks(text)
    text = align_styles(text)
    text = add_header(text)
    text = add_copyright(text)
    text = format_bible_verses(text, title)
    text = format_lists(text)
    assertion_test(text, text_raw, title)

    lang = detect_language(text_raw)
    text = format_language(text, lang)

    if lang == 'de':
        bible_check(text, title)

    text = final_cut(text)
    #text = format_ascii(text)  # Do we need this?
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
        text = text.replace('<b>.', '.<b>')
        text = text.replace('<b> ', ' <b>')
        text = text.replace('</b><b> ', '')

        text = text.replace('<em> ', ' <em>')
        text = text.replace(' </em>', '</em> ')

        text = text.replace('<li><ul>', '')
        text = text.replace('</ul></li>', '')

        text = text.replace('  ', ' ')
        text = text.replace('\t', '')

        try:  # not compatible with py27 due to non-ascii characters
            text = text.replace(' ', ' ')
            text = text.replace('­', '')
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

    return text


def format_quotation_marks(text):
    # single quotes
    text = re.sub(r' \'(<em>)([^\']*)(</em>)\'', r' &sbquo;\1\2\3&lsquo;', text)
    text = re.sub(r' \'(<b>)([^\']*)(</b>)\'', r' &sbquo;\1\2\3&lsquo;', text)
    text = re.sub(r' \'([^\']*)\'', r' &sbquo;\1&lsquo;', text)

    # double quotes
    text = re.sub(r'(\s|\(|>)&quot;(<b>)([^&quot;]*)(</b>)&quot;', r'\1&bdquo;\2\3\4&ldquo;', text)
    text = re.sub(r'(\s|\(|>)&quot;(<em>)([^&quot;]*)(</em>)&quot;', r'\1&bdquo;\2\3\4&ldquo;', text)
    text = re.sub(r'(\s|\(|>)&quot;([^&quot;]*)&quot;', r'\1&bdquo;\2&ldquo;', text)

    # double quotes from word-specific symbols
    text = re.sub(r'„', r'&bdquo;', text)
    text = re.sub(r' “([^\s])', r' &bdquo;\1', text)
    text = re.sub(r'(“|”)([\s\:\.\;\,])', r'&ldquo;\2', text)
    text = re.sub(r'([^\s])(|</b>|</em>)(“|”)', r'\1\2&ldquo;', text)

    # double quotes edge cases
    text = re.sub(r'(\s|\(|>)&quot;([^\s\:\.\;\,])', r'\1&bdquo;\2', text)
    text = re.sub(r'([^\s])&quot;', r'\1&ldquo;', text)
    text = re.sub(r'(&ldquo;)([\w])', r'\1 \2', text)
    text = re.sub(r'(&bdquo;.*?)([^$ldquo;][\.]|[\.][^$ldquo;])( \(.*?\))', r'\1\2&ldquo;\3', text)

    # single quotes if no more than 3 words
    single_term = '\w+|[^\s]+\-[^\s]+|[^\s]+\s[^\s]+|[^\s]+\s[^\s]+\s[^\s]+'
    text = re.sub(r'(&bdquo;)({})(&bdquo;|&ldquo;)'.format(single_term), r'&sbquo;\2&lsquo;', text)
    text = re.sub(r'(&bdquo;)(<b>)({})(</b>)(&bdquo;|&ldquo;)'.format(single_term), r'&sbquo;\2\3\4&lsquo;', text)
    text = re.sub(r'(&bdquo;)(<em>)({})(</em>)(&bdquo;|&ldquo;)'.format(single_term), r'&sbquo;\2\3\4&lsquo;', text)
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


def format_lists(text):
    pad0 = r'<p style="padding-left: {};">'.format(PADDINGS[0])
    pad1 = r'<p style="padding-left: {};">'.format(PADDINGS[1])
    pad2 = r'<p style="margin-top:-10; padding-left: {};">&bull;'.format(PADDINGS[2])

    # list -> 'a.' to '<ol><li>...</li>', 'i.' to '  <ol class="i"><li>...</li>', bullets to '<li>...</li>'
    text = re.sub(r'({}a. )'.format(pad0), r'<ol>\n\1', text)
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
    text = header + text

    text = re.sub(r'<b style="color:#004161;">', r'<b>', text)
    text = re.sub(r'<p style="font-weight: bold; color:#004161;">', r'<p class="verse">', text)
    return text


def add_copyright(text):
    copyright = '\n<p><br /><em>&copy; 2022 The <a href="https://enduringword.com/">Enduring Word</a> '
    copyright += 'Bible Commentary by David Guzik.</em></p>\n<body>'
    text = re.sub(r'([\n\r])([\n\r])', r'\1', text + copyright)
    return text


def format_bible_verses(text, title=None):
    h4_1 = '(<h4>\d{1,3}\. )(\(Vers )(\d{1,3}\s?\w?)(|,\d{1,2})(|\-\d{1,3}\s?\w?)(\) )(.*</h4>[\r\n])'
    h4_2 = '(<h4>\d{1,3}\. )(\(Vers )(\d{1,3}\s?\w?)(|,\d{1,2})(\-\d{1,3}\s?\w?,\d{1,2})(\) )(.*</h4>[\r\n])'
    for h4 in [h4_1, h4_2]:
        h4_verse = r'{}(<p class="verse"> )(.*)(</p>)'.format(h4)
        if title[-1].isdigit():
            text = re.sub(h4_verse, r'\1\7<hr>\8&bdquo;\9&ldquo;  <small>({},&thinsp;\3\4\5)</small>\10<hr>'.format(title), text)
        else:
            text = re.sub(h4_verse, r'\1\7<hr>\8&bdquo;\9&ldquo;  <small>({} \3\4\5)</small>\10<hr>'.format(title), text)
    text = re.sub('(\d{1,3}),(\d{1,3})', r'\1,&thinsp;\2', text)
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


def assertion_test(text, text_orig, title):
    title_with_space = title + ' ' * (15 - len(re.sub(r'[^a-zA-Z0-9\s]', r'', title)))

    for item in ['h2', 'h3', 'h4', 'p', 'ol', 'li']:
        count_open = text.count('<{}'.format(item))
        count_close = text.count('</{}'.format(item))
        if count_open != count_close:
            print('{} Unbalanced <{}>: {} <> {}'.format(title_with_space, item, count_open, count_close))
        if (item == 'ol') and (text_orig.count('<ol>') > 0):
            text_sample = ' '.join(re.findall(r'<ol>(.*)</ol>', text_orig)[0].split()[:10])
            print('{} {} <ol> in raw html detected: {}'.format(title_with_space, text_orig.count("<ol>"), text_sample))

    if text.count('. (Vers ') > 0:
        print('{} {} verse not correctly formatted'.format(title_with_space, text.count("(Vers ")))
    if text.count('style="padding-left') > 0:
        print('{} {} bullets not correctly formatted'.format(title_with_space), text.count('style="padding-left'))

    if False:  #check quotation marks later
        count_open, count_close = text.count('&bdquo;'), text.count('&ldquo;')
        if count_open != count_close:
            print('{} Unbalanced quotation marks: {} <> {}'.format(title_with_space, count_open, count_close))


"""Markdown mappings"""

def style_mappings_md(text):
    text = re.sub(r'[\r\n](\w)', r'\1', text)
    text = re.sub(r'([\r\n])(\#\#\# [A-Z]\.)', r'\1\n\2', text)
    text = re.sub(r'([\r\n])(\#\#\#\# \d{1,3})', r'\1\n\2', text)

    text = re.sub(r'([\r\n])  \d{1,3}\. (\*\*)', r'\1\n\n\2', text)
    text = re.sub(r'([\r\n])    \d{1,3}\.', r'\1*', text)
    text = re.sub(r'([\r\n])      \d{1,3}\.', r'\1   *', text)
    text = re.sub(r'([\r\n])([\r\n])', r'\1', text)

    text = re.sub(r'(\* \* \*[\r\n]„)(.*)(")', r'\1**\2** \3', text)
    return text


"""Compare text with Schlachter bible text"""

def load_bible():
    file = os.path.join(os.path.dirname(__file__), 'Schlachter.txt')
    bible = open(file, 'rb').read().decode('ISO-8859-1')
    bible = re.sub(r'[^a-zA-Z0-9\s]', r'', bible)
    bible = re.sub(r'([\r\n])', r' ', bible)
    bible = re.sub(r' \d{1,3} ', r' ', bible)
    bible = re.sub(r'  ', r' ', bible)
    return bible


def bible_check(text, title):
    title_with_space = title + ' ' * (15 - len(re.sub(r'[^a-zA-Z0-9\s]', r'', title)))

    bible = load_bible().lower()
    verses = re.findall(r'<hr><p class="verse"> &bdquo;(.*)&ldquo;  <small>', text.lower())
    verse_nums = re.findall(r'<hr><p class="verse"> &bdquo;.*&ldquo;  <small>\((.*)\)</small>', text.lower())

    n = 0
    for vers, vers_num in zip(verses, verse_nums):
        vers = copy(re.sub(r'<br />|<small>|<small>|&bdquo;|&ldquo;', r'', vers))
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
            print('{} {}% of verses covered by Schlachter'.format(title_with_space, perc_covered))

    return bible


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