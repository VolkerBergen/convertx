import argparse
import io
import os
import sys

from mammoth import convert, writers
from html2text import html2text

from .styles import style_mappings, style_mappings_md


def main():
    argv = [arg for arg in sys.argv if not arg.startswith('--')]

    command = 'find . -name "*docx*" -print0 | while IFS= read -r -d "" filename; do\n'
    command += 'convertx "$filename" "${filename//docx/html}"\ndone'

    if '--output-dir' in sys.argv[-1]:
        command = command.replace('\ndone', ' {}\ndone'.format(sys.argv[-1]))

    # loop through directory for html conversion
    if len(argv) == 1:
        os.system(command)

    # loop through directory for html conversion
    elif (len(argv) == 2) and ('html' in argv[-1]):
        os.system(command)

    # loop through directory for markdown conversion
    elif (len(argv) == 2) and ('markdown' in argv[-1]):
        os.system(command.replace('html', 'md'))

    # html conversion if only input file provided
    elif len(argv) == 2:
        filename_docx = argv[-1]
        filename_html = filename_docx.replace("docx", "html")
        os.system('convertx "{}" "{}"'.format(filename_docx, filename_html))

    # actual html or markdown conversion
    else:
        args = _parse_args()

        if not '~$' in args.path:
            with open(args.path, "rb") as docx_fileobj:

                if args.output_dir is None:
                    output_path = args.output
                else:
                    output_path = os.path.join(args.output_dir, os.path.basename(args.output))

                result = convert(docx_fileobj).value

                if args.output.endswith('html'):
                    title = args.output.split('/')[-1].strip('.html')
                    result = style_mappings(result, title)

                elif args.output.endswith('md'):
                    title = args.output.split('/')[-1].strip('.md')
                    result = style_mappings(result, title)

                    result = html2text(result)
                    result = style_mappings_md(result)

                _write_output(output_path, result)


def _write_output(path, contents):
    with io.open(path, "w", encoding="utf-8") as fileobj:
        fileobj.write(contents)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        metavar="docx-path",
        help="Path to the .docx file to convert.")

    parser.add_argument(
        "output",
        nargs="?",
        metavar="output-path",
        help="Output path for the generated document.")

    parser.add_argument(
        "--output-dir",
        help="Output directory for generated HTML.")

    return parser.parse_args()


if __name__ == "__main__":
    main()

