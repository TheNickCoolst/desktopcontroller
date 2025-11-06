#!/usr/bin/env python3
"""
Desktop Controller mit Groq Vision AI
Hauptprogramm für autonome Desktop-Steuerung
"""

import logging
import sys
import time
from typing import Optional
import argparse
from datetime import datetime

import config
from screenshot_handler import ScreenshotHandler
from groq_handler import GroqHandler
from action_executor import ActionExecutor

# Logging Setup
logger = logging.getLogger(__name__)


class DesktopController:
    """Hauptklasse für Desktop-Steuerung"""

    def __init__(self):
        self.screenshot_handler = ScreenshotHandler()
        self.groq_handler = GroqHandler()
        self.action_executor = ActionExecutor()

        self.current_task = None
        self.task_steps = 0
        self.task_start_time = None
        self.is_running = False

        logger.info("Desktop Controller initialisiert")

    def execute_task(self, task: str) -> bool:
        """
        Führt eine Benutzeraufgabe aus

        Args:
            task: Aufgabenbeschreibung

        Returns:
            True wenn erfolgreich abgeschlossen
        """
        self.current_task = task
        self.task_steps = 0
        self.task_start_time = time.time()
        self.is_running = True

        logger.info(f"Starte Task: {task}")
        print("\n" + "=" * 70)
        print(f"📋 TASK: {task}")
        print("=" * 70)

        context = f"Schritt 1 - Initialisierung"

        try:
            while self.is_running and self.task_steps < config.MAX_TASK_STEPS:
                # Prüfe Timeout
                elapsed_time = time.time() - self.task_start_time
                if elapsed_time > config.TASK_TIMEOUT:
                    logger.error(f"Task Timeout nach {elapsed_time:.1f} Sekunden")
                    print(f"\n⏱️  Timeout: Task abgebrochen nach {elapsed_time:.1f}s")
                    return False

                # Schritt Nummer
                self.task_steps += 1
                print(f"\n{'─' * 70}")
                print(f"🔄 Schritt {self.task_steps}/{config.MAX_TASK_STEPS}")
                print(f"{'─' * 70}")

                # 1. Screenshot erstellen
                print("📸 Erstelle Screenshot...")
                base64_image = self.screenshot_handler.capture_and_encode()

                if not base64_image:
                    logger.error("Screenshot fehlgeschlagen")
                    print("❌ Screenshot Fehler")
                    return False

                screenshot_size = len(base64_image)
                print(f"✓ Screenshot: {screenshot_size} bytes")

                # Optional: Screenshot speichern für Debugging
                if logger.level == logging.DEBUG:
                    filename = f"debug_step_{self.task_steps}.jpg"
                    self.screenshot_handler.save_screenshot(filename)
                    logger.debug(f"Screenshot gespeichert: {filename}")

                # 2. Groq nach nächster Aktion fragen
                print("🤖 Frage Groq AI...")
                action = self.groq_handler.get_next_action(
                    base64_image=base64_image,
                    user_task=task,
                    context=context
                )

                if not action:
                    logger.error("Keine Action von Groq erhalten")
                    print("❌ AI Antwort fehlgeschlagen")
                    return False

                # 3. Action anzeigen
                print(f"\n💭 AI Reasoning: {action['reasoning']}")
                print(f"🎯 Action: {action['action']}")
                print(f"📊 Konfidenz: {action['confidence']:.2%}")

                # 4. Prüfe ob Task abgeschlossen
                if action['action'] == 'done':
                    success_message = action['parameters'].get('message', 'Task abgeschlossen')
                    print(f"\n✅ {success_message}")
                    self._print_summary(success=True)
                    return True

                # 5. Validiere Action
                if not self.groq_handler.validate_action(action):
                    logger.warning("Action Validierung fehlgeschlagen")
                    print("⚠️  Action ungültig, überspringe...")
                    context = f"Letzte Action war ungültig. Versuche es anders."
                    continue

                # 6. Führe Action aus
                print(f"⚙️  Führe aus: {action['action']} {action['parameters']}")
                success = self.action_executor.execute_action(action)

                if success:
                    print("✓ Action erfolgreich")
                    context = f"Letzte Action ({action['action']}) war erfolgreich"
                else:
                    print("✗ Action fehlgeschlagen")
                    context = f"Letzte Action ({action['action']}) ist fehlgeschlagen"

                # Kurze Pause zwischen Schritten
                time.sleep(0.5)

            # Max Steps erreicht
            if self.task_steps >= config.MAX_TASK_STEPS:
                logger.warning(f"Maximale Schrittanzahl erreicht: {config.MAX_TASK_STEPS}")
                print(f"\n⚠️  Maximale Schritte ({config.MAX_TASK_STEPS}) erreicht")
                self._print_summary(success=False)
                return False

        except KeyboardInterrupt:
            print("\n\n⏸️  Task vom Benutzer abgebrochen")
            self._print_summary(success=False)
            return False

        except Exception as e:
            logger.error(f"Fehler bei Task Ausführung: {e}", exc_info=True)
            print(f"\n❌ Fehler: {e}")
            self._print_summary(success=False)
            return False

        return False

    def _print_summary(self, success: bool):
        """Druckt Zusammenfassung nach Task"""
        elapsed_time = time.time() - self.task_start_time

        print("\n" + "=" * 70)
        print("📊 ZUSAMMENFASSUNG")
        print("=" * 70)
        print(f"Task: {self.current_task}")
        print(f"Status: {'✅ Erfolgreich' if success else '❌ Fehlgeschlagen'}")
        print(f"Schritte: {self.task_steps}")
        print(f"Dauer: {elapsed_time:.1f}s")
        print(f"Durchschn. Zeit/Schritt: {elapsed_time / max(self.task_steps, 1):.1f}s")

        # Executor Stats
        executor_stats = self.action_executor.get_stats()
        print(f"Aktionen gesamt: {executor_stats['total_actions']}")
        print(f"Fehlerrate: {executor_stats['failed_actions']}/{executor_stats['total_actions']}")

        # Groq Stats
        groq_stats = self.groq_handler.get_stats()
        print(f"API Requests: {groq_stats['request_count']}")

        print("=" * 70 + "\n")

    def interactive_mode(self):
        """Interaktiver Modus - Aufgaben von stdin"""
        print("\n" + "=" * 70)
        print("🎮 DESKTOP CONTROLLER - INTERAKTIVER MODUS")
        print("=" * 70)
        print("Gib Aufgaben ein, die ausgeführt werden sollen.")
        print("Beispiel: 'Öffne Firefox und suche nach Groq AI'")
        print("Befehle: 'exit' oder 'quit' zum Beenden")
        print("=" * 70 + "\n")

        while True:
            try:
                task = input("📝 Task eingeben: ").strip()

                if not task:
                    continue

                if task.lower() in ['exit', 'quit', 'q']:
                    print("👋 Auf Wiedersehen!")
                    break

                # Führe Task aus
                self.execute_task(task)

            except KeyboardInterrupt:
                print("\n\n👋 Auf Wiedersehen!")
                break
            except EOFError:
                break

    def single_task_mode(self, task: str):
        """Führt eine einzelne Aufgabe aus und beendet dann"""
        success = self.execute_task(task)
        sys.exit(0 if success else 1)


