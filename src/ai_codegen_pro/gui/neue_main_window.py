import os
import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QPushButton, QComboBox, QFileDialog, QFrame, QMessageBox,
    QSplitter, QGroupBox, QSpinBox, QSlider, QDialog, QDialogButtonBox, QInputDialog
)
from PySide6.QtGui import QAction, QTextCursor, QFont
from PySide6.QtCore import Qt, QThread, Signal, Slot

from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient

CONFIG_PATH = Path.home() / ".ai_codegen_pro_config.json"

def save_settings(settings):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

def load_settings():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
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

    def __init__(self, model, prompt, system_prompt, api_key, temperature, max_tokens):
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens

    def run(self):
        try:
            client = OpenRouterClient(api_key=self.api_key, model=self.model)
            for chunk in client.generate_code_streaming(
                prompt=self.prompt,
                systemprompt=self.system_prompt,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            ):
                self.chunk_received.emit(chunk)
        except Exception as e:
            self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI CodeGen Pro")
        self.resize(1100, 800)
        self.settings = load_settings()
        if self.settings.get("api_key"):
            os.environ["AICODEGEN_API_KEY"] = self.settings["api_key"]

        self.create_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Main Interaction Area
        chat_area = QWidget()
        chat_layout = QVBoxLayout(chat_area)
        
        splitter = QSplitter(Qt.Vertical)
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Beschreibe hier, was generiert werden soll...")
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        
        splitter.addWidget(self.prompt_input)
        splitter.addWidget(self.result_output)
        splitter.setSizes([200, 500])
        chat_layout.addWidget(splitter)

        self.generate_btn = QPushButton("Generieren")
        self.generate_btn.setObjectName("generate_btn")
        chat_layout.addWidget(self.generate_btn)
        
        main_layout.addWidget(chat_area, 3) # Takes 3/4 of the space

        # Settings Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar_layout = QVBoxLayout(sidebar)
        
        sidebar_layout.addWidget(QLabel("Model & Parameter"))
        self.model_combo = QComboBox()
        sidebar_layout.addWidget(self.model_combo)

        self.refresh_btn = QPushButton("Modelle aktualisieren")
        sidebar_layout.addWidget(self.refresh_btn)

        # Temperature
        temp_group = QGroupBox("Temperatur")
        temp_layout = QHBoxLayout(temp_group)
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        self.temp_label = QLabel(f"{self.temp_slider.value()/100:.2f}")
        temp_layout.addWidget(self.temp_slider)
        temp_layout.addWidget(self.temp_label)
        self.temp_slider.valueChanged.connect(lambda v: self.temp_label.setText(f"{v/100:.2f}"))
        sidebar_layout.addWidget(temp_group)

        # Max Tokens
        tokens_group = QGroupBox("Max Tokens")
        tokens_layout = QVBoxLayout(tokens_group)
        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(256, 16384)
        self.max_tokens_spin.setValue(4096)
        self.max_tokens_spin.setSingleStep(128)
        tokens_layout.addWidget(self.max_tokens_spin)
        sidebar_layout.addWidget(tokens_group)
        
        sidebar_layout.addStretch()

        self.save_btn = QPushButton("Antwort speichern")
        sidebar_layout.addWidget(self.save_btn)
        
        main_layout.addWidget(sidebar, 1) # Takes 1/4 of the space

        self.set_style()
        self.connect_signals()
        self.load_models()

    def set_style(self):
        style_path = Path(__file__).parent / "minimalist_dark.qss"
        if style_path.exists():
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def connect_signals(self):
        self.generate_btn.clicked.connect(self.run_generation)
        self.refresh_btn.clicked.connect(self.load_models)
        self.save_btn.clicked.connect(self.save_result)
    
    def create_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("Datei")
        settings_action = QAction("API-Key setzen...", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)

    def load_models(self):
        api_key = os.environ.get("AICODEGEN_API_KEY")
        if not api_key:
            QMessageBox.warning(self, "API-Key fehlt", "Bitte setze deinen OpenRouter API-Key im Menü unter 'Datei'.")
            return
        self.model_manager = ModelManager(api_key)
        self.model_manager.models_fetched.connect(self.on_models_loaded)
        self.model_manager.error_occurred.connect(lambda e: QMessageBox.critical(self, "Fehler", f"Modelle konnten nicht geladen werden:\n{e}"))
        self.model_manager.start()

    @Slot(list)
    def on_models_loaded(self, models):
        self.model_combo.clear()
        sorted_models = sorted(models, key=lambda m: m.get('name', ''))
        for model in sorted_models:
            self.model_combo.addItem(model.get('name', model['id']), model['id'])

    def run_generation(self):
        prompt = self.prompt_input.toPlainText().strip()
        model_id = self.model_combo.currentData()
        api_key = os.environ.get("AICODEGEN_API_KEY")

        if not all([prompt, model_id, api_key]):
            QMessageBox.critical(self, "Fehler", "Prompt, Modell und API-Key müssen vorhanden sein.")
            return

        self.generate_btn.setEnabled(False)
        self.result_output.clear()
        
        self.generator = CodeGenerator(
            model=model_id,
            prompt=prompt,
            system_prompt="",
            api_key=api_key,
            temperature=self.temp_slider.value() / 100.0,
            max_tokens=self.max_tokens_spin.value()
        )
        self.generator.chunk_received.connect(self.append_chunk)
        self.generator.error_occurred.connect(self.on_generation_error)
        self.generator.finished.connect(lambda: self.generate_btn.setEnabled(True))
        self.generator.start()
    
    @Slot(str)
    def append_chunk(self, chunk):
        self.result_output.moveCursor(QTextCursor.End)
        self.result_output.insertPlainText(chunk)

    @Slot(str)
    def on_generation_error(self, msg):
        self.result_output.setPlainText(f"Ein Fehler ist aufgetreten:\n{msg}")

    def save_result(self):
        content = self.result_output.toPlainText()
        if not content.strip(): return
        path, _ = QFileDialog.getSaveFileName(self, "Speichern", "", "Python-Datei (*.py);;Textdatei (*.txt);;Alle Dateien (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
            except Exception as e:
                QMessageBox.critical(self, "Speicherfehler", str(e))

    def show_settings_dialog(self):
        api_key, ok = QInputDialog.getText(self, "API-Key", "OpenRouter API-Key eingeben:", text=self.settings.get("api_key", ""))
        if ok and api_key:
            self.settings["api_key"] = api_key
            save_settings(self.settings)
            os.environ["AICODEGEN_API_KEY"] = api_key
            self.load_models()

def start_gui():
    app = QApplication(sys.argv)
    font = QFont("Cantarell", 11) # Eine passende Schriftart für Linux Mint
    app.setFont(font)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
