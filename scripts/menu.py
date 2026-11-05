#!/usr/bin/env python3
"""Interactive console menu for maintaining this Zangbundel library.

Every step of the release process is a menu item of its own. Each item runs at
most one git command that changes something (add, commit, tag, push, pull);
that command is shown first and runs only after the user confirms it.
Read-only git queries (status, fetch, rev-list, ls-remote, ...) run without a
question, but are printed as well.

Before steps that would conflict with newer commits on GitHub, the menu fetches
from GitHub and stops if there is something to pull.

Run from anywhere:  python scripts/menu.py
Needs Python 3.8+ (standard library only) and git on the PATH.
"""

import datetime
import os
import re
import subprocess
import sys

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.dirname(SCRIPTS_DIR)
DIST_DIR = 'dist'
MAIN_BRANCH = 'main'
REMOTE = 'origin'
TEST_TAG = 'v0.0.0-test'
TAG_PATTERN = re.compile(r'^v(\d{4})\.(\d{1,2})\.(\d+)$')
LINE = '-' * 66

# Tag chosen in this session (set by "create tag", offered as default later).
session_tag = None


class StopMenu(Exception):
    """Raised to end the program after a message the user must act on."""


# ---------------------------------------------------------------------------
# Output and input helpers
# ---------------------------------------------------------------------------

