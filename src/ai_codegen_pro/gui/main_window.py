from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QFileDialog, QFrame, QGraphicsDropShadowEffect, QListWidget, QListWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from pathlib import Path
import os

from ai_codegen_pro.core.model_router import ModelRouter

MODEL_OPTIONS = [
    ("OpenAI GPT-3.5", "openai", "gpt-3.5-turbo"),
    ("OpenAI GPT-4", "openai", "gpt-4"),
    ("OpenRouter Mistral", "openrouter", "mistral-7b"),
    ("Anthropic Claude 3 Haiku", "anthropic", "claude-3-haiku-20240307")
]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ai_codegen_pro – KI Codegenerierung")
        self.resize(850, 600)
        self.setMinimumSize(700, 500)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(13)
        # Sidebar für Modellwahl
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(170)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(7, 6, 7, 6)
        sidebar_layout.setSpacing(10)
        sidebar_layout.addWidget(QLabel("Modell:"))
        self.modelbox = QComboBox()
        for name, provider, model in MODEL_OPTIONS:
            self.modelbox.addItem(name, (provider, model))
        sidebar_layout.addWidget(self.modelbox)
        sidebar_layout.addStretch()
        layout.addWidget(self.sidebar)
        # Content
        self.content = QFrame()
        content_layout = QVBoxLayout(self.content)
        content_layout.setContentsMargins(12,10,12,10)
        content_layout.setSpacing(9)
        # Prompt Card
        content_layout.addWidget(QLabel("Prompt:"))
        prompt_card = QFrame()
        prompt_card.setMinimumHeight(55)
        prompt_layout = QVBoxLayout(prompt_card)
        prompt_layout.setContentsMargins(8,4,8,4)
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Beschreibe, was generiert werden soll ...")
        self.prompt_input.setMinimumHeight(28)
        prompt_layout.addWidget(self.prompt_input)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(17)
        shadow.setOffset(0, 2)
        shadow.setColor(Qt.gray)
        prompt_card.setGraphicsEffect(shadow)
        content_layout.addWidget(prompt_card)
        # Generieren-Button
        self.generate_btn = QPushButton("Generieren")
        self.generate_btn.setMinimumWidth(100)
        content_layout.addWidget(self.generate_btn)
        # Antwort Card
        content_layout.addWidget(QLabel("Antwort:"))
        result_card = QFrame()
        result_card.setMinimumHeight(70)
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(8,4,8,4)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Hier erscheint das KI-Ergebnis ...")
        self.result_output.setMinimumHeight(35)
        result_layout.addWidget(self.result_output)
        shadow2 = QGraphicsDropShadowEffect(self)
        shadow2.setBlurRadius(17)
        shadow2.setOffset(0, 2)
        shadow2.setColor(Qt.gray)
        result_card.setGraphicsEffect(shadow2)
        content_layout.addWidget(result_card)
        # Verlauf/History
        content_layout.addWidget(QLabel("Verlauf:"))
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(90)
        content_layout.addWidget(self.history_list)
        # Save-Button
        self.save_btn = QPushButton("In Datei speichern…")
        self.save_btn.setMinimumWidth(90)
        content_layout.addWidget(self.save_btn)
        layout.addWidget(self.content)
        # Events
        self.generate_btn.clicked.connect(self.on_generate)
        self.save_btn.clicked.connect(self.on_save)
        self.history_list.itemDoubleClicked.connect(self.on_history_select)

    def on_generate(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "Fehler", "Bitte Prompt eingeben!")
            return
        provider, model = self.modelbox.currentData()
        api_key = os.environ.get("AICODEGEN_API_KEY", "")
        api_base = os.environ.get("AICODEGEN_API_BASE", None)
        if not api_key:
            QMessageBox.critical(self, "API-Key fehlt", "API-Key nicht gesetzt! Bitte Umgebungsvariable setzen.")
            return
        router = ModelRouter(provider=provider, api_key=api_key, api_base=api_base, model_name=model)
        try:
            self.result_output.setPlainText("... Anfrage läuft ...")
            out = router.generate(prompt)
            self.result_output.setPlainText(out)
            # Verlauf hinzufügen
            entry = f"{prompt[:40]}... → {model}"
            self.history_list.addItem(QListWidgetItem(entry))
        except Exception as e:
            self.result_output.setPlainText(f"Fehler: {e}")

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

def start_gui():
    from PySide6.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    style_file = Path(__file__).parent / "style.qss"
    if style_file.exists():
        with open(style_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
