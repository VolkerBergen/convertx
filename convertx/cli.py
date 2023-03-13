import argparse
import json
import logging
import os
import re
import sys
from datetime import date
from logging.handlers import RotatingFileHandler

from html2text import html2text
from mammoth import convert
from markdown_it import MarkdownIt

from .styles import style_mappings, style_mappings_md, check_comments


def init_logger(args):
    logger = get_logger()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger.setLevel(logging.DEBUG)

    # file logging
    logging_file = None
    if args.command == "html":
        logging_file = "convert2html.log"
    elif args.command == "markdown":
        logging_file = "convert2md.log"
    elif args.command == "json":
        logging_file = "merge2json.log"
    file_logging = RotatingFileHandler(logging_file)
    file_logging.setLevel(log_level)
    file_logging.setFormatter(formatter)
    logger.addHandler(file_logging)

    # console logging
    console_logging = logging.StreamHandler()
    console_logging.setLevel(logging.INFO)
    logger.addHandler(console_logging)
    pass


def get_logger():
    return logging.getLogger("convertx")


def main():
    args = _parse_args()
    init_logger(args)

    if args.output_dir is None:
        args.output_dir = args.command

    if args.command == "json":
        combine_markdown_to_json(args.file_or_folder)
    else:
        convert_docx_files(args)


def combine_markdown_to_json(file_or_dir):
    data = {}
    resources = {'name': "Resource Reference Schema", 'locale': "en", 'abbreviation': "RRS",
                 'provider': "commentary", 'cacheable': True, 'publisher': "ERF Medien",
                 'logo': "https:\/\/www.erf.de\/download\/logo\/L_ERF_Basis.jpg",
                 'copyright': "\u00a9 ERF Medien", 'api': None, 'public_url': True}
    items = []

    md = MarkdownIt()
    files = []
    if os.path.isdir(file_or_dir):
        files += [os.path.join(file_or_dir, file) for file in os.listdir(file_or_dir) if file.endswith(".md")]
    files.sort()
    file_pattern = re.compile(r'[\w/]*?([0-9]*?)(_\w*_)([0-9]*?).md')
    for file in files:
        match = file_pattern.fullmatch(file)
        chapter_canonical = int(match.group(1)) * 1000000 + int(match.group(3)) * 1000
        should_process_file = True
        # should_process_file = "Matthew" in file
        # should_process_file = "043_John_Deutsch_Johannes_019" in file
        if should_process_file:
            get_logger().info("Processing file {}".format(file))
            with open(file, "r") as file_obj:
                tokens = md.parse(file_obj.read())
                parse_tokens(tokens, chapter_canonical, items)

    resources['items'] = items
    data['resources'] = resources
    formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
    output_folder = "json"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_filename = os.path.join(output_folder, "output.json")
    with open(output_filename, "w", encoding="utf-8") as output_file:
        output_file.write(formatted_json)


def wait_for_token(iterator, token_type, token_tag):
    while True:
        try:
            token = next(iterator)
            if token.type == token_type and token.tag == token_tag:
                break
        except StopIteration:
            get_logger().error("wait_for_token {} {} - stopped unexpectedly".format(token_type, token_tag))
            break


def handle_title(iterator, token, entry, chapter_canonical, items, title_found):
    title_tag = 'h3'
    if token.type == 'heading_open' and token.tag == title_tag:
        if not entry['canonicals'] and 'title' in entry:
            if len(items) < 2 or items[-2]['chapter_canonical'] != chapter_canonical:
                # Set default canonical for introduction and other chapters without verse context
                default_canonical = chapter_canonical + 1
                entry['canonicals'].append(default_canonical)
                get_logger().info('no verses found for entry with title \"{}\". First entry in this chapter, so assuming intro and setting default canonical: {}'.format(entry['title'], default_canonical))
            else:
                next_canonical = items[-2]['canonicals'][-1] + 1
                entry['canonicals'].append(next_canonical)
                get_logger().info('no verses found for entry with title \"{}\" and not first entry in this chapter. Getting the next verse as canonical {}'.format(entry['title'], next_canonical))
        entry = create_entry()
        items.append(entry)
        entry['id'] = len(items)
        entry['chapter_canonical'] = chapter_canonical
        title_raw = next(iterator).content
        entry['title'] = title_raw
        entry['content'] = ''
        wait_for_token(iterator, 'heading_close', title_tag)
        title_found = True
    return entry, title_found


