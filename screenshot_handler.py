"""
Screenshot Handler
Verwaltet Screenshot-Erstellung und Base64-Encoding für Groq Vision API
"""

import base64
import io
import time
from typing import Tuple, Optional
from PIL import Image, ImageGrab
import logging

import config

logger = logging.getLogger(__name__)


class ScreenshotHandler:
    """Verwaltet Screenshot-Erfassung und -Verarbeitung"""

    def __init__(self):
        self.last_screenshot_time = 0
        self.last_screenshot = None
        self.screenshot_count = 0

    def capture_screenshot(self) -> Optional[Image.Image]:
        """
        Erstellt einen Screenshot des gesamten Bildschirms

        Returns:
            PIL Image oder None bei Fehler
        """
        try:
            screenshot = ImageGrab.grab()
            self.screenshot_count += 1
            self.last_screenshot = screenshot
            self.last_screenshot_time = time.time()

            logger.debug(f"Screenshot #{self.screenshot_count} erstellt: {screenshot.size}")
            return screenshot

        except Exception as e:
            logger.error(f"Fehler beim Erstellen des Screenshots: {e}")
            return None

    def resize_screenshot(self, image: Image.Image, max_size: Tuple[int, int] = None) -> Image.Image:
        """
        Verkleinert das Bild wenn nötig

        Args:
            image: PIL Image
            max_size: Maximale Größe (width, height)

        Returns:
            Verkleinertes PIL Image
        """
        if max_size is None:
            max_size = config.SCREENSHOT_MAX_SIZE

        # Berechne neues Seitenverhältnis
        if image.width > max_size[0] or image.height > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            logger.debug(f"Screenshot verkleinert auf: {image.size}")

        return image

    def image_to_base64(self, image: Image.Image, quality: int = None) -> str:
        """
        Konvertiert PIL Image zu Base64 String

        Args:
            image: PIL Image
            quality: JPEG Qualität (0-100)

        Returns:
            Base64 encoded String
        """
        if quality is None:
            quality = config.SCREENSHOT_QUALITY

        try:
            # Konvertiere zu RGB falls nötig (für JPEG)
            if image.mode in ('RGBA', 'P'):
                rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                rgb_image.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = rgb_image

            # Speichere als JPEG in BytesIO
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=quality, optimize=True)
            buffer.seek(0)

            # Encode zu Base64
            base64_string = base64.b64encode(buffer.read()).decode('utf-8')

            logger.debug(f"Base64 String Länge: {len(base64_string)} Zeichen")
            return base64_string

        except Exception as e:
            logger.error(f"Fehler beim Base64 Encoding: {e}")
            raise

    def capture_and_encode(self) -> Optional[str]:
        """
        Erstellt Screenshot und gibt Base64 String zurück

        Returns:
            Base64 encoded Screenshot oder None bei Fehler
        """
        screenshot = self.capture_screenshot()
        if screenshot is None:
            return None

        # Verkleinere falls nötig
        screenshot = self.resize_screenshot(screenshot)

        # Encode zu Base64
        try:
            base64_string = self.image_to_base64(screenshot)
            return base64_string
        except Exception as e:
            logger.error(f"Fehler beim Encoding: {e}")
            return None

    def save_screenshot(self, filename: str, image: Image.Image = None) -> bool:
        """
        Speichert Screenshot als Datei

        Args:
            filename: Pfad zur Zieldatei
            image: PIL Image (verwendet letzten Screenshot wenn None)

        Returns:
            True bei Erfolg, False bei Fehler
        """
        if image is None:
            image = self.last_screenshot

        if image is None:
            logger.error("Kein Screenshot zum Speichern vorhanden")
            return False

        try:
            image.save(filename)
            logger.info(f"Screenshot gespeichert: {filename}")
            return True
        except Exception as e:
            logger.error(f"Fehler beim Speichern: {e}")
            return False

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Gibt die aktuelle Bildschirmauflösung zurück

        Returns:
            (width, height) Tupel
        """
        screenshot = ImageGrab.grab()
        return screenshot.size

    def should_capture(self) -> bool:
        """
        Prüft ob genug Zeit seit dem letzten Screenshot vergangen ist

        Returns:
            True wenn ein neuer Screenshot erstellt werden sollte
        """
        time_since_last = time.time() - self.last_screenshot_time
        return time_since_last >= config.SCREENSHOT_INTERVAL

    def annotate_screenshot(self, image: Image.Image, x: int, y: int,
                           color: str = 'red', radius: int = 10) -> Image.Image:
        """
        Markiert eine Position auf dem Screenshot (für Debugging)

        Args:
            image: PIL Image
            x, y: Koordinaten
            color: Farbe der Markierung
            radius: Radius des Markers

        Returns:
            Annotiertes PIL Image
        """
        from PIL import ImageDraw

        annotated = image.copy()
        draw = ImageDraw.Draw(annotated)

        # Zeichne Kreis
        draw.ellipse(
            [x - radius, y - radius, x + radius, y + radius],
            outline=color,
            width=3
        )

        # Zeichne Fadenkreuz
        draw.line([x - radius - 5, y, x + radius + 5, y], fill=color, width=2)
        draw.line([x, y - radius - 5, x, y + radius + 5], fill=color, width=2)

        return annotated


def main():
    """Test-Funktion für Screenshot Handler"""
    logging.basicConfig(
        level=logging.DEBUG,
        format=config.LOG_FORMAT
    )

    print("Screenshot Handler Test")
    print("=" * 50)

    handler = ScreenshotHandler()

    # Screen Size
    width, height = handler.get_screen_size()
    print(f"Bildschirmgröße: {width}x{height}")

    # Erstelle Screenshot
    print("\nErstelle Screenshot...")
    screenshot = handler.capture_screenshot()

    if screenshot:
        print(f"✓ Screenshot erstellt: {screenshot.size}")

        # Speichere Screenshot
        handler.save_screenshot("test_screenshot.jpg")
        print("✓ Screenshot gespeichert: test_screenshot.jpg")

        # Base64 Encoding
        print("\nKonvertiere zu Base64...")
        base64_str = handler.image_to_base64(screenshot)
        print(f"✓ Base64 String: {len(base64_str)} Zeichen")
        print(f"  Erste 100 Zeichen: {base64_str[:100]}...")

        # Test annotate
        annotated = handler.annotate_screenshot(screenshot, width // 2, height // 2)
        handler.save_screenshot("test_annotated.jpg", annotated)
        print("✓ Annotierter Screenshot gespeichert: test_annotated.jpg")
    else:
        print("✗ Fehler beim Erstellen des Screenshots")


if __name__ == "__main__":
    main()
