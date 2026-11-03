# German Songs – Zangbundel library

A song library for the [Zangbundel](https://github.com/pe1mew/Zangbundel) app. The app shows the lyrics on the phones of all singers at the same time; a leader phone pushes the songs over Bluetooth. The songs themselves come from libraries like this one.

This library (`pepe-deutsche-lieder`) holds **public-domain German songs**: children's, lantern, Christmas and church songs. It follows the Zangbundel library format 1.1.

German original: [README_deutsch_german.md](README_deutsch_german.md)

## Quick start

**Add the library to the app:** enter the URL of the release index in the app:

```
https://raw.githubusercontent.com/<account>/<repository>/main/releases.json
```

Or download the `.zbl` file from the release webpage and open it in the app with "import from file".

**Add a song and check it:** on Windows start `Menu for zangbundel-tools.bat` and choose item 1, or directly:

```
python scripts/validate.py --strict --info .
```

All details – layout, song format, copyright, releases and publishing – are in [DOCUMENTATION.md](DOCUMENTATION.md).

## License

The songs are in the public domain. The collection (selection, transcriptions, metadata, documentation) is licensed under [CC0 1.0](LICENSE). The tools under `scripts/` come from [pe1mew/Zangbundel-bibliotheek](https://github.com/pe1mew/Zangbundel-bibliotheek) by Remko Welling, PE1MEW, and are licensed under Apache 2.0 with the Commons Clause (see [scripts/LICENSE](scripts/LICENSE)).
