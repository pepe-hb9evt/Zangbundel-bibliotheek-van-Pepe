@echo off
rem Menu for the Zangbundel library tools: validator and release tool.
rem Keep this menu in sync with the options of scripts\validate.py and
rem scripts\release.py (every option used here has a menu item).
setlocal EnableExtensions
cd /d "%~dp0"
chcp 65001 >nul

rem Prefer the Python launcher, fall back to python on the PATH.
set "PY=python"
where py >nul 2>&1 && set "PY=py -3"

:menu
cls
echo ==========================================================
echo   Zangbundel library - tools
echo ==========================================================
echo   1  Validate library (strict, with info)
echo   2  Validate library (strict, errors and warnings only)
echo   3  Build release archive from a git tag
echo   4  Build test archive from the last commit (no tag)
echo   5  Verify newest archive in dist\
echo   6  Show help of both tools
echo   0  Exit
echo.
echo   Note: 3 and 4 use the last commit only, not uncommitted changes.
echo.
set "CHOICE="
set /p "CHOICE=Choice: "
if "%CHOICE%"=="1" goto validate_full
if "%CHOICE%"=="2" goto validate_short
if "%CHOICE%"=="3" goto build_tag
if "%CHOICE%"=="4" goto build_test
if "%CHOICE%"=="5" goto verify
if "%CHOICE%"=="6" goto help
if "%CHOICE%"=="0" goto end
goto menu

:validate_full
call :run %PY% scripts\validate.py --strict --info .
goto done

:validate_short
call :run %PY% scripts\validate.py --strict .
goto done

:build_tag
call :find_git
if errorlevel 1 goto done
set "TAG="
set /p "TAG=Git tag (e.g. v2026.11.0): "
if "%TAG%"=="" goto menu
rem Tags are case-sensitive: v2026.11.0 and V2026.11.0 are different tags.
git rev-parse -q --verify "refs/tags/%TAG%" >nul 2>&1
if errorlevel 1 goto tag_missing
call :run %PY% scripts\release.py build --tag %TAG% --out dist
goto done

:tag_missing
echo.
echo Tag "%TAG%" does not exist in this repository (tags are case-sensitive).
echo Existing tags:
git tag --list
echo.
choice /c JN /n /m "Create tag %TAG% now (commit open changes first)? [J/N] "
if errorlevel 2 goto tag_declined

rem Release tags use calendar versioning: v<year>.<month>.<sequence>, lower-case v.
echo %TAG%| findstr /r /x "v[0-9][0-9][0-9][0-9]\.[0-9][0-9]*\.[0-9][0-9]*" >nul
if errorlevel 1 goto tag_bad_format

rem Commit and tag need a git identity.
git config user.name >nul 2>&1
if errorlevel 1 goto git_no_identity
git config user.email >nul 2>&1
if errorlevel 1 goto git_no_identity

rem Never commit or tag a library that does not validate.
echo.
echo Validating library before commit and tag ...
%PY% scripts\validate.py --strict .
if errorlevel 1 goto tag_invalid_library

rem Commit open changes (the .gitignore allow-list decides what is included).
set "DIRTY="
for /f "delims=" %%L in ('git status --porcelain') do set "DIRTY=1"
if not defined DIRTY goto tag_create
echo.
echo Open changes:
git status --short
echo.
choice /c JN /n /m "Commit these changes? [J/N] "
if errorlevel 2 goto tag_declined
set "MSG="
set /p "MSG=Commit message (Enter = Release %TAG%): "
if not defined MSG set "MSG=Release %TAG%"
set "MSG=%MSG:"='%"
git add -A
if errorlevel 1 goto tag_git_failed
git commit -m "%MSG%"
if errorlevel 1 goto tag_git_failed

:tag_create
git tag -a "%TAG%" -m "Release %TAG%"
if errorlevel 1 goto tag_git_failed
echo.
echo Tag %TAG% created on the last commit.
echo To publish: git push origin main  and then  git push origin %TAG%
echo.
call :run %PY% scripts\release.py build --tag %TAG% --out dist
goto done

:tag_declined
echo.
echo Nothing changed. Create the tag yourself with  git tag %TAG%
echo or use item 4 to build a test archive without a tag.
set "RC=1"
goto done

:tag_bad_format
echo.
echo "%TAG%" is not a valid release tag. Use v^<year^>.^<month^>.^<sequence^>,
echo with a lower-case v, e.g. v2026.11.0. Nothing changed.
set "RC=1"
goto done

:git_no_identity
echo.
echo Git does not know your name and e-mail address yet. Set them once with:
echo   git config --global user.name "Your Name"
echo   git config --global user.email "you@example.org"
echo Nothing changed.
set "RC=1"
goto done

:tag_invalid_library
echo.
echo The library has errors or warnings (see above). Nothing was committed or tagged.
set "RC=1"
goto done

:tag_git_failed
echo.
echo A git command failed (see above). Check with  git status  and  git log -1.
set "RC=1"
goto done

:build_test
call :find_git
if errorlevel 1 goto done
call :run %PY% scripts\release.py build --tag v0.0.0-test --allow-untagged --out dist
goto done

:verify
set "ZBL="
for /f "delims=" %%F in ('dir /b /o-d "dist\*.zbl" 2^>nul') do if not defined ZBL set "ZBL=dist\%%F"
if not defined ZBL (
    echo No archive found in dist\ - build one first with 3 or 4.
    set "RC=1"
    goto done
)
echo Verifying %ZBL%
call :run %PY% scripts\release.py verify --strict "%ZBL%"
goto done

:help
call :run %PY% scripts\validate.py --help
echo.
call :run %PY% scripts\release.py --help
goto done

:find_git
rem release.py calls "git". Use git from the PATH, otherwise look for
rem Git for Windows or the git bundled with GitHub Desktop.
where git >nul 2>&1 && exit /b 0
set "GITDIR="
if exist "%ProgramFiles%\Git\cmd\git.exe" set "GITDIR=%ProgramFiles%\Git\cmd"
if not defined GITDIR if exist "%LOCALAPPDATA%\Programs\Git\cmd\git.exe" set "GITDIR=%LOCALAPPDATA%\Programs\Git\cmd"
if not defined GITDIR for /d %%D in ("%LOCALAPPDATA%\GitHubDesktop\app-*") do if exist "%%~D\resources\app\git\cmd\git.exe" set "GITDIR=%%~D\resources\app\git\cmd"
if not defined GITDIR goto git_missing
set "PATH=%GITDIR%;%PATH%"
echo Using git from: %GITDIR%
exit /b 0

:git_missing
echo.
echo Git was not found. Building archives needs git.exe.
echo Install Git for Windows (https://git-scm.com/download/win) and restart this menu.
set "RC=1"
exit /b 1

:run
rem Run the given command and keep its exit code.
%*
set "RC=%ERRORLEVEL%"
exit /b

:done
echo.
if "%RC%"=="0" (echo Result: OK) else (echo Result: FAILED - see the messages above.)
echo.
pause
goto menu

:end
endlocal
