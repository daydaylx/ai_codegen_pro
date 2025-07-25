import os, sys, json
from pathlib import Path
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTextEdit, QPushButton, QComboBox, QFileDialog, QFrame, QMessageBox, 
                             QSplitter, QInputDialog)
from PySide6.QtGui import QAction, QFont, QIcon
from PySide6.QtCore import Qt, QThread, Signal, Slot
from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient
from .side_panels import CollapsiblePanel

CONFIG_PATH = Path.home() / ".ai_codegen_pro_config.json"

# ... (Hier bleiben die Hilfsfunktionen save_settings, load_settings und die QThread-Klassen unverändert) ...
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
    def __init__(self, key): super().__init__(); self.api_key = key
    def run(self):
        try: self.models_fetched.emit(OpenRouterClient(api_key=self.api_key).get_available_models())
        except Exception as e: self.error_occurred.emit(str(e))

class CodeGenerator(QThread):
    chunk_received, error_occurred, generation_finished = Signal(str), Signal(str), Signal()
    def __init__(self, **kwargs): super().__init__(); self.params = kwargs
    def run(self):
        try:
            client = OpenRouterClient(api_key=self.params.pop('api_key'), model=self.params['model'])
            for chunk in client.generate_code_streaming(**self.params): self.chunk_received.emit(chunk)
            self.generation_finished.emit()
        except Exception as e: self.error_occurred.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI CodeGen Pro"); self.resize(1400, 900)
        self.settings = load_settings()
        if self.settings.get("api_key"): os.environ["AICODEGEN_API_KEY"] = self.settings["api_key"]
        
        self.create_menu()
        self.init_ui()
        self.load_theme()
        self.connect_signals()
        self.load_models()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)

        # Linkes Panel
        self.system_prompt_panel = CollapsiblePanel("System-Prompt", "Definiere die Rolle der KI...")
        main_layout.addWidget(self.system_prompt_panel)

        # Hauptbereich
        main_area = QFrame(); main_area_layout = QVBoxLayout(main_area)
        self.model_combo = QComboBox()
        main_area_layout.addWidget(self.model_combo)

        splitter = QSplitter(Qt.Vertical)
        self.prompt_input = QTextEdit(); self.prompt_input.setPlaceholderText("Beschreibe hier, was generiert werden soll...")
        self.result_output = QTextEdit(); self.result_output.setReadOnly(True)
        splitter.addWidget(self.prompt_input); splitter.addWidget(self.result_output)
        splitter.setSizes([250, 650])
        main_area_layout.addWidget(splitter)
        
        self.generate_btn = QPushButton("Generieren"); self.generate_btn.setObjectName("generate_btn")
        main_area_layout.addWidget(self.generate_btn)
        main_layout.addWidget(main_area, 1)

        # Rechtes Panel
        self.rules_panel = CollapsiblePanel("Formatierungsregeln", "Gib hier Zusatzregeln an...")
        main_layout.addWidget(self.rules_panel)

    def load_theme(self):
        style_path = Path(__file__).parent / "orange_dark.qss"
        if style_path.exists():
            with open(style_path, "r", encoding="utf-8") as f: self.setStyleSheet(f.read())

    def connect_signals(self):
        self.generate_btn.clicked.connect(self.run_generation)

    def create_menu(self):
        menu = self.menuBar().addMenu("Datei")
        key_action = QAction("API-Key setzen...", self)
        key_action.triggered.connect(self.show_settings_dialog)
        menu.addAction(key_action)
        save_action = QAction("Antwort speichern...", self)
        save_action.triggered.connect(self.save_result)
        menu.addAction(save_action)

    def load_models(self):
        key = os.environ.get("AICODEGEN_API_KEY")
        if not key: QMessageBox.warning(self, "API-Key fehlt", "Bitte setze deinen OpenRouter API-Key."); return
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
        if not all([prompt, model, key]): return
        
        self.generate_btn.setEnabled(False); self.result_output.clear()
        
        system_prompt = self.system_prompt_panel.prompt_edit.toPlainText().strip()
        rules_prompt = self.rules_panel.prompt_edit.toPlainText().strip()
        
        # Kombiniere Prompts
        final_system_prompt = system_prompt
        if rules_prompt:
            final_system_prompt += "\n\nZusätzliche Regeln:\n" + rules_prompt
        
        params = {'model': model, 'prompt': prompt, 'systemprompt': final_system_prompt, 'api_key': key}
        self.generator = CodeGenerator(**params)
        self.generator.chunk_received.connect(self.result_output.insertPlainText)
        self.generator.error_occurred.connect(lambda msg: self.result_output.setPlainText(f"Fehler:\n{msg}"))
        self.generator.generation_finished.connect(lambda: self.generate_btn.setEnabled(True))
        self.generator.start()
        
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
    app = QApplication(sys.argv); app.setFont(QFont("Fira Sans", 11))
    win = MainWindow(); win.show()
    sys.exit(app.exec())
