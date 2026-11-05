# Zangbundel bibliotheek van Pepe

( **Deutsche Version** dieses Dokuments verfügbar: [README_deutsch_german.md](README_deutsch_german.md) )

<br>

A song library for the [Zangbundel](https://github.com/pe1mew/Zangbundel) app. The app shows the lyrics on the phones of all singers at the same time; a leader phone pushes the songs over Bluetooth. The songs themselves come from libraries like this one.

This library holds **public-domain German-language songs**. It follows the Zangbundel library format 1.1 - see https://github.com/pe1mew/Zangbundel/blob/main/design/song-format.md

<br>

## Quick start

**Add the library to the app:** enter the URL of the release index in the app:

```
https://raw.githubusercontent.com/<account>/<repository>/main/releases.json
```

Or download the `.zbl` file from the release webpage and open it in the app with "import from file".

**Add, check and publish songs:**

```cmd
python menu-with-tutorial-for-release-process.py
```

This menu leads step by step to the release (on Windows there is also `menu-for-release-process.bat`). To check only, run directly:

```
python scripts/validate.py --strict --info .
```

<br>

## Full documentation

All details – layout, song format, copyright, releases and publishing – are in [DOCUMENTATION.md](DOCUMENTATION.md).

<br>

## Vibe coding declaration

This software was created by **vibe coding**: the two menus (`menu-with-tutorial-for-release-process.py`, `menu-for-release-process.bat`) were written by the AI Claude (Anthropic). The tools under `scripts/` come from Remko Welling, PE1MEW. As the author, I specified the requirements and the intended functionality and extended them in several stages; the AI wrote and adapted the code accordingly each time. The project documentation (README etc.) was also written with AI support. The lyrics were transcribed with AI support and must be checked against a public-domain source.

I tested the result thoroughly for its functionality. The tests were limited to the externally observable behaviour (**black-box tests**).

I have neither read the Python code itself nor checked it for quality or security. The only check was whether the code is well commented in English, as this was one of the requirements.

Use at your own risk (see also the [licence](LICENSE)). Anyone who reviews the code and finds bugs or vulnerabilities is warmly invited to open an [issue on GitHub](https://github.com/pepe-hb9evt/Zangbundel-bibliotheek-van-Pepe/issues).

<br>

## License

The songs are in the public domain. The collection (selection, transcriptions, metadata, documentation) and the two menus in the root folder are licensed under [CC0 1.0](LICENSE). The tools under `scripts/` come from [pe1mew/Zangbundel-bibliotheek](https://github.com/pe1mew/Zangbundel-bibliotheek) by Remko Welling, PE1MEW, and are licensed under Apache 2.0 with the Commons Clause (see [scripts/LICENSE](scripts/LICENSE)).

<br>

## Author

Pepe HB9EVT, https://github.com/pepe-hb9evt
with support from the AI Claude by Anthropic (see chapter [Vibe coding declaration](#vibe-coding-declaration))
