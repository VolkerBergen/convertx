# Word-to-HTML/JSON (for EnduringWord commentary) 

Ziel des Projekts ist es unsere deutsche Übersetzung ([ICF-Projekt](https://bibel-kommentar.de)) von [Enduring Word](https://enduringword.com/) von Word zu HTML/JSON zu konvertieren, um sie auf EnduringWord und Bibleserver zu publizieren. 
Hierfür benötigen wir einen Konvertierer (und ggf. ein Plugin für WordPress). 

#### Wichtige Ressourcen:
- (Input) Word-Dateien im [OneDrive](https://bibel-kommentar.de/onedrive).
- (Output) HTML/JSON-Beispiele unter [/examples](https://github.com/VolkerBergen/bible_commentary/tree/main/examples). 

#### Ziel-Platformen:

- [Enduring Word](https://enduringword.com/) -- HTML
- [Bibleserver](https://bibleserver.com/) -- JSON
- [Eigene Website](https://bibel-kommentar.de) -- HTML


## Project Outline

### Enduring Word
- WordPress / HTML (Format siehe [/examples](https://github.com/VolkerBergen/bible_commentary/tree/main/examples).)
- Kontakt: Andrea Kölsch
- ***Aktueller Stand: `convertx` - erster Prototyp. ***

#### Qs:
- Plug-in für Wordpress (bspw. [mammoth](https://de.wordpress.org/plugins/mammoth-docx-converter/))? 
- Wie automatisiert hochladen?


### Bibleserver
- JSON (Format siehe [/examples](https://github.com/VolkerBergen/bible_commentary/tree/main/examples).)
- Kontakt: Timotheus Israel

#### Qs:
- Utf8? Ja. 
- Wie automatisiert hochladen?
- Wie sind Bücher/Kapitel in JSON-files unterteilt?


## ConvertX

Konvertierung von Docx zu HTML (in Python using [mammoth](https://github.com/mwilliamson/python-mammoth) und regexp).

Installation: `pip install git+https://github.com/VolkerBergen/convertx`

CLI: `convertx document.docx output.html`

CLI entire directory: 

```angular2html
find . -name '*docx*' -print0 | while IFS= read -r -d '' filename; do
  convertx "$filename" "${filename//docx/html}"
done
```
