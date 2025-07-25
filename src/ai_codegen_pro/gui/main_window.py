from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QFileDialog, QFrame, QListWidget, QListWidgetItem,
    QMessageBox, QMenuBar, QInputDialog, QPlainTextEdit, QDialog, QDialogButtonBox,
    QSplitter, QTabWidget, QTabBar
)
from PySide6.QtGui import QAction, QTextCursor, QFont
from PySide6.QtCore import Qt, QThread, Signal, Slot
from pathlib import Path
import os
import sys
import json
from datetime import datetime

from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient

CONFIG_PATH = Path.home() / ".ai_codegen_pro_config.json"

def save_settings(settings):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Fehler beim Speichern der Einstellungen: {e}")

def load_settings():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except: return {}
    return {}

class ModelManager(QThread):
    models_fetched = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.models = []

    def run(self):
        try:
            client = OpenRouterClient(api_key=self.api_key)
            self.models = client.get_available_models()
            self.models_fetched.emit(self.models)
        except Exception as e:
            self.error_occurred.emit(str(e))

class CodeGenerator(QThread):
    chunk_received = Signal(str)
    generation_complete = Signal(str)
    error_occurred = Signal(str)

    def __init__(self, model, prompt, system_prompt, api_key):
        super().__init__()
        self.model, self.prompt, self.system_prompt, self.api_key = model, prompt, system_prompt, api_key

    def run(self):
        try:
            client = OpenRouterClient(api_key=self.api_key, model=self.model)
            full_response = ""
            for chunk in client.generate_code_streaming(prompt=self.prompt, systemprompt=self.system_prompt):
                full_response += chunk
                self.chunk_received.emit(chunk)
            self.generation_complete.emit(full_response)
        except Exception as e:
            self.error_occurred.emit(str(e))

class SettingsDialog(QDialog):
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        layout = QVBoxLayout(self)
        self.api_key_edit = QTextEdit()
        self.api_key_edit.setPlaceholderText("API-Key für OpenRouter…")
        self.api_key_edit.setText(current_settings.get("api_key", ""))
        layout.addWidget(QLabel("API-Key (wird in ~/.ai_codegen_pro_config.json gespeichert):"))
        layout.addWidget(self.api_key_edit)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept); btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_settings(self):
        return {"api_key": self.api_key_edit.toPlainText().strip()}