def handle_content(iterator, token, entry, title_found):
    section_title = "h4"
    if title_found and token.type == "heading_open" and token.tag == section_title:
        if entry['content'] != "":
            entry['content'] += "\n"
        token = next(iterator)
        if token.type == "inline":
            get_logger().debug("entry {} - content for section title found".format(entry['id']))
            section_title_raw = token.children[0].content
            entry['content'] += "### {} \n\n".format(section_title_raw)
        else:
            get_logger().info("no section title found in token: {}", token)
        wait_for_token(iterator, "heading_close", section_title)

    citation_tag = "hr"
    get_logger().debug("handle_content: {}".format(token))
    citation_marker = '****'
    if title_found and token.type == citation_tag and token.tag == citation_tag and token.markup == citation_marker:
        citation_search_start = True
        citation_raw_parts = []
        while citation_search_start or not (token.type == citation_tag and token.tag == citation_tag and token.markup == citation_marker):
            citation_search_start = False
            token = next(iterator)
            if token.type == "inline":
                get_logger().debug("entry {} - citation part found: {}".format(entry['id'], token.content))
                citation_raw_parts.append(token.content)
                token = next(iterator)
        citation_raw = ' '.join(citation_raw_parts)
        get_logger().debug("entry {} - combined citation parts: {}".format(entry['id'], citation_raw))
        entry['content'] += "**{}**\n".format(citation_raw)
        handle_canonicals(entry['id'], entry['chapter_canonical'], entry['canonicals'], citation_raw)

    basic_content = "p"
    if title_found and token.type == "paragraph_open" and token.tag == "p":
        token = next(iterator)
        if token.type == "inline":
            get_logger().debug("entry {} - content found at level {}".format(entry['id'], token.level))
            basic_content_raw = token.content
            indent = " ".join([""] * token.level)
            entry['content'] += "{}* {}\n".format(indent, basic_content_raw)
        else:
            print("handle_content - basic content paragraph not found in token: " + token)
        wait_for_token(iterator, "paragraph_close", basic_content)
    return entry


def handle_canonicals(entry_id, chapter_canonical, canonicals, citation):
    citation = citation.replace("\n", "")
    verse_match = re.match(r'.*\(.*[0-9]*,[\s]*([0-9]*)[a-d]?[-]?([0-9]*)[a-d]?\)', citation)
    if verse_match is not None:
        if verse_match.group(2) == "" and (chapter_canonical + int(verse_match.group(1))) not in canonicals:
            canonicals.append(chapter_canonical + int(verse_match.group(1)))
        elif verse_match.group(2) != "":
            for verse in range(int(verse_match.group(1)), int(verse_match.group(2))+1):
                if (chapter_canonical + verse) not in canonicals:
                    canonicals.append(chapter_canonical + verse)
    else:
        get_logger().warning("entry {} - verses could not be parsed for citation {}".format(entry_id, citation))


def parse_tokens(tokens, chapter_canonical, items):
    iterator = iter(tokens)
    entry = create_entry()
    token = None
    title_found = False
    while True:
        try:
            token = next(iterator)
            entry, title_found = handle_title(iterator, token, entry, chapter_canonical, items, title_found)
            entry = handle_content(iterator, token, entry, title_found)
        except StopIteration:
            break
        except Exception as e:
            get_logger().error("Processing stopped unexpectedly: {}".format(e))
            get_logger().error("Current token: {}".format(token))
            raise


