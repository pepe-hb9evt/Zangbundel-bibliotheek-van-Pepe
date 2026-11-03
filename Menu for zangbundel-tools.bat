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
set "TAG="
set /p "TAG=Git tag (e.g. v2026.11.0): "
if "%TAG%"=="" goto menu
call :run %PY% scripts\release.py build --tag %TAG% --out dist
goto done

:build_test
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
