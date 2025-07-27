import keyring
from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")

        self.layout = QVBoxLayout(self)

        self.api_key_label = QLabel("OpenRouter API Key:")
        self.api_key_edit = QLineEdit()
        self.layout.addWidget(self.api_key_label)
        self.layout.addWidget(self.api_key_edit)

        btn_save = QPushButton("Speichern")
        btn_save.clicked.connect(self.save_key)
        self.layout.addWidget(btn_save)

        self.load_key()

    def load_key(self):
        key = keyring.get_password("ai_codegen_pro", "openrouter_api_key")
        if key:
            self.api_key_edit.setText(key)

    def save_key(self):
        key = self.api_key_edit.text().strip()
        if key:
            keyring.set_password("ai_codegen_pro", "openrouter_api_key", key)
            QMessageBox.information(self, "Gespeichert", "API-Key wurde sicher gespeichert.")
            self.accept()
        else:
            QMessageBox.warning(self, "Fehler", "API-Key darf nicht leer sein.")