class SessionWidget(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        top_bar_layout = QHBoxLayout()
        top_bar_layout.addWidget(QLabel("Modell:"))
        self.modelbox = QComboBox()
        self.modelbox.setMinimumWidth(250)
        top_bar_layout.addWidget(self.modelbox)
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedSize(32, 32)
        top_bar_layout.addWidget(self.refresh_btn)
        top_bar_layout.addStretch()
        main_layout.addLayout(top_bar_layout)

        splitter = QSplitter(Qt.Vertical)
        
        prompt_container = QWidget()
        prompt_layout = QVBoxLayout(prompt_container)
        prompt_layout.setContentsMargins(0,0,0,0); prompt_layout.setSpacing(4)
        prompt_layout.addWidget(QLabel("Prompt:"))
        self.prompt_input = QPlainTextEdit()
        self.prompt_input.setPlaceholderText("Beschreibe, was generiert werden soll...")
        prompt_layout.addWidget(self.prompt_input)
        splitter.addWidget(prompt_container)

        response_container = QWidget()
        response_layout = QVBoxLayout(response_container)
        response_layout.setContentsMargins(0,0,0,0); response_layout.setSpacing(4)
        response_layout.addWidget(QLabel("Antwort:"))
        self.result_output = QPlainTextEdit()
        self.result_output.setReadOnly(True)
        response_layout.addWidget(self.result_output)
        splitter.addWidget(response_container)
        
        splitter.setSizes([200, 400])
        main_layout.addWidget(splitter, 1)
        
        action_bar_layout = QHBoxLayout()
        action_bar_layout.addStretch()
        self.save_btn = QPushButton("Speichern")
        action_bar_layout.addWidget(self.save_btn)
        self.generate_btn = QPushButton("Generieren")
        self.generate_btn.setObjectName("generate_btn")
        action_bar_layout.addWidget(self.generate_btn)
        main_layout.addLayout(action_bar_layout)

        self.generate_btn.clicked.connect(self.on_generate)
        self.save_btn.clicked.connect(self.on_save)
        self.refresh_btn.clicked.connect(self.parent_window.load_models)
        
    def on_generate(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt: return
        model_id = self.modelbox.currentData()
        if not model_id: return
        api_key = os.environ.get("AICODEGEN_API_KEY")
        if not api_key:
            QMessageBox.critical(self, "API-Key fehlt", "API-Key nicht gefunden.")
            return

        self.generate_btn.setEnabled(False)
        self.result_output.setPlainText("")
        
        self.generator = CodeGenerator(model_id, prompt, "", api_key)
        self.generator.chunk_received.connect(self.append_chunk)
        self.generator.generation_complete.connect(self.generation_finished)
        self.generator.error_occurred.connect(self.handle_error)
        self.generator.start()

    @Slot(str)
    def append_chunk(self, chunk):
        self.result_output.moveCursor(QTextCursor.End)
        self.result_output.insertPlainText(chunk)

    @Slot(str)
    def generation_finished(self, full_response):
        self.generate_btn.setEnabled(True)

    @Slot(str)
    def handle_error(self, msg):
        self.result_output.setPlainText(f"Fehler beim Streaming:\n{msg}")
        self.generate_btn.setEnabled(True)

    def on_save(self):
        text = self.result_output.toPlainText()
        if not text.strip(): return
        file, _ = QFileDialog.getSaveFileName(self, "Ergebnis speichern", "", "Alle Dateien (*);;Python (*.py)")
        if file:
            with open(file, "w", encoding="utf-8") as f: f.write(text)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI CodeGen Pro")
        self.resize(1000, 750)
        self.settings = load_settings()
        if self.settings.get("api_key"):
            os.environ["AICODEGEN_API_KEY"] = self.settings["api_key"]
        
        self.create_menu()
        
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.setMovable(True)
        self.setCentralWidget(self.tabs)
        
        self.add_session()
        
        self.load_models()
        self.set_theme()

    def create_menu(self):
        menu_bar = self.menuBar()
        settings_action = QAction("Einstellungen", self)
        settings_action.triggered.connect(self.show_settings)
        menu_bar.addAction(settings_action)

    def load_models(self):
        api_key = os.environ.get("AICODEGEN_API_KEY")
        if api_key:
            self.model_manager = ModelManager(api_key)
            self.model_manager.models_fetched.connect(self.update_all_sessions_models)
            self.model_manager.error_occurred.connect(lambda e: QMessageBox.critical(self, "Fehler", f"Modelle konnten nicht geladen werden:\n{e}"))
            self.model_manager.start()
        else:
             QMessageBox.warning(self, "API-Key fehlt", "Bitte API-Key in den Einstellungen setzen, um Modelle zu laden.")

    @Slot(list)
    def update_all_sessions_models(self, models):
        sorted_models = sorted(models, key=lambda m: m.get('name', ''))
        for i in range(self.tabs.count()):
            session = self.tabs.widget(i)
            if isinstance(session, SessionWidget):
                session.modelbox.clear()
                for model in sorted_models:
                    session.modelbox.addItem(model.get('name', model['id']), model['id'])
    
    def add_session(self):
        session = SessionWidget(self)
        idx = self.tabs.addTab(session, f"Session {self.tabs.count() + 1}")
        self.tabs.setCurrentIndex(idx)
        if hasattr(self, 'model_manager') and self.model_manager.models:
            self.update_all_sessions_models(self.model_manager.models)

    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            QMessageBox.information(self, "Info", "Der letzte Tab kann nicht geschlossen werden.")

    def set_theme(self):
        style_path = Path(__file__).parent / "professional_dark.qss"
        if style_path.exists():
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def show_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec():
            new_settings = dlg.get_settings()
            self.settings.update(new_settings)
            save_settings(self.settings)
            os.environ["AICODEGEN_API_KEY"] = self.settings.get("api_key", "")
            self.load_models()

def start_gui():
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