def setup_console():
    """Make sure umlauts are printed correctly, also when output is redirected."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass


def say(text=''):
    print(text, flush=True)


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
    """Ask a yes/no question; only 'j' or 'ja' counts as yes."""
    answer = input('%s [j/N]: ' % prompt).strip().lower()
    return answer in ('j', 'ja', 'y', 'yes')


def pause():
    try:
        input('\nWeiter mit Enter ...')
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
    say('  Abfrage: %s' % show_command(cmd))
    result = subprocess.run(cmd, cwd=REPO_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            universal_newlines=True, encoding='utf-8', errors='replace')
    return result.returncode, result.stdout.strip()


def git_change(args, what):
    """Show a git command that changes something, ask, then run it. Returns True on success."""
    cmd = ['git'] + list(args)
    say('Dieser Git-Befehl wird jetzt ausgeführt:')
    say()
    say('    %s' % show_command(cmd))
    say()
    say(what)
    say()
    if not confirm('Befehl ausführen?'):
        say('Abgebrochen – es wurde nichts geändert.')
        return False
    say()
    result = subprocess.run(cmd, cwd=REPO_DIR)
    say()
    if result.returncode != 0:
        say('FEHLER: Der Git-Befehl ist fehlgeschlagen (Exit-Code %d), siehe Meldungen oben.'
            % result.returncode)
        return False
    say('OK: Befehl erfolgreich ausgeführt.')
    return True


def run_tool(script, *args):
    """Run one of the library tools with the current Python. Returns its exit code."""
    cmd = [sys.executable, os.path.join('scripts', script)] + list(args)
    say('  Aufruf: %s' % show_command(['python'] + cmd[1:]))
    say()
    result = subprocess.run(cmd, cwd=REPO_DIR)
    say()
    say('Ergebnis: %s' % ('OK' if result.returncode == 0 else
                          'FEHLER (Exit-Code %d), siehe Meldungen oben' % result.returncode))
    return result.returncode


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_git_available():
    try:
        subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except OSError:
        raise StopMenu('Git wurde nicht gefunden. Bitte den Ordner von git.exe in den PATH '
                       'eintragen (z. B. C:\\Program Files\\Git\\cmd) und das Menü neu starten.')
    code, _ = git_query('rev-parse', '--is-inside-work-tree')
    if code != 0:
        raise StopMenu('Der Ordner %s ist kein Git-Repository.' % REPO_DIR)


def current_branch():
    code, out = git_query('symbolic-ref', '--short', 'HEAD')
    return out if code == 0 else None


def fetch_and_count_incoming():
    """Fetch from GitHub and return the number of commits on GitHub missing locally, or None."""
    code, _ = git_query('fetch', '--quiet', REMOTE)
    if code != 0:
        say('WARNUNG: GitHub ist nicht erreichbar (git fetch fehlgeschlagen).')
        return None
    code, out = git_query('rev-list', '--count', 'HEAD..%s/%s' % (REMOTE, MAIN_BRANCH))
    if code != 0:
        say('WARNUNG: Der Stand von %s/%s konnte nicht verglichen werden.' % (REMOTE, MAIN_BRANCH))
        return None
    return int(out or 0)


def require_nothing_to_pull():
    """Stop the program when GitHub has commits that are not here yet. False: cannot check."""
    say('Prüfe, ob es auf GitHub Neues gibt, das zuerst geholt werden muss ...')
    incoming = fetch_and_count_incoming()
    if incoming is None:
        say('Dieser Schritt wird abgebrochen, weil nicht geprüft werden konnte, ob etwas zu holen ist.')
        return False
    if incoming:
        code, out = git_query('log', '--oneline', 'HEAD..%s/%s' % (REMOTE, MAIN_BRANCH))
        say(out)
        raise StopMenu(
            'Auf GitHub gibt es %d Commit(s), die hier noch fehlen (z. B. die neue releases.json '
            'nach einem Release).\n'
            'Bitte zuerst bereinigen: Menü neu starten und den letzten Menüpunkt "git pull" '
            'ausführen, oder im Terminal "git pull" eingeben.\n'
            'Das Menü wird jetzt beendet.' % incoming)
    say('OK: Auf GitHub gibt es nichts Neues.')
    return True


def library_is_valid():
    say('Prüfe die Bibliothek (validate.py --strict) ...')
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
    say('WARNUNG: GitHub ist nicht erreichbar (git ls-remote fehlgeschlagen).')
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
    explain('1  Bibliothek prüfen',
            'validate.py prüft zangbundel.json und alle Lieder unter songs/ nach den Regeln des '
            'Zangbundel-Formats.\nFehler und Warnungen müssen behoben werden, bevor ein Release '
            'gemacht wird. Es wird nichts verändert.')
    run_tool('validate.py', '--strict', '--info', '.')


def item_status():
    explain('2  Status anzeigen',
            'Zeigt den Stand des Repositorys: Branch, geänderte Dateien, Tags und den Vergleich mit '
            'GitHub.\nEs werden nur Abfragen ausgeführt; es wird nichts verändert.')
    branch = current_branch()
    say('Branch: %s' % (branch or '(kein Branch)'))
    code, out = git_query('status', '--short')
    say('Geänderte Dateien:' if out else 'Geänderte Dateien: keine')
    if out:
        say(out)
    tags = release_tags(local_tags())
    say('Release-Tags lokal: %s' % (', '.join(tags) if tags else 'keine'))
    incoming = fetch_and_count_incoming()
    code, ahead = git_query('rev-list', '--count', '%s/%s..HEAD' % (REMOTE, MAIN_BRANCH))
    if incoming is not None:
        say('Auf GitHub neu (zu pullen): %d Commit(s)' % incoming)
    if code == 0:
        say('Lokal neu (zu pushen): %s Commit(s)' % ahead)
    if incoming:
        say('Hinweis: Vor Commit oder Push zuerst Menüpunkt 11 (git pull) ausführen.')


def item_add():
    explain('3  Änderungen vormerken (git add)',
            'Alle geänderten und neuen Dateien werden für den nächsten Commit vorgemerkt.\nWas ins '
            'Repository darf, bestimmt die Allow-List in .gitignore; anderes wird übergangen.')
    code, out = git_query('status', '--short')
    if not out:
        say('Es gibt keine Änderungen – nichts zu tun.')
        return
    say('Diese Änderungen liegen vor:')
    say(out)
    say()
    git_change(['add', '-A'], 'Danach sind die Änderungen vorgemerkt, aber noch nicht committet '
                              '(nächster Schritt: Menüpunkt 4).')


def item_commit():
    explain('4  Commit erstellen (git commit)',
            'Die vorgemerkten Änderungen werden als neuer Stand (Commit) gespeichert.\nVorher wird '
            'geprüft, ob auf GitHub etwas Neues liegt, und die Bibliothek wird geprüft.')
    if not require_nothing_to_pull():
        return
    code, _ = git_query('diff', '--cached', '--quiet')
    if code == 0:
        say('Es ist nichts vorgemerkt. Zuerst Menüpunkt 3 (git add) ausführen.')
        return
    code, out = git_query('diff', '--cached', '--stat')
    say(out)
    if not library_is_valid():
        say('Die Bibliothek hat Fehler oder Warnungen – es wird nicht committet.')
        return
    say()
    message = ask('Commit-Nachricht', 'Update library')
    git_change(['commit', '-m', message], 'Danach ist der Commit lokal gespeichert, aber noch nicht '
                                          'auf GitHub (dafür später Menüpunkt 9).')


def item_tag():
    global session_tag
    explain('5  Tag setzen (git tag)',
            'Ein Tag gibt dem letzten Commit einen Release-Namen, z. B. v2026.11.0 '
            '(v<Jahr>.<Monat>.<Nummer>, kleines v).\nAus diesem Tag wird das Release gebaut; '
            'auf GitHub startet der Push des Tags (Menüpunkt 10) die Release-Erstellung.')
    code, out = git_query('status', '--porcelain')
    if out:
        say('ACHTUNG: Es gibt Änderungen, die noch nicht committet sind. Sie sind NICHT im Tag '
            'enthalten.')
        say(out)
        if not confirm('Trotzdem den Tag auf den letzten Commit setzen?'):
            say('Abgebrochen. Zuerst Menüpunkte 3 und 4 ausführen.')
            return
    tag = ask('Name des Tags', suggest_next_tag())
    if not TAG_PATTERN.match(tag):
        say('"%s" ist kein gültiger Release-Tag. Format: v<Jahr>.<Monat>.<Nummer>, z. B. v2026.11.0.'
            % tag)
        return
    if tag_exists_locally(tag):
        say('Der Tag %s existiert schon. Bitte einen neuen Namen wählen (nächste Nummer).' % tag)
        return
    if not library_is_valid():
        say('Die Bibliothek hat Fehler oder Warnungen – es wird kein Tag gesetzt.')
        return
    say()
    if git_change(['tag', '-a', tag, '-m', 'Release %s' % tag],
                  'Danach trägt der letzte Commit lokal den Tag %s (nächster Schritt: Menüpunkt 7 '
                  'oder direkt 9).' % tag):
        session_tag = tag


def item_build_test():
    explain('6  Test-Archiv bauen (ohne Tag)',
            'release.py baut ein Archiv aus dem letzten Commit, ohne dass ein Tag nötig ist.\n'
            'Nicht committete Änderungen sind NICHT enthalten. Das Archiv landet in dist/ und dient '
            'nur zum Testen. Es wird nichts in Git verändert.')
    run_tool('release.py', 'build', '--tag', TEST_TAG, '--allow-untagged', '--out', DIST_DIR)


def item_build_release():
    explain('7  Release-Archiv aus Tag bauen',
            'release.py baut das Archiv aus dem Commit, der den Tag trägt – genau so, wie es später '
            'auf GitHub gebaut wird.\nDas Archiv landet in dist/. Es wird nichts in Git verändert.')
    tag = ask('Tag', default_tag())
    if not tag:
        return
    if not tag_exists_locally(tag):
        say('Der Tag %s existiert nicht (Gross-/Kleinschreibung beachten). Zuerst Menüpunkt 5.' % tag)
        return
    run_tool('release.py', 'build', '--tag', tag, '--out', DIST_DIR)


def item_verify():
    explain('8  Archiv prüfen',
            'release.py prüft das neueste Archiv in dist/ so, wie es die App beim Import tut.\n'
            'Es wird nichts verändert.')
    folder = os.path.join(REPO_DIR, DIST_DIR)
    archives = []
    if os.path.isdir(folder):
        archives = [os.path.join(folder, name) for name in os.listdir(folder) if name.endswith('.zbl')]
    if not archives:
        say('In dist/ liegt kein Archiv. Zuerst Menüpunkt 6 oder 7.')
        return
    newest = max(archives, key=os.path.getmtime)
    say('Neuestes Archiv: %s' % os.path.relpath(newest, REPO_DIR))
    run_tool('release.py', 'verify', '--strict', os.path.relpath(newest, REPO_DIR))


def item_push_main():
    explain('9  Commits zu GitHub pushen (git push origin main)',
            'Die lokalen Commits werden auf GitHub hochgeladen.\nAuf GitHub prüft danach der '
            'Workflow "Validate library" die Bibliothek automatisch.')
    branch = current_branch()
    if branch != MAIN_BRANCH:
        say('Aktueller Branch ist "%s", nicht "%s". Bitte zuerst auf %s wechseln.'
            % (branch, MAIN_BRANCH, MAIN_BRANCH))
        return
    if not require_nothing_to_pull():
        return
    code, ahead = git_query('rev-list', '--count', '%s/%s..HEAD' % (REMOTE, MAIN_BRANCH))
    if code == 0 and ahead == '0':
        say('Es gibt keine lokalen Commits, die auf GitHub fehlen – nichts zu pushen.')
        return
    code, out = git_query('log', '--oneline', '%s/%s..HEAD' % (REMOTE, MAIN_BRANCH))
    say(out)
    git_change(['push', REMOTE, MAIN_BRANCH], 'Danach sind die Commits auf GitHub.')


def item_push_tag():
    explain('10  Tag zu GitHub pushen (git push origin <Tag>)',
            'Der Tag wird auf GitHub hochgeladen. Das startet dort den Workflow "Release": er baut '
            'das Archiv, veröffentlicht es unter "Releases" und aktualisiert releases.json.')
    tag = ask('Tag', default_tag())
    if not tag:
        return
    if not tag_exists_locally(tag):
        say('Der Tag %s existiert lokal nicht. Zuerst Menüpunkt 5.' % tag)
        return
    on_github = tag_on_github(tag)
    if on_github is None:
        return
    if on_github:
        say('Der Tag %s ist schon auf GitHub – nichts zu pushen. Für ein neues Release einen neuen '
            'Tag setzen (Menüpunkt 5).' % tag)
        return
    if not require_nothing_to_pull():
        return
    code, _ = git_query('merge-base', '--is-ancestor', tag, '%s/%s' % (REMOTE, MAIN_BRANCH))
    if code != 0:
        say('Der Commit mit dem Tag %s ist noch nicht auf GitHub. Zuerst Menüpunkt 9 '
            '(git push origin main) ausführen.' % tag)
        return
    if git_change(['push', REMOTE, tag], 'Danach startet auf GitHub die Release-Erstellung.'):
        url = actions_url()
        say()
        say(LINE)
        say('Auf GitHub im Repository unter "Actions" prüfen, ob die Release-Erstellung einen grünen '
            'Haken bekommen hat.')
        if url:
            say('    %s' % url)
        say('Wenn als Symbol ein Kreis dargestellt wird, ist die Release-Erstellung noch am Laufen.')
        say('Sobald der grüne Haken da ist, muss noch ein "git pull" ausgeführt werden '
            '(Menüpunkt 11), da releases.json auf GitHub in neuer Version vorliegt.')
        say(LINE)


def item_pull():
    explain('11  Nach dem grünen Haken: Änderungen holen (git pull)',
            'Holt die Commits, die auf GitHub neu sind – nach einem Release vor allem die neue '
            'releases.json.\nErst ausführen, wenn unter "Actions" der grüne Haken da ist.')
    incoming = fetch_and_count_incoming()
    if incoming is None:
        return
    if incoming == 0:
        say('Auf GitHub gibt es nichts Neues. Läuft die Release-Erstellung noch (Kreis-Symbol unter '
            '"Actions")? Dann später nochmals versuchen.')
        return
    say('Auf GitHub neu (%d Commit(s)):' % incoming)
    code, out = git_query('log', '--oneline', 'HEAD..%s/%s' % (REMOTE, MAIN_BRANCH))
    say(out)
    say()
    git_change(['pull', REMOTE, MAIN_BRANCH], 'Danach ist der lokale Stand gleich wie auf GitHub.')


MENU = [
    ('1', 'Bibliothek prüfen', '', item_validate),
    ('2', 'Status anzeigen (Vergleich mit GitHub)', '', item_status),
    ('3', 'Änderungen vormerken', 'git add', item_add),
    ('4', 'Commit erstellen', 'git commit', item_commit),
    ('5', 'Tag setzen', 'git tag', item_tag),
    ('6', 'Test-Archiv bauen (ohne Tag)', '', item_build_test),
    ('7', 'Release-Archiv aus Tag bauen', '', item_build_release),
    ('8', 'Neuestes Archiv in dist/ prüfen', '', item_verify),
    ('9', 'Commits zu GitHub pushen', 'git push origin main', item_push_main),
    ('10', 'Tag zu GitHub pushen (startet Release)', 'git push origin <Tag>', item_push_tag),
    ('11', 'Nach grünem Haken: Änderungen holen', 'git pull', item_pull),
]


def show_menu():
    say()
    say('=' * 66)
    say('  Zangbundel-Bibliothek – Werkzeuge')
    say('=' * 66)
    for key, label, command, _ in MENU:
        say(('  %2s  %-40s %s' % (key, label, '[%s]' % command if command else '')).rstrip())
    say('   0  Beenden')
    say()
    say('  Ablauf für ein Release: 1 > 3 > 4 > 5 > 7 > 8 > 9 > 10 > (grüner Haken) > 11')
    if session_tag:
        say('  Tag in dieser Sitzung: %s' % session_tag)
    say()


def main():
    setup_console()
    os.chdir(REPO_DIR)
    try:
        check_git_available()
        actions = {key: func for key, _, _, func in MENU}
        while True:
            show_menu()
            choice = input('Auswahl: ').strip()
            if choice == '0':
                return 0
            func = actions.get(choice)
            if func is None:
                say('Unbekannte Auswahl.')
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
