# German Songs – Documentation

German original: [DOCUMENTATION_deutsch_german.md](DOCUMENTATION_deutsch_german.md)

## 1. Repository layout

```
zangbundel.json            library metadata: id, name, licence, maintainer, tag labels
LICENSE                    licence text of the collection (CC0 1.0); the app shows it on first import
songs/                     one ChordPro file (.cho) per song
releases.json              release index; created automatically by the first release
scripts/validate.py        checks the library against the rules of the format
scripts/release.py         builds, verifies and indexes the release archives (.zbl)
scripts/menu.py            menu for checking, git steps and release (Python)
scripts/LICENSE            licence of the tools (Apache 2.0 with the Commons Clause)
Menu for zangbundel-tools.bat  menu for the tools on Windows
.github/workflows/         check on every push; release on every tag
.gitignore                 allow-list: only explicitly listed files go into the repository
.gitattributes             pins the line endings (LF) so hashes are identical everywhere
.editorconfig              editor settings matching the format (UTF-8, LF)
CLAUDE.md                  working rules for Claude (local only, not in the repository)
```

The app reads only `zangbundel.json`, every `.cho` file under `songs/` and the licence file. The subfolders under `songs/` carry no meaning for the app; they only keep things organised.

## 2. Song format

A song is one `.cho` file in ChordPro format according to the [Zangbundel format specification 1.1](https://github.com/pe1mew/Zangbundel/blob/main/design/song-format.md).

**File name = song id:** lower-case letters, digits and single hyphens, derived from the title. Umlauts are transliterated: `ä` → `ae`, `ö` → `oe`, `ü` → `ue`, `ß` → `ss`. Example: "Gott ist gegenwärtig" → `gott-ist-gegenwaertig.cho`. A published id never changes.

**Required:** `{title: …}`, `{meta: id …}` (equal to the file name), `{meta: language de}`.

**Always filled in this library:** `{lyricist: …}`, `{composer: …}`, `{copyright: Public domain}`, `{meta: license public-domain}`, `{meta: source …}` and at least one `{meta: tag …}`.

**Lyrics:** in `{start_of_verse}` … `{end_of_verse}`, `{start_of_chorus}` … `{end_of_chorus}` or `{start_of_bridge}` … `{end_of_bridge}` blocks, without labels of their own (the app generates "Verse 1", "Chorus" in the user's language). A chorus is repeated with `{chorus}`. Chords in square brackets (`[F]`) are allowed.

**Notes:** lines starting with `#` are maintainer notes and are never shown. They say which stanzas were included and where the text comes from.

**Files:** UTF-8 without BOM, LF line endings, no trailing spaces, exactly one final newline.

Example (shortened):

```
# Song - origin
# Words: …, melody: …; stanzas 1 and 2 of 4.
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

Tags group the songs in the app. Every tag used in a song needs a label in German, Dutch and English under `tags` in `zangbundel.json`. Without an entry the app shows the tag as is.

| Tag | German | Dutch | English |
|---|---|---|---|
| `kinderlied` | Kinderlied | Kinderlied | Children's song |
| `volkslied` | Volkslied | Volkslied | Folk song |
| `laterne` | Laternenlied | Sint-Maarten | Lantern song |
| `weihnachten` | Weihnachten | Kerst | Christmas |
| `kirchenlied` | Kirchenlied | Kerklied | Hymn |

## 4. Copyright

Only **public-domain** songs go into this library:

- traditional songs (folk songs), or
- songs whose lyricists and composers all died more than 70 years ago (as of 2026: before 1956).

Note:

- **Use the original wording.** Newer revisions of old songs can be protected, e.g. the revised texts in the Reformiertes Gesangbuch 1998 or modernised versions of children's songs. Take the text from old hymn books or public-domain sources.
- **New melodies to old texts** can be protected even when the text is free.
- **Sheet music settings and recordings** are works of their own and not part of this library.
- **State the origin:** `{meta: source …}` names the source so it can be checked later.
- **Do not take content from pe1mew/Zangbundel-bibliotheek:** songs, metadata and documentation there are licensed CC BY-NC 4.0 and do not fit the CC0 licence of this collection.

These notes are not legal advice.

## 5. Validating

`scripts/validate.py` checks the whole library: `zangbundel.json`, every song file and the line endings. It needs Python 3.8 or newer and no other packages.

```
python scripts/validate.py --strict --info .
```

Every finding appears as `path:line LEVEL CODE message`, followed by the hash of each song and a summary. `--strict` also fails on warnings, `--info` shows additional notes. Before every commit the check must pass without errors and without warnings. On GitHub the same check runs automatically on every push.

### Menu in Python

`scripts/menu.py` leads through the whole process up to the release. Start it in the library folder or from anywhere:

```
python scripts/menu.py
```

Requirements: Python 3.8 or newer and git on the PATH.

At start the menu asks for the language: `de` (German, the default with Enter) or `en` (English). All dialogs then appear in that language.

| Item | Purpose | Git command |
|---|---|---|
| 1 | Validate the library (`validate.py --strict --info`) | – |
| 2 | Status: changed files, tags, comparison with GitHub | queries only |
| 3 | Stage changes | `git add -A` |
| 4 | Create a commit (asks for the message) | `git commit -m "…"` |
| 5 | Set a tag (suggests the next free tag) | `git tag -a <tag>` |
| 6 | Build a test archive from the last commit | – |
| 7 | Build the release archive from a tag | – |
| 8 | Verify the newest archive in `dist/` as the app does | – |
| 9 | Push commits to GitHub | `git push origin main` |
| 10 | Push the tag to GitHub – starts the release | `git push origin <tag>` |
| 11 | After the green tick under "Actions": fetch the changes | `git pull origin main` |

Release sequence: 1 → 3 → 4 → 5 (→ 7 → 8) → 9 → 10 → green tick on GitHub → 11. Items 7 and 8 are an optional local test; GitHub builds the release itself.

**Rules of the menu:**

- Each menu item runs at most one git command that changes something. The command is shown and explained first and runs only after confirming with `j`.
- Read-only queries (`git status`, `git fetch`, `git rev-list`, `git ls-remote` …) run without a question but are shown as "Abfrage" (query).
- Before items 4, 9 and 10 the menu fetches the state of GitHub with `git fetch` and counts with `git rev-list --count HEAD..origin/main` whether there are commits that are missing locally. If so, it ends and asks to run item 11 (`git pull`) first.
- Before commit and tag the library is validated; with errors or warnings it does not continue.
- Item 10 pushes only when the tagged commit is already on GitHub (otherwise item 9 first) and the tag is not there yet. Afterwards the menu shows the link to "Actions" and the note about the green tick and item 11.

### Menu on Windows

`Menu for zangbundel-tools.bat` calls the tools with the right parameters. A double click is enough; the menu always works in the library folder.

| Item | Call | Purpose |
|---|---|---|
| 1 | `validate.py --strict --info .` | full check with notes |
| 2 | `validate.py --strict .` | errors and warnings only |
| 3 | `release.py build --tag <tag> --out dist` | build the archive from an existing git tag |
| 4 | `release.py build --tag v0.0.0-test --allow-untagged --out dist` | test archive from the last commit, without a tag |
| 5 | `release.py verify --strict <newest archive in dist>` | check the archive as the app does |
| 6 | `--help` of both tools | show all options |

The menu uses the Python launcher `py`, otherwise `python` from the PATH. After every item it shows "Result: OK" or "Result: FAILED".

**Git is needed:** items 3 and 4 call `git`. The menu takes git from the PATH, otherwise it looks for Git for Windows and the git bundled with GitHub Desktop. If it finds none, it says so. For item 3 the menu first checks that the tag exists; tags are case-sensitive (`v2026.11.0` is not `V2026.11.0`).

**Creating a tag through the menu:** if the tag is missing for item 3, the menu asks whether to create it. With "J" it proceeds as follows:

1. Checks the tag format `v<year>.<month>.<sequence>` with a lower-case `v`.
2. Checks that git knows your name and e-mail address (`git config --global user.name` and `user.email`).
3. Validates the library with `validate.py --strict`; it stops on errors or warnings.
4. Shows open changes, asks whether to commit them and asks for the commit message (Enter = "Release <tag>"). What is committed is decided by the allow-list in `.gitignore`.
5. Sets the tag on the last commit and builds the archive.

**Pushing to GitHub:** after every successful build in item 3 – with a new or an existing tag – the menu asks whether to push. With "J" it runs `git push origin main` and then `git push origin <tag>`; pushing the tag starts the release on GitHub. If the tag is already on GitHub, the menu says so and does not push. With "N" it shows both commands for later.

After the push the menu shows a note: check under "Actions" on GitHub whether the release run has a green tick (a circle means it is still running). As soon as the tick is there, run `git pull`: the workflow adds the archive to `releases.json`. Pushing needs git to be signed in to GitHub; Git for Windows asks for it the first time.

**Important:** items 3 and 4 build from the last commit. Uncommitted changes are not in the archive. When options of the tools change, the menu must be updated.

## 6. Publishing on GitHub

1. Create a **public** repository on GitHub, e.g. `https://github.com/example-alpha/example-bravo`, without README, licence or `.gitignore`.
2. Push the contents of this folder into it.
3. Add the two fields pointing at the repository to `zangbundel.json`:
   ```json
   "homepage": "https://github.com/example-alpha/example-bravo",
   "release_index": "https://raw.githubusercontent.com/example-alpha/example-bravo/main/releases.json",
   ```
4. Under *Settings → Actions → General*, check that workflows are allowed to run. The release workflow needs write access; it requests it itself through `permissions: contents: write`.

## 7. Releases

A release is a git tag `v<version>` in calendar format `year.month.sequence`, e.g. `v2026.11.0`.

```
git tag v2026.11.0
git push origin v2026.11.0
```

The workflow `.github/workflows/release.yml` builds the archive from it, verifies it, publishes it as a GitHub release under `pepe-deutsche-lieder-<version>.zbl` and `pepe-deutsche-lieder-latest.zbl`, and adds it to `releases.json` on `main`. Afterwards pull `main` so the local `releases.json` is up to date.

Build and verify locally (without GitHub):

```
python scripts/release.py build --tag v2026.11.0
python scripts/release.py verify dist/pepe-deutsche-lieder-2026.11.0.zbl
```

The same tag always gives a byte-identical archive. The `dist/` folder does not go into the repository.

## 8. Using the library in the app

- **Through the release index:** enter the URL of `releases.json` in the app, e.g. `https://raw.githubusercontent.com/example-alpha/example-bravo/main/releases.json`. The app also uses it to check for updates.
- **Through a file:** copy the `.zbl` file to the leader's phone and open it with "import from file".

Singers do not need the library; the leader's phone pushes the songs over Bluetooth while singing.

The library id `pepe-deutsche-lieder` must not change, otherwise the app sees a new library.

## 9. Licences

| Part | Licence |
|---|---|
| Songs | Public domain; marked in the song with `{meta: license public-domain}` |
| Collection (selection, transcriptions, metadata, documentation) | CC0 1.0, see [LICENSE](LICENSE) |
| Tools under `scripts/` | Apache 2.0 with the Commons Clause, © Remko Welling, PE1MEW, see [scripts/LICENSE](scripts/LICENSE) |

The tools may be used, modified and shared, but not sold. `scripts/LICENSE` must stay unchanged.
