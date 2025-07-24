from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox,
    QFileDialog, QFrame, QGraphicsDropShadowEffect
)
from PySide6.QtCore import Qt
from pathlib import Path
import sys, os

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
        self.setWindowTitle("ai_codegen_pro GUI")
        self.resize(920, 700)
        self.setMinimumSize(700, 540)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(28)

        # Modell-Auswahl
        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("Modell:"))
        self.modelbox = QComboBox()
        for name, provider, model in MODEL_OPTIONS:
            self.modelbox.addItem(name, (provider, model))
        self.modelbox.setMinimumWidth(230)
        top_row.addWidget(self.modelbox)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Prompt-Card mit Schatten
        layout.addWidget(QLabel("Prompt:"))
        prompt_card = QFrame()
        prompt_card.setMinimumHeight(120)
        prompt_layout = QVBoxLayout(prompt_card)
        prompt_layout.setContentsMargins(16,14,16,14)
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Beschreibe hier, was die KI generieren soll …")
        self.prompt_input.setMinimumHeight(70)
        prompt_layout.addWidget(self.prompt_input)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 7)
        shadow.setColor(Qt.gray)
        prompt_card.setGraphicsEffect(shadow)
        layout.addWidget(prompt_card)

        # Buttonzeile
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.generate_btn = QPushButton("Generieren")
        self.generate_btn.setMinimumWidth(160)
        btn_row.addWidget(self.generate_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

        # Antwort-Card mit Schatten
        layout.addWidget(QLabel("Antwort:"))
        result_card = QFrame()
        result_card.setMinimumHeight(210)
        result_layout = QVBoxLayout(result_card)
        result_layout.setContentsMargins(16,14,16,14)
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        self.result_output.setPlaceholderText("Hier erscheint das KI-Ergebnis …")
        self.result_output.setMinimumHeight(120)
        result_layout.addWidget(self.result_output)
        shadow2 = QGraphicsDropShadowEffect(self)
        shadow2.setBlurRadius(32)
        shadow2.setOffset(0, 7)
        shadow2.setColor(Qt.gray)
        result_card.setGraphicsEffect(shadow2)
        layout.addWidget(result_card)

        # Save-Buttonzeile
        btn_row2 = QHBoxLayout()
        btn_row2.addStretch()
        self.save_btn = QPushButton("In Datei speichern…")
        self.save_btn.setMinimumWidth(180)
        btn_row2.addWidget(self.save_btn)
        btn_row2.addStretch()
        layout.addLayout(btn_row2)

        # Signale
        self.generate_btn.clicked.connect(self.on_generate)
        self.save_btn.clicked.connect(self.on_save)

    def on_generate(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            self.result_output.setPlainText("Bitte Prompt eingeben!")
            return
        provider, model = self.modelbox.currentData()
        api_key = os.environ.get("AICODEGEN_API_KEY", "")
        api_base = os.environ.get("AICODEGEN_API_BASE", None)
        if not api_key:
            self.result_output.setPlainText("API-Key nicht gesetzt! Bitte Umgebungsvariable setzen.")
            return
        router = ModelRouter(provider=provider, api_key=api_key, api_base=api_base, model_name=model)
        try:
            self.result_output.setPlainText("... Anfrage läuft ...")
            out = router.generate(prompt)
            self.result_output.setPlainText(out)
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

def main():
    app = QApplication(sys.argv)
    # Stylesheet laden (Neumorph)
    style_file = Path(__file__).parent / "neumorph.qss"
    if style_file.exists():
        with open(style_file, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
