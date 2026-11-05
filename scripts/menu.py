#!/usr/bin/env python3
"""Interactive console menu for maintaining this Zangbundel library.

Every step of the release process is a menu item of its own. Each item runs at
most one git command that changes something (add, commit, tag, push, pull);
that command is shown first and runs only after the user confirms it.
Read-only git queries (status, fetch, rev-list, ls-remote, ...) run without a
question, but are printed as well.

Before steps that would conflict with newer commits on GitHub, the menu fetches
from GitHub and stops if there is something to pull.

All dialogs are available in German and English; the language is chosen at start.

Run from anywhere:  python scripts/menu.py
Needs Python 3.8+ (standard library only) and git on the PATH.
"""

import datetime
import os
import re
import subprocess
import sys
import textwrap

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPTS_DIR)
DIST_DIR = 'dist'
MAIN_BRANCH = 'main'
REMOTE = 'origin'
TEST_TAG = 'v0.0.0-test'
TAG_PATTERN = re.compile(r'^v(\d{4})\.(\d{1,2})\.(\d+)$')
LINE = '-' * 66
MAX_WIDTH = 75
# A git command inside a text, e.g. "git push origin main"; it is never split across lines.
GIT_COMMAND = re.compile(r'git(?: [^\s"(),]*[^\s"(),.])+')
NO_BREAK_SPACE = '\x00'
NO_BREAK_HYPHEN = '\x01'
LANGUAGES = ('de', 'en')
DEFAULT_LANGUAGE = 'de'
DUTCH_REPLY = "Oh come on, Remko, your English is good enough. You don\u2019t need a Dutch translation."

# Language of the dialogs ('de' or 'en'), chosen at start.
language = DEFAULT_LANGUAGE

# Tag chosen in this session (set by "create tag", offered as default later).
session_tag = None


class StopMenu(Exception):
    """Raised to end the program after a message the user must act on."""


# ---------------------------------------------------------------------------
# Language, output and input helpers
# ---------------------------------------------------------------------------

def tr(de, en):
    """Return the text in the chosen language."""
    return de if language == 'de' else en


