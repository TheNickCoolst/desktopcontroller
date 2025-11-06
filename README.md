# 🤖 Desktop Controller mit Groq Vision AI

Ein autonomes Desktop-Steuerungs-Tool, das **Groq Llama 3.2 Vision** verwendet, um Desktop-Aufgaben visuell zu verstehen und automatisch auszuführen.

## 🌟 Features

- **🎯 Visuelle KI-Steuerung**: Nutzt Groq's Vision API zur visuellen Analyse des Desktops
- **🖱️ Automatische Aktionen**: Klicks, Tastatureingaben, Scrolling, etc.
- **🔒 Sicherheit**: Bestätigungsabfragen für kritische Aktionen
- **⚙️ Konfigurierbar**: Vollständig anpassbar über `config.py`
- **📊 Detailliertes Logging**: Verfolge alle Aktionen und Entscheidungen
- **🎮 Interaktiver Modus**: Stelle mehrere Aufgaben nacheinander

## 📋 Voraussetzungen

- Python 3.8+
- Groq API Key (kostenlos erhältlich bei [console.groq.com](https://console.groq.com))
- Linux/Windows/macOS mit grafischer Oberfläche

## 🚀 Installation

### 1. Repository klonen

```bash
git clone <repository-url>
cd desktopcontroller
```

### 2. Virtuelle Umgebung erstellen (empfohlen)

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder
venv\Scripts\activate  # Windows
```

### 3. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 4. API Key konfigurieren

Erstelle eine `.env` Datei:

```bash
cp .env.example .env
```

Bearbeite `.env` und füge deinen Groq API Key ein:

```env
GROQ_API_KEY=dein_groq_api_key_hier
```

Alternativ als Umgebungsvariable:

```bash
export GROQ_API_KEY="dein_groq_api_key_hier"
```

## 📖 Verwendung

### Einzelne Aufgabe ausführen

```bash
python main.py --task "Öffne Firefox und suche nach Groq AI"
```

### Interaktiver Modus

```bash
python main.py --interactive
```

Im interaktiven Modus kannst du mehrere Aufgaben nacheinander eingeben:

```
📝 Task eingeben: Öffne den Datei-Manager
📝 Task eingeben: Erstelle einen neuen Ordner namens Test
📝 Task eingeben: exit
```

### Test-Modus

Prüfe ob alles korrekt konfiguriert ist:

```bash
python main.py --test
```

### Verbose-Modus (Debugging)

```bash
python main.py --verbose --task "Meine Aufgabe"
```

## 🏗️ Architektur

Das System besteht aus 5 Hauptkomponenten:

### 1. **config.py** - Konfiguration

- API-Einstellungen
- Sicherheitsparameter
- System-Prompt für die KI
- Erlaubte Aktionen und Hotkeys

### 2. **screenshot_handler.py** - Screenshot-Verwaltung

- Erstellt Screenshots des Desktops
- Konvertiert Bilder zu Base64 für API-Übertragung
- Bildoptimierung und Resize

### 3. **groq_handler.py** - Groq API Integration

- Kommunikation mit Groq Vision API
- Parsing der KI-Antworten
- Action-Validierung

### 4. **action_executor.py** - Aktionsausführung

- PyAutoGUI-Integration
- Maus- und Tastatursteuerung
- Sicherheitsabfragen für kritische Aktionen

### 5. **main.py** - Hauptprogramm

- Task-Orchestrierung
- Haupt-Loop
- CLI-Interface

## 🎯 Verfügbare Aktionen

Die KI kann folgende Aktionen ausführen:

| Aktion | Parameter | Beschreibung |
|--------|-----------|--------------|
| `click` | `x, y` | Einfacher Mausklick |
| `double_click` | `x, y` | Doppelklick |
| `right_click` | `x, y` | Rechtsklick |
| `move_mouse` | `x, y` | Maus bewegen |
| `type_text` | `text` | Text eingeben |
| `press_key` | `key` | Taste drücken (z.B. 'enter', 'esc') |
| `scroll` | `amount` | Scrollen (+ = runter, - = hoch) |
| `hotkey` | `keys` | Tastenkombination (z.B. ['ctrl', 'c']) |
| `wait` | `seconds` | Warten |
| `done` | `message` | Task abgeschlossen |

## ⚙️ Konfiguration

Passe `config.py` an deine Bedürfnisse an:

### Screenshot-Einstellungen

```python
SCREENSHOT_INTERVAL = 2.0  # Sekunden zwischen Screenshots
SCREENSHOT_QUALITY = 85    # JPEG Qualität (0-100)
SCREENSHOT_MAX_SIZE = (1920, 1080)  # Max. Auflösung
```

### Sicherheit

```python
SAFETY_CHECK_ENABLED = True  # Sicherheitsabfragen aktivieren
CONFIDENCE_THRESHOLD = 0.7   # Minimale KI-Konfidenz für Aktionen
```

### Task-Limits

```python
MAX_TASK_STEPS = 50    # Max. Schritte pro Task
TASK_TIMEOUT = 300     # Timeout in Sekunden
```

## 🔒 Sicherheit

### Integrierte Sicherheitsmaßnahmen

1. **Erlaubte Aktionen**: Nur vordefinierte Aktionen sind erlaubt
2. **Koordinaten-Validierung**: Prüft ob Klick-Koordinaten gültig sind
3. **Hotkey-Whitelist**: Nur erlaubte Tastenkombinationen
4. **Bestätigungsabfragen**: Kritische Aktionen erfordern Benutzerbestätigung
5. **Konfidenz-Schwellwert**: Aktionen werden nur bei hoher KI-Sicherheit ausgeführt
6. **Failsafe**: PyAutoGUI's Failsafe (Maus in obere linke Ecke = Notfall-Stop)

### Kritische Aktionen

Diese Aktionen erfordern eine manuelle Bestätigung (wenn `SAFETY_CHECK_ENABLED = True`):

- `delete_file`
- `close_window`
- `shutdown` / `restart`
- `execute_command`
- `install` / `uninstall`

## 📊 Logging

Logs werden gespeichert in `desktop_controller.log`:

```bash
tail -f desktop_controller.log  # Live-Logs anzeigen
```

Log-Level in `config.py` anpassen:

```python
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
```

## 🧪 Beispiele

### Beispiel 1: Firefox öffnen und suchen

```bash
python main.py --task "Öffne Firefox und suche nach 'Groq AI'"
```

### Beispiel 2: Datei erstellen

```bash
python main.py --task "Öffne einen Texteditor und erstelle eine neue Datei namens test.txt"
```

### Beispiel 3: E-Mail schreiben

```bash
python main.py --task "Öffne Gmail und schreibe eine E-Mail an test@example.com"
```

### Beispiel 4: Screenshot machen

```bash
python main.py --task "Mache einen Screenshot und speichere ihn"
```

## 🐛 Troubleshooting

### Problem: "GROQ_API_KEY nicht gesetzt"

**Lösung**: Erstelle eine `.env` Datei oder setze die Umgebungsvariable:

```bash
export GROQ_API_KEY="dein_key_hier"
```

### Problem: Screenshots funktionieren nicht

**Lösung**: Stelle sicher, dass du eine grafische Oberfläche hast. Auf Servern ohne Display funktioniert dies nicht.

### Problem: PyAutoGUI Fehler

**Lösung**: Installiere ggf. zusätzliche System-Dependencies:

**Linux:**
```bash
sudo apt-get install python3-tk python3-dev
sudo apt-get install scrot  # Für Screenshots
```

**macOS:**
```bash
brew install python-tk
```

### Problem: API Timeout

**Lösung**: Erhöhe den Timeout in `groq_handler.py`:

```python
timeout=60  # statt 30
```

### Problem: Maus bewegt sich zu schnell

**Lösung**: Erhöhe die Bewegungsdauer in `config.py`:

```python
MOUSE_MOVE_DURATION = 0.5  # statt 0.3
```

## 🔧 Entwicklung

### Module einzeln testen

Jedes Modul kann einzeln getestet werden:

```bash
python screenshot_handler.py  # Screenshot Test
python groq_handler.py        # Groq API Test
python action_executor.py     # Action Executor Test
```

### Debug-Modus

Im Debug-Modus werden Screenshots jedes Schritts gespeichert:

```bash
python main.py --verbose --task "Deine Aufgabe"
```

Screenshots werden gespeichert als `debug_step_1.jpg`, `debug_step_2.jpg`, etc.

## 📝 KI-Prompt Anpassung

Der System-Prompt kann in `config.py` angepasst werden:

```python
SYSTEM_PROMPT = """
Deine Anweisungen hier...
"""
```

Dies beeinflusst, wie die KI Screenshots interpretiert und Aktionen wählt.

## 🚧 Bekannte Limitierungen

1. **Textextraktion**: Die KI kann Text auf dem Bildschirm lesen, aber OCR ist nicht 100% genau
2. **Kleine Elemente**: Sehr kleine UI-Elemente können schwer zu erkennen sein
3. **Dynamische Inhalte**: Schnell wechselnde Inhalte können Probleme bereiten
4. **Mehrere Monitore**: Derzeit nur ein Monitor unterstützt

## 🤝 Contributing

Beiträge sind willkommen! Bitte:

1. Fork das Repository
2. Erstelle einen Feature-Branch
3. Commit deine Änderungen
4. Push zum Branch
5. Erstelle einen Pull Request

## 📄 Lizenz

MIT License - siehe LICENSE Datei

## ⚠️ Haftungsausschluss

Dieses Tool führt automatisch Aktionen auf deinem Desktop aus. Nutze es mit Vorsicht und:

- Teste zuerst mit harmlosen Aufgaben
- Überwache die Ausführung
- Nutze es nicht auf Produktionssystemen ohne ausreichende Tests
- Der Autor übernimmt keine Haftung für Schäden

## 🙏 Credits

- [Groq](https://groq.com) für die schnelle Vision API
- [PyAutoGUI](https://pyautogui.readthedocs.io/) für Desktop-Automation
- [Pillow](https://python-pillow.org/) für Bildverarbeitung

## 📞 Support

Bei Fragen oder Problemen:

1. Prüfe zuerst die Troubleshooting-Sektion
2. Schaue in die Logs (`desktop_controller.log`)
3. Erstelle ein Issue im Repository

---

**Viel Spaß mit deinem KI-gesteuerten Desktop! 🚀**
