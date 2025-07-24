from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QFileDialog, QFrame, QGraphicsDropShadowEffect,
    QListWidget, QListWidgetItem, QMessageBox, QTabBar, QCheckBox, QMenuBar,
    QAction, QInputDialog, QPlainTextEdit, QDialog, QDialogButtonBox
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from pathlib import Path
import os
import sys

from ai_codegen_pro.core.model_router import ModelRouter

MODEL_OPTIONS = [
    ("Mistral 7B", "openrouter", "mistral-7b"),
    ("Mixtral 8x7B", "openrouter", "mixtral-8x7b"),
    ("Qwen 72B", "openrouter", "qwen-72b"),
    ("Phi-3", "openrouter", "phi-3-mini-128k-instruct"),
    ("Nous Hermes 2", "openrouter", "nous-hermes-2-mixtral-8x7b-dpo"),
]

MODEL_INFO = {
    "mistral-7b": {"Provider": "OpenRouter", "Preis": "kostenlos", "Kontext": "32k", "Features": "Sehr günstig, solide Antworten"},
    "mixtral-8x7b": {"Provider": "OpenRouter", "Preis": "kostenlos", "Kontext": "64k", "Features": "Sehr gute Allround-Qualität"},
    "qwen-72b": {"Provider": "OpenRouter", "Preis": "kostenlos", "Kontext": "128k", "Features": "Sehr großes Kontextfenster"},
    "phi-3-mini-128k-instruct": {"Provider": "OpenRouter", "Preis": "kostenlos", "Kontext": "128k", "Features": "Sehr effizient, kleiner Speicherbedarf"},
    "nous-hermes-2-mixtral-8x7b-dpo": {"Provider": "OpenRouter", "Preis": "kostenlos", "Kontext": "64k", "Features": "Spezialisiert für längere Kontexte"},
}

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
            from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient
            client = OpenRouterClient(
                api_key=self.api_key,
                api_base=self.api_base,
                model=self.model
            )
            for chunk in client.generate_code_streaming(
                prompt=self.prompt, systemprompt=self.systemprompt
            ):
                self.chunk_signal.emit(chunk)
            self.finished_signal.emit()
        except Exception as e:
            self.error_signal.emit(str(e))

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        layout = QVBoxLayout(self)
        self.api_key_edit = QTextEdit()
        self.api_key_edit.setPlaceholderText("API-Key für OpenRouter …")
        layout.addWidget(QLabel("API-Key (AICODEGEN_API_KEY):"))
        layout.addWidget(self.api_key_edit)
        self.theme_switch = QCheckBox("Light Theme verwenden")
        layout.addWidget(self.theme_switch)
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)
    def get_settings(self):
        return {
            "api_key": self.api_key_edit.toPlainText().strip(),
            "light_theme": self.theme_switch.isChecked()
        }

class SystemPromptWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Box)
        self.setFrameShadow(QFrame.Plain)
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
    def toggle(self):
        self.collapsed = not self.collapsed
        self.textedit.setVisible(not self.collapsed)
        self.toggle_btn.setText("▼" if self.collapsed else "▲")
        if self.collapsed:
            self.setFixedHeight(26)
        else:
            self.setFixedHeight(60)
    def get_prompt(self):
        return self.textedit.toPlainText().strip()