def setup_console():
    """Make sure umlauts are printed correctly, also when output is redirected."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass


def choose_language():
    """Ask for the dialog language until German or English is chosen."""
    global language
    while True:
        answer = input('Sprache / Language / Taal (de/en/nl) (Enter=de): ').strip().lower()
        answer = answer or DEFAULT_LANGUAGE
        if answer in LANGUAGES:
            language = answer
            return
        if answer == 'nl':
            say()
            say(DUTCH_REPLY)
            say()
            continue
        say()
        say("de: Bitte 'de', 'en' oder 'nl' eingeben.")
        say("en: Please enter 'de', 'en' or 'nl'.")
        say("nl: Voer alstublieft 'de', 'en' of 'nl' in.")
        say()


def wrap_text(text):
    """Wrap text at MAX_WIDTH, at the last space or hyphen before the limit.

    Git commands inside the text are kept on one line; if one does not fit, the
    line break is made before it.
    """
    lines = []
    for line in text.split('\n'):
        if len(line) <= MAX_WIDTH:
            lines.append(line)
            continue
        protected = GIT_COMMAND.sub(
            lambda m: m.group(0).replace(' ', NO_BREAK_SPACE).replace('-', NO_BREAK_HYPHEN), line)
        indent = ' ' * (len(line) - len(line.lstrip(' ')))
        wrapped = textwrap.wrap(protected, width=MAX_WIDTH, break_long_words=False,
                                break_on_hyphens=True, subsequent_indent=indent)
        lines.extend(part.replace(NO_BREAK_SPACE, ' ').replace(NO_BREAK_HYPHEN, '-')
                     for part in wrapped)
    return '\n'.join(lines)


def say(text='', wrap=True):
    """Print a message; long texts are wrapped. wrap=False for commands, URLs and git output."""
    print(wrap_text(text) if wrap else text, flush=True)


def explain(title, text):
    """Print a step title and a short explanation of what happens now."""
    say()
    say(LINE)
    say(title)
    say(LINE)
    for paragraph in text.strip().split('\n'):
        say(paragraph.strip())
    say()


def ask(prompt, default=None):
    """Ask for a line of text; Enter returns the default."""
    suffix = ' (Enter = %s)' % default if default else ''
    answer = input('%s%s: ' % (prompt, suffix)).strip()
    return answer or (default or '')


def confirm(prompt):
    """Ask a yes/no question; 'j', 'ja', 'y' or 'yes' counts as yes, anything else as no."""
    answer = input('%s %s: ' % (prompt, tr('[j/N]', '[y/N]'))).strip().lower()
    return answer in ('j', 'ja', 'y', 'yes')


def pause():
    try:
        input(tr('\nWeiter mit Enter ...', '\nPress Enter to continue ...'))
    except EOFError:
        pass


# ---------------------------------------------------------------------------
# git and tool calls
# ---------------------------------------------------------------------------

def show_command(args):
    return subprocess.list2cmdline(args)


def git_query(*args):
    """Run a read-only git command and return (exit code, output). It is shown, not confirmed."""
    cmd = ['git'] + list(args)
    say('  %s: %s' % (tr('Abfrage', 'Query'), show_command(cmd)), wrap=False)
    result = subprocess.run(cmd, cwd=REPO_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True, encoding='utf-8', errors='replace')
    return result.returncode, result.stdout.strip()


def git_change(args, what):
    """Show a git command that changes something, ask, then run it. Returns True on success."""
    cmd = ['git'] + list(args)
    say(tr('Dieser Git-Befehl wird jetzt ausgeführt:', 'This git command will be run now:'))
    say()
    say('    %s' % show_command(cmd), wrap=False)
    say()
    say(what)
    say()
    if not confirm(tr('Befehl ausführen?', 'Run the command?')):
        say(tr('Abgebrochen – es wurde nichts geändert.', 'Cancelled – nothing was changed.'))
        return False
    say()
    result = subprocess.run(cmd, cwd=REPO_DIR)
    say()
    if result.returncode != 0:
        say(tr('FEHLER: Der Git-Befehl ist fehlgeschlagen (Exit-Code %d), siehe Meldungen oben.',
               'ERROR: The git command failed (exit code %d), see the messages above.')
            % result.returncode)
        return False
    say(tr('OK: Befehl erfolgreich ausgeführt.', 'OK: Command completed successfully.'))
    return True


def run_tool(script, *args):
    """Run one of the library tools with the current Python. Returns its exit code."""
    cmd = [sys.executable, os.path.join('scripts', script)] + list(args)
    say('  %s: %s' % (tr('Aufruf', 'Call'), show_command(['python'] + cmd[1:])), wrap=False)
    say()
    result = subprocess.run(cmd, cwd=REPO_DIR)
    say()
    if result.returncode == 0:
        say(tr('Ergebnis: OK', 'Result: OK'))
    else:
        say(tr('Ergebnis: FEHLER (Exit-Code %d), siehe Meldungen oben',
               'Result: ERROR (exit code %d), see the messages above') % result.returncode)
    return result.returncode


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_git_available():
    try:
        subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        raise StopMenu(tr(
            'Git wurde nicht gefunden. Bitte den Ordner von git.exe in den PATH eintragen '
            '(z. B. C:\\Program Files\\Git\\cmd) und das Menü neu starten.',
            'Git was not found. Please add the folder of git.exe to the PATH '
            '(e.g. C:\\Program Files\\Git\\cmd) and restart the menu.'))
    code, _ = git_query('rev-parse', '--is-inside-work-tree')
    if code != 0:
        raise StopMenu(tr('Der Ordner %s ist kein Git-Repository.',
                          'The folder %s is not a git repository.') % REPO_DIR)


def current_branch():
    code, out = git_query('symbolic-ref', '--short', 'HEAD')
    return out if code == 0 else None


def fetch_and_count_incoming():
    """Fetch from GitHub and return the number of commits on GitHub missing locally, or None."""
    code, _ = git_query('fetch', '--quiet', REMOTE)
    if code != 0:
        say(tr('WARNUNG: GitHub ist nicht erreichbar (git fetch fehlgeschlagen).',
               'WARNING: GitHub cannot be reached (git fetch failed).'))
        return None
    code, out = git_query('rev-list', '--count', 'HEAD..%s/%s' % (REMOTE, MAIN_BRANCH))
    if code != 0:
        say(tr('WARNUNG: Der Stand von %s/%s konnte nicht verglichen werden.',
               'WARNING: The state of %s/%s could not be compared.') % (REMOTE, MAIN_BRANCH))
        return None
    return int(out or 0)


def require_nothing_to_pull():
    """Stop the program when GitHub has commits that are not here yet. False: cannot check."""
    say(tr('Prüfe, ob es auf GitHub Neues gibt, das zuerst geholt werden muss ...',
           'Checking whether GitHub has new commits that must be pulled first ...'))
    incoming = fetch_and_count_incoming()
    if incoming is None:
        say(tr('Dieser Schritt wird abgebrochen, weil nicht geprüft werden konnte, ob etwas zu '
               'holen ist.',
               'This step is cancelled because it could not be checked whether there is something '
               'to pull.'))
        return False
    if incoming:
        code, out = git_query('log', '--oneline', 'HEAD..%s/%s' % (REMOTE, MAIN_BRANCH))
        say(out, wrap=False)
        raise StopMenu(tr(
            'Auf GitHub gibt es %d Commit(s), die hier noch fehlen (z. B. die neue releases.json '
            'nach einem Release).\n'
            'Bitte zuerst bereinigen: Menü neu starten und den letzten Menüpunkt "git pull" '
            'ausführen, oder im Terminal "git pull" eingeben.\n'
            'Das Menü wird jetzt beendet.',
            'GitHub has %d commit(s) that are missing here (e.g. the new releases.json after a '
            'release).\n'
            'Please clean this up first: restart the menu and run the last menu item "git pull", '
            'or enter "git pull" in a terminal.\n'
            'The menu ends now.') % incoming)
    say(tr('OK: Auf GitHub gibt es nichts Neues.', 'OK: There is nothing new on GitHub.'))
    return True


def library_is_valid():
    say(tr('Prüfe die Bibliothek (validate.py --strict) ...',
           'Validating the library (validate.py --strict) ...'))
    return run_tool('validate.py', '--strict', '.') == 0


def local_tags():
    code, out = git_query('tag', '--list')
    return out.splitlines() if code == 0 and out else []


def tag_exists_locally(tag):
    code, _ = git_query('rev-parse', '-q', '--verify', 'refs/tags/%s' % tag)
    return code == 0


def tag_on_github(tag):
    """True / False, or None when GitHub cannot be reached."""
    code, _ = git_query('ls-remote', '--exit-code', '--tags', REMOTE, 'refs/tags/%s' % tag)
    if code == 0:
        return True
    if code == 2:
        return False
    say(tr('WARNUNG: GitHub ist nicht erreichbar (git ls-remote fehlgeschlagen).',
           'WARNING: GitHub cannot be reached (git ls-remote failed).'))
    return None


def release_tags(tags):
    """Release tags sorted by version, newest last."""
    found = []
    for tag in tags:
        match = TAG_PATTERN.match(tag)
        if match:
            found.append((tuple(int(x) for x in match.groups()), tag))
    return [tag for _, tag in sorted(found)]


def suggest_next_tag():
    today = datetime.date.today()
    numbers = []
    for tag in local_tags():
        match = TAG_PATTERN.match(tag)
        if match and int(match.group(1)) == today.year and int(match.group(2)) == today.month:
            numbers.append(int(match.group(3)))
    return 'v%d.%d.%d' % (today.year, today.month, max(numbers) + 1 if numbers else 0)


def default_tag():
    if session_tag:
        return session_tag
    tags = release_tags(local_tags())
    return tags[-1] if tags else None


def actions_url():
    code, url = git_query('remote', 'get-url', REMOTE)
    if code != 0:
        return None
    match = re.match(r'^(?:https://github\.com/|git@github\.com:)(.+?)(?:\.git)?/?$', url)
    return 'https://github.com/%s/actions' % match.group(1) if match else None


# ---------------------------------------------------------------------------
# Menu items
# ---------------------------------------------------------------------------

def item_validate():
    explain(tr('1  Bibliothek prüfen', '1  Validate library'),
            tr('validate.py prüft zangbundel.json und alle Lieder unter songs/ nach den Regeln des '
               'Zangbundel-Formats.\nFehler und Warnungen müssen behoben werden, bevor ein Release '
               'gemacht wird. Es wird nichts verändert.',
               'validate.py checks zangbundel.json and all songs under songs/ against the rules of '
               'the Zangbundel format.\nErrors and warnings must be fixed before a release is made. '
               'Nothing is changed.'))
    run_tool('validate.py', '--strict', '--info', '.')


def item_status():
    explain(tr('2  Status anzeigen', '2  Show status'),
            tr('Zeigt den Stand des Repositorys: Branch, geänderte Dateien, Tags und den Vergleich '
               'mit GitHub.\nEs werden nur Abfragen ausgeführt; es wird nichts verändert.',
               'Shows the state of the repository: branch, changed files, tags and the comparison '
               'with GitHub.\nOnly queries are run; nothing is changed.'))
    branch = current_branch()
    say('Branch: %s' % (branch or tr('(kein Branch)', '(no branch)')))
    code, out = git_query('status', '--short')
    if out:
        say(tr('Geänderte Dateien:', 'Changed files:'))
        say(out, wrap=False)
    else:
        say(tr('Geänderte Dateien: keine', 'Changed files: none'))
    tags = release_tags(local_tags())
    say(tr('Release-Tags lokal: %s', 'Local release tags: %s')
        % (', '.join(tags) if tags else tr('keine', 'none')))
    incoming = fetch_and_count_incoming()
    code, ahead = git_query('rev-list', '--count', '%s/%s..HEAD' % (REMOTE, MAIN_BRANCH))
    if incoming is not None:
        say(tr('Auf GitHub neu (zu pullen): %d Commit(s)',
               'New on GitHub (to pull): %d commit(s)') % incoming)
    if code == 0:
        say(tr('Lokal neu (zu pushen): %s Commit(s)', 'New locally (to push): %s commit(s)') % ahead)
    if incoming:
        say(tr('Hinweis: Vor Commit oder Push zuerst Menüpunkt 11 (git pull) ausführen.',
               'Note: run menu item 11 (git pull) before committing or pushing.'))


def item_add():
    explain(tr('3  Änderungen vormerken (git add)', '3  Stage changes (git add)'),
            tr('Alle geänderten und neuen Dateien werden für den nächsten Commit vorgemerkt.\n'
               'Was ins Repository darf, bestimmt die Allow-List in .gitignore; anderes wird '
               'übergangen.',
               'All changed and new files are staged for the next commit.\n'
               'What may go into the repository is decided by the allow-list in .gitignore; '
               'anything else is skipped.'))
    code, out = git_query('status', '--short')
    if not out:
        say(tr('Es gibt keine Änderungen – nichts zu tun.', 'There are no changes – nothing to do.'))
        return
    say(tr('Diese Änderungen liegen vor:', 'These changes exist:'))
    say(out, wrap=False)
    say()
    git_change(['add', '-A'],
               tr('Danach sind die Änderungen vorgemerkt, aber noch nicht committet (nächster '
                  'Schritt: Menüpunkt 4).',
                  'Afterwards the changes are staged but not yet committed (next step: menu '
                  'item 4).'))


def item_commit():
    explain(tr('4  Commit erstellen (git commit)', '4  Create commit (git commit)'),
            tr('Die vorgemerkten Änderungen werden als neuer Stand (Commit) gespeichert.\n'
               'Vorher wird geprüft, ob auf GitHub etwas Neues liegt, und die Bibliothek wird '
               'geprüft.',
               'The staged changes are saved as a new state (commit).\n'
               'First the menu checks whether there is something new on GitHub, and the library is '
               'validated.'))
    if not require_nothing_to_pull():
        return
    code, _ = git_query('diff', '--cached', '--quiet')
    if code == 0:
        say(tr('Es ist nichts vorgemerkt. Zuerst Menüpunkt 3 (git add) ausführen.',
               'Nothing is staged. Run menu item 3 (git add) first.'))
        return
    code, out = git_query('diff', '--cached', '--stat')
    say(out, wrap=False)
    if not library_is_valid():
        say(tr('Die Bibliothek hat Fehler oder Warnungen – es wird nicht committet.',
               'The library has errors or warnings – nothing is committed.'))
        return
    say()
    message = ask(tr('Commit-Nachricht', 'Commit message'), 'Update library')
    git_change(['commit', '-m', message],
               tr('Danach ist der Commit lokal gespeichert, aber noch nicht auf GitHub (dafür '
                  'später Menüpunkt 9).',
                  'Afterwards the commit is saved locally but not yet on GitHub (menu item 9 does '
                  'that later).'))


def item_tag():
    global session_tag
    explain(tr('5  Tag setzen (git tag)', '5  Set tag (git tag)'),
            tr('Ein Tag gibt dem letzten Commit einen Release-Namen, z. B. v2026.11.0 '
               '(v<Jahr>.<Monat>.<Nummer>, kleines v).\nAus diesem Tag wird das Release gebaut; auf '
               'GitHub startet der Push des Tags (Menüpunkt 10) die Release-Erstellung.',
               'A tag gives the last commit a release name, e.g. v2026.11.0 '
               '(v<year>.<month>.<sequence>, lower-case v).\nThe release is built from this tag; on '
               'GitHub, pushing the tag (menu item 10) starts the release.'))
    code, out = git_query('status', '--porcelain')
    if out:
        say(tr('ACHTUNG: Es gibt Änderungen, die noch nicht committet sind. Sie sind NICHT im Tag '
               'enthalten.',
               'ATTENTION: There are changes that are not committed yet. They are NOT part of the '
               'tag.'))
        say(out, wrap=False)
        if not confirm(tr('Trotzdem den Tag auf den letzten Commit setzen?',
                          'Set the tag on the last commit anyway?')):
            say(tr('Abgebrochen. Zuerst Menüpunkte 3 und 4 ausführen.',
                   'Cancelled. Run menu items 3 and 4 first.'))
            return
    tag = ask(tr('Name des Tags', 'Tag name'), suggest_next_tag())
    if not TAG_PATTERN.match(tag):
        say(tr('"%s" ist kein gültiger Release-Tag. Format: v<Jahr>.<Monat>.<Nummer>, '
               'z. B. v2026.11.0.',
               '"%s" is not a valid release tag. Format: v<year>.<month>.<sequence>, '
               'e.g. v2026.11.0.') % tag)
        return
    if tag_exists_locally(tag):
        say(tr('Der Tag %s existiert schon. Bitte einen neuen Namen wählen (nächste Nummer).',
               'The tag %s already exists. Please choose a new name (next sequence number).') % tag)
        return
    if not library_is_valid():
        say(tr('Die Bibliothek hat Fehler oder Warnungen – es wird kein Tag gesetzt.',
               'The library has errors or warnings – no tag is set.'))
        return
    say()
    if git_change(['tag', '-a', tag, '-m', 'Release %s' % tag],
                  tr('Danach trägt der letzte Commit lokal den Tag %s (nächster Schritt: '
                     'Menüpunkt 7 oder direkt 9).',
                     'Afterwards the last commit carries the tag %s locally (next step: menu '
                     'item 7, or 9 directly).') % tag):
        session_tag = tag


def item_build_test():
    explain(tr('6  Test-Archiv bauen (ohne Tag)', '6  Build test archive (no tag)'),
            tr('release.py baut ein Archiv aus dem letzten Commit, ohne dass ein Tag nötig ist.\n'
               'Nicht committete Änderungen sind NICHT enthalten. Das Archiv landet in dist/ und '
               'dient nur zum Testen. Es wird nichts in Git verändert.',
               'release.py builds an archive from the last commit, without needing a tag.\n'
               'Uncommitted changes are NOT included. The archive goes to dist/ and is for '
               'testing only. Nothing is changed in git.'))
    run_tool('release.py', 'build', '--tag', TEST_TAG, '--allow-untagged', '--out', DIST_DIR)


def item_build_release():
    explain(tr('7  Release-Archiv aus Tag bauen', '7  Build release archive from tag'),
            tr('release.py baut das Archiv aus dem Commit, der den Tag trägt – genau so, wie es '
               'später auf GitHub gebaut wird.\nDas Archiv landet in dist/. Es wird nichts in Git '
               'verändert.',
               'release.py builds the archive from the commit that carries the tag – exactly as it '
               'will be built on GitHub later.\nThe archive goes to dist/. Nothing is changed in '
               'git.'))
    tag = ask('Tag', default_tag())
    if not tag:
        return
    if not tag_exists_locally(tag):
        say(tr('Der Tag %s existiert nicht (Gross-/Kleinschreibung beachten). Zuerst Menüpunkt 5.',
               'The tag %s does not exist (tags are case-sensitive). Run menu item 5 first.') % tag)
        return
    run_tool('release.py', 'build', '--tag', tag, '--out', DIST_DIR)


def item_verify():
    explain(tr('8  Archiv prüfen', '8  Verify archive'),
            tr('release.py prüft das neueste Archiv in dist/ so, wie es die App beim Import tut.\n'
               'Es wird nichts verändert.',
               'release.py checks the newest archive in dist/ the way the app does on import.\n'
               'Nothing is changed.'))
    folder = os.path.join(REPO_DIR, DIST_DIR)
    archives = []
    if os.path.isdir(folder):
        archives = [os.path.join(folder, name) for name in os.listdir(folder) if name.endswith('.zbl')]
    if not archives:
        say(tr('In dist/ liegt kein Archiv. Zuerst Menüpunkt 6 oder 7.',
               'There is no archive in dist/. Run menu item 6 or 7 first.'))
        return
    newest = max(archives, key=os.path.getmtime)
    say(tr('Neuestes Archiv: %s', 'Newest archive: %s') % os.path.relpath(newest, REPO_DIR))
    run_tool('release.py', 'verify', '--strict', os.path.relpath(newest, REPO_DIR))


def item_push_main():
    explain(tr('9  Commits zu GitHub pushen (git push origin main)',
               '9  Push commits to GitHub (git push origin main)'),
            tr('Die lokalen Commits werden auf GitHub hochgeladen.\nAuf GitHub prüft danach der '
               'Workflow "Validate library" die Bibliothek automatisch.',
               'The local commits are uploaded to GitHub.\nOn GitHub the workflow "Validate '
               'library" then checks the library automatically.'))
    branch = current_branch()
    if branch != MAIN_BRANCH:
        say(tr('Aktueller Branch ist "%s", nicht "%s". Bitte zuerst auf %s wechseln.',
               'The current branch is "%s", not "%s". Please switch to %s first.')
            % (branch, MAIN_BRANCH, MAIN_BRANCH))
        return
    if not require_nothing_to_pull():
        return
    code, ahead = git_query('rev-list', '--count', '%s/%s..HEAD' % (REMOTE, MAIN_BRANCH))
    if code == 0 and ahead == '0':
        say(tr('Es gibt keine lokalen Commits, die auf GitHub fehlen – nichts zu pushen.',
               'There are no local commits missing on GitHub – nothing to push.'))
        return
    code, out = git_query('log', '--oneline', '%s/%s..HEAD' % (REMOTE, MAIN_BRANCH))
    say(out, wrap=False)
    git_change(['push', REMOTE, MAIN_BRANCH],
               tr('Danach sind die Commits auf GitHub.', 'Afterwards the commits are on GitHub.'))


def item_push_tag():
    explain(tr('10  Tag zu GitHub pushen (git push origin <Tag>)',
               '10  Push tag to GitHub (git push origin <tag>)'),
            tr('Der Tag wird auf GitHub hochgeladen. Das startet dort den Workflow "Release": er '
               'baut das Archiv, veröffentlicht es unter "Releases" und aktualisiert releases.json.',
               'The tag is uploaded to GitHub. This starts the workflow "Release" there: it builds '
               'the archive, publishes it under "Releases" and updates releases.json.'))
    tag = ask('Tag', default_tag())
    if not tag:
        return
    if not tag_exists_locally(tag):
        say(tr('Der Tag %s existiert lokal nicht. Zuerst Menüpunkt 5.',
               'The tag %s does not exist locally. Run menu item 5 first.') % tag)
        return
    on_github = tag_on_github(tag)
    if on_github is None:
        return
    if on_github:
        say(tr('Der Tag %s ist schon auf GitHub – nichts zu pushen. Für ein neues Release einen '
               'neuen Tag setzen (Menüpunkt 5).',
               'The tag %s is already on GitHub – nothing to push. For a new release, set a new '
               'tag (menu item 5).') % tag)
        return
    if not require_nothing_to_pull():
        return
    code, _ = git_query('merge-base', '--is-ancestor', tag, '%s/%s' % (REMOTE, MAIN_BRANCH))
    if code != 0:
        say(tr('Der Commit mit dem Tag %s ist noch nicht auf GitHub. Zuerst Menüpunkt 9 '
               '(git push origin main) ausführen.',
               'The commit with the tag %s is not on GitHub yet. Run menu item 9 '
               '(git push origin main) first.') % tag)
        return
    if git_change(['push', REMOTE, tag],
                  tr('Danach startet auf GitHub die Release-Erstellung.',
                     'Afterwards the release starts on GitHub.')):
        url = actions_url()
        say()
        say(LINE)
        say(tr('Auf GitHub im Repository unter "Actions" prüfen, ob die Release-Erstellung einen '
               'grünen Haken bekommen hat.',
               'On GitHub, check under "Actions" in the repository whether the release run got a '
               'green tick.'))
        if url:
            say('    %s' % url, wrap=False)
        say(tr('Wenn als Symbol ein Kreis dargestellt wird, ist die Release-Erstellung noch am '
               'Laufen.',
               'If a circle is shown as the symbol, the release run is still in progress.'))
        say(tr('Sobald der grüne Haken da ist, muss noch ein "git pull" ausgeführt werden '
               '(Menüpunkt 11), da releases.json auf GitHub in neuer Version vorliegt.',
               'As soon as the green tick is there, a "git pull" must still be run (menu item 11), '
               'because releases.json on GitHub is in a new version.'))
        say(LINE)


def item_pull():
    explain(tr('11  Nach dem grünen Haken: Änderungen holen (git pull)',
               '11  After the green tick: fetch changes (git pull)'),
            tr('Holt die Commits, die auf GitHub neu sind – nach einem Release vor allem die neue '
               'releases.json.\nErst ausführen, wenn unter "Actions" der grüne Haken da ist.',
               'Fetches the commits that are new on GitHub – after a release mainly the new '
               'releases.json.\nRun it only when the green tick is shown under "Actions".'))
    incoming = fetch_and_count_incoming()
    if incoming is None:
        return
    if incoming == 0:
        say(tr('Auf GitHub gibt es nichts Neues. Läuft die Release-Erstellung noch (Kreis-Symbol '
               'unter "Actions")? Dann später nochmals versuchen.',
               'There is nothing new on GitHub. Is the release run still in progress (circle symbol '
               'under "Actions")? Then try again later.'))
        return
    say(tr('Auf GitHub neu (%d Commit(s)):', 'New on GitHub (%d commit(s)):') % incoming)
    code, out = git_query('log', '--oneline', 'HEAD..%s/%s' % (REMOTE, MAIN_BRANCH))
    say(out, wrap=False)
    say()
    git_change(['pull', REMOTE, MAIN_BRANCH],
               tr('Danach ist der lokale Stand gleich wie auf GitHub.',
                  'Afterwards the local state is the same as on GitHub.'))


# Menu entries: key, German label, English label, git command shown in brackets, function.
MENU = [
    ('1', 'Bibliothek prüfen', 'Validate library', '', item_validate),
    ('2', 'Status anzeigen (Vergleich mit GitHub)', 'Show status (comparison with GitHub)', '',
     item_status),
    ('3', 'Änderungen vormerken', 'Stage changes', 'git add', item_add),
    ('4', 'Commit erstellen', 'Create commit', 'git commit', item_commit),
    ('5', 'Tag setzen', 'Set tag', 'git tag', item_tag),
    ('6', 'Test-Archiv bauen (ohne Tag)', 'Build test archive (no tag)', '', item_build_test),
    ('7', 'Release-Archiv aus Tag bauen', 'Build release archive from tag', '', item_build_release),
    ('8', 'Neuestes Archiv in dist/ prüfen', 'Verify newest archive in dist/', '', item_verify),
    ('9', 'Commits zu GitHub pushen', 'Push commits to GitHub', 'git push origin main',
     item_push_main),
    ('10', 'Tag zu GitHub pushen (startet Release)', 'Push tag to GitHub (starts release)',
     'git push origin <Tag>', item_push_tag),
    ('11', 'Nach grünem Haken: Änderungen holen', 'After green tick: fetch changes', 'git pull',
     item_pull),
]


def show_menu():
    say()
    say('=' * 66)
    say(tr('  Zangbundel-Bibliothek – Werkzeuge', '  Zangbundel library – tools'))
    say('=' * 66)
    for key, label_de, label_en, command, _ in MENU:
        label = tr(label_de, label_en)
        if command and language == 'en':
            command = command.replace('<Tag>', '<tag>')
        say(('  %2s  %-40s %s' % (key, label, '[%s]' % command if command else '')).rstrip(),
            wrap=False)
    say(tr('   0  Beenden', '   0  Exit'))
    say()
    say(tr('  Ablauf für ein Release: 1 > 3 > 4 > 5 (> 7 > 8) > 9 > 10 > grüner Haken > 11',
           '  Release sequence: 1 > 3 > 4 > 5 (> 7 > 8) > 9 > 10 > green tick > 11'))
    if session_tag:
        say(tr('  Tag in dieser Sitzung: %s', '  Tag in this session: %s') % session_tag)
    say()


def main():
    setup_console()
    os.chdir(REPO_DIR)
    try:
        choose_language()
        check_git_available()
        actions = {entry[0]: entry[-1] for entry in MENU}
        while True:
            show_menu()
            choice = input(tr('Auswahl: ', 'Choice: ')).strip()
            if choice == '0':
                return 0
            func = actions.get(choice)
            if func is None:
                say(tr('Unbekannte Auswahl.', 'Unknown choice.'))
                continue
            func()
            pause()
    except StopMenu as stop:
        say()
        say(LINE)
        say(str(stop))
        say(LINE)
        pause()
        return 1
    except (EOFError, KeyboardInterrupt):
        say()
        return 0


if __name__ == '__main__':
    sys.exit(main())
