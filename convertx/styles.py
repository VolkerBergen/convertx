import re

PADDINGS = ['30px', '60px', '80px']
COLOR = '#004161'


def style_mappings(text):
    text = standardize(text)
    text = regexp_style_mappings(text)
    text = align_styles(text)
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

        text = text.replace('<li><ul>', '')
        text = text.replace('</ul></li>', '')

    return text


def regexp_style_mappings(text):
    # Regular expressions used for parsing
    for _ in range(5):
        text = re.sub(r'(<div>)([\r\n]+)(<p>)(.*)(</p>)', r'\1\2<h2>\4</h2>', text)

        text = re.sub(r'(<p>)(<b>)?(<em>)?([A-Z]\.)(.*)(</b>)(</p>)', r'<h3>\4\5</h3>', text)
        text = re.sub(r'(<p>)(<b>)?(<em>)?([A-Z]\.)(.*)(</p>)', r'<h3>\4\5</h3>', text)

        text = re.sub(r'(<p>)(<b>)([0-9])(\. )(\()([0-9])(.*)(</b>)(</p>)', r'<h4>\3\4\5Vers \6\7</h4>', text)
        text = re.sub(r'(<p>)(<b>)?([0-9])(\. )(\()([0-9])(.*)(</b>)?(</p>)', r'<h4>\3\4\5Vers \6\7</h4>', text)

        text = re.sub(r'(<h2>)(.*)(<b><em>)(.*)(</em></b>)(.*)(</h2>)', r'\1\2\4\6\7', text)
        text = re.sub(r'(<h2>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h2>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h2>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h2>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h3>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h3>)', r'\1\2\4\5', text)
        text = re.sub(r'(<h3>)(.*)(<b>|<strong>|<em>|</em>|</b>)(.*)(</h3>)', r'\1\2\4\5', text)

        text = re.sub(r'(<h4>)(.*)(</h4>)([\r\n]+)(<p>)(.*)(</p>)', fr'\1\2\3\4<p style="font-weight: bold; color:{COLOR};"> \6\7', text)

        text = re.sub(r'(<p>)(<b>)?([a-h])(\.)', fr'<p style="padding-left: {PADDINGS[0]};">\2\3\4', text)
        text = re.sub(r'(<p>)(<b>)?([iv]+)(\.)', fr'<p style="padding-left: {PADDINGS[1]};">\2\3\4', text)

        text = re.sub(r'<p>&middot; (.*)</p>', fr'<p style="margin-top:-10; padding-left: {PADDINGS[2]};">&bull; \1</p>', text)
        text = re.sub(r'(<li>)(.*)(</li>)', fr'<p style="margin-top:-10; padding-left: {PADDINGS[2]};">&bull; \2</p>', text)

        text = re.sub(r'<ul>', r'', text)
        text = re.sub(r'</ul>', r'', text)

        text = re.sub(r'([\r\n]+)([\r\n][\r\n]+)', r'\1', text)
        text = re.sub(r'([\r\n]+)([\r\n]+)', r'\1', text)

        text = re.sub(r'<b>', r'<b style="color:#004161;">', text)

        text = re.sub(r'(</p>)([\r\n]+)(</div>)', r'\1\2<p><br /><em>&copy; 2022 The <a href="https://enduringword.com/">Enduring Word</a> Bible Commentary by David Guzik.</em></p> <! -- Copyright --> </div>', text)

        text = re.sub(r'(>[A-za-z0-9]\.)([^\s])', r'\1 \2', text)
        text = re.sub(r'<[^/>]+>[ \n\r\t]*</[^>]+>', r'', text)
        text = re.sub(r'\n(\w|\&)', r' \1', text)
        text = re.sub(r'([^\s])(\()', r'\1 \2', text)

        text = re.sub(r'„', r'&bdquo;', text)
        text = re.sub(r'“ ', r'&rdquo;', text)
        text = re.sub(r' “([^\s])', r' &bdquo;\1', text)

        text = re.sub(r' &quot;([^\s])', r' &bdquo;\1', text)
        text = re.sub(r'>&quot;([^\s])', r'>&bdquo;\1', text)
        text = re.sub(r'([^\s])&quot;', r'\1&rdquo;', text)
        text = re.sub(r' “([^\s])', r' &bdquo;\1', text)
        text = re.sub(r'&ldquo;', r'&bdquo;', text)

    return text


def align_styles(text):
    # Style unformatted html lines by applying style from preceding line
    for _ in range(20):
        for pad in PADDINGS:
            text = re.sub(fr'(<p style="padding-left: {pad};">)(.*)(</p>\n)(<p>)([^\d])', r'\1\2\3\1\5', text)
        text = re.sub(fr'(<p style="font-weight: bold; color:{COLOR};">)(.*)(</p>\n)(<p>)([^\d])', r'\1\2\3\1\5', text)
    return text