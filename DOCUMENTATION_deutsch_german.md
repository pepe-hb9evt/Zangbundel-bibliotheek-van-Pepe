# Zangbundel bibliotheek van Pepe

# Dokumentation

Dokumentation zum Projekt "**[Zangbundel-bibliotheek-van-Pepe](https://github.com/pepe-hb9evt/Zangbundel-bibliotheek-van-Pepe)**" auf GitHub.

( **English version** of this document available: [DOCUMENTATION.md](DOCUMENTATION.md) )

Dies ist eine ausführliche Dokumentation der Liederbibliothek und ihrer Werkzeuge. Für einen kurzen Überblick konsultiere das deutschsprachige [README](README_deutsch_german.md).

<br>

## 1. Aufbau des Repositorys

```
zangbundel.json            Metadaten der Bibliothek: id, Name, Lizenz, Maintainer, Tag-Bezeichnungen
LICENSE                    Lizenztext der Sammlung (CC0 1.0); die App zeigt ihn beim ersten Import
songs/                     eine ChordPro-Datei (.cho) pro Lied
releases.json              Release-Index; wird beim ersten Release automatisch erzeugt
scripts/validate.py        prüft die Bibliothek nach den Regeln des Formats
scripts/release.py         baut, prüft und indexiert die Release-Archive (.zbl)
scripts/LICENSE            Lizenz der Werkzeuge (Apache 2.0 mit Commons Clause)
menu-with-tutorial-for-release-process.py  Menü für Prüfen, Git-Schritte und Release (Python)
menu-for-release-process.bat  Menü für die Werkzeuge unter Windows
.github/workflows/         Prüfung bei jedem Push; Release bei jedem Tag
.gitignore                 Allow-List: nur ausdrücklich genannte Dateien kommen ins Repository
.gitattributes             legt die Zeilenenden fest (LF), damit Prüfsummen überall gleich sind
.editorconfig              Editor-Einstellungen passend zum Format (UTF-8, LF)
CLAUDE.md                  Arbeitsregeln für Claude (nur lokal, nicht im Repository)
```

Die App liest nur `zangbundel.json`, alle `.cho`-Dateien unter `songs/` und die Lizenzdatei. Die Unterordner unter `songs/` haben für die App keine Bedeutung; sie dienen nur der Übersicht.

## 2. Liedformat

