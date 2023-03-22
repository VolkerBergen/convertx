ConvertX for the Enduring Word commentary
=========================================

Converting Word documents to HTML/JSON, in order to publish our german translation of the Enduring
Word commentary at
`enduringword.de <https://de.enduringword.com/>`_ and `bibleserver.com <https://bibleserver.com/>`_.

How to convertX
---------------

Installation: ``pip install -U convertx``

Command: ``convertx [html|doc|json] [file|folder]``

HTML

- ``convertx html document.docx`` (single file)
- ``convertx html .`` (entire directory)

Markdown/JSON

- ``convertx markdown . --input-dir Deutsch`` (markdown)
- ``convertx json markdown`` (json)

Additional arguments:

- ``--output-dir=html``  (directory for generated output files)
- ``--input-dir=Deutsch``  (sub-/directories to include)
- ``--dry-run`` (only validate without converting)
- ``--verbose`` (debug logging)