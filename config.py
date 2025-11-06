"""
Desktop Controller Configuration
Konfigurationsdatei für das Groq Vision Desktop Steuerungs-Tool
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# ================== API KONFIGURATION ==================
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.2-90b-vision-preview"  # Groq Vision Modell
GROQ_API_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

# ================== SCREENSHOT EINSTELLUNGEN ==================
SCREENSHOT_INTERVAL = 2.0  # Sekunden zwischen Screenshots
SCREENSHOT_QUALITY = 85  # JPEG Qualität (0-100)
SCREENSHOT_MAX_SIZE = (1920, 1080)  # Maximale Auflösung

# ================== AKTION EINSTELLUNGEN ==================
# Aktionen die eine Sicherheitsbestätigung erfordern
CRITICAL_ACTIONS = [
    "delete_file",
    "close_window",
    "shutdown",
    "restart",
    "execute_command",
    "install",
    "uninstall",
    "format"
]

# PyAutoGUI Einstellungen
PYAUTOGUI_PAUSE = 0.5  # Pause zwischen Aktionen (Sekunden)
PYAUTOGUI_FAILSAFE = True  # Maus in obere linke Ecke = Notfall-Stop
MOUSE_MOVE_DURATION = 0.3  # Dauer der Mausbewegung (Sekunden)
TYPING_INTERVAL = 0.05  # Intervall zwischen Tastenanschlägen

# ================== SICHERHEIT ==================
SAFETY_CHECK_ENABLED = True  # Sicherheitsabfragen aktivieren
ALLOWED_ACTIONS = [
    "click",
    "double_click",
    "right_click",
    "type_text",
    "press_key",
    "scroll",
    "move_mouse",
    "hotkey",
    "wait",
    "screenshot"
]

# Tastenkombinationen die erlaubt sind
ALLOWED_HOTKEYS = [
    ["ctrl", "c"],  # Kopieren
    ["ctrl", "v"],  # Einfügen
    ["ctrl", "a"],  # Alles markieren
    ["ctrl", "f"],  # Suchen
    ["ctrl", "t"],  # Neuer Tab
    ["ctrl", "w"],  # Tab schließen
    ["alt", "tab"],  # Fenster wechseln
    ["win"],  # Start-Menü
]

# ================== TASK EINSTELLUNGEN ==================
MAX_TASK_STEPS = 50  # Maximale Anzahl von Schritten pro Task
TASK_TIMEOUT = 300  # Timeout in Sekunden (5 Minuten)
CONFIDENCE_THRESHOLD = 0.7  # Minimale Konfidenz für Aktionen (0.0-1.0)

# ================== LOGGING ==================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = "desktop_controller.log"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ================== WEB UI (OPTIONAL) ==================
WEB_UI_ENABLED = False  # Web-UI aktivieren
WEB_UI_PORT = 5000
WEB_UI_HOST = "127.0.0.1"  # Nur localhost aus Sicherheitsgründen

# ================== SYSTEM PROMPT ==================
SYSTEM_PROMPT = """Du bist ein Desktop-Steuerungs-Assistent mit Zugriff auf Computer-Vision.
Du erhältst einen Screenshot des aktuellen Desktop-Zustands und eine Benutzeranfrage.

Deine Aufgabe ist es, die nächste Aktion zu bestimmen, um die Anfrage zu erfüllen.

Verfügbare Aktionen:
- click(x, y): Klicke an Position (x, y)
- double_click(x, y): Doppelklick an Position (x, y)
- right_click(x, y): Rechtsklick an Position (x, y)
- type_text(text): Tippe den angegebenen Text
- press_key(key): Drücke eine Taste (z.B. 'enter', 'esc', 'tab')
- scroll(amount): Scrolle (positiv = runter, negativ = hoch)
- move_mouse(x, y): Bewege Maus zu Position (x, y)
- hotkey(keys): Tastenkombination (z.B. ['ctrl', 'c'])
- wait(seconds): Warte X Sekunden
- done(message): Task abgeschlossen

Antworte IMMER im folgenden JSON-Format:
{
    "reasoning": "Kurze Erklärung was du siehst und warum du diese Aktion wählst",
    "action": "action_name",
    "parameters": {...},
    "confidence": 0.95,
    "is_critical": false
}

Beispiele:
{
    "reasoning": "Ich sehe die Firefox-Ikone auf dem Desktop bei Position (100, 200)",
    "action": "click",
    "parameters": {"x": 100, "y": 200},
    "confidence": 0.9,
    "is_critical": false
}

{
    "reasoning": "Firefox ist geöffnet, ich sehe die Suchleiste",
    "action": "type_text",
    "parameters": {"text": "Groq AI"},
    "confidence": 0.95,
    "is_critical": false
}

Wichtig:
- Sei präzise bei Koordinaten
- Erkläre deine Überlegungen
- Markiere kritische Aktionen
- Gib eine Konfidenz an (0.0 - 1.0)
- Wenn der Task abgeschlossen ist, verwende action: "done"
"""

# ================== VALIDIERUNG ==================
def validate_config() -> bool:
    """Validiert die Konfiguration"""
    if not GROQ_API_KEY:
        print("FEHLER: GROQ_API_KEY nicht gesetzt!")
        print("Bitte setze die Umgebungsvariable oder erstelle eine .env Datei")
        return False
    return True

def get_config_summary() -> Dict:
    """Gibt eine Zusammenfassung der Konfiguration zurück"""
    return {
        "model": GROQ_MODEL,
        "safety_enabled": SAFETY_CHECK_ENABLED,
        "max_steps": MAX_TASK_STEPS,
        "web_ui_enabled": WEB_UI_ENABLED,
        "screenshot_interval": SCREENSHOT_INTERVAL,
    }
