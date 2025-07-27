import json
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
    QComboBox,
    QWidget,
    QSplitter,
    QMessageBox,
    QGroupBox,
    QFormLayout,
    QCheckBox,
    QTabWidget,
    QApplication,
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont

# Enterprise Features
from ..themes.theme_manager import ThemeManager
from .widgets.code_preview import CodePreviewWidget
from .widgets.multi_file_generator_widget import MultiFileGeneratorWidget
from .widgets.status_bar import ProfessionalStatusBar
from ..core.template_service import TemplateService
from ..utils.logger_service import LoggerService


class CodeGeneratorThread(QThread):
    """Thread für Codegenerierung ohne UI-Blockierung"""

    result_ready = Signal(str)
    error_occurred = Signal(str)
    progress_update = Signal(str)

    def __init__(
        self, api_key, model, prompt, systemprompt, template_name, parent=None
    ):
        super().__init__(parent)
        self.api_key = api_key
        self.model = model
        self.prompt = prompt
        self.systemprompt = systemprompt
        self.template_name = template_name
        self.logger = LoggerService().get_logger(__name__)

    def run(self):
        """Führt die Codegenerierung im Hintergrund aus"""
        try:
            self.progress_update.emit("Simuliere Codegenerierung...")

            # Simulierte Generierung für Demo
            import time

            time.sleep(2)

            result = f"""# Generiert mit Model: {self.model}
# Template: {self.template_name or 'Kein Template'}

def example_function():
    '''
    Generierte Funktion basierend auf Prompt:
    {self.prompt[:100]}...
    '''
    pass

class ExampleClass:
    def __init__(self):
        self.name = "Generated Class"

    def process(self):
        return "Processing complete"

if __name__ == "__main__":
    example = ExampleClass()
    print(example.process())
"""

            self.progress_update.emit("Fertig!")
            self.result_ready.emit(result)

        except Exception as e:
            self.logger.error(f"Fehler bei Codegenerierung: {e}")
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    """Erweiterte Hauptanwendung mit Enterprise Features"""

    def __init__(self):
        super().__init__()
        self.logger = LoggerService().get_logger(__name__)
        self.settings_file = Path.home() / ".ai_codegen_pro" / "settings.json"
        self.current_thread = None

        # Theme Manager initialisieren
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.on_theme_changed)

        self.init_ui()
        self.load_settings()
        self.setup_connections()

        # Theme anwenden
        self.theme_manager.apply_theme()

    def init_ui(self):
        """Initialisiert die erweiterte Benutzeroberfläche"""
        self.setWindowTitle("AI CodeGen Pro - Enterprise Edition")
        self.setGeometry(100, 100, 1400, 900)

        # Zentrales Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Hauptlayout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(12)

        # Konfigurationsbereich
        self.setup_config_section(main_layout)

        # Hauptinhalt
        self.setup_main_content(main_layout)

        # Professional Status Bar
        self.status_bar = ProfessionalStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.status_bar.theme_toggle_requested.connect(self.toggle_theme)

    def setup_config_section(self, parent_layout):
        """Konfigurationsbereich einrichten"""
        config_group = QGroupBox("🔧 Konfiguration")
        config_layout = QFormLayout(config_group)
        config_layout.setSpacing(8)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("OpenRouter API Key eingeben...")
        config_layout.addRow("🔑 API Key:", self.api_key_input)

        # Model Selector
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.populate_models()
        config_layout.addRow("🤖 Model:", self.model_combo)

        # Template Selector
        self.template_combo = QComboBox()
        self.populate_templates()
        config_layout.addRow("📄 Template:", self.template_combo)

        # Advanced options
        advanced_layout = QHBoxLayout()

        self.streaming_checkbox = QCheckBox("Streaming")
        self.streaming_checkbox.setChecked(True)
        advanced_layout.addWidget(self.streaming_checkbox)

        self.auto_copy_checkbox = QCheckBox("Auto-Copy")
        advanced_layout.addWidget(self.auto_copy_checkbox)

        # Theme toggle button
        self.theme_button = QPushButton("🌙 Theme")
        self.theme_button.setMaximumWidth(80)
        self.theme_button.clicked.connect(self.toggle_theme)
        advanced_layout.addWidget(self.theme_button)

        advanced_layout.addStretch()
        config_layout.addRow("⚙️ Optionen:", advanced_layout)

        parent_layout.addWidget(config_group)

    def setup_main_content(self, parent_layout):
        """Hauptinhalt einrichten"""
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Eingabebereich
        self.setup_input_section(main_splitter)

        # Ausgabebereich mit Tabs
        self.setup_output_section(main_splitter)

        main_splitter.setSizes([400, 1000])
        parent_layout.addWidget(main_splitter)

    def setup_input_section(self, parent_splitter):
        """Eingabebereich einrichten"""
        input_group = QGroupBox("📝 Eingabe")
        input_layout = QVBoxLayout(input_group)
        input_layout.setSpacing(8)

        # System Prompt
        system_label = QLabel("System Prompt:")
        system_label.setProperty("class", "heading")
        input_layout.addWidget(system_label)

        self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setMaximumHeight(120)
        placeholder = "System-Anweisungen für das KI-Model..."
        self.system_prompt_input.setPlaceholderText(placeholder)
        default_prompt = (
            "Du bist ein erfahrener Software-Entwickler. "
            "Erstelle sauberen, gut dokumentierten Code mit "
            "Best Practices."
        )
        self.system_prompt_input.setPlainText(default_prompt)
        input_layout.addWidget(self.system_prompt_input)

        # User Prompt
        user_label = QLabel("User Prompt:")
        user_label.setProperty("class", "heading")
        input_layout.addWidget(user_label)

        self.prompt_input = QTextEdit()
        prompt_placeholder = "Beschreibe hier was generiert werden soll..."
        self.prompt_input.setPlaceholderText(prompt_placeholder)
        input_layout.addWidget(self.prompt_input)

        # Action buttons
        button_layout = QHBoxLayout()

        self.generate_button = QPushButton("🚀 Code Generieren")
        self.generate_button.setProperty("class", "primary")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        button_layout.addWidget(self.generate_button)

        self.clear_input_button = QPushButton("🗑️ Leeren")
        button_layout.addWidget(self.clear_input_button)

        input_layout.addLayout(button_layout)
        parent_splitter.addWidget(input_group)

    def setup_output_section(self, parent_splitter):
        """Ausgabebereich mit Tabs einrichten"""
        output_group = QGroupBox("💻 Output & Tools")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(8)

        # Tab widget für verschiedene Ansichten
        self.output_tabs = QTabWidget()
        self.output_tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Raw Output Tab
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        self.output_tabs.addTab(self.output_text, "📄 Raw Output")

        # Code Preview Tab
        self.code_preview = CodePreviewWidget()
        self.code_preview.set_read_only(True)
        self.output_tabs.addTab(self.code_preview, "🎨 Preview")

        # Multi-File Generator Tab
        self.multi_file_widget = MultiFileGeneratorWidget()
        self.output_tabs.addTab(self.multi_file_widget, "🏗️ Multi-File")

        output_layout.addWidget(self.output_tabs)

        # Action buttons
        self.setup_output_buttons(output_layout)

        parent_splitter.addWidget(output_group)

    def setup_output_buttons(self, parent_layout):
        """Output-Aktions-Buttons einrichten"""
        button_layout = QHBoxLayout()

        self.copy_button = QPushButton("📋 Kopieren")
        self.copy_button.setProperty("class", "success")
        self.copy_button.setEnabled(False)
        button_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("💾 Speichern")
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()

        self.clear_output_button = QPushButton("🗑️ Output leeren")
        button_layout.addWidget(self.clear_output_button)

        parent_layout.addLayout(button_layout)

    def populate_models(self):
        """Model-Dropdown füllen"""
        models = [
            "openai/gpt-4-turbo",
            "openai/gpt-4",
            "openai/gpt-3.5-turbo",
            "anthropic/claude-3-opus",
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku",
        ]
        self.model_combo.addItems(models)
        self.model_combo.setCurrentText("openai/gpt-4-turbo")

    def populate_templates(self):
        """Template-Dropdown füllen"""
        try:
            template_service = TemplateService()
            templates = template_service.list_all_templates()

            self.template_combo.addItem("🚫 Kein Template", "")

            for template in templates:
                display_name = template.replace(".j2", "").replace("_", " ")
                display_name = display_name.title()
                self.template_combo.addItem(f"📄 {display_name}", template)

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Templates: {e}")
            self.template_combo.addItem("❌ Fehler beim Laden", "")

    def setup_connections(self):
        """Signal-Verbindungen einrichten"""
        self.generate_button.clicked.connect(self.generate_code)
        self.copy_button.clicked.connect(self.copy_output)
        self.save_button.clicked.connect(self.save_output)
        self.clear_input_button.clicked.connect(self.clear_input)
        self.clear_output_button.clicked.connect(self.clear_output)

        # Auto-save settings
        self.api_key_input.textChanged.connect(self.save_settings)
        self.model_combo.currentTextChanged.connect(self.save_settings)
        self.template_combo.currentTextChanged.connect(self.save_settings)

    def generate_code(self):
        """Codegenerierung starten"""
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            self.status_bar.show_error("Prompt ist erforderlich!")
            return

        # UI vorbereiten
        self.generate_button.setEnabled(False)
        self.status_bar.show_progress("Generiere Code...")
        self.clear_output()

        # Thread starten
        model = self.model_combo.currentText()
        system_prompt = self.system_prompt_input.toPlainText()
        template_name = self.template_combo.currentData()

        self.current_thread = CodeGeneratorThread(
            api_key="dummy_key",  # Für Demo
            model=model,
            prompt=prompt,
            systemprompt=system_prompt,
            template_name=template_name,
        )

        self.current_thread.result_ready.connect(self.on_generation_complete)
        self.current_thread.error_occurred.connect(self.on_generation_error)
        self.current_thread.progress_update.connect(self.status_bar.show_message)
        self.current_thread.finished.connect(self.on_thread_finished)

        self.current_thread.start()

        # API Status aktualisieren
        self.status_bar.update_api_status(True, model.split("/")[0])

    def on_generation_complete(self, result):
        """Erfolgreiche Generierung behandeln"""
        self.output_text.setPlainText(result)
        self.code_preview.set_code(result, "python")

        # Buttons aktivieren
        self.copy_button.setEnabled(True)
        self.save_button.setEnabled(True)

        if self.auto_copy_checkbox.isChecked():
            self.copy_output()
            self.status_bar.show_success("Code generiert und kopiert!")
        else:
            self.status_bar.show_success("Code erfolgreich generiert!")

        # Zum Preview-Tab wechseln
        self.output_tabs.setCurrentIndex(1)

    def on_generation_error(self, error_message):
        """Generierungsfehler behandeln"""
        error_text = f"Generierung fehlgeschlagen: {error_message}"
        self.status_bar.show_error(error_text)

    def on_thread_finished(self):
        """Thread-Abschluss behandeln"""
        self.generate_button.setEnabled(True)
        self.status_bar.hide_progress()
        self.current_thread = None

    def copy_output(self):
        """Output kopieren"""
        if self.output_tabs.currentIndex() == 0:
            content = self.output_text.toPlainText()
        else:
            content = self.code_preview.get_code()

        if content.strip():
            QApplication.clipboard().setText(content)
            self.status_bar.show_success("Code kopiert!")

    def save_output(self):
        """Output speichern"""
        content = self.output_text.toPlainText()
        if not content.strip():
            self.status_bar.show_error("Kein Code zum Speichern!")
            return

        from PySide6.QtWidgets import QFileDialog

        filename, _ = QFileDialog.getSaveFileName(
            self, "Code speichern", "", "Python Files (*.py);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_bar.show_success("Code gespeichert!")
            except Exception as e:
                self.status_bar.show_error(f"Speichern fehlgeschlagen: {e}")

    def clear_input(self):
        """Eingabe leeren"""
        self.prompt_input.clear()
        self.status_bar.show_info("Eingabe geleert")

    def clear_output(self):
        """Output leeren"""
        self.output_text.clear()
        self.code_preview.clear()
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)

    def toggle_theme(self):
        """Theme wechseln"""
        self.theme_manager.toggle_theme()
        current_theme = self.theme_manager.get_current_theme_name()

        # Button-Text aktualisieren
        icon = "🌙" if current_theme == "light" else "☀️"
        self.theme_button.setText(f"{icon} Theme")

        self.status_bar.show_info(f"Theme: {current_theme.title()}")

    def on_theme_changed(self):
        """Theme wurde geändert"""
        self.logger.debug("Theme wurde gewechselt")

    def save_settings(self):
        """Einstellungen speichern"""
        settings = {
            "api_key": self.api_key_input.text(),
            "model": self.model_combo.currentText(),
            "template": self.template_combo.currentData(),
            "streaming": self.streaming_checkbox.isChecked(),
            "auto_copy": self.auto_copy_checkbox.isChecked(),
            "theme": self.theme_manager.get_current_theme_name(),
        }

        try:
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Settings save error: {e}")

    def load_settings(self):
        """Einstellungen laden"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    settings = json.load(f)

                self.api_key_input.setText(settings.get("api_key", ""))
                model = settings.get("model", "openai/gpt-4-turbo")
                self.model_combo.setCurrentText(model)

                template = settings.get("template", "")
                if template:
                    index = self.template_combo.findData(template)
                    if index >= 0:
                        self.template_combo.setCurrentIndex(index)

                streaming = settings.get("streaming", True)
                self.streaming_checkbox.setChecked(streaming)
                auto_copy = settings.get("auto_copy", False)
                self.auto_copy_checkbox.setChecked(auto_copy)

                # Theme laden
                theme_name = settings.get("theme", "dark")
                current_theme = self.theme_manager.get_current_theme_name()
                if theme_name != current_theme:
                    self.theme_manager.set_theme(theme_name)

            except Exception as e:
                self.logger.error(f"Fehler beim Laden der Einstellungen: {e}")

    def closeEvent(self, event):
        """Anwendung schließen"""
        if self.current_thread and self.current_thread.isRunning():
            reply = QMessageBox.question(
                self,
                "Codegenerierung läuft",
                "Eine Codegenerierung ist noch aktiv. Trotzdem beenden?",
                (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.current_thread.terminate()
                self.current_thread.wait()
                event.accept()
            else:
                event.ignore()
        else:
            self.save_settings()
            event.accept()