Ein Lied ist eine `.cho`-Datei im ChordPro-Format nach der [Zangbundel-Formatspezifikation 1.1](https://github.com/pe1mew/Zangbundel/blob/main/design/song-format.md).

**Dateiname = Lied-ID:** Kleinbuchstaben, Ziffern und einzelne Bindestriche, aus dem Titel abgeleitet. Umlaute werden umgeschrieben: `ä` → `ae`, `ö` → `oe`, `ü` → `ue`, `ß` → `ss`. Beispiel: «Gott ist gegenwärtig» → `gott-ist-gegenwaertig.cho`. Eine veröffentlichte ID wird nie mehr geändert.

**Pflichtangaben:** `{title: …}`, `{meta: id …}` (gleich dem Dateinamen), `{meta: language de}`.

**In dieser Bibliothek immer ausfüllen:** `{lyricist: …}`, `{composer: …}`, `{copyright: Public domain}`, `{meta: license public-domain}`, `{meta: source …}` und mindestens ein `{meta: tag …}`.

**Liedtext:** in Blöcken `{start_of_verse}` … `{end_of_verse}`, `{start_of_chorus}` … `{end_of_chorus}` oder `{start_of_bridge}` … `{end_of_bridge}`, ohne eigene Beschriftung (die App erzeugt «Strophe 1», «Refrain» in der Sprache des Benutzers). Ein Refrain wird mit `{chorus}` wiederholt. Akkorde in eckigen Klammern (`[F]`) sind erlaubt.

**Notizen:** Zeilen mit `#` am Anfang sind Notizen für den Maintainer und werden nie angezeigt. Dort steht, welche Strophen übernommen wurden und woher der Text stammt.

**Dateien:** UTF-8 ohne BOM, Zeilenende LF, keine Leerzeichen am Zeilenende, genau ein Zeilenumbruch am Dateiende.

Beispiel (gekürzt):

```
# Lied - Herkunft
# Text: …, Melodie: …; Strophen 1 und 2 von 4.
{title: Beispiel-Lied}
{meta: id beispiel-lied}
{meta: language de}
{lyricist: traditionell}
{composer: traditionell}
{copyright: Public domain}
{meta: license public-domain}
{meta: source Traditionelles Volkslied, allgemein gesungene Fassung}
{meta: tag volkslied}

{start_of_verse}
Erste Zeile der Strophe,
zweite Zeile der Strophe.
{end_of_verse}
```

## 3. Tags

Tags ordnen die Lieder in der App. Jeder Tag, der in einem Lied vorkommt, braucht in `zangbundel.json` unter `tags` eine Bezeichnung auf Deutsch, Niederländisch und Englisch. Ohne Eintrag zeigt die App den Tag unverändert an.

| Tag | Deutsch | Niederländisch | Englisch |
|---|---|---|---|
| `kinderlied` | Kinderlied | Kinderlied | Children's song |
| `volkslied` | Volkslied | Volkslied | Folk song |
| `laterne` | Laternenlied | Sint-Maarten | Lantern song |
| `weihnachten` | Weihnachten | Kerst | Christmas |
| `kirchenlied` | Kirchenlied | Kerklied | Hymn |

## 4. Urheberrecht

In diese Bibliothek kommen nur **gemeinfreie** Lieder:

- traditionelle Lieder (Volkslieder) oder
- Lieder, deren Text- und Melodieautoren alle vor mehr als 70 Jahren gestorben sind (Stand 2026: vor 1956).

Zu beachten:

- **Originalwortlaut verwenden.** Neuere Bearbeitungen alter Lieder können geschützt sein, z. B. die überarbeiteten Texte im Reformierten Gesangbuch 1998 oder modernisierte Fassungen von Kinderliedern. Den Text aus alten Gesangbüchern oder gemeinfreien Quellen nehmen.
- **Neue Melodien zu alten Texten** können geschützt sein, auch wenn der Text frei ist.
- **Notensätze und Aufnahmen** sind eigene Werke und nicht Teil dieser Bibliothek.
- **Herkunft angeben:** `{meta: source …}` nennt die Quelle, damit sie später geprüft werden kann.
- **Keine Inhalte aus pe1mew/Zangbundel-bibliotheek übernehmen:** Lieder, Metadaten und Dokumentation stehen dort unter CC BY-NC 4.0 und passen nicht zur CC0-Lizenz dieser Sammlung.

Diese Hinweise sind keine Rechtsberatung.

## 5. Prüfen

`scripts/validate.py` prüft die ganze Bibliothek: `zangbundel.json`, jede Lieddatei und die Zeilenenden. Es braucht Python 3.8 oder neuer und keine weiteren Pakete.

```
python scripts/validate.py --strict --info .
```

Jeder Befund erscheint als `Pfad:Zeile STUFE CODE Meldung`, danach pro Lied die Prüfsumme und eine Zusammenfassung. `--strict` lässt auch Warnungen scheitern, `--info` zeigt zusätzliche Hinweise. Vor jedem Commit muss die Prüfung ohne Fehler und ohne Warnungen durchlaufen. Auf GitHub läuft dieselbe Prüfung automatisch bei jedem Push.

### Menü in Python

`menu-with-tutorial-for-release-process.py` führt durch den ganzen Ablauf bis zum Release. Start im Ordner der Bibliothek oder von überall:

```
python menu-with-tutorial-for-release-process.py
```

Voraussetzungen: Python 3.8 oder neuer und Git im PATH.

Beim Start fragt das Menü nach der Sprache: `de` (Deutsch, Standard mit Enter) oder `en` (Englisch). Alle Dialoge erscheinen dann in dieser Sprache.

| Punkt | Zweck | Git-Befehl |
|---|---|---|
| 1 | Erläuterungstexte (Tutorial) ein- bzw. ausblenden | – |
| 2 | Bibliothek prüfen (`validate.py --strict --info`) | – |
| 3 | Status: geänderte Dateien, Tags, Vergleich mit GitHub | nur Abfragen |
| 4 | Änderungen vormerken | `git add -A` |
| 5 | Commit erstellen (fragt nach der Nachricht) | `git commit -m "…"` |
| 6 | Tag setzen (schlägt den nächsten freien Tag vor) | `git tag -a <Tag>` |
| 7 | Test-Archiv aus dem letzten Commit bauen | – |
| 8 | Release-Archiv aus einem Tag bauen | – |
| 9 | Neuestes Archiv in `dist/` prüfen wie die App | – |
| 10 | Commits zu GitHub pushen | `git push origin main` |
| 11 | Tag zu GitHub pushen – startet das Release | `git push origin <Tag>` |
| 12 | Nach dem grünen Haken unter «Actions»: Änderungen holen | `git pull origin main` |

Ablauf für ein Release: 2 → 4 → 5 → 6 (→ 8 → 9) → 10 → 11 → grüner Haken auf GitHub → 12. Die Punkte 8 und 9 sind ein freiwilliger lokaler Test; das Release selbst baut GitHub.

**Erläuterungstexte (Tutorial):** Beim Start sind sie ausgeblendet; Punkt 1 blendet sie für die laufende Sitzung ein oder wieder aus. Ohne Erläuterungen bleibt alles sichtbar, was für sicheres Arbeiten nötig ist: der Titel des Schritts, jeder ändernde Git-Befehl mit Bestätigung, Eingaben, Ergebnisse, Warnungen, Abbrüche, die Ausgaben der Werkzeuge und nach dem Tag-Push eine Kurzzeile mit dem Link zu «Actions». Ausgeblendet werden nur die Erklärtexte, die «Danach …»-Sätze, die Zeilen «Abfrage: …» und «Aufruf: …», Fortschrittsmeldungen und Hinweise auf den nächsten Schritt.

**Regeln des Menüs:**

- Jeder Menüpunkt führt höchstens einen Git-Befehl aus, der etwas verändert. Der Befehl wird vorher angezeigt und läuft erst nach Bestätigung mit `j`.
- Reine Abfragen (`git status`, `git fetch`, `git rev-list`, `git ls-remote` …) laufen ohne Rückfrage, werden aber bei eingeblendeten Erläuterungen als «Abfrage» angezeigt.
- Vor Punkt 5, 10 und 11 holt das Menü mit `git fetch` den Stand von GitHub und zählt mit `git rev-list --count HEAD..origin/main`, ob dort Commits liegen, die lokal fehlen. Ist das so, beendet es sich mit der Aufforderung, zuerst Punkt 12 (`git pull`) auszuführen.
- Vor Commit und Tag wird die Bibliothek geprüft; bei Fehlern oder Warnungen geht es nicht weiter.
- Punkt 11 pusht nur, wenn der Commit des Tags schon auf GitHub ist (sonst zuerst Punkt 10) und der Tag noch nicht dort liegt. Danach zeigt das Menü den Link zu «Actions» und den Hinweis auf den grünen Haken und Punkt 12.

### Menü unter Windows

`menu-for-release-process.bat` ruft die Werkzeuge mit den passenden Parametern auf. Doppelklick genügt; das Menü arbeitet immer im Ordner der Bibliothek.

| Punkt | Aufruf | Zweck |
|---|---|---|
| 1 | `validate.py --strict --info .` | vollständige Prüfung mit Hinweisen |
| 2 | `validate.py --strict .` | nur Fehler und Warnungen |
| 3 | `release.py build --tag <Tag> --out dist` | Archiv aus einem vorhandenen Git-Tag bauen |
| 4 | `release.py build --tag v0.0.0-test --allow-untagged --out dist` | Test-Archiv aus dem letzten Commit, ohne Tag |
| 5 | `release.py verify --strict <neuestes Archiv in dist>` | Archiv prüfen wie die App |
| 6 | `--help` beider Werkzeuge | alle Optionen anzeigen |

Das Menü verwendet den Python-Launcher `py`, sonst `python` aus dem PATH. Nach jedem Punkt zeigt es «Result: OK» oder «Result: FAILED».

**Git wird gebraucht:** Punkt 3 und 4 rufen `git` auf. Das Menü nimmt Git aus dem PATH, sonst sucht es Git for Windows und das in GitHub Desktop enthaltene Git. Findet es keines, meldet es das. Bei Punkt 3 prüft das Menü vorher, ob der Tag existiert; Tags unterscheiden Gross- und Kleinschreibung (`v2026.11.0` ist nicht `V2026.11.0`).

**Tag anlegen über das Menü:** Fehlt der Tag bei Punkt 3, fragt das Menü, ob es ihn anlegen soll. Bei «J» läuft es so ab:

1. Prüft das Tag-Format `v<Jahr>.<Monat>.<Nummer>` mit kleinem `v`.
2. Prüft, ob Git Name und Mailadresse kennt (`git config --global user.name` bzw. `user.email`).
3. Prüft die Bibliothek mit `validate.py --strict`; bei Fehlern oder Warnungen bricht es ab.
4. Zeigt offene Änderungen, fragt, ob sie committet werden sollen, und fragt nach der Commit-Nachricht (Enter = «Release <Tag>»). Committet wird, was die Allow-List in `.gitignore` zulässt.
5. Setzt den Tag auf den letzten Commit und baut das Archiv.

**Zu GitHub pushen:** Nach jedem erfolgreichen Build bei Punkt 3 – mit neuem oder vorhandenem Tag – fragt das Menü, ob es pushen soll. Bei «J» führt es `git push origin main` und danach `git push origin <Tag>` aus; der Push des Tags startet das Release auf GitHub. Ist der Tag schon auf GitHub, meldet das Menü das und pusht nicht. Bei «N» zeigt es die beiden Befehle für später.

Nach dem Push zeigt das Menü einen Hinweis: unter «Actions» auf GitHub prüfen, ob die Release-Erstellung einen grünen Haken hat (ein Kreis bedeutet, dass sie noch läuft). Sobald der Haken da ist, `git pull` ausführen: der Workflow trägt das Archiv in `releases.json` ein. Für den Push muss Git bei GitHub angemeldet sein; Git for Windows fragt beim ersten Mal danach.

**Wichtig:** Punkt 3 und 4 bauen aus dem letzten Commit. Nicht committete Änderungen sind nicht im Archiv. Werden Optionen der Werkzeuge geändert, muss das Menü angepasst werden.

## 6. Veröffentlichung auf GitHub

1. Auf GitHub ein **öffentliches** Repository anlegen, z. B. `https://github.com/example-alpha/example-bravo`, ohne README, Lizenz oder `.gitignore`.
2. Den Inhalt dieses Ordners hineinpushen.
3. In `zangbundel.json` die beiden Felder ergänzen, die auf das Repository zeigen:
   ```json
   "homepage": "https://github.com/example-alpha/example-bravo",
   "release_index": "https://raw.githubusercontent.com/example-alpha/example-bravo/main/releases.json",
   ```
4. Unter *Settings → Actions → General* prüfen, dass Workflows laufen dürfen. Der Release-Workflow braucht Schreibrechte; er fordert sie selbst über `permissions: contents: write` an.

## 7. Releases

Ein Release ist ein Git-Tag `v<Version>` im Kalenderformat `Jahr.Monat.Nummer`, z. B. `v2026.11.0`.

```
git tag v2026.11.0
git push origin v2026.11.0
```

Der Workflow `.github/workflows/release.yml` baut daraus das Archiv, prüft es, veröffentlicht es als GitHub-Release unter `pepe-deutsche-lieder-<Version>.zbl` und `pepe-deutsche-lieder-latest.zbl` und trägt es in `releases.json` auf `main` ein. Danach `main` holen, damit die lokale `releases.json` aktuell ist.

Lokal bauen und prüfen (ohne GitHub):

```
python scripts/release.py build --tag v2026.11.0
python scripts/release.py verify dist/pepe-deutsche-lieder-2026.11.0.zbl
```

Gleiche Tags ergeben immer byteidentische Archive. Der Ordner `dist/` kommt nicht ins Repository.

## 8. Bibliothek in der App verwenden

- **Über den Release-Index:** in der App die URL von `releases.json` angeben, z. B. `https://raw.githubusercontent.com/example-alpha/example-bravo/main/releases.json`. Die App prüft damit auch auf Updates.
- **Über eine Datei:** die `.zbl`-Datei auf das Leiter-Handy kopieren und mit «Aus Datei importieren» öffnen.

Die Sängerinnen und Sänger brauchen die Bibliothek nicht; das Leiter-Handy schickt die Lieder während des Singens per Bluetooth.

Die Bibliotheks-ID `pepe-deutsche-lieder` darf nicht geändert werden, sonst sieht die App eine neue Bibliothek.

## 9. Vibe-Coding-Deklaration

Diese Software wurde mittels **Vibe Coding** erstellt: Als Autor habe ich die Anforderungen und die beabsichtigte Funktionalität spezifiziert und in mehreren Etappen ergänzt; die KI hat den Code jeweils entsprechend geschrieben und angepasst. Auch die Projektdokumentation (README usw.) wurde KI-unterstützt verfasst.

Das Ergebnis habe ich bezüglich Funktionalität eingehend geprüft. Die Tests beschränkten sich auf das von aussen beobachtbare Verhalten (**Black-Box-Tests**).

Den Python-Code selbst habe ich weder gelesen noch bezüglich Qualität oder Sicherheit geprüft. Geprüft wurde lediglich, ob der Code gut und in englischer Sprache kommentiert ist, da dies eine der Vorgaben war.

Die Nutzung erfolgt auf eigenes Risiko (siehe auch die [Lizenz](LICENSE)). Wer den Code prüft und dabei Fehler oder Schwachstellen findet, ist herzlich eingeladen, ein [Issue auf GitHub](https://github.com/pepe-hb9evt/Zangbundel-bibliotheek-van-Pepe/issues) zu eröffnen.

## 10. Lizenzen

| Teil | Lizenz |
|---|---|
| Lieder | Public Domain; im Lied mit `{meta: license public-domain}` gekennzeichnet |
| Sammlung (Auswahl, Abschriften, Metadaten, Dokumentation) | CC0 1.0, siehe [LICENSE](LICENSE) |
| Menüs im Hauptordner (`menu-with-tutorial-for-release-process.py`, `menu-for-release-process.bat`) | CC0 1.0, siehe [LICENSE](LICENSE) |
| Werkzeuge unter `scripts/` | Apache 2.0 mit Commons Clause, © Remko Welling, PE1MEW, siehe [scripts/LICENSE](scripts/LICENSE) |

Die Werkzeuge dürfen genutzt, geändert und weitergegeben, aber nicht verkauft werden. `scripts/LICENSE` muss unverändert bleiben.

## 11. Autor

Pepe HB9EVT, https://github.com/pepe-hb9evt
mit Unterstützung durch die KI Claude von Anthropic (vgl. Kapitel [Vibe-Coding-Deklaration](#9-vibe-coding-deklaration))
