from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox, QFileDialog
)
from PySide6.QtCore import Qt
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
        self.resize(800, 600)
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel("Modell:"))
        self.modelbox = QComboBox()
        for name, provider, model in MODEL_OPTIONS:
            self.modelbox.addItem(name, (provider, model))
        hlayout.addWidget(self.modelbox)
        layout.addLayout(hlayout)

        layout.addWidget(QLabel("Prompt:"))
        self.prompt_input = QTextEdit()
        layout.addWidget(self.prompt_input)

        self.generate_btn = QPushButton("Generieren")
        layout.addWidget(self.generate_btn)

        layout.addWidget(QLabel("Antwort:"))
        self.result_output = QTextEdit()
        self.result_output.setReadOnly(True)
        layout.addWidget(self.result_output)

        self.save_btn = QPushButton("In Datei speichern...")
        layout.addWidget(self.save_btn)

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
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
