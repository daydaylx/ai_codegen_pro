import os, sys, json
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox, QFileDialog, QFrame, QMessageBox, QSplitter, QGroupBox, QSpinBox, QSlider, QDialog, QDialogButtonBox, QInputDialog)
from PySide6.QtGui import QAction, QTextCursor, QFont
from PySide6.QtCore import Qt, QThread, Signal, Slot
from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient

CONFIG_PATH = Path.home() / ".ai_codegen_pro_config.json"

def save_settings(s):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f: json.dump(s, f, indent=2)
    except Exception as e: print(f"Error saving settings: {e}")

def load_settings():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f: return json.load(f)
        except: return {}
    return {}

class ModelManager(QThread):
    models_fetched, error_occurred = Signal(list), Signal(str)
    def __init__(self, key):
        super().__init__(); self.api_key = key
    def run(self):
        try: self.models_fetched.emit(OpenRouterClient(api_key=self.api_key).get_available_models())
        except Exception as e: self.error_occurred.emit(str(e))

class CodeGenerator(QThread):
    chunk_received, error_occurred = Signal(str), Signal(str)
    def __init__(self, **kwargs):
        super().__init__(); self.params = kwargs
    def run(self):
        try:
            client = OpenRouterClient(api_key=self.params['api_key'], model=self.params['model'])
            for chunk in client.generate_code_streaming(**self.params): self.chunk_received.emit(chunk)
        except Exception as e: self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI CodeGen Pro"); self.resize(1100, 800)
        self.settings = load_settings()
        if self.settings.get("api_key"): os.environ["AICODEGEN_API_KEY"] = self.settings["api_key"]
        self.create_menu()
        
        central = QWidget(); self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        chat_area = QWidget(); chat_layout = QVBoxLayout(chat_area)
        splitter = QSplitter(Qt.Vertical)
        self.prompt_input = QTextEdit(); self.prompt_input.setPlaceholderText("Beschreibe hier, was generiert werden soll...")
        self.result_output = QTextEdit(); self.result_output.setReadOnly(True)
        splitter.addWidget(self.prompt_input); splitter.addWidget(self.result_output); splitter.setSizes([200, 500])
        chat_layout.addWidget(splitter)
        self.generate_btn = QPushButton("Generieren"); self.generate_btn.setObjectName("generate_btn")
        chat_layout.addWidget(self.generate_btn)
        main_layout.addWidget(chat_area, 3)

        sidebar = QFrame(); sidebar.setObjectName("sidebar"); sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.addWidget(QLabel("Model & Parameter")); self.model_combo = QComboBox()
        sidebar_layout.addWidget(self.model_combo); self.refresh_btn = QPushButton("Modelle aktualisieren")
        sidebar_layout.addWidget(self.refresh_btn)
        
        temp_group = QGroupBox("Temperatur"); temp_layout = QHBoxLayout(temp_group)
        self.temp_slider = QSlider(Qt.Horizontal); self.temp_slider.setRange(0, 100); self.temp_slider.setValue(70)
        self.temp_label = QLabel(f"{self.temp_slider.value()/100:.2f}")
        temp_layout.addWidget(self.temp_slider); temp_layout.addWidget(self.temp_label)
        self.temp_slider.valueChanged.connect(lambda v: self.temp_label.setText(f"{v/100:.2f}"))
        sidebar_layout.addWidget(temp_group)
        
        tokens_group = QGroupBox("Max Tokens"); tokens_layout = QVBoxLayout(tokens_group)
        self.max_tokens_spin = QSpinBox(); self.max_tokens_spin.setRange(256, 16384); self.max_tokens_spin.setValue(4096); self.max_tokens_spin.setSingleStep(128)
        tokens_layout.addWidget(self.max_tokens_spin); sidebar_layout.addWidget(tokens_group)
        sidebar_layout.addStretch(); self.save_btn = QPushButton("Antwort speichern")
        sidebar_layout.addWidget(self.save_btn); main_layout.addWidget(sidebar, 1)

        self.set_style(); self.connect_signals(); self.load_models()

    def set_style(self):
        p = Path(__file__).parent / "minimalist_dark.qss"
        if p.exists():
            with open(p, "r", encoding="utf-8") as f: self.setStyleSheet(f.read())
    
    def connect_signals(self):
        self.generate_btn.clicked.connect(self.run_generation)
        self.refresh_btn.clicked.connect(self.load_models)
        self.save_btn.clicked.connect(self.save_result)

    def create_menu(self):
        menu = self.menuBar().addMenu("Datei")
        act = QAction("API-Key setzen...", self); act.triggered.connect(self.show_settings_dialog)
        menu.addAction(act)

    def load_models(self):
        key = os.environ.get("AICODEGEN_API_KEY")
        if not key: QMessageBox.warning(self, "API-Key fehlt", "Bitte setze deinen OpenRouter API-Key im Menü."); return
        self.model_manager = ModelManager(key)
        self.model_manager.models_fetched.connect(self.on_models_loaded)
        self.model_manager.error_occurred.connect(lambda e: QMessageBox.critical(self, "Fehler", f"Modelle konnten nicht geladen werden:\n{e}"))
        self.model_manager.start()

    @Slot(list)
    def on_models_loaded(self, models):
        self.model_combo.clear()
        for m in sorted(models, key=lambda x: x.get('name','')): self.model_combo.addItem(m.get('name',m['id']), m['id'])

    def run_generation(self):
        prompt = self.prompt_input.toPlainText().strip()
        model = self.model_combo.currentData()
        key = os.environ.get("AICODEGEN_API_KEY")
        if not all([prompt, model, key]): QMessageBox.critical(self, "Fehler", "Prompt, Modell & API-Key benötigt."); return
        self.generate_btn.setEnabled(False); self.result_output.clear()
        
        params = {'model': model, 'prompt': prompt, 'system_prompt': "", 'api_key': key, 'temperature': self.temp_slider.value()/100.0, 'max_tokens': self.max_tokens_spin.value()}
        self.generator = CodeGenerator(**params)
        self.generator.chunk_received.connect(self.append_chunk)
        self.generator.error_occurred.connect(self.on_generation_error)
        self.generator.finished.connect(lambda: self.generate_btn.setEnabled(True))
        self.generator.start()

    @Slot(str)
    def append_chunk(self, chunk):
        self.result_output.moveCursor(QTextCursor.End); self.result_output.insertPlainText(chunk)
    
    @Slot(str)
    def on_generation_error(self, msg): self.result_output.setPlainText(f"Ein Fehler ist aufgetreten:\n{msg}")

    def save_result(self):
        content = self.result_output.toPlainText()
        if not content.strip(): return
        path, _ = QFileDialog.getSaveFileName(self, "Speichern", "", "Python-Datei (*.py);;Alle Dateien (*)")
        if path:
            try:
                with open(path, 'w', encoding='utf-8') as f: f.write(content)
            except Exception as e: QMessageBox.critical(self, "Speicherfehler", str(e))

    def show_settings_dialog(self):
        key, ok = QInputDialog.getText(self, "API-Key", "OpenRouter API-Key:", text=self.settings.get("api_key", ""))
        if ok and key:
            self.settings["api_key"] = key; save_settings(self.settings)
            os.environ["AICODEGEN_API_KEY"] = key; self.load_models()

def start_gui():
    app = QApplication(sys.argv); app.setFont(QFont("Cantarell", 11))
    win = MainWindow(); win.show()
    sys.exit(app.exec())
