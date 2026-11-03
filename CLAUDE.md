# Project rules for Claude - Zangbundel-bibliotheek (Deutsche Lieder)

A song library for the Zangbundel app (https://github.com/pe1mew/Zangbundel).
Library id `pepe-deutsche-lieder`, public-domain German songs only.

## Communication and language

- Communicate with the user in German.
- All variable names, function names and code comments (e.g. in `scripts/`) are in English.
- Song files (`.cho`): lyrics, metadata values and maintainer notes (`#` lines) are in the
  language of the song (German for `{meta: language de}`).
- The documentation (`README_deutsch_german.md` or - if it exists - `DOCUMENTATION_deutsch_german.md`)
  is in German. `README.md` or - if it exists - `DOCUMENTATION.md` are translations of the German original.
- Plans and design documents in German.
- "Mache einen Vorschlag" (or similar) -> work out a plan for approval, do not change files.
- "Erstellen", "Ausführen" -> implement the approved plan.

## File handling

- Files are also edited outside of Claude. Before changing a file, ALWAYS read its
  current version from the project folder and base the planned changes on that version.
  Never rebuild a file from an older copy, a previous tool result or memory.
- If a file changed since Claude last read it, keep the user's changes and merge
  Claude's changes into them. Never silently overwrite edits made by the user.
- After creating or changing a file in the project folder, wait one second, read the
  file again and verify that it actually contains the new content. Report any mismatch.
- Do not rename or move the user's folders under `songs/` (their names carry no meaning
  for the app, but they are the user's choice).
- Song files, `zangbundel.json` and Markdown files: UTF-8 without BOM, LF line endings,
  no trailing spaces, exactly one final newline.
- Keep Windows line endings (CRLF) in `.bat` and `.ps1` files.

## Song format

- Follow the Zangbundel library format 1.1:
  https://github.com/pe1mew/Zangbundel/blob/main/design/song-format.md
- One song per `.cho` file under `songs/`. The file name is the song id: lower-case letters,
  digits and single hyphens, derived from the title, umlauts transliterated
  (`ä` -> `ae`, `ö` -> `oe`, `ü` -> `ue`, `ß` -> `ss`). An id never changes once published.
- Required: `{title: …}`, `{meta: id …}` equal to the file name, `{meta: language de}`.
- Always fill: `{lyricist}`, `{composer}`, `{copyright}`, `{meta: license}`, `{meta: source}`
  and at least one `{meta: tag …}`.
- Lyrics in `{start_of_verse}` / `{start_of_chorus}` / `{start_of_bridge}` blocks without labels;
  repeat a chorus with `{chorus}` so the text is complete and in sung order.
- Every tag used in a song needs an entry in `tags` of `zangbundel.json` with labels in
  `de`, `nl` and `en`.
- Do not change the library `id` in `zangbundel.json`.

## Copyright and licensing

- Only public-domain songs: traditional, or every lyricist and composer died more than
  70 years ago. Check the dates; when in doubt, ask the user instead of adding the song.
- Use the original wording of the authors, not modern revisions (e.g. the texts of the
  Reformiertes Gesangbuch 1998 or modernised children's song versions), which may still be protected.
- Mark public-domain songs with `{copyright: Public domain}` and `{meta: license public-domain}`.
- State in a `#` note when stanzas were left out, which ones are included, and any
  uncertainty about the text, so the user can check it against a source.
- Do not copy songs, metadata or documentation from pe1mew/Zangbundel-bibliotheek into this
  library (CC BY-NC 4.0). The validator scripts (Apache 2.0 + Commons Clause) may be used;
  keep `scripts/LICENSE` unchanged.

## Security and privacy

- The maintainer entry in `zangbundel.json` is the only place for the user's real name
  and e-mail address. Do not repeat them elsewhere without the user's approval.
- Never use real URLs, names or e-mail addresses in README, documentation or example files.
  Use fictitious ones based on the NATO alphabet (`example-alpha`, `example-bravo`,
  `example-charlie` ...), no Greek letters.
- If a `.gitignore` is introduced, it is an allow-list: every new file that belongs in the
  repository must be added explicitly. Files with personal data or secrets must never be added.

## Code

- Python 3.8+, standard library only - no extra packages without the user's approval.

## Testing

- Before reporting a change as done, run the validator on the whole library:
  `python scripts/validate.py --strict --info .` - it must report no errors and no warnings.
- Never tag, build or publish a release without asking the user.

## Git

- Claude does not access Git: no `git` commands (no init, add, commit, push, pull, tag, ...),
  no changes inside the `.git` folder. The user handles Git himself.

## Documentation

- `README_deutsch_german.md` / `README.md` give a short overview and quick start only;
  all details belong in `DOCUMENTATION_deutsch_german.md` / `DOCUMENTATION.md`.
- When files, songs or behaviour change, update the German files (`README_deutsch_german.md`,
  `DOCUMENTATION_deutsch_german.md`) and their English translations (`README.md`, `DOCUMENTATION.md`)
  in the same step and keep the versions equivalent in content. But do not remove the German
  translation of the title in `README_deutsch_german.md`.
- In documentation and communication use "webpage" instead of "website" or "site".
- Don't remove the `<br>` set by the user in the Markdown files.
- No changelog file.
