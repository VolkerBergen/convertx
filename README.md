# Word-to-HTML/JSON (for EnduringWord commentary) 

We aim bto build a converter for our german translations (see [ICF project](https://bibel-kommentar.de)) of the [Enduring Word](https://enduringword.com/) commentary from Word to HTML/JSON, in order to publish it at EnduringWord and Bibleserver. 

#### Important ressources:
- (Input) Word-files at [OneDrive](https://bibel-kommentar.de/onedrive).
- (Output) HTML/JSON at [/examples](https://github.com/VolkerBergen/bible_commentary/tree/main/examples). 

#### Platforms:

- [Enduring Word](https://enduringword.com/) & [our website](https://bibel-kommentar.de) -- HTML
- [Bibleserver](https://bibleserver.com/) -- JSON

## ConvertX

Our Python implementation `convertx` converts Docx-to-HTML (and will be extended for markdown). 
It makes use of [mammoth](https://github.com/mwilliamson/python-mammoth) and multiple regexp commands.

Installation: `pip install git+https://github.com/VolkerBergen/convertx`

CLI: `convertx document.docx output.html`

To loop through the entire directory, simply `cd` into a directory and run `convertx`.


## Project Outline

### Enduring Word
- Point of contact: **Andrea Kölsch**
- HTML converter `convertx` nearly done.
- tbd: WordPress plugin (e.g. [mammoth](https://de.wordpress.org/plugins/mammoth-docx-converter/))
- tbd: Auto-upload of files to WordPress

### Bibleserver
- Point of contact: **Timotheus Israel**
- tbd: JSON (using UTF-8, see [/examples](https://github.com/VolkerBergen/bible_commentary/tree/main/examples))
- tbd: Clarify auto-upload possibilities
- tbd: How are chapters divided into single-multiple JSON-files?