def create_entry():
    return {'amp': False, 'canonicals': []}


def convert_docx_files(args):
    files = collect_files(args.file_or_folder, args.sub_input_dir_name, ".docx")

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    file_pattern = re.compile(r'([0-9]*?)(_\w*_)([0-9]*?)')

    for file in files:
        output_filename = os.path.splitext(os.path.basename(file))[0].replace(' ', '_')
        if args.command == "markdown":
            folder_prefix = os.path.dirname(file).replace("." + os.sep, "").replace(os.sep, '_').replace(" ", "_") + "_"
            output_filename = folder_prefix + output_filename
            match = file_pattern.fullmatch(output_filename)
            output_filename = f'{int(match.group(1)):03}' + match.group(2) + f'{int(match.group(3)):03}' + ".md"
        elif args.command == "html":
            output_filename += ".html"

        convert_file(file, os.path.join(args.output_dir, output_filename), args.dry_run)


def collect_files(file_or_dir, sub_folder, file_ext):
    files = []
    if os.path.isdir(file_or_dir):
        get_files_in_dir(files, file_or_dir, sub_folder, file_ext)
    elif os.path.isfile(file_or_dir) and file_or_dir.endswith(file_ext):
        files.append(file_or_dir)
    else:
        raise ValueError("File or directory {} not found".format(file_or_dir))
    return files


def get_files_in_dir(files, base_dir, expected_sub_dir, file_ext):
    for file_or_dir in os.listdir(base_dir):
        full_path = os.path.join(base_dir, file_or_dir)
        sub_dir = os.path.join(full_path, expected_sub_dir)
        if os.path.isdir(full_path):
            if os.path.exists(sub_dir):
                files += [os.path.join(sub_dir, file) for file in os.listdir(sub_dir) if file.endswith(file_ext)]
            else:
                get_files_in_dir(files, full_path, expected_sub_dir, file_ext)
        # elif os.path.isfile(full_path) and full_path.endswith(full_path):
        #     files.append(full_path)


def convert_file(input_file, output_file, dry_run):
    with open(input_file, "rb") as docx_fileobj:
        format_errors_file = "format_errors.txt"
        if not os.path.exists(format_errors_file):
            sys.stdout = open(format_errors_file, 'a')
        if str(date.today()) not in open(format_errors_file).readline():
            sys.stdout = open(format_errors_file, 'w')  # reset
            print('{}\n'.format(date.today()))

            sys.stdout = open(format_errors_file, 'a')
            print('see --> https://youtu.be/9HIv-R8lg9I <-- for explanations.\n\n')

        sys.stdout = open(format_errors_file, 'a')

        result = convert(docx_fileobj).value

        title = os.path.splitext(os.path.basename(input_file))[0]
        if output_file.endswith('html'):
            result = style_mappings(result, title)
        elif output_file.endswith('md'):
            result = style_mappings(result, title, wordpress=False)
            result = html2text(result)
            result = style_mappings_md(result)

        else:
            raise ValueError('File format not supported.')

        check_comments(input_file, title)

        if not dry_run:
            _write_output(output_file, result)


def _write_output(path, contents):
    with open(path, "w", encoding="utf-8") as fileobj:
        fileobj.write(contents)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "command",
        help="Command to execute [html, markdown, json]")

    parser.add_argument(
        "file_or_folder",
        help="File and folder to process")

    parser.add_argument(
        "--sub-input-dir-name",
        default="",
        help="Name of sub directory of input docx files.")

    parser.add_argument(
        "--output-dir",
        default="",
        help="Output directory for generated HTML.")

    parser.add_argument(
        "--dry-run",
        action='store_true',
        default=False,
        help="only validate, do not write converted files.")

    parser.add_argument(
        "--verbose",
        action='store_true',
        default=False,
        help="Enables debug logging")

    return parser.parse_args()


if __name__ == "__main__":
    main()

