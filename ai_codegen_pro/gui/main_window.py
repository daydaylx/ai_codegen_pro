import os
import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QComboBox, QFrame, QMessageBox,
    QInputDialog
)
from PySide6.QtGui import QFont, QTextCursor, QAction
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer

from ai_codegen_pro.core.providers.openrouter_client import OpenRouterClient
from ai_codegen_pro.core.template_service import TemplateService
from ai_codegen_pro.utils.logger_service import log
try:
    from ai_codegen_pro.utils.settings_manager import SettingsManager
    SETTINGS_AVAILABLE = True
except ImportError:
    SETTINGS_AVAILABLE = False

CONFIG_PATH = Path.home() / ".ai_codegen_pro_config.json"

def save_settings(settings):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except (IOError, TypeError) as e:
        log.error(f"Einstellungen konnten nicht gespeichert werden: {e}")
        QMessageBox.warning(None, "Speicherfehler", f"Einstellungen konnten nicht gespeichert werden:\n{e}")

def load_settings():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f: return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            log.error(f"Fehler beim Laden der Einstellungen: {e}")
            return {}
    return {}

class ModelManager(QThread):
    models_fetched = Signal(list)
    error_occurred = Signal(str)

    def __init__(self, api_key, parent=None):
        super().__init__(parent)
        self.api_key = api_key

    def run(self):
        try:
            client = OpenRouterClient(api_key=self.api_key)
            self.models_fetched.emit(client.get_available_models())
        except Exception as e:
            log.error(f"ModelManager Fehler: {e}")
            self.error_occurred.emit(str(e))

class CodeGenerator(QThread):

    chunk_received = Signal(str)

    error_occurred = Signal(str)

    generation_finished = Signal(str)



    def __init__(self, api_key, model, prompt, systemprompt, template_name, parent=None):

        super().__init__(parent)

        self.api_key = api_key

        self.model = model

        self.prompt = prompt

        self.systemprompt = systemprompt

        self.template_name = template_name

        self.result_buffer = ""



    def run(self):

        try:

            client = OpenRouterClient(api_key=self.api_key, model=self.model)

            for chunk in client.generate_code_streaming(prompt=self.prompt, systemprompt=self.systemprompt):

                self.result_buffer += chunk

                self.chunk_received.emit(chunk)

            self.generation_finished.emit(self.result_buffer)

        except Exception as e:

            log.error(f"CodeGenerator Fehler: {e}")

            self.error_occurred.emit(str(e))


    def __init__(self, api_key, model, prompt, systemprompt, template_name, parent=None):
        super().__init__(parent)
        self.api_key = api_key
        self.model = model
        self.prompt = prompt
        self.systemprompt = systemprompt
        self.template_name = template_name

    def run(self):
        try:
            client = OpenRouterClient(api_key=self.api_key, model=self.model)
            for chunk in client.generate_code_streaming(prompt=self.prompt, systemprompt=self.systemprompt):
                self.chunk_received.emit(chunk)
            self.generation_finished.emit()
        except Exception as e:
            log.error(f"CodeGenerator Fehler: {e}")
            self.error_occurred.emit(str(e))

