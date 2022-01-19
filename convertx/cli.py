import argparse
import io
import os
import sys

from mammoth import convert, writers
from html2text import html2text

from .styles import style_mappings, style_mappings_md, check_comments


def main():
    argv = [arg for arg in sys.argv if not arg.startswith('--')]
    argv_dir = ' '.join([arg for arg in sys.argv if arg.startswith('--')])

    command = 'find -s . -name "*docx*" -print0 | while IFS= read -r -d "" filename; do\n'  # find docx files
    command += 'convertx "$filename" "${filename//docx/html}"'  # execute convertx command
    command += ' {}\ndone'.format(argv_dir)  # add input/output directories

    # `convertx` to loop through directory for conversion
    if (len(argv) == 1):
        os.system(command)

    # `convertx html` to loop through directory for conversion
    elif (len(argv) == 2) and ('html' in argv[-1]):
        os.system(command)

    # `convertx markdown` to loop through directory for conversion
    elif (len(argv) == 2) and ('markdown' in argv[-1]):
        os.system(command.replace('html', 'md'))

    # `convertx filename.docx` for html conversion into filename.html
    elif len(argv) == 2:
        filename_docx = argv[-1]
        filename_html = filename_docx.replace("docx", "html")
        os.system('convertx "{}" "{}"'.format(filename_docx, filename_html))

    # actual html or markdown conversion
    else:
        args = _parse_args()

        outdir = args.output_dir
        if outdir is not None and not os.path.exists(outdir):
            os.makedirs(outdir)

        is_valid = (not '~$' in args.path) and (not '/._' in  args.path)
        is_selected = (args.input_dir is None) or (args.input_dir in args.path)

        if is_valid and is_selected:
            with open(args.path, "rb") as docx_fileobj:

                if outdir is None:
                    path, file = os.path.split(args.output)
                else:
                    path, file = outdir, os.path.basename(args.output)
                output_path = os.path.join(path, file.replace(' ', ''))

                if outdir is not None:
                    output_file = os.path.join(path, "output.txt")
                    sys.stdout = open(output_file, 'a')  # todo: reset at beginning

                result = convert(docx_fileobj).value

                if args.output.endswith('html'):
                    title = args.output.split('/')[-1].strip('.html')
                    result = style_mappings(result, title)

                elif args.output.endswith('md'):
                    title = args.output.split('/')[-1].strip('.md')
                    result = style_mappings(result, title)

                    result = html2text(result)
                    result = style_mappings_md(result)

                else:
                    raise ValueError('File format not supported.')

                check_comments(args.path, title)

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
        "--input-dir",
        help="Input directory for generated HTML.")

    parser.add_argument(
        "--output-dir",
        help="Output directory for generated HTML.")

    return parser.parse_args()


if __name__ == "__main__":
    main()

