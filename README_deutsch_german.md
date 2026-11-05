# Zangbundel bibliotheek van Pepe

( **English version** of this document available: [README.md](README.md) )

<br>

Eine Liederbibliothek für die App [Zangbundel](https://github.com/pe1mew/Zangbundel). Die App zeigt die Liedtexte gleichzeitig auf den Handys aller Sängerinnen und Sänger an; ein Leiter-Handy schickt die Lieder per Bluetooth. Die Lieder selbst kommen aus Bibliotheken wie dieser.

Diese Bibliothek enthält **gemeinfreie deutschsprachige Lieder**. Sie folgt dem Zangbundel-Bibliotheksformat 1.1 - vgl. https://github.com/pe1mew/Zangbundel/blob/main/design/song-format.md

<br>

## Schnellstart

**Bibliothek in der App hinzufügen:** In der App die URL des Release-Index angeben:

```
https://raw.githubusercontent.com/<konto>/<repository>/main/releases.json
```

Oder die `.zbl`-Datei von der Release-Webpage herunterladen und in der App mit «Aus Datei importieren» öffnen.

**Lied hinzufügen, prüfen und veröffentlichen:**

```cmd
python menu-with-tutorial-for-release-process.py
```

Dieses Menü führt Schritt für Schritt bis zum Release (unter Windows gibt es zusätzlich `menu-for-release-process.bat`). Nur prüfen geht auch direkt:

```
python scripts/validate.py --strict --info .
```

<br>

## Vollständige Dokumentation

Alle Details – Aufbau, Liedformat, Urheberrecht, Releases und Veröffentlichung – stehen in [DOCUMENTATION_deutsch_german.md](DOCUMENTATION_deutsch_german.md).

<br>

## Vibe-Coding-Deklaration

Diese Software wurde mittels **Vibe Coding** erstellt: Die beiden Menüs (`menu-with-tutorial-for-release-process.py`, `menu-for-release-process.bat`) wurden von der KI Claude (Anthropic) geschrieben. Die Werkzeuge unter `scripts/` stammen von Remko Welling, PE1MEW. Als Autor habe ich die Anforderungen und die beabsichtigte Funktionalität spezifiziert und in mehreren Etappen ergänzt; die KI hat den Code jeweils entsprechend geschrieben und angepasst. Auch die Projektdokumentation (README usw.) wurde KI-unterstützt verfasst. Die Liedtexte wurden KI-gestützt erfasst und sind gegen eine gemeinfreie Quelle zu prüfen.

Das Ergebnis habe ich bezüglich Funktionalität eingehend geprüft. Die Tests beschränkten sich auf das von aussen beobachtbare Verhalten (**Black-Box-Tests**).

Den Python-Code selbst habe ich weder gelesen noch bezüglich Qualität oder Sicherheit geprüft. Geprüft wurde lediglich, ob der Code gut und in englischer Sprache kommentiert ist, da dies eine der Vorgaben war.

Die Nutzung erfolgt auf eigenes Risiko (siehe auch die [Lizenz](LICENSE)). Wer den Code prüft und dabei Fehler oder Schwachstellen findet, ist herzlich eingeladen, ein [Issue auf GitHub](https://github.com/pepe-hb9evt/Zangbundel-bibliotheek-van-Pepe/issues) zu eröffnen.

<br>

## Lizenz

Die Lieder sind gemeinfrei (Public Domain). Die Sammlung (Auswahl, Abschriften, Metadaten, Dokumentation) und die beiden Menüs im Hauptordner stehen unter [CC0 1.0](LICENSE). Die Werkzeuge unter `scripts/` stammen aus [pe1mew/Zangbundel-bibliotheek](https://github.com/pe1mew/Zangbundel-bibliotheek) von Remko Welling, PE1MEW, und stehen unter Apache 2.0 mit Commons Clause (siehe [scripts/LICENSE](scripts/LICENSE)).

<br>

## Autor

Pepe HB9EVT, https://github.com/pepe-hb9evt
mit Unterstützung durch die KI Claude von Anthropic (vgl. Kapitel [Vibe-Coding-Deklaration](#vibe-coding-deklaration))
