# Word-to-HTML/JSON (for EnduringWord commentary) 

Vielen Dank für Deine wertvolle Unterstützung! 
Ziel des IT-Projekts ist es unsere Arbeit der deutschen Übersetzung ([ICF-Projekt](https://bibel-kommentar.de)) von [Enduring Word](https://enduringword.com/) publizierbar zu machen. 
Hierfür benötigen wir einen Konvertierer von Word zu HTML/JSON (und ggf. ein Plugin für WordPress). 

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

#### Qs:
- Extend https://pydocx.readthedocs.io/?
- Langfristige Lösung für mehrere Sprachen?
- Plug-in für Wordpress (bspw. [mammoth docx converter](https://de.wordpress.org/plugins/mammoth-docx-converter/)? 
- Automatisiertes Hochladen?
- Wie kommen die Inhalte von der Website in die App?
- Autor Rolle (WordPress-Benutzer ohne administrativen Rechte, nur Inhalte ausgewählter Seiten bearbeiten)?


### Bibleserver
- JSON (Format siehe [/examples](https://github.com/VolkerBergen/bible_commentary/tree/main/examples).)
- Kontakt: Timotheus Israel

#### Qs:
- Utf8? Ja. 
- Wie automatisiert hochladen?
- Wie sind Bücher/Kapitel in JSON-files unterteilt?


## Weitere Details

### HTML
Aktuell verwendete ad-hoc HTML-Konvertierung:
- CONVERT with Word365-HTML internal converter (vorher alle Kommentare entfernen)
- REPLACE ([MassReplaceIt](http://www.hexmonkeysoftware.com/)):
  - ```<p class=BibleText> —> <p style="font-weight: bold; color:#004161;">```
- CLEAN ([html-cleaner](https://html-cleaner.com/)) with settings:
  - Remove classes and IDs 
  - Remove successive &nbps;s 
  - Remove empty tags 
  - Remove tags with one &nbps; 
  - Remove span tags 
  - Remove links 
  - Encode special characters
  
- REPLACE, um EnduringWord-Formatierung (e.g., color #004161) zu übernehmen:
  - ```<div> —> <div style="margin:30px;">``` (margin)
  - ```<strong> —> <b style='color:#004161;’>``` (blue color)
  - ```</strong> —> </b>```
  - ```margin-left —> padding-left``` (paddings)
  - ```.5in —>  30px```
  - ```1.0in —>  60px```
  - ```1.0in —>  60px```
  - ```style="padding-left: 60px; text-indent: -.25in;  —>  style="padding-left: 75px;``` (bullets)
  - ```style="padding-left: 90px; text-indent: -.25in;  —>  style="padding-left: 75px;```
  - ```Remove style="vertical-align: middle;"```
  - ```Remove punctuation-wrap: hanging;```
  - ```Remove text-autospace: none;```
  - ```&hellip;  —>  ...```

### JSON
Aktuell benutzen wir die Konvertierung von HTML in Markdown, um dann manuell JSON files zu erstellen.