class SessionWidget(QWidget):
    def __init__(self, session_id=None):
        super().__init__()
        self.session_id = session_id
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10,8,10,8)
        layout.setSpacing(8)
        # Modellwahl + Info
        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Modell:"))
        self.modelbox = QComboBox()
        for name, provider, model in MODEL_OPTIONS:
            self.modelbox.addItem(name, (provider, model))
        self.modelbox.setMinimumWidth(120)
        hlayout.addWidget(self.modelbox)
        self.info_btn = QPushButton("🛈")
        self.info_btn.setFixedSize(28, 28)
        self.info_btn.setToolTip("Details zum gewählten Modell anzeigen")
        hlayout.addWidget(self.info_btn)
        hlayout.addStretch()
        layout.addLayout(hlayout)
        self.info_btn.clicked.connect(self.show_model_info)
        # Systemprompt (collapsible)
        self.sys_prompt = SystemPromptWidget(self)
        layout.addWidget(self.sys_prompt)
        # Prompt-Card
        layout.addWidget(QLabel("Prompt:"))
        prompt_card = QFrame()
        prompt_card.setMinimumHeight(48)
        prompt_layout = QVBoxLayout(prompt_card)
        prompt_layout.setContentsMargins(7,4,7,4)
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Beschreibe, was generiert werden soll ...")
        self.prompt_input.setMinimumHeight(22)
        prompt_layout.addWidget(self.prompt_input)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(13)
        shadow.setOffset(0, 1)
        shadow.setColor(Qt.gray)
        prompt_card.setGraphicsEffect(shadow)
        layout.addWidget(prompt_card)
        # Generieren-Button
        self.generate_btn = QPushButton("Live generieren")
        self.generate_btn.setMinimumWidth(110)
        layout.addWidget(self.generate_btn)
        # Antwort Card mit Syntax-Highlighting (minimal)
        layout.addWidget(QLabel("Antwort:"))
        result_card = QFrame()
        result_card.setMinimumHeight(60)
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(7,4,7,4)
        self.result_output = QPlainTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Hier erscheint das KI-Ergebnis ...")
        self.result_output.setMinimumHeight(25)
        result_layout.addWidget(self.result_output)
        shadow2 = QGraphicsDropShadowEffect(self)
        shadow2.setBlurRadius(13)
        shadow2.setOffset(0, 1)
        shadow2.setColor(Qt.gray)
        result_card.setGraphicsEffect(shadow2)
        layout.addWidget(result_card)
        # Verlauf/History
        layout.addWidget(QLabel("Verlauf:"))
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(80)
        layout.addWidget(self.history_list)
        # Save-Button
        self.save_btn = QPushButton("In Datei speichern…")
        self.save_btn.setMinimumWidth(90)
        layout.addWidget(self.save_btn)
        # Events
        self.generate_btn.clicked.connect(self.on_generate)
        self.save_btn.clicked.connect(self.on_save)
        self.history_list.itemDoubleClicked.connect(self.on_history_select)
        # Streaming
        self.streaming_thread = None
    def show_model_info(self):
        current = self.modelbox.currentData()
        if not current:
            return
        _, model = current
        info = MODEL_INFO.get(model, None)
        if not info:
            QMessageBox.information(self, "Modell-Info", f"Keine Details gefunden für Modell: {model}")
            return
        msg = "<br>".join([f"<b>{k}:</b> {v}" for k, v in info.items()])
        QMessageBox.information(self, "Modell-Info", msg)
    def on_generate(self):
        prompt = self.prompt_input.toPlainText().strip()
        systemprompt = self.sys_prompt.get_prompt()
        if not prompt:
            QMessageBox.warning(self, "Fehler", "Bitte Prompt eingeben!")
            return
        model = self.modelbox.currentData()[2]
        api_key = os.environ.get("AICODEGEN_API_KEY", "")
        api_base = os.environ.get("AICODEGEN_API_BASE", None)
        if not api_key:
            QMessageBox.critical(self, "API-Key fehlt", "API-Key nicht gesetzt! Bitte Umgebungsvariable setzen.")
            return
        self.result_output.setPlainText("… Anfrage läuft, Live-Stream …")
        self.generate_btn.setEnabled(False)
        self.result_output.setPlainText("")
        self.streaming_thread = StreamingThread(
            model=model, prompt=prompt, systemprompt=systemprompt,
            api_key=api_key, api_base=api_base
        )
        self.streaming_thread.chunk_signal.connect(self.append_stream_chunk)
        self.streaming_thread.error_signal.connect(self.stream_error)
        self.streaming_thread.finished_signal.connect(self.stream_finished)
        self.streaming_thread.start()
    @Slot(str)
    def append_stream_chunk(self, chunk):
        self.result_output.moveCursor(self.result_output.textCursor().End)
        self.result_output.insertPlainText(chunk)
        self.result_output.moveCursor(self.result_output.textCursor().End)
    @Slot()
    def stream_finished(self):
        self.generate_btn.setEnabled(True)
        # Verlauf aktualisieren
        prompt = self.prompt_input.toPlainText().strip()
        model = self.modelbox.currentData()[2]
        entry = f"{prompt[:40]}... → {model}"
        self.history_list.addItem(QListWidgetItem(entry))
    @Slot(str)
    def stream_error(self, msg):
        self.result_output.setPlainText(f"Fehler beim Streaming:\n{msg}")
        self.generate_btn.setEnabled(True)
    def on_save(self):
        text = self.result_output.toPlainText()
        if not text.strip():
            return
        file, _ = QFileDialog.getSaveFileName(self, "Ergebnis speichern", "", "Text (*.txt);;Python (*.py);;Markdown (*.md);;Alle Dateien (*)")
        if file:
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)
    def on_history_select(self, item):
        self.prompt_input.setPlainText(item.text().split("... →")[0].strip())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ai_codegen_pro – KI Codegenerierung (OpenRouter-only)")
        self.resize(950, 650)
        self.setMinimumSize(730, 520)
        self.theme_dark = True
        self.menu = self.menuBar()
        self.settings_action = QAction("Einstellungen", self)
        self.theme_action = QAction("Theme wechseln", self)
        self.menu.addAction(self.settings_action)
        self.menu.addAction(self.theme_action)
        self.settings_action.triggered.connect(self.show_settings)
        self.theme_action.triggered.connect(self.toggle_theme)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.tabs.tabBarDoubleClicked.connect(self.rename_tab)
        self.session_count = 0
        self.add_session()
        self.tabs.addTab(QWidget(), "+")
        self.tabs.tabBar().setTabButton(self.tabs.count() - 1, QTabBar.RightSide, None)
        self.tabs.currentChanged.connect(self.check_add_tab)
        self.set_theme(dark=True)
    def set_theme(self, dark=True):
        style_path = Path(__file__).parent / "glass_neumorph.qss"
        if style_path.exists():
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        else:
            # Fallback QSS
            style = "QWidget { background: #222; color: #eee; }"
            self.setStyleSheet(style)
        self.theme_dark = dark
    def show_settings(self):
        dlg = SettingsDialog(self)
        if dlg.exec():
            settings = dlg.get_settings()
            if settings.get("api_key"):
                os.environ["AICODEGEN_API_KEY"] = settings["api_key"]
            self.set_theme(not settings.get("light_theme", False))
    def toggle_theme(self):
        self.set_theme(not self.theme_dark)
    def add_session(self):
        self.session_count += 1
        session = SessionWidget(session_id=self.session_count)
        idx = self.tabs.count() - 1
        self.tabs.insertTab(idx, session, f"Session {self.session_count}")
        self.tabs.setCurrentIndex(idx)
    def close_tab(self, index):
        if self.tabs.widget(index):
            self.tabs.removeTab(index)
            if self.tabs.count() == 1:
                self.add_session()
    def check_add_tab(self, idx):
        if idx == self.tabs.count() - 1:
            self.add_session()
    def on_tab_changed(self, idx):
        pass
    def rename_tab(self, index):
        if index == self.tabs.count() - 1:
            return
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
