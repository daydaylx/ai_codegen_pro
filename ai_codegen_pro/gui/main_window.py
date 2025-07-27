import sys
import traceback

from PySide6.QtCore import QThread, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ai_codegen_pro.core.multi_file_codegen import GenerationResult, MultiFileCodeGenerator
from ai_codegen_pro.utils.exporter import export_project_as_zip


class CodeGenWorker(QThread):
    progress_signal = Signal(int)
    result_signal = Signal(object)
    error_signal = Signal(str)

    def __init__(self, api_key, project_spec):
        super().__init__()
        self.api_key = api_key
        self.project_spec = project_spec

    def run(self):
        try:
            generator = MultiFileCodeGenerator(self.api_key)
            self.progress_signal.emit(10)
            result: GenerationResult = generator.generate_project(self.project_spec)
            self.progress_signal.emit(100)
            self.result_signal.emit(result)
        except Exception as e:
            tb = traceback.format_exc()
            self.error_signal.emit(f"Fehler bei Code-Generierung:\n{e}\n{tb}")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI CodeGen Pro")
        self.resize(800, 600)

        self.api_key = None

        central = QWidget()
        self.setCentralWidget(central)

        vbox = QVBoxLayout(central)

        self.status_label = QLabel("Status: Bereit")
        vbox.addWidget(self.status_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        vbox.addWidget(self.progress_bar)

        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        vbox.addWidget(self.output_edit)

        btn_layout = QHBoxLayout()
        vbox.addLayout(btn_layout)

        self.gen_button = QPushButton("Projekt generieren")
        self.gen_button.clicked.connect(self.on_generate_clicked)
        btn_layout.addWidget(self.gen_button)

        self.export_button = QPushButton("Als ZIP exportieren")
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self.on_export_clicked)
        btn_layout.addWidget(self.export_button)

        self.generated_files = []
        self.worker = None

    def on_generate_clicked(self):
        if not self.api_key:
            QMessageBox.warning(
                self,
                "API Key fehlt",
                "Bitte Umgebungsvariable OPENROUTER_API_KEY setzen oder Key im Settings speichern.",
            )
            return

        self.status_label.setText("Status: Generiere Code...")
        self.progress_bar.setValue(0)
        self.output_edit.clear()
        self.gen_button.setEnabled(False)
        self.export_button.setEnabled(False)
        self.generated_files = []

        project_spec = {
            "type": "python",
            "name": "MeinProjekt",
            "components": [
                {"type": "module", "name": "main", "description": "Hauptmodul"},
                {
                    "type": "service",
                    "name": "backend",
                    "description": "Backend-Service",
                },
            ],
            "architecture": "standard",
            "dependencies": ["fastapi", "pydantic"],
        }

        self.worker = CodeGenWorker(self.api_key, project_spec)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.result_signal.connect(self.on_generation_done)
        self.worker.error_signal.connect(self.on_generation_error)
        self.worker.start()

    @Slot(object)
    def on_generation_done(self, result: GenerationResult):
        self.status_label.setText("Status: Fertig")
        self.progress_bar.setValue(100)
        self.gen_button.setEnabled(True)
        self.generated_files = result.files

        if result.success:
            self.output_edit.append("=== Generation erfolgreich! ===")
            for file in result.files:
                self.output_edit.append(f"Datei: {file.name}\n{file.content}\n{'-'*40}")
            self.export_button.setEnabled(True)
        else:
            self.output_edit.append("=== Fehler bei der Generation: ===")
            for err in result.errors:
                self.output_edit.append(err)
            self.export_button.setEnabled(False)

    @Slot(str)
    def on_generation_error(self, error_msg):
        self.status_label.setText("Status: Fehler")
        self.gen_button.setEnabled(True)
        self.export_button.setEnabled(False)

        dlg = QMessageBox(self)
        dlg.setWindowTitle("Fehler")
        dlg.setIcon(QMessageBox.Critical)
        dlg.setText("Beim Generieren des Codes ist ein Fehler aufgetreten.")
        dlg.setDetailedText(error_msg)
        dlg.exec()

    def on_export_clicked(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Speichere Projekt als ZIP",
            "projekt.zip",
            "ZIP Dateien (*.zip)",
        )
        if path:
            try:
                export_project_as_zip(self.generated_files, path)
                QMessageBox.information(
                    self,
                    "ZIP Export",
                    f"Projekt erfolgreich exportiert:\n{path}",
                )
            except Exception as e:
                QMessageBox.critical(self, "Fehler", f"Fehler beim Export:\n{e}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    import os

    window.api_key = os.getenv("OPENROUTER_API_KEY")
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
