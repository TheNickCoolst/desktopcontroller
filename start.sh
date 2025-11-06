#!/bin/bash
# ====================================================================
# Desktop Controller - Automatischer Starter (Linux/macOS)
# ====================================================================

echo ""
echo "===================================================================="
echo "  🤖 DESKTOP CONTROLLER MIT GROQ VISION AI"
echo "===================================================================="
echo ""

# Prüfe ob Python installiert ist
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 ist nicht installiert!"
    echo "   Bitte installiere Python 3.8+ von https://www.python.org"
    exit 1
fi

echo "✓ Python gefunden: $(python3 --version)"
echo ""

# Prüfe ob virtuelle Umgebung existiert
if [ ! -d "venv" ]; then
    echo "📦 Erstelle virtuelle Umgebung..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Fehler beim Erstellen der virtuellen Umgebung"
        exit 1
    fi
    echo "✓ Virtuelle Umgebung erstellt"
    echo ""
fi

# Aktiviere virtuelle Umgebung
echo "⚙️  Aktiviere virtuelle Umgebung..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Fehler beim Aktivieren der virtuellen Umgebung"
    exit 1
fi
echo "✓ Virtuelle Umgebung aktiviert"
echo ""

# Prüfe ob Dependencies installiert sind
if [ ! -f "venv/lib/python*/site-packages/groq/__init__.py" ] && [ ! -f "venv/lib/python3*/site-packages/groq/__init__.py" ]; then
    echo "📦 Installiere Dependencies..."
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Fehler beim Installieren der Dependencies"
        exit 1
    fi
    echo "✓ Dependencies installiert"
    echo ""
fi

# Prüfe ob .env Datei existiert
if [ ! -f ".env" ]; then
    echo "⚠️  Keine .env Datei gefunden!"
    echo ""
    if [ -f ".env.example" ]; then
        echo "📝 Kopiere .env.example zu .env..."
        cp .env.example .env
        echo ""
        echo "⚠️  WICHTIG: Bitte bearbeite die .env Datei und füge deinen GROQ_API_KEY ein!"
        echo "   Öffne .env in einem Texteditor und füge deinen API Key ein."
        echo ""

        # Versuche .env zu öffnen
        if command -v nano &> /dev/null; then
            read -p "Drücke Enter um .env mit nano zu öffnen..."
            nano .env
        elif command -v vim &> /dev/null; then
            read -p "Drücke Enter um .env mit vim zu öffnen..."
            vim .env
        else
            echo "   Bitte öffne .env manuell mit einem Texteditor."
        fi

        echo ""
        echo "   Nachdem du deinen API Key eingegeben hast, starte dieses Skript erneut."
        exit 0
    else
        echo "❌ .env.example nicht gefunden! Erstelle manuell eine .env Datei mit:"
        echo "   GROQ_API_KEY=dein_api_key_hier"
        exit 1
    fi
fi

echo "✓ Konfiguration geladen"
echo ""

# Zeige Menü
show_menu() {
    echo "===================================================================="
    echo "  DESKTOP CONTROLLER - STARTMENÜ"
    echo "===================================================================="
    echo ""
    echo "  1) Interaktiver Modus (mehrere Aufgaben nacheinander)"
    echo "  2) Einzelne Aufgabe ausführen"
    echo "  3) Test-Modus (Konfiguration prüfen)"
    echo "  4) GUI Launcher starten"
    echo "  5) Beenden"
    echo ""
    read -p "Wähle eine Option (1-5): " choice

    case $choice in
        1)
            echo ""
            echo "===================================================================="
            echo "  🎮 INTERAKTIVER MODUS"
            echo "===================================================================="
            echo ""
            python3 main.py --interactive
            ;;
        2)
            echo ""
            read -p "📝 Gib deine Aufgabe ein: " task
            if [ -z "$task" ]; then
                echo "❌ Keine Aufgabe eingegeben"
                echo ""
                show_menu
            else
                echo ""
                python3 main.py --task "$task"
                echo ""
                echo "===================================================================="
                read -p "Drücke Enter um fortzufahren..."
                show_menu
            fi
            ;;
        3)
            echo ""
            echo "===================================================================="
            echo "  🧪 TEST-MODUS"
            echo "===================================================================="
            echo ""
            python3 main.py --test
            echo ""
            read -p "Drücke Enter um fortzufahren..."
            show_menu
            ;;
        4)
            echo ""
            echo "===================================================================="
            echo "  🖥️  GUI LAUNCHER"
            echo "===================================================================="
            echo ""
            if [ -f "launcher.pyw" ]; then
                python3 launcher.pyw &
                echo "✓ GUI gestartet"
                sleep 2
            elif [ -f "launcher.py" ]; then
                python3 launcher.py &
                echo "✓ GUI gestartet"
                sleep 2
            else
                echo "❌ GUI Launcher nicht gefunden (launcher.pyw oder launcher.py)"
                read -p "Drücke Enter um fortzufahren..."
                show_menu
            fi
            ;;
        5)
            echo ""
            echo "👋 Auf Wiedersehen!"
            deactivate
            exit 0
            ;;
        *)
            echo "❌ Ungültige Auswahl"
            echo ""
            show_menu
            ;;
    esac
}

show_menu
