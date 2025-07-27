import os

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class TemplateEditor(QWidget):
    def __init__(self, template_dir="ai_codegen_pro/templates"):
        super().__init__()
        self.setWindowTitle("Template Editor")
        self.resize(700, 500)
        self.template_dir = template_dir

        layout = QHBoxLayout(self)

        # Liste aller Templates
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget, 1)

        # Texteditor für Template Inhalt
        vbox = QVBoxLayout()
        self.text_edit = QTextEdit()
        vbox.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        btn_save = QPushButton("Speichern")
        btn_save.clicked.connect(self.save_template)
        btn_layout.addWidget(btn_save)

        btn_new = QPushButton("Neu")
        btn_new.clicked.connect(self.create_new_template)
        btn_layout.addWidget(btn_new)

        vbox.addLayout(btn_layout)
        layout.addLayout(vbox, 3)

        self.list_widget.itemSelectionChanged.connect(self.load_selected_template)
        self.load_template_list()

    def load_template_list(self):
        self.list_widget.clear()
        if not os.path.isdir(self.template_dir):
            os.makedirs(self.template_dir, exist_ok=True)
        templates = [f for f in os.listdir(self.template_dir) if f.endswith(".j2")]
        self.list_widget.addItems(templates)

    def load_selected_template(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            self.text_edit.clear()
            return
        filename = selected_items[0].text()
        path = os.path.join(self.template_dir, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.text_edit.setPlainText(content)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Template konnte nicht geladen werden:\n{e}")

    def save_template(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self, "Kein Template ausgewählt", "Bitte wählen Sie ein Template aus."
            )
            return
        filename = selected_items[0].text()
        path = os.path.join(self.template_dir, filename)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text_edit.toPlainText())
            QMessageBox.information(self, "Gespeichert", f"Template {filename} wurde gespeichert.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Template konnte nicht gespeichert werden:\n{e}")

    def create_new_template(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Neues Template speichern",
            self.template_dir,
            "Jinja2 Templates (*.j2)",
        )
        if file_path:
            if not file_path.endswith(".j2"):
                file_path += ".j2"
            if os.path.exists(file_path):
                QMessageBox.warning(self, "Existiert bereits", "Diese Datei existiert bereits.")
                return
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("")  # Leere Datei
                self.load_template_list()
                # Select and load the new template
                items = self.list_widget.findItems(os.path.basename(file_path), Qt.MatchExactly)
                if items:
                    self.list_widget.setCurrentItem(items[0])
                QMessageBox.information(self, "Erstellt", "Neues Template wurde erstellt.")
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Template konnte nicht erstellt werden:\n{e}")
