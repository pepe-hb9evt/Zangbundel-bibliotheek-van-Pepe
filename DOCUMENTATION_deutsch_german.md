# Deutsche Lieder – Dokumentation

English version: [DOCUMENTATION.md](DOCUMENTATION.md)

## 1. Aufbau des Repositorys

```
zangbundel.json            Metadaten der Bibliothek: id, Name, Lizenz, Maintainer, Tag-Bezeichnungen
LICENSE                    Lizenztext der Sammlung (CC0 1.0); die App zeigt ihn beim ersten Import
songs/                     eine ChordPro-Datei (.cho) pro Lied
releases.json              Release-Index; wird beim ersten Release automatisch erzeugt
scripts/validate.py        prüft die Bibliothek nach den Regeln des Formats
scripts/release.py         baut, prüft und indexiert die Release-Archive (.zbl)
scripts/LICENSE            Lizenz der Werkzeuge (Apache 2.0 mit Commons Clause)
Menu for zangbundel-tools.bat  Menü für die Werkzeuge unter Windows
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

### Menü unter Windows

`Menu for zangbundel-tools.bat` ruft die Werkzeuge mit den passenden Parametern auf. Doppelklick genügt; das Menü arbeitet immer im Ordner der Bibliothek.

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

## 9. Lizenzen

| Teil | Lizenz |
|---|---|
| Lieder | Public Domain; im Lied mit `{meta: license public-domain}` gekennzeichnet |
| Sammlung (Auswahl, Abschriften, Metadaten, Dokumentation) | CC0 1.0, siehe [LICENSE](LICENSE) |
| Werkzeuge unter `scripts/` | Apache 2.0 mit Commons Clause, © Remko Welling, PE1MEW, siehe [scripts/LICENSE](scripts/LICENSE) |

Die Werkzeuge dürfen genutzt, geändert und weitergegeben, aber nicht verkauft werden. `scripts/LICENSE` muss unverändert bleiben.
