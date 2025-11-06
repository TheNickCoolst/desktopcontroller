#!/usr/bin/env python3
"""
Desktop Controller GUI Launcher
Graphische Oberfläche zum Starten des Desktop Controllers
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import os
import sys
from pathlib import Path


class DesktopControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Desktop Controller - Groq Vision AI")
        self.root.geometry("700x600")
        self.root.resizable(True, True)

        # Set minimum size
        self.root.minsize(600, 500)

        # Process handle
        self.process = None
        self.is_running = False

        # Prüfe ob im richtigen Verzeichnis
        self.check_environment()

        # Setup GUI
        self.setup_gui()

        # Center window
        self.center_window()

    def check_environment(self):
        """Prüft ob die Umgebung korrekt ist"""
        # Prüfe ob main.py existiert
        if not os.path.exists("main.py"):
            messagebox.showerror(
                "Fehler",
                "main.py nicht gefunden!\n\n"
                "Bitte starte den Launcher aus dem Desktop Controller Verzeichnis."
            )
            sys.exit(1)

        # Prüfe ob .env existiert
        if not os.path.exists(".env"):
            if os.path.exists(".env.example"):
                response = messagebox.askyesno(
                    "Konfiguration fehlt",
                    ".env Datei nicht gefunden!\n\n"
                    "Möchtest du die .env.example kopieren und bearbeiten?"
                )
                if response:
                    import shutil
                    shutil.copy(".env.example", ".env")
                    messagebox.showinfo(
                        "Info",
                        "Die .env Datei wurde erstellt.\n\n"
                        "Bitte füge deinen GROQ_API_KEY ein und starte den Launcher neu."
                    )
                    # Öffne .env im Standard-Editor
                    if sys.platform == "win32":
                        os.startfile(".env")
                    elif sys.platform == "darwin":
                        subprocess.run(["open", ".env"])
                    else:
                        subprocess.run(["xdg-open", ".env"])
                    sys.exit(0)
            else:
                messagebox.showwarning(
                    "Warnung",
                    ".env Datei nicht gefunden!\n\n"
                    "Die API-Aufrufe funktionieren möglicherweise nicht."
                )

    def center_window(self):
        """Zentriert das Fenster auf dem Bildschirm"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def setup_gui(self):
        """Erstellt die GUI-Elemente"""
        # Header
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        title_label = tk.Label(
            header_frame,
            text="🤖 Desktop Controller",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=10)

        subtitle_label = tk.Label(
            header_frame,
            text="mit Groq Vision AI",
            font=("Arial", 12),
            bg="#2c3e50",
            fg="#ecf0f1"
        )
        subtitle_label.pack()

        # Main content area
        content_frame = tk.Frame(self.root, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Mode selection
        mode_frame = tk.LabelFrame(content_frame, text="Modus auswählen", padx=10, pady=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.mode_var = tk.StringVar(value="interactive")

        tk.Radiobutton(
            mode_frame,
            text="🎮 Interaktiver Modus (mehrere Aufgaben)",
            variable=self.mode_var,
            value="interactive",
            command=self.on_mode_change
        ).pack(anchor=tk.W, pady=2)

        tk.Radiobutton(
            mode_frame,
            text="🎯 Einzelne Aufgabe",
            variable=self.mode_var,
            value="single",
            command=self.on_mode_change
        ).pack(anchor=tk.W, pady=2)

        tk.Radiobutton(
            mode_frame,
            text="🧪 Test-Modus (Konfiguration prüfen)",
            variable=self.mode_var,
            value="test",
            command=self.on_mode_change
        ).pack(anchor=tk.W, pady=2)

        # Task input frame
        self.task_frame = tk.LabelFrame(content_frame, text="Aufgabe eingeben", padx=10, pady=10)
        self.task_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(
            self.task_frame,
            text="Beschreibe was der Desktop Controller tun soll:",
            font=("Arial", 9)
        ).pack(anchor=tk.W, pady=(0, 5))

        self.task_entry = tk.Entry(self.task_frame, font=("Arial", 10))
        self.task_entry.pack(fill=tk.X, pady=(0, 5))
        self.task_entry.insert(0, "Öffne Firefox und suche nach Groq AI")

        # Beispiele
        examples_text = "Beispiele:\n" \
                       "• Öffne den Datei-Manager\n" \
                       "• Erstelle eine neue Textdatei namens test.txt\n" \
                       "• Mache einen Screenshot"
        tk.Label(
            self.task_frame,
            text=examples_text,
            font=("Arial", 8),
            fg="gray",
            justify=tk.LEFT
        ).pack(anchor=tk.W)

        # Control buttons
        button_frame = tk.Frame(content_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        self.start_button = tk.Button(
            button_frame,
            text="▶ Start",
            command=self.start_controller,
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))

        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop",
            command=self.stop_controller,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20,
            pady=8,
            state=tk.DISABLED,
            cursor="hand2"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(
            button_frame,
            text="🗑 Log löschen",
            command=self.clear_log,
            font=("Arial", 9),
            padx=15,
            pady=8,
            cursor="hand2"
        )
        self.clear_button.pack(side=tk.RIGHT)

        # Status
        self.status_label = tk.Label(
            content_frame,
            text="⚫ Bereit",
            font=("Arial", 10, "bold"),
            fg="#7f8c8d"
        )
        self.status_label.pack(anchor=tk.W, pady=(0, 5))

        # Log output
        log_frame = tk.LabelFrame(content_frame, text="Ausgabe / Log", padx=5, pady=5)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#2c3e50",
            fg="#ecf0f1",
            insertbackground="white"
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Initial mode setup
        self.on_mode_change()

        # Log initial message
        self.log("Desktop Controller GUI gestartet")
        self.log(f"Arbeitsverzeichnis: {os.getcwd()}")
        self.log("Bereit zum Starten...")

    def on_mode_change(self):
        """Handler wenn Modus geändert wird"""
        mode = self.mode_var.get()

        if mode == "single":
            self.task_frame.pack(fill=tk.X, pady=(0, 10))
            self.task_entry.config(state=tk.NORMAL)
        elif mode == "interactive":
            self.task_frame.pack_forget()
        elif mode == "test":
            self.task_frame.pack_forget()

    def log(self, message):
        """Schreibt eine Nachricht in den Log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.update()

    def clear_log(self):
        """Löscht den Log"""
        self.log_text.delete(1.0, tk.END)

    def start_controller(self):
        """Startet den Desktop Controller"""
        if self.is_running:
            messagebox.showwarning("Warnung", "Der Controller läuft bereits!")
            return

        mode = self.mode_var.get()

        # Build command
        python_cmd = sys.executable
        cmd = [python_cmd, "main.py"]

        if mode == "interactive":
            cmd.append("--interactive")
        elif mode == "single":
            task = self.task_entry.get().strip()
            if not task:
                messagebox.showwarning("Warnung", "Bitte gib eine Aufgabe ein!")
                return
            cmd.extend(["--task", task])
        elif mode == "test":
            cmd.append("--test")

        # Log command
        self.log("\n" + "=" * 70)
        self.log(f"Starte: {' '.join(cmd)}")
        self.log("=" * 70 + "\n")

        # Update UI
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_label.config(text="🟢 Läuft...", fg="#27ae60")

        # Start process in thread
        thread = threading.Thread(target=self.run_process, args=(cmd,), daemon=True)
        thread.start()

    def run_process(self, cmd):
        """Führt den Prozess aus (in separatem Thread)"""
        try:
            # Windows: CREATE_NO_WINDOW flag
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                startupinfo=startupinfo
            )

            # Read output line by line
            for line in self.process.stdout:
                if line:
                    self.log(line.rstrip())

            # Wait for completion
            self.process.wait()

            # Log completion
            if self.process.returncode == 0:
                self.log("\n✅ Erfolgreich abgeschlossen")
            else:
                self.log(f"\n❌ Beendet mit Fehlercode {self.process.returncode}")

        except Exception as e:
            self.log(f"\n❌ Fehler: {e}")

        finally:
            self.is_running = False
            self.root.after(0, self.on_process_finished)

    def stop_controller(self):
        """Stoppt den laufenden Controller"""
        if self.process and self.is_running:
            self.log("\n⏹ Stoppe Controller...")
            self.process.terminate()

            # Give it time to terminate gracefully
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.log("⚠️ Forciere Beendigung...")
                self.process.kill()

            self.log("✓ Controller gestoppt")
            self.on_process_finished()

    def on_process_finished(self):
        """Callback wenn Prozess beendet ist"""
        self.is_running = False
        self.process = None
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_label.config(text="⚫ Bereit", fg="#7f8c8d")


def main():
    """Hauptfunktion"""
    root = tk.Tk()
    app = DesktopControllerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
