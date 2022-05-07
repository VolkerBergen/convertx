import argparse
import io
import os
import sys
from datetime import date

from html2text import html2text
from mammoth import convert

from .styles import style_mappings, style_mappings_md, check_comments


def main():
    args = _parse_args()
    if args.output_dir is None:
        args.output_dir = args.command

    files = []
    if os.path.isdir(args.file_or_folder):
        print("collecting files from folder {}".format(args.file_or_folder))
        get_files_in_dir(files, args.file_or_folder, args.sub_input_dir_name)
    elif os.path.isfile(args.file_or_folder):
        files.append(args.file_or_folder)
    else:
        raise ValueError("File or directory {} not found".format(args.file_or_folder))

    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    for file in files:
        folder_prefix = os.path.dirname(file).replace(os.sep, '_').replace(" ", "_") + "_" if args.command == "markdown" else ""
        file_name_without_ext = os.path.splitext(os.path.basename(file))[0].replace(' ', '_')
        output_ext = ".md" if args.command == "markdown" else ".html"
        convert_file(file, os.path.join(args.output_dir, folder_prefix + file_name_without_ext + output_ext), args.dry_run)
        pass


def get_files_in_dir(files, base_dir, expected_sub_dir):
    for file_or_dir in os.listdir(base_dir):
        sub_dir = os.path.join(file_or_dir, expected_sub_dir)
        if os.path.isdir(file_or_dir):
            if os.path.exists(sub_dir):
                files += [os.path.join(sub_dir, file) for file in os.listdir(sub_dir) if file.endswith(".docx")]
            else:
                get_files_in_dir(files, file_or_dir, expected_sub_dir)
        elif os.path.isfile(file_or_dir) and file_or_dir.endswith(".docx"):
            return files.append(file_or_dir)


def convert_file(input_file, output_file, dry_run):
    with open(input_file, "rb") as docx_fileobj:201
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

        title = os.path.splitext(os.path.basename(output_file))[0]
        result = style_mappings(result, title)

        if output_file.endswith('md'):
            result = html2text(result)
            result = style_mappings_md(result)

        else:
            raise ValueError('File format not supported.')

        check_comments(input_file, title)

        if not dry_run:
            _write_output(output_file, result)


def _write_output(path, contents):
    with io.open(path, "w", encoding="utf-8") as fileobj:
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
        type=bool,
        default=False,
        help="only validate, do not write converted files.")

    return parser.parse_args()


if __name__ == "__main__":
    main()

