"""
Groq Handler
Verwaltet die Kommunikation mit der Groq Vision API
"""

import json
import logging
import requests
from typing import Dict, Optional, List
import time

import config

logger = logging.getLogger(__name__)


class GroqHandler:
    """Verwaltet Groq API Anfragen und Antworten"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GROQ_API_KEY
        self.model = config.GROQ_MODEL
        self.endpoint = config.GROQ_API_ENDPOINT
        self.conversation_history = []
        self.request_count = 0

        if not self.api_key:
            raise ValueError("Groq API Key ist erforderlich!")

    def create_vision_message(self, base64_image: str, user_task: str, context: str = None) -> List[Dict]:
        """
        Erstellt eine Nachricht mit Bild für die Vision API

        Args:
            base64_image: Base64-encoded Screenshot
            user_task: Benutzeraufgabe
            context: Zusätzlicher Kontext (optional)

        Returns:
            Message List für API Request
        """
        # User Content mit Bild und Text
        content = [
            {
                "type": "text",
                "text": f"Benutzeraufgabe: {user_task}\n\n"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        ]

        # Füge Kontext hinzu wenn vorhanden
        if context:
            content.insert(0, {
                "type": "text",
                "text": f"Kontext: {context}\n\n"
            })

        return [
            {"role": "system", "content": config.SYSTEM_PROMPT},
            {"role": "user", "content": content}
        ]

    def get_next_action(self, base64_image: str, user_task: str,
                       context: str = None, max_retries: int = 3) -> Optional[Dict]:
        """
        Fragt Groq nach der nächsten Aktion

        Args:
            base64_image: Base64-encoded Screenshot
            user_task: Benutzeraufgabe
            context: Zusätzlicher Kontext
            max_retries: Maximale Anzahl von Wiederholungsversuchen

        Returns:
            Action Dictionary oder None bei Fehler
        """
        messages = self.create_vision_message(base64_image, user_task, context)

        for attempt in range(max_retries):
            try:
                logger.info(f"Sende Request an Groq API (Versuch {attempt + 1}/{max_retries})...")

                response = self._make_api_request(messages)

                if response:
                    self.request_count += 1
                    return response

                logger.warning(f"Versuch {attempt + 1} fehlgeschlagen")
                time.sleep(1)  # Kurze Pause vor Wiederholung

            except Exception as e:
                logger.error(f"Fehler bei API Request (Versuch {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Längere Pause bei Fehler

        logger.error("Alle Versuche fehlgeschlagen")
        return None

    def _make_api_request(self, messages: List[Dict]) -> Optional[Dict]:
        """
        Macht den eigentlichen API Request

        Args:
            messages: Message List

        Returns:
            Parsed Action Dictionary oder None
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,  # Niedrige Temperatur für konsistente Ergebnisse
            "max_tokens": 1024,
            "top_p": 1,
            "stream": False
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # Extrahiere Antwort
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                logger.debug(f"Groq Antwort: {content}")

                # Parse JSON Response
                action = self._parse_action_response(content)
                return action

            logger.error("Ungültige API Response Struktur")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP Request Fehler: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response Status: {e.response.status_code}")
                logger.error(f"Response Body: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Unerwarteter Fehler: {e}")
            return None

    def _parse_action_response(self, content: str) -> Optional[Dict]:
        """
        Parst die JSON Response von Groq

        Args:
            content: Response String

        Returns:
            Action Dictionary oder None bei Fehler
        """
        try:
            # Suche nach JSON in der Response (könnte von Text umgeben sein)
            # Versuche zuerst direktes JSON Parsing
            try:
                action = json.loads(content)
            except json.JSONDecodeError:
                # Suche nach JSON Block in Text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    action = json.loads(json_match.group())
                else:
                    logger.error(f"Kein JSON in Response gefunden: {content}")
                    return None

            # Validiere Action Format
            required_fields = ["action", "parameters", "reasoning", "confidence"]
            if not all(field in action for field in required_fields):
                logger.error(f"Fehlende Felder in Action: {action}")
                return None

            # Validiere Action Type
            if action["action"] not in config.ALLOWED_ACTIONS + ["done"]:
                logger.warning(f"Unbekannte Action: {action['action']}")

            # Set default for is_critical
            if "is_critical" not in action:
                action["is_critical"] = False

            logger.info(f"Action geparst: {action['action']} (Konfidenz: {action['confidence']})")
            logger.debug(f"Reasoning: {action['reasoning']}")

            return action

        except json.JSONDecodeError as e:
            logger.error(f"JSON Parse Fehler: {e}")
            logger.error(f"Content: {content}")
            return None
        except Exception as e:
            logger.error(f"Fehler beim Parsen: {e}")
            return None

    def validate_action(self, action: Dict) -> bool:
        """
        Validiert eine Action

        Args:
            action: Action Dictionary

        Returns:
            True wenn Action gültig ist
        """
        try:
            # Prüfe Konfidenz
            if action["confidence"] < config.CONFIDENCE_THRESHOLD:
                logger.warning(f"Konfidenz zu niedrig: {action['confidence']}")
                return False

            # Prüfe Action Type
            action_type = action["action"]
            if action_type == "done":
                return True

            if action_type not in config.ALLOWED_ACTIONS:
                logger.error(f"Action nicht erlaubt: {action_type}")
                return False

            # Prüfe Parameter
            params = action["parameters"]
            if not isinstance(params, dict):
                logger.error("Parameters müssen ein Dictionary sein")
                return False

            # Spezifische Validierung je nach Action Type
            if action_type in ["click", "double_click", "right_click", "move_mouse"]:
                if "x" not in params or "y" not in params:
                    logger.error(f"{action_type} benötigt x und y Parameter")
                    return False

            elif action_type == "type_text":
                if "text" not in params:
                    logger.error("type_text benötigt text Parameter")
                    return False

            elif action_type == "hotkey":
                if "keys" not in params:
                    logger.error("hotkey benötigt keys Parameter")
                    return False

            return True

        except Exception as e:
            logger.error(f"Fehler bei Action Validierung: {e}")
            return False

    def get_stats(self) -> Dict:
        """Gibt Statistiken zurück"""
        return {
            "request_count": self.request_count,
            "model": self.model,
            "api_configured": bool(self.api_key)
        }


def main():
    """Test-Funktion für Groq Handler"""
    logging.basicConfig(
        level=logging.DEBUG,
        format=config.LOG_FORMAT
    )

    print("Groq Handler Test")
    print("=" * 50)

    # Prüfe API Key
    if not config.GROQ_API_KEY:
        print("✗ GROQ_API_KEY nicht gesetzt!")
        print("Setze die Umgebungsvariable: export GROQ_API_KEY='your-key'")
        return

    handler = GroqHandler()
    print(f"✓ Handler initialisiert")
    print(f"  Model: {handler.model}")
    print(f"  API Key: {'*' * 20}{handler.api_key[-4:]}")

    # Test mit Dummy Screenshot
    print("\nTest Action Parsing...")
    test_response = '''
    {
        "reasoning": "Ich sehe ein Firefox Icon auf dem Desktop",
        "action": "click",
        "parameters": {"x": 100, "y": 200},
        "confidence": 0.95,
        "is_critical": false
    }
    '''

    action = handler._parse_action_response(test_response)
    if action:
        print(f"✓ Action geparst: {action}")
        is_valid = handler.validate_action(action)
        print(f"✓ Action gültig: {is_valid}")
    else:
        print("✗ Fehler beim Parsen")

    # Statistiken
    print(f"\nStatistiken: {handler.get_stats()}")


if __name__ == "__main__":
    main()
