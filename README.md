# Word-to-HTML/JSON (for EnduringWord commentary) 

We aim to build a converter for our german translations (see [ICF project](https://bibel-kommentar.de)) of the 
Enduring Word commentary from Word to HTML/JSON, in order to publish it at 
[Enduring Word](https://de.enduringword.com/) and [Bibleserver](https://bibleserver.com/) . 

#### Important ressources:
- (Input) Word-files at OneDrive.
- (Output) HTML/JSON at [/examples](https://github.com/VolkerBergen/bible_commentary/tree/main/examples).

## ConvertX

Our Python implementation `convertx` converts Docx-to-HTML. 

Installation: `pip install git+https://github.com/VolkerBergen/convertx`

CLI (single file)
- `convertx document.docx output.html`
- `convertx document.docx output.md`

CLI (full directory)
- `cd` into directory and run `convertx html`
- `cd` into directory and run `convertx markdown`

Additional arguments:
- `--output-dir=output`  (directory for generated HTML)
- `--input-dir=Deutsch`  (sub-/directories to include)

## Project Outline

### Enduring Word
- Point of contact: **Andrea Kölsch**
- HTML converter `convertx` done.
- tbd: choose WordPress plugin ([wpeverest](https://wpeverest.com/wordpress-plugins/everest-forms/) or [mammoth](https://de.wordpress.org/plugins/mammoth-docx-converter/) or [seraphinite](https://www.pluginforthat.com/plugin/seraphinite-post-docx-source/))
- tbd: Auto-upload of files to WordPress -->  streamline the process of uploading [Google Docs to WordPress](https://kinsta.com/blog/google-docs-to-wordpress/) by:
     1. Switch to the Gutenberg Block Editor
     2. Try Wordable to Streamline the Google Docs to WordPress Workflow
     3. Install the Mammoth .docx Converter Plugin
     4. Use the Jetpack WordPress.com for Google Docs Add-On
     5. Convert to Markdown with the Docs to Markdown Add-On
     6. Give Writers a WordPress Account

### Bibleserver
- Point of contact: **Timotheus Israel**
- tbd: JSON (using UTF-8, see [/examples](https://github.com/VolkerBergen/bible_commentary/tree/main/examples))
- tbd: Clarify auto-upload possibilities
- tbd: How are chapters divided into single-multiple JSON-files?