class ModernPromptSection(QFrame):
    def __init__(self, label_text, placeholder, height, parent=None):
        super().__init__(parent)
        self.setProperty("promptFrame", True)
        self.setLayout(QVBoxLayout())
        self.layout().setContentsMargins(12, 8, 12, 12)
        self.layout().setSpacing(6)
        label = QLabel(label_text, objectName="prompt_label")
        self.text_edit = QTextEdit(placeholderText=placeholder, minimumHeight=height)
        self.layout().addWidget(label)
        self.layout().addWidget(self.text_edit)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI CodeGen Pro")
        self.resize(850, 900)
        if SETTINGS_AVAILABLE:
            self.settings_mgr = SettingsManager()
            self.settings = self.settings_mgr.settings
        else:
            self.settings = load_settings()
        self.init_ui()
        self.connect_signals()
        QTimer.singleShot(50, self.post_init_setup)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget, spacing=15, contentsMargins=(20, 20, 20, 20))

        menu = self.menuBar()
        file_menu = menu.addMenu("Datei")
        self.key_action = QAction("API-Key setzen...", self)
        file_menu.addAction(self.key_action)

        self.sys_prompt = ModernPromptSection("System-Prompt", "Rolle der KI...", 60)
        self.regel_prompt = ModernPromptSection("Regel-Prompt", "Formatierungsregeln...", 60)
        self.norm_prompt = ModernPromptSection("Benutzer-Prompt", "Deine Aufgabe...", 120)

        controls_layout = self._create_controls_layout()
        self.output_area = self._create_output_area()

        main_layout.addWidget(self.sys_prompt)
        main_layout.addWidget(self.regel_prompt)
        main_layout.addWidget(self.norm_prompt)
        main_layout.addLayout(controls_layout)
        main_layout.addWidget(QLabel("Antwort:", objectName="prompt_label"))
        main_layout.addWidget(self.output_area, 1)

    def _create_controls_layout(self):
        layout = QHBoxLayout()
        self.model_box = QComboBox()
        self.template_box = QComboBox()
        self.send_btn = QPushButton("Senden", objectName="send_btn")
        self.clear_btn = QPushButton("Löschen")

        layout.addWidget(QLabel("Modell:", objectName="prompt_label"))
        layout.addWidget(self.model_box, 1)
        layout.addSpacing(20)
        layout.addWidget(QLabel("Template:", objectName="prompt_label"))
        layout.addWidget(self.template_box, 1)
        layout.addSpacing(20)
        layout.addWidget(self.send_btn)
        layout.addWidget(self.clear_btn)
        return layout

    def _create_output_area(self):
        area = QTextEdit(readOnly=True, objectName="outputArea")
        return area

    def connect_signals(self):
        self.key_action.triggered.connect(self.prompt_for_api_key)
        self.send_btn.clicked.connect(self.run_generation)
        self.clear_btn.clicked.connect(self.clear_all)

    def post_init_setup(self):
        self.load_stylesheet()
        self.load_templates()
        api_key = self.settings.get("api_key")
        if not api_key:
            log.info("Kein API-Key gespeichert, frage Benutzer ab.")
            self.prompt_for_api_key()
        else:
            os.environ["AICODEGEN_API_KEY"] = api_key
            self.load_models()

    def load_stylesheet(self):
        style_path = Path(__file__).parent / "orange_dark.qss"
        try:
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            log.warning(f"Stylesheet {style_path} nicht gefunden.")

    def load_models(self):
        api_key = os.environ.get("AICODEGEN_API_KEY")
        if not api_key:
            log.error("Kein API-Key zum Laden der Modelle gesetzt.")
            return

        self.model_box.clear()
        self.model_box.addItem("Lade Modelle...")
        self.model_manager = ModelManager(api_key, self)
        self.model_manager.models_fetched.connect(self.on_models_loaded)
        self.model_manager.error_occurred.connect(self.on_model_load_error)
        self.model_manager.start()

    def load_templates(self):
        # Automatisch alle j2-Templates aus dem templates-Ordner laden
        template_dir = Path(__file__).parent.parent / "templates"
        if not template_dir.exists():
            self.template_box.addItem("Keine Templates gefunden")
            return
        templates = [f.name for f in template_dir.glob("*.j2")]
        if not templates:
            self.template_box.addItem("Keine Templates gefunden")
        else:
            self.template_box.clear()
            for tpl in templates:
                self.template_box.addItem(tpl)

    @Slot(list)
    def on_models_loaded(self, models):
        self.model_box.clear()
        for model in sorted(models, key=lambda m: m.get('name', '')):
            self.model_box.addItem(model.get('name', model['id']), model['id'])

    @Slot(str)
    def on_model_load_error(self, error_msg):
        self.model_box.clear()
        self.model_box.addItem("Fehler")
        log.error(f"Fehler beim Modell-Laden: {error_msg}")
        QMessageBox.critical(self, "Modell-Fehler", f"Laden fehlgeschlagen:\n{error_msg}")

    def run_generation(self):
        user_prompt, model_id, api_key = (
            self.norm_prompt.text_edit.toPlainText().strip(),
            self.model_box.currentData(),
            os.environ.get("AICODEGEN_API_KEY")
        )
        template_name = self.template_box.currentText()
        if not all([user_prompt, model_id, api_key, template_name]):
            log.warning("Fehlende Eingaben für Generierung.")
            QMessageBox.warning(self, "Eingabe fehlt", "Bitte Prompt, Modell und Template auswählen.")
            return

        self.send_btn.setEnabled(False)
        self.output_area.clear()
        full_system_prompt = self.sys_prompt.text_edit.toPlainText().strip()
        regel_prompt = self.regel_prompt.text_edit.toPlainText().strip()
        if regel_prompt:
            full_system_prompt += f"\n\n--- REGELN ---\n{regel_prompt}"

        self.generator = CodeGenerator(api_key, model_id, user_prompt, full_system_prompt, template_name, self)
        self.generator.chunk_received.connect(self.append_chunk)
        self.generator.error_occurred.connect(self.on_generation_error)
        self.generator.generation_finished.connect(self.on_generation_finished)
        self.generator.start()

    @Slot(str)
    def append_chunk(self, chunk):
        self.output_area.moveCursor(QTextCursor.End)
        self.output_area.insertPlainText(chunk)

    @Slot(str)
    def on_generation_error(self, msg):
        log.error(f"Fehler bei der Generierung: {msg}")
        self.output_area.setHtml(f"<font color='#e74c3c'><b>Fehler:</b><br>{msg}</font>")
        self.send_btn.setEnabled(True)

    def clear_all(self):
        self.sys_prompt.text_edit.clear()
        self.regel_prompt.text_edit.clear()
        self.norm_prompt.text_edit.clear()
        self.output_area.clear()

    def prompt_for_api_key(self):
        key, ok = QInputDialog.getText(
            self, "API-Key benötigt", "OpenRouter API-Key:", text=self.settings.get("api_key", "")
        )
        if ok and key:
            self.settings["api_key"] = key
            if SETTINGS_AVAILABLE:
                self.settings_mgr.set("api_key", key)
            else:
                save_settings(self.settings)
            os.environ["AICODEGEN_API_KEY"] = key
            self.load_models()

