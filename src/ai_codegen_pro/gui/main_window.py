from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QFileDialog, QFrame,
    QListWidget, QListWidgetItem, QMessageBox, QTabBar, QCheckBox, QMenuBar,
    QInputDialog, QPlainTextEdit, QDialog, QDialogButtonBox
)
from PySide6.QtGui import QAction, QTextCursor
from PySide6.QtCore import Qt, QThread, Signal, Slot
from pathlib import Path
import os
import sys
import json

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
        except Exception as e:
            print(f"Fehler beim Laden der Einstellungen: {e}")
    return {}

class ModelFetchThread(QThread):
    models_fetched_signal = Signal(list)
    error_signal = Signal(str)

    def __init__(self, api_key, api_base=None):
        super().__init__()
        self.api_key = api_key
        self.api_base = api_base

    def run(self):
        try:
            if not self.api_key:
                raise ValueError("API-Key nicht gefunden.")
            client = OpenRouterClient(api_key=self.api_key, api_base=self.api_base)
            models = client.get_available_models()
            self.models_fetched_signal.emit(models)
        except Exception as e:
            self.error_signal.emit(str(e))

class StreamingThread(QThread):
    chunk_signal = Signal(str)
    error_signal = Signal(str)
    finished_signal = Signal()
    def __init__(self, model, prompt, systemprompt, api_key, api_base=None):
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.systemprompt = systemprompt
        self.api_key = api_key
        self.api_base = api_base
    def run(self):
        try:
            client = OpenRouterClient(
                api_key=self.api_key, api_base=self.api_base, model=self.model
            )
            for chunk in client.generate_code_streaming(
                prompt=self.prompt, systemprompt=self.systemprompt
            ):
                self.chunk_signal.emit(chunk)
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

class SettingsDialog(QDialog):
    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        layout = QVBoxLayout(self)
        self.api_key_edit = QTextEdit()
        self.api_key_edit.setPlaceholderText("API-Key für OpenRouter …")
        self.api_key_edit.setText(current_settings.get("api_key", ""))
        layout.addWidget(QLabel("API-Key (wird in ~/.ai_codegen_pro_config.json gespeichert):"))
        layout.addWidget(self.api_key_edit)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def get_settings(self):
        return { "api_key": self.api_key_edit.toPlainText().strip() }

class SystemPromptWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.textedit = QTextEdit()
        self.textedit.setPlaceholderText("Systemprompt (Anweisungen für die KI, optional)…")
        self.textedit.setFixedHeight(44)
        layout.addWidget(self.textedit)
        self.toggle_btn = QPushButton("▲")
        self.toggle_btn.setFixedWidth(24)
        layout.addWidget(self.toggle_btn)
        self.collapsed = False
        self.toggle_btn.clicked.connect(self.toggle)
        self.setMinimumHeight(60)

    def toggle(self):
        self.collapsed = not self.collapsed
        self.textedit.setVisible(not self.collapsed)
        self.toggle_btn.setText("▼" if self.collapsed else "▲")
        self.setFixedHeight(26) if self.collapsed else self.setMinimumHeight(60)

    def get_prompt(self):
        return self.textedit.toPlainText().strip()

