import argparse
import io
import os
import sys

from mammoth import convert, writers
from html2text import html2text

from .styles import style_mappings, style_mappings_md


def main():
    command = 'find . -name "*docx*" -print0 | while IFS= read -r -d "" filename; do\n'
    command += 'convertx "$filename" "${filename//docx/html}"\ndone'

    # loop through directory for html conversion
    if len(sys.argv) == 1:
        os.system(command)

    # loop through directory for markdown conversion
    elif (len(sys.argv) == 2) and (sys.argv[-1] == 'markdown'):
        os.system(command.replace('html', 'md'))

    # html conversion if only input file provided
    elif len(sys.argv) == 2:
        filename_docx = sys.argv[-1]
        filename_html = filename_docx.replace("docx", "html")
        os.system('convertx "{}" "{}"'.format(filename_docx, filename_html))

    # actual html or markdown conversion
    else:
        args = _parse_args()

        if args.style_map is None:
            style_map = None
        else:
            with open(args.style_map) as style_map_fileobj:
                style_map = style_map_fileobj.read()

        if not '~$' in args.path:
            with open(args.path, "rb") as docx_fileobj:
                if args.output_dir is None:
                    output_path = args.output
                else:
                    output_filename = "{0}.html".format(os.path.basename(args.path).rpartition(".")[0])
                    output_path = os.path.join(args.output_dir, output_filename)

                result = convert(
                    docx_fileobj,
                    style_map=style_map,
                    output_format=args.output_format,
                )

                if args.output.endswith('html'):
                    title = args.output.split('/')[-1].strip('.html')
                    result.value = style_mappings(result.value, title)

                elif args.output.endswith('md'):
                    title = args.output.split('/')[-1].strip('.md')
                    result.value = style_mappings(result.value, title)

                    result.value = html2text(result.value)
                    result.value = style_mappings_md(result.value)

                _write_output(output_path, result.value)


def _write_output(path, contents):
    if path is None:
        if sys.version_info[0] <= 2:
            stdout = sys.stdout
        else:
            stdout = sys.stdout.buffer

        stdout.write(contents.encode("utf-8"))
        stdout.flush()
    else:
        with io.open(path, "w", encoding="utf-8") as fileobj:
            fileobj.write(contents)


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        metavar="docx-path",
        help="Path to the .docx file to convert.")
    
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "output",
        nargs="?",
        metavar="output-path",
        help="Output path for the generated document. Images will be stored inline in the output document. Output is written to stdout if not set.")
    output_group.add_argument(
        "--output-dir",
        help="Output directory for generated HTML and images. Images will be stored in separate files. Mutually exclusive with output-path.")
    
    parser.add_argument(
        "--output-format",
        required=False,
        choices=writers.formats(),
        help="Output format.")
    parser.add_argument(
        "--style-map",
        required=False,
        help="File containg a style map.")
    return parser.parse_args()


if __name__ == "__main__":
    main()

