import os
import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QComboBox, QFrame, QMessageBox,
    QInputDialog
)
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt, QThread, Signal, Slot

# Integration mit den bestehenden Core-Modulen
from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient

CONFIG_PATH = Path.home() / ".ai_codegen_pro_config.json"

def save_settings(settings):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        QMessageBox.warning(None, "Speicherfehler", f"Einstellungen konnten nicht gespeichert werden:\n{e}")

def load_settings():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

class ModelManager(QThread):
    models_fetched = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key

    def run(self):
        try:
            client = OpenRouterClient(api_key=self.api_key)
            models = client.get_available_models()
            self.models_fetched.emit(models)
        except Exception as e:
            self.error_occurred.emit(str(e))

class CodeGenerator(QThread):
    chunk_received = Signal(str)
    error_occurred = Signal(str)
    generation_finished = Signal()

    def __init__(self, api_key, model, prompt, systemprompt):
        super().__init__()
        self.api_key = api_key
        self.model = model
        self.prompt = prompt
        self.systemprompt = systemprompt

    def run(self):
        try:
            client = OpenRouterClient(api_key=self.api_key, model=self.model)
            for chunk in client.generate_code_streaming(prompt=self.prompt, systemprompt=self.systemprompt):
                self.chunk_received.emit(chunk)
            self.generation_finished.emit()
        except Exception as e:
            self.error_occurred.emit(str(e))

class ModernPromptSection(QFrame):
    """Ein wiederverwendbarer UI-Abschnitt für einen Prompt-Typ."""
    def __init__(self, label, placeholder="", height=70):
        super().__init__()
        self.setProperty("promptFrame", True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(6)
        
        label_widget = QLabel(label)
        label_widget.setObjectName("prompt_label")
        layout.addWidget(label_widget)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText(placeholder)
        self.text_edit.setFixedHeight(height)
        layout.addWidget(self.text_edit)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI CodeGen Pro")
        self.resize(800, 850)
        self.settings = load_settings()
        if self.settings.get("api_key"):
            os.environ["AICODEGEN_API_KEY"] = self.settings["api_key"]

        self.init_ui()
        self.load_stylesheet()
        self.connect_signals()
        self.load_models()

    def init_ui(self):
        central = QWidget()
        vbox = QVBoxLayout(central)
        vbox.setSpacing(15)
        vbox.setContentsMargins(20, 20, 20, 20)
        self.setCentralWidget(central)

        # Prompt Sections
        self.sys_prompt = ModernPromptSection("System-Prompt", placeholder="Rolle der KI, z.B. 'Du bist ein Python-Experte'...", height=60)
        self.regel_prompt = ModernPromptSection("Regel-Prompt", placeholder="Formatierungsregeln, z.B. 'Antworte nur mit Code'...", height=60)
        self.norm_prompt = ModernPromptSection("Benutzer-Prompt", placeholder="Deine eigentliche Aufgabe oder Frage...", height=120)
        vbox.addWidget(self.sys_prompt)
        vbox.addWidget(self.regel_prompt)
        vbox.addWidget(self.norm_prompt)

        # Steuerung
        hbox = QHBoxLayout()
        model_label = QLabel("Modell:")
        model_label.setObjectName("prompt_label")
        hbox.addWidget(model_label)
        self.model_box = QComboBox()
        hbox.addWidget(self.model_box, 1) # Stretch-Faktor
        hbox.addSpacing(20)
        self.send_btn = QPushButton("Senden")
        self.send_btn.setObjectName("send_btn")
        self.clear_btn = QPushButton("Löschen")
        hbox.addWidget(self.send_btn)
        hbox.addWidget(self.clear_btn)
        vbox.addLayout(hbox)

        # Output
        output_label = QLabel("Antwort:")
        output_label.setObjectName("prompt_label")
        vbox.addWidget(output_label)
        self.output = QTextEdit()
        self.output.setObjectName("outputArea")
        self.output.setReadOnly(True)
        vbox.addWidget(self.output, 1) # Stretch-Faktor

    def load_stylesheet(self):
        style_path = Path(__file__).parent / "orange_dark.qss"
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Stylesheet nicht gefunden. Standard-Stil wird verwendet.")

    def connect_signals(self):
        self.send_btn.clicked.connect(self.on_send)
        self.clear_btn.clicked.connect(self.on_clear)

    def load_models(self):
        api_key = os.environ.get("AICODEGEN_API_KEY")
        if not api_key:
            self.prompt_for_api_key()
            api_key = os.environ.get("AICODEGEN_API_KEY")
        
        if api_key:
            self.model_manager = ModelManager(api_key)
            self.model_manager.models_fetched.connect(self.on_models_loaded)
            self.model_manager.error_occurred.connect(self.on_model_load_error)
            self.model_manager.start()

    @Slot(list)
    def on_models_loaded(self, models):
        self.model_box.clear()
        sorted_models = sorted(models, key=lambda m: m.get('name', ''))
        for model in sorted_models:
            self.model_box.addItem(model.get('name', model['id']), model['id'])

    @Slot(str)
    def on_model_load_error(self, error_msg):
        QMessageBox.critical(self, "Modell-Fehler", f"Modelle konnten nicht geladen werden:\n{error_msg}\n\nBitte prüfe deinen API-Key.")
        self.prompt_for_api_key()

    def on_send(self):
        user_prompt = self.norm_prompt.text_edit.toPlainText().strip()
        model_id = self.model_box.currentData()
        api_key = os.environ.get("AICODEGEN_API_KEY")

        if not all([user_prompt, model_id, api_key]):
            QMessageBox.warning(self, "Eingabe fehlt", "Bitte Prompt, Modell und API-Key überprüfen.")
            return

        self.send_btn.setEnabled(False)
        self.output.clear()

        sys_prompt = self.sys_prompt.text_edit.toPlainText().strip()
        regel_prompt = self.regel_prompt.text_edit.toPlainText().strip()
        
        full_system_prompt = sys_prompt
        if regel_prompt:
            full_system_prompt += "\n\n--- ZUSÄTZLICHE REGELN ---\n" + regel_prompt

        self.generator = CodeGenerator(api_key, model_id, user_prompt, full_system_prompt)
        self.generator.chunk_received.connect(self.append_chunk)
        self.generator.error_occurred.connect(self.on_generation_error)
        self.generator.generation_finished.connect(lambda: self.send_btn.setEnabled(True))
        self.generator.start()
    
    @Slot(str)
    def append_chunk(self, chunk):
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(chunk)
        self.output.ensureCursorVisible()

    @Slot(str)
    def on_generation_error(self, error_msg):
        self.output.setHtml(f"<font color='red'><b>Fehler bei der Generierung:</b><br>{error_msg}</font>")
        self.send_btn.setEnabled(True)

    def on_clear(self):
        self.sys_prompt.text_edit.clear()
        self.regel_prompt.text_edit.clear()
        self.norm_prompt.text_edit.clear()
        self.output.clear()

    def prompt_for_api_key(self):
        key, ok = QInputDialog.getText(self, "API-Key benötigt", "Bitte gib deinen OpenRouter API-Key ein:", text=self.settings.get("api_key", ""))
        if ok and key:
            self.settings["api_key"] = key
            save_settings(self.settings)
            os.environ["AICODEGEN_API_KEY"] = key
            self.load_models()

def start_gui():
    app = QApplication(sys.argv)
    # Eine passende Schriftart für Linux Mint, falls Fira Sans nicht verfügbar ist
    font = QFont("Cantarell", 11) 
    app.setFont(font)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