class SessionWidget(QWidget):
    def __init__(self, session_id=None):
        super().__init__()
        self.session_id = session_id
        self.all_models = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,8,10,8)
        layout.setSpacing(8)
        
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Modell:"))
        self.modelbox = QComboBox()
        self.modelbox.setMinimumWidth(120)
        hlayout.addWidget(self.modelbox)
        
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setFixedSize(28, 28)
        self.refresh_btn.setToolTip("Modell-Liste neu laden")
        hlayout.addWidget(self.refresh_btn)
        hlayout.addStretch()
        layout.addLayout(hlayout, 0)
        
        self.sys_prompt = SystemPromptWidget(self)
        layout.addWidget(self.sys_prompt, 0)

        layout.addWidget(QLabel("Prompt:"), 0)
        prompt_card = QFrame()
        prompt_layout = QVBoxLayout(prompt_card)
        prompt_layout.setContentsMargins(0,0,0,0)
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Beschreibe, was generiert werden soll ...")
        prompt_layout.addWidget(self.prompt_input)
        layout.addWidget(prompt_card, 2)

        self.generate_btn = QPushButton("Live generieren")
        layout.addWidget(self.generate_btn, 0)
        
        layout.addWidget(QLabel("Antwort:"), 0)
        result_card = QFrame()
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(0,0,0,0)
        self.result_output = QPlainTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Hier erscheint das KI-Ergebnis ...")
        result_layout.addWidget(self.result_output)
        layout.addWidget(result_card, 5)
        
        layout.addWidget(QLabel("Verlauf:"), 0)
        self.history_list = QListWidget()
        layout.addWidget(self.history_list, 1)
        
        self.save_btn = QPushButton("In Datei speichern…")
        layout.addWidget(self.save_btn, 0)
        
        self.generate_btn.clicked.connect(self.on_generate)
        self.save_btn.clicked.connect(self.on_save)
        self.history_list.itemDoubleClicked.connect(self.on_history_select)
        self.refresh_btn.clicked.connect(self.fetch_models)
        
        self.model_fetch_thread = None
        self.streaming_thread = None
        self.fetch_models()

    def fetch_models(self):
        api_key = os.environ.get("AICODEGEN_API_KEY", "")
        if not api_key:
            self.modelbox.clear()
            self.modelbox.addItem("API-Key fehlt!")
            return

        self.modelbox.clear()
        self.modelbox.addItem("Lade Modelle...")
        self.modelbox.setEnabled(False)
        self.refresh_btn.setEnabled(False)

        self.model_fetch_thread = ModelFetchThread(api_key=api_key)
        self.model_fetch_thread.models_fetched_signal.connect(self.populate_model_box)
        self.model_fetch_thread.error_signal.connect(self.on_model_fetch_error)
        self.model_fetch_thread.start()

    @Slot(list)
    def populate_model_box(self, models):
        self.all_models = sorted(models, key=lambda m: m.get('name', ''))
        self.modelbox.clear()
        for model in self.all_models:
            self.modelbox.addItem(model.get('name', model['id']), model['id'])
        self.modelbox.setEnabled(True)
        self.refresh_btn.setEnabled(True)

    @Slot(str)
    def on_model_fetch_error(self, error_msg):
        self.modelbox.clear()
        self.modelbox.addItem("Fehler beim Laden")
        self.modelbox.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        QMessageBox.critical(self, "Fehler", f"Modelle konnten nicht geladen werden:\n{error_msg}")

    def on_generate(self):
        prompt = self.prompt_input.toPlainText().strip()
        systemprompt = self.sys_prompt.get_prompt()
        if not prompt: return
        model_id = self.modelbox.currentData()
        if not model_id or "Lade" in self.modelbox.currentText(): return
        api_key = os.environ.get("AICODEGEN_API_KEY", "")
        if not api_key: return

        self.generate_btn.setEnabled(False)
        self.result_output.setPlainText("")
        
        self.streaming_thread = StreamingThread(
            model=model_id, prompt=prompt, systemprompt=systemprompt, api_key=api_key
        )
        self.streaming_thread.chunk_signal.connect(self.append_stream_chunk)
        self.streaming_thread.error_signal.connect(self.stream_error)
        self.streaming_thread.finished_signal.connect(self.stream_finished)
        self.streaming_thread.start()

    @Slot(str)
    def append_stream_chunk(self, chunk):
        self.result_output.moveCursor(QTextCursor.End)
        self.result_output.insertPlainText(chunk)
        self.result_output.moveCursor(QTextCursor.End)

    @Slot()
    def stream_finished(self):
        self.generate_btn.setEnabled(True)
        prompt = self.prompt_input.toPlainText().strip()
        model = self.modelbox.currentText()
        entry = f"{prompt[:40]}... → {model}"
        self.history_list.addItem(QListWidgetItem(entry))

    @Slot(str)
    def stream_error(self, msg):
        self.result_output.setPlainText(f"Fehler beim Streaming:\n{msg}")
        self.generate_btn.setEnabled(True)

    def on_save(self):
        text = self.result_output.toPlainText()
        if not text.strip(): return
        file, _ = QFileDialog.getSaveFileName(self, "Ergebnis speichern", "", "Alle Dateien (*);;Python (*.py);;Markdown (*.md)")
        if file:
            with open(file, "w", encoding="utf-8") as f: f.write(text)

    def on_history_select(self, item):
        self.prompt_input.setPlainText(item.text().split("... →")[0].strip())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ai_codegen_pro")
        self.resize(950, 700)
        self.setMinimumSize(730, 520)
        self.settings = load_settings()
        if self.settings.get("api_key"):
            os.environ["AICODEGEN_API_KEY"] = self.settings["api_key"]
        
        self.menu = self.menuBar()
        self.settings_action = QAction("Einstellungen", self)
        self.menu.addAction(self.settings_action)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBarDoubleClicked.connect(self.rename_tab)
        
        self.session_count = 0
        self.add_session()
        
        self.tabs.addTab(QWidget(), "+")
        self.tabs.tabBar().setTabButton(self.tabs.count() - 1, QTabBar.RightSide, None)
        self.tabs.currentChanged.connect(self.check_add_tab)
        
        self.settings_action.triggered.connect(self.show_settings)
        self.set_theme()

    def set_theme(self):
        # Lädt das neue, moderne Theme
        style_path = Path(__file__).parent / "modern_dark.qss"
        if style_path.exists():
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def show_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec():
            new_settings = dlg.get_settings()
            self.settings.update(new_settings)
            save_settings(self.settings)
            if self.settings.get("api_key"):
                os.environ["AICODEGEN_API_KEY"] = self.settings["api_key"]
                current_widget = self.tabs.currentWidget()
                if isinstance(current_widget, SessionWidget):
                    current_widget.fetch_models()

    def add_session(self):
        self.session_count += 1
        session = SessionWidget(session_id=self.session_count)
        idx = self.tabs.count() - 1
        self.tabs.insertTab(idx, session, f"Session {self.session_count}")
        self.tabs.setCurrentIndex(idx)

    def close_tab(self, index):
        if self.tabs.widget(index) and self.tabs.count() > 2:
            self.tabs.removeTab(index)

    def check_add_tab(self, idx):
        if idx == self.tabs.count() - 1:
            self.add_session()

    def rename_tab(self, index):
        if index < self.tabs.count() - 1:
            current_name = self.tabs.tabText(index)
            new_name, ok = QInputDialog.getText(self, "Tab umbenennen", "Neuer Name:", text=current_name)
            if ok and new_name:
                self.tabs.setTabText(index, new_name)

def start_gui():
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
