"""
Action Executor
Führt Desktop-Aktionen mit PyAutoGUI aus
"""

import logging
import time
import pyautogui
from typing import Dict, Any, Optional, Tuple
import sys

import config

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Führt Desktop-Aktionen aus"""

    def __init__(self):
        # Konfiguriere PyAutoGUI
        pyautogui.PAUSE = config.PYAUTOGUI_PAUSE
        pyautogui.FAILSAFE = config.PYAUTOGUI_FAILSAFE

        self.action_count = 0
        self.failed_actions = 0
        self.screen_width, self.screen_height = pyautogui.size()

        logger.info(f"ActionExecutor initialisiert (Bildschirm: {self.screen_width}x{self.screen_height})")

    def execute_action(self, action: Dict) -> bool:
        """
        Führt eine Action aus

        Args:
            action: Action Dictionary mit 'action' und 'parameters'

        Returns:
            True bei Erfolg, False bei Fehler
        """
        action_type = action.get("action")
        parameters = action.get("parameters", {})
        is_critical = action.get("is_critical", False)

        logger.info(f"Führe Action aus: {action_type} {parameters}")

        # Sicherheitsabfrage für kritische Aktionen
        if is_critical and config.SAFETY_CHECK_ENABLED:
            if not self._confirm_critical_action(action):
                logger.warning("Kritische Action vom Benutzer abgelehnt")
                return False

        # Validiere Koordinaten falls nötig
        if action_type in ["click", "double_click", "right_click", "move_mouse"]:
            x, y = parameters.get("x"), parameters.get("y")
            if not self._validate_coordinates(x, y):
                logger.error(f"Ungültige Koordinaten: ({x}, {y})")
                self.failed_actions += 1
                return False

        # Führe Action aus
        try:
            success = self._execute_action_internal(action_type, parameters)

            if success:
                self.action_count += 1
                logger.info(f"✓ Action erfolgreich: {action_type}")
            else:
                self.failed_actions += 1
                logger.error(f"✗ Action fehlgeschlagen: {action_type}")

            return success

        except Exception as e:
            logger.error(f"Fehler bei Action Ausführung: {e}")
            self.failed_actions += 1
            return False

    def _execute_action_internal(self, action_type: str, parameters: Dict) -> bool:
        """
        Interne Methode zum Ausführen der Action

        Args:
            action_type: Action Type
            parameters: Parameter Dictionary

        Returns:
            True bei Erfolg
        """
        try:
            if action_type == "click":
                x, y = parameters["x"], parameters["y"]
                pyautogui.click(x, y, duration=config.MOUSE_MOVE_DURATION)
                return True

            elif action_type == "double_click":
                x, y = parameters["x"], parameters["y"]
                pyautogui.doubleClick(x, y, duration=config.MOUSE_MOVE_DURATION)
                return True

            elif action_type == "right_click":
                x, y = parameters["x"], parameters["y"]
                pyautogui.rightClick(x, y, duration=config.MOUSE_MOVE_DURATION)
                return True

            elif action_type == "move_mouse":
                x, y = parameters["x"], parameters["y"]
                pyautogui.moveTo(x, y, duration=config.MOUSE_MOVE_DURATION)
                return True

            elif action_type == "type_text":
                text = parameters["text"]
                pyautogui.write(text, interval=config.TYPING_INTERVAL)
                return True

            elif action_type == "press_key":
                key = parameters["key"]
                pyautogui.press(key)
                return True

            elif action_type == "scroll":
                amount = parameters.get("amount", 0)
                # PyAutoGUI scroll: positive = up, negative = down
                # Unsere Konvention: positive = down, negative = up
                pyautogui.scroll(-amount)
                return True

            elif action_type == "hotkey":
                keys = parameters["keys"]
                if isinstance(keys, str):
                    keys = [keys]

                # Prüfe ob Hotkey erlaubt ist
                if not self._is_hotkey_allowed(keys):
                    logger.error(f"Hotkey nicht erlaubt: {keys}")
                    return False

                pyautogui.hotkey(*keys)
                return True

            elif action_type == "wait":
                seconds = parameters.get("seconds", 1.0)
                time.sleep(seconds)
                return True

            elif action_type == "done":
                logger.info("Task als abgeschlossen markiert")
                return True

            else:
                logger.error(f"Unbekannte Action: {action_type}")
                return False

        except Exception as e:
            logger.error(f"Fehler bei {action_type}: {e}")
            return False

    def _validate_coordinates(self, x: Any, y: Any) -> bool:
        """
        Validiert Koordinaten

        Args:
            x, y: Koordinaten

        Returns:
            True wenn gültig
        """
        try:
            x, y = int(x), int(y)
            return (0 <= x < self.screen_width and
                    0 <= y < self.screen_height)
        except (TypeError, ValueError):
            return False

    def _is_hotkey_allowed(self, keys: list) -> bool:
        """
        Prüft ob eine Tastenkombination erlaubt ist

        Args:
            keys: Liste von Tasten

        Returns:
            True wenn erlaubt
        """
        # Konvertiere zu lowercase für Vergleich
        keys_lower = [k.lower() for k in keys]

        for allowed in config.ALLOWED_HOTKEYS:
            allowed_lower = [k.lower() for k in allowed]
            if keys_lower == allowed_lower:
                return True

        logger.warning(f"Hotkey {keys} nicht in erlaubter Liste")
        return False

    def _confirm_critical_action(self, action: Dict) -> bool:
        """
        Fragt Benutzer nach Bestätigung für kritische Action

        Args:
            action: Action Dictionary

        Returns:
            True wenn bestätigt
        """
        print("\n" + "=" * 60)
        print("⚠️  KRITISCHE AKTION - BESTÄTIGUNG ERFORDERLICH")
        print("=" * 60)
        print(f"Action: {action['action']}")
        print(f"Parameter: {action['parameters']}")
        print(f"Begründung: {action['reasoning']}")
        print("-" * 60)

        try:
            response = input("Aktion ausführen? (j/n): ").strip().lower()
            return response in ['j', 'ja', 'y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return False

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Gibt aktuelle Mausposition zurück

        Returns:
            (x, y) Tupel
        """
        return pyautogui.position()

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Gibt Bildschirmgröße zurück

        Returns:
            (width, height) Tupel
        """
        return self.screen_width, self.screen_height

    def screenshot_test(self) -> bool:
        """
        Testet ob Screenshots funktionieren

        Returns:
            True bei Erfolg
        """
        try:
            screenshot = pyautogui.screenshot()
            return screenshot is not None
        except Exception as e:
            logger.error(f"Screenshot Test fehlgeschlagen: {e}")
            return False

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        return {
            "total_actions": self.action_count,
            "failed_actions": self.failed_actions,
            "success_rate": (self.action_count / max(self.action_count + self.failed_actions, 1)) * 100,
            "screen_size": (self.screen_width, self.screen_height),
            "failsafe_enabled": pyautogui.FAILSAFE
        }


def main():
    """Test-Funktion für Action Executor"""
    logging.basicConfig(
        level=logging.DEBUG,
        format=config.LOG_FORMAT
    )

    print("Action Executor Test")
    print("=" * 50)

    executor = ActionExecutor()

    # Screen Info
    width, height = executor.get_screen_size()
    print(f"Bildschirmgröße: {width}x{height}")

    # Mouse Position
    x, y = executor.get_mouse_position()
    print(f"Mausposition: ({x}, {y})")

    # Screenshot Test
    can_screenshot = executor.screenshot_test()
    print(f"Screenshot funktioniert: {can_screenshot}")

    # Test Actions
    print("\n" + "=" * 50)
    print("Test Actions (3 Sekunden Pause)...")
    print("=" * 50)
    time.sleep(3)

    test_actions = [
        {
            "action": "move_mouse",
            "parameters": {"x": width // 2, "y": height // 2},
            "reasoning": "Bewege Maus zur Bildschirmmitte",
            "confidence": 1.0,
            "is_critical": False
        },
        {
            "action": "wait",
            "parameters": {"seconds": 1},
            "reasoning": "Warte kurz",
            "confidence": 1.0,
            "is_critical": False
        }
    ]

    for action in test_actions:
        print(f"\nFühre aus: {action['action']}")
        success = executor.execute_action(action)
        print(f"Result: {'✓' if success else '✗'}")

    # Statistiken
    print("\n" + "=" * 50)
    stats = executor.get_stats()
    print("Statistiken:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
