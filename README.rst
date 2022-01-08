ConvertX for the Enduring Word commentary
=========================================

Converting Word-to-HTML/JSON, in order to publish our german translations
(see `ICF project <https://bibel-kommentar.de>`_) Enduring Word commentary at
`Enduring Word <https://de.enduringword.com/>`_ and `Bibleserver <https://bibleserver.com/>`_.

How to convertX
---------------

Installation: `pip install -U convertx`

CLI (single file)

- `convertx document.docx output.html`
- `convertx document.docx output.md`

CLI (full directory)

- `cd` into directory and run `convertx html`
- `cd` into directory and run `convertx markdown`

Additional arguments:

- `--output-dir=output`  (directory for generated HTML)
- `--input-dir=Deutsch`  (sub-/directories to include)


Project Outline
---------------

File formats:

- (Input-format) Word-files at OneDrive.
- (Output-format) HTML/JSON at `/examples <https://github.com/VolkerBergen/bible_commentary/tree/main/examples>`_.


Enduring Word
^^^^^^^^^^^^^

- Point of contact: **Andrea Kölsch**
- HTML converter `convertx` done.
- tbd: choose WordPress plugin (`wpeverest <https://wpeverest.com/wordpress-plugins/everest-forms/>`_, `mammoth <https://de.wordpress.org/plugins/mammoth-docx-converter/>`_ or `seraphinite <https://www.pluginforthat.com/plugin/seraphinite-post-docx-source/>`_)
- tbd: streamline the process of uploading `Google Docs to WordPress <https://kinsta.com/blog/google-docs-to-wordpress/>`_ by:
     1. Switch to the Gutenberg Block Editor
     2. Try Wordable to Streamline the Google Docs to WordPress Workflow
     3. Install the Mammoth .docx Converter Plugin
     4. Use the Jetpack WordPress.com for Google Docs Add-On
     5. Convert to Markdown with the Docs to Markdown Add-On
     6. Give Writers a WordPress Account

Bibleserver
^^^^^^^^^^^

- Point of contact: **Timotheus Israel**
- tbd: JSON (using UTF-8)
- tbd: Clarify auto-upload possibilities
- tbd: How are chapters divided into single-multiple JSON-files?
