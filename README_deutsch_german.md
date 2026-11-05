# Deutsche Lieder – Zangbundel-Bibliothek

Eine Liederbibliothek für die App [Zangbundel](https://github.com/pe1mew/Zangbundel). Die App zeigt die Liedtexte gleichzeitig auf den Handys aller Sängerinnen und Sänger an; ein Leiter-Handy schickt die Lieder per Bluetooth. Die Lieder selbst kommen aus Bibliotheken wie dieser.

Diese Bibliothek (`pepe-deutsche-lieder`) enthält **gemeinfreie deutsche Lieder**: Kinder-, Laternen-, Weihnachts- und Kirchenlieder. Sie folgt dem Zangbundel-Bibliotheksformat 1.1.

English version: [README.md](README.md)

## Schnellstart

**Bibliothek in der App hinzufügen:** In der App die URL des Release-Index angeben:

```
https://raw.githubusercontent.com/<konto>/<repository>/main/releases.json
```

Oder die `.zbl`-Datei von der Release-Webpage herunterladen und in der App mit «Aus Datei importieren» öffnen.

**Lied hinzufügen, prüfen und veröffentlichen:** `python scripts/menu.py` starten – das Menü führt Schritt für Schritt bis zum Release (unter Windows gibt es zusätzlich `Menu for zangbundel-tools.bat`). Nur prüfen geht auch direkt:

```
python scripts/validate.py --strict --info .
```

Alle Details – Aufbau, Liedformat, Urheberrecht, Releases und Veröffentlichung – stehen in [DOCUMENTATION_deutsch_german.md](DOCUMENTATION_deutsch_german.md).

## Lizenz

Die Lieder sind gemeinfrei (Public Domain). Die Sammlung (Auswahl, Abschriften, Metadaten, Dokumentation) steht unter [CC0 1.0](LICENSE). Die Werkzeuge unter `scripts/` stammen aus [pe1mew/Zangbundel-bibliotheek](https://github.com/pe1mew/Zangbundel-bibliotheek) von Remko Welling, PE1MEW, und stehen unter Apache 2.0 mit Commons Clause (siehe [scripts/LICENSE](scripts/LICENSE)).
