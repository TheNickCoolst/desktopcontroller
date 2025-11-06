@echo off
REM ====================================================================
REM Desktop Controller - Automatischer Starter
REM ====================================================================

echo.
echo ====================================================================
echo  🤖 DESKTOP CONTROLLER MIT GROQ VISION AI
echo ====================================================================
echo.

REM Prüfe ob Python installiert ist
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python ist nicht installiert oder nicht im PATH!
    echo    Bitte installiere Python 3.8+ von https://www.python.org
    pause
    exit /b 1
)

echo ✓ Python gefunden
echo.

REM Prüfe ob virtuelle Umgebung existiert
if not exist "venv\" (
    echo 📦 Erstelle virtuelle Umgebung...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Fehler beim Erstellen der virtuellen Umgebung
        pause
        exit /b 1
    )
    echo ✓ Virtuelle Umgebung erstellt
    echo.
)

REM Aktiviere virtuelle Umgebung
echo ⚙️  Aktiviere virtuelle Umgebung...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Fehler beim Aktivieren der virtuellen Umgebung
    pause
    exit /b 1
)
echo ✓ Virtuelle Umgebung aktiviert
echo.

REM Prüfe ob Dependencies installiert sind
if not exist "venv\Lib\site-packages\groq\" (
    echo 📦 Installiere Dependencies...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Fehler beim Installieren der Dependencies
        pause
        exit /b 1
    )
    echo ✓ Dependencies installiert
    echo.
)

REM Prüfe ob .env Datei existiert
if not exist ".env" (
    echo ⚠️  Keine .env Datei gefunden!
    echo.
    if exist ".env.example" (
        echo 📝 Kopiere .env.example zu .env...
        copy .env.example .env >nul
        echo.
        echo ⚠️  WICHTIG: Bitte bearbeite die .env Datei und füge deinen GROQ_API_KEY ein!
        echo    Öffne .env in einem Texteditor und füge deinen API Key ein.
        echo.
        echo    Drücke eine Taste um .env zu öffnen...
        pause >nul
        notepad .env
        echo.
        echo    Nachdem du deinen API Key eingegeben hast, speichere und schließe den Editor.
        echo    Dann starte diese Batch-Datei erneut.
        pause
        exit /b 0
    ) else (
        echo ❌ .env.example nicht gefunden! Erstelle manuell eine .env Datei mit:
        echo    GROQ_API_KEY=dein_api_key_hier
        pause
        exit /b 1
    )
)

echo ✓ Konfiguration geladen
echo.

REM Zeige Menü
:menu
echo ====================================================================
echo  DESKTOP CONTROLLER - STARTMENÜ
echo ====================================================================
echo.
echo  1) Interaktiver Modus (mehrere Aufgaben nacheinander)
echo  2) Einzelne Aufgabe ausführen
echo  3) Test-Modus (Konfiguration prüfen)
echo  4) GUI Launcher starten
echo  5) Beenden
echo.
set /p choice="Wähle eine Option (1-5): "

if "%choice%"=="1" goto interactive
if "%choice%"=="2" goto single_task
if "%choice%"=="3" goto test
if "%choice%"=="4" goto gui
if "%choice%"=="5" goto end

echo ❌ Ungültige Auswahl
echo.
goto menu

:interactive
echo.
echo ====================================================================
echo  🎮 INTERAKTIVER MODUS
echo ====================================================================
echo.
python main.py --interactive
goto end

:single_task
echo.
set /p task="📝 Gib deine Aufgabe ein: "
if "%task%"=="" (
    echo ❌ Keine Aufgabe eingegeben
    echo.
    goto menu
)
echo.
python main.py --task "%task%"
echo.
echo ====================================================================
pause
goto menu

:test
echo.
echo ====================================================================
echo  🧪 TEST-MODUS
echo ====================================================================
echo.
python main.py --test
echo.
pause
goto menu

:gui
echo.
echo ====================================================================
echo  🖥️  GUI LAUNCHER
echo ====================================================================
echo.
if exist "launcher.pyw" (
    start pythonw launcher.pyw
    echo ✓ GUI gestartet
    timeout /t 2 >nul
    goto end
) else if exist "launcher.py" (
    start pythonw launcher.py
    echo ✓ GUI gestartet
    timeout /t 2 >nul
    goto end
) else (
    echo ❌ GUI Launcher nicht gefunden (launcher.pyw oder launcher.py)
    pause
    goto menu
)

:end
echo.
echo 👋 Auf Wiedersehen!
deactivate
exit /b 0