def start_gui():
    app = QApplication(sys.argv)
    app.setFont(QFont("Cantarell", 11))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

    def on_generation_finished(self, raw_output):
        self.send_btn.setEnabled(True)
        try:
            import json
            from ai_codegen_pro.core.template_service import TemplateService
            context = json.loads(raw_output)
            template_name = self.template_box.currentText()
            tpl_service = TemplateService()
            code = tpl_service.render(template_name, context)
            self.output_area.setPlainText(code)
        except Exception as e:
            log.error(f"Fehler beim Rendern mit Template: {e}")
            self.output_area.setHtml(f"<font color='#e74c3c'><b>Template-Fehler:</b><br>{e}</font>")

from PySide6.QtWidgets import QListWidget, QStackedWidget, QFileDialog

class FileViewerWidget(QWidget):
    def __init__(self, file_dict, parent=None):
        super().__init__(parent)
        self.files = file_dict
        layout = QHBoxLayout(self)
        self.list = QListWidget()
        self.stacked = QStackedWidget()
        for fname, content in self.files.items():
            self.list.addItem(fname)
            editor = QTextEdit()
            editor.setReadOnly(True)
            editor.setPlainText(content)
            self.stacked.addWidget(editor)
        layout.addWidget(self.list, 1)
        layout.addWidget(self.stacked, 4)
        self.list.currentRowChanged.connect(self.stacked.setCurrentIndex)

        # Export-Button
        self.export_btn = QPushButton("Export als ZIP")
        self.export_btn.clicked.connect(self.export_zip)
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(self.export_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    def export_zip(self):
        path, _ = QFileDialog.getSaveFileName(self, "Projekt als ZIP exportieren", "projekt.zip", "ZIP Files (*.zip)")
        if path:
            from ai_codegen_pro.core.multi_file_codegen import export_zip
            export_zip(self.files, path)

    def on_generation_finished(self, raw_output):
        self.send_btn.setEnabled(True)
        try:
            # Multi-File Parsing versuchen
            file_dict = parse_multi_file_response(raw_output)
            if file_dict:
                # Multi-File-Viewer zeigen
                viewer = FileViewerWidget(file_dict, self)
                self.centralWidget().layout().addWidget(viewer)
                viewer.list.setCurrentRow(0)
                # Option: OutputArea ausblenden
                self.output_area.hide()
                self.file_viewer = viewer
            else:
                # Fallback: Single File
                import json
                from ai_codegen_pro.core.template_service import TemplateService
                context = json.loads(raw_output)
                template_name = self.template_box.currentText()
                tpl_service = TemplateService()
                code = tpl_service.render(template_name, context)
                self.output_area.setPlainText(code)
                self.output_area.show()
        except Exception as e:
            log.error(f"Fehler beim Rendern mit Template: {e}")
            self.output_area.setHtml(f"<font color='#e74c3c'><b>Template-Fehler:</b><br>{e}</font>")
            self.output_area.show()