def setup_logging(verbose: bool = False):
    """Konfiguriert Logging"""
    log_level = logging.DEBUG if verbose else getattr(logging, config.LOG_LEVEL)

    logging.basicConfig(
        level=log_level,
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(
        description="Desktop Controller mit Groq Vision AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Beispiele:
  %(prog)s --task "Öffne Firefox und suche nach Groq AI"
  %(prog)s --interactive
  %(prog)s --verbose --task "Erstelle neue Textdatei"

Umgebungsvariablen:
  GROQ_API_KEY    Groq API Schlüssel (erforderlich)
        """
    )

    parser.add_argument(
        '--task', '-t',
        type=str,
        help='Aufgabe die ausgeführt werden soll'
    )

    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interaktiver Modus (Aufgaben von stdin)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Ausführliche Ausgabe (DEBUG Level)'
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test-Modus (prüft Konfiguration)'
    )

    args = parser.parse_args()

    # Setup Logging
    setup_logging(args.verbose)

    # Banner
    print("\n" + "=" * 70)
    print("🤖 DESKTOP CONTROLLER MIT GROQ VISION AI")
    print("=" * 70)
    print(f"Version: 1.0.0")
    print(f"Modell: {config.GROQ_MODEL}")
    print(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")

    # Validiere Konfiguration
    if not config.validate_config():
        logger.error("Konfiguration ungültig")
        sys.exit(1)

    # Test Modus
    if args.test:
        print("🧪 Test-Modus")
        print("-" * 70)

        controller = DesktopController()

        # Screen Info
        width, height = controller.screenshot_handler.get_screen_size()
        print(f"✓ Bildschirm: {width}x{height}")

        # Screenshot Test
        screenshot = controller.screenshot_handler.capture_screenshot()
        print(f"✓ Screenshot: {screenshot.size if screenshot else 'Fehler'}")

        # Groq Test
        groq_stats = controller.groq_handler.get_stats()
        print(f"✓ Groq API: {groq_stats['api_configured']}")

        # Executor Test
        executor_stats = controller.action_executor.get_stats()
        print(f"✓ Action Executor: {executor_stats['screen_size']}")

        print("-" * 70)
        print("✅ Alle Tests bestanden!\n")
        sys.exit(0)

    # Initialisiere Controller
    controller = DesktopController()

    # Modus auswählen
    if args.task:
        # Einzelne Aufgabe
        controller.single_task_mode(args.task)
    elif args.interactive:
        # Interaktiver Modus
        controller.interactive_mode()
    else:
        # Keine Argumente - zeige Hilfe
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
