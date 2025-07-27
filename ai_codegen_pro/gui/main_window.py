"""Professional AI CodeGen Pro Main Window"""

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
from PySide6.QtCore import Qt, QThread, Signal, QSettings, QTimer
from PySide6.QtGui import QFont

from ..core.template_service import TemplateService
from ..utils.logger_service import LoggerService
from .widgets.code_preview import CodePreviewWidget
from .widgets.multi_file_generator_widget import MultiFileGeneratorWidget
from .widgets.plugin_manager_widget import PluginManagerWidget
from .widgets.status_bar import ProfessionalStatusBar
from .themes.theme_manager import ThemeManager


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
            from ..core.openrouter_client import OpenRouterClient

            self.progress_update.emit("Initialisiere OpenRouter Client...")
            client = OpenRouterClient(self.api_key)

            self.progress_update.emit("Bereite Prompt vor...")
            template_service = TemplateService()
            full_prompt = f"{self.systemprompt}\n\n{self.prompt}"

            if self.template_name and self.template_name != "":
                try:
                    template_content = template_service.get_template_with_plugins(
                        self.template_name
                    )
                    full_prompt += f"\n\nTemplate-Kontext:\n{template_content}"
                except Exception as e:
                    self.logger.warning(f"Template konnte nicht geladen werden: {e}")

            self.progress_update.emit("Generiere Code...")

            response = client.generate_code(
                model=self.model, prompt=full_prompt, temperature=0.7, max_tokens=2048
            )

            self.progress_update.emit("Fertig!")
            self.result_ready.emit(response)

        except Exception as e:
            self.logger.error(f"Fehler bei Codegenerierung: {e}")
            self.error_occurred.emit(str(e))


class MainWindow(QMainWindow):
    """Professional AI CodeGen Pro Main Window"""

    def __init__(self):
        super().__init__()
        self.logger = LoggerService().get_logger(__name__)
        self.settings = QSettings("AICodeGenPro", "MainWindow")
        self.current_thread = None

        # Theme Manager
        self.theme_manager = ThemeManager()
        self.theme_manager.theme_changed.connect(self.apply_theme)

        self.init_ui()
        self.load_settings()
        self.setup_connections()

        # Apply theme
        self.apply_theme()

    def init_ui(self):
        """Initialize professional UI"""
        self.setWindowTitle("AI CodeGen Pro - Professional Edition")
        self.setMinimumSize(1200, 800)

        # Setup central widget
        self.setup_central_widget()

        # Professional status bar
        self.status_bar = ProfessionalStatusBar(self)
        self.setStatusBar(self.status_bar)

    def setup_central_widget(self):
        """Setup main central widget"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Configuration section
        self.setup_config_section(layout)

        # Main content area
        self.setup_content_area(layout)

    def setup_config_section(self, parent_layout):
        """Setup configuration section"""
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

        # Options
        options_layout = QHBoxLayout()

        self.streaming_checkbox = QCheckBox("Streaming aktivieren")
        self.streaming_checkbox.setChecked(True)
        options_layout.addWidget(self.streaming_checkbox)

        self.auto_copy_checkbox = QCheckBox("Auto-Kopieren")
        options_layout.addWidget(self.auto_copy_checkbox)

        # Theme Toggle
        self.theme_toggle_btn = QPushButton("🌙 Theme")
        self.theme_toggle_btn.setMaximumWidth(80)
        self.theme_toggle_btn.clicked.connect(self.toggle_theme)
        options_layout.addWidget(self.theme_toggle_btn)

        options_layout.addStretch()
        config_layout.addRow("⚙️ Optionen:", options_layout)

        parent_layout.addWidget(config_group)

    def setup_content_area(self, parent_layout):
        """Setup main content area"""
        main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # Input section
        self.setup_input_section(main_splitter)

        # Output section
        self.setup_output_section(main_splitter)

        main_splitter.setSizes([400, 800])
        parent_layout.addWidget(main_splitter)

    def setup_input_section(self, parent_splitter):
        """Setup input section"""
        input_group = QGroupBox("📝 Eingabe")
        input_layout = QVBoxLayout(input_group)

        # System Prompt
        system_label = QLabel("System Prompt:")
        system_label.setProperty("class", "heading")
        input_layout.addWidget(system_label)

        self.system_prompt_input = QTextEdit()
        self.system_prompt_input.setMaximumHeight(120)
        self.system_prompt_input.setPlaceholderText("System-Anweisungen...")
        self.system_prompt_input.setPlainText(
            "Du bist ein erfahrener Software-Entwickler. "
            "Erstelle sauberen, gut dokumentierten Code mit Best Practices."
        )
        input_layout.addWidget(self.system_prompt_input)

        # User Prompt
        user_label = QLabel("User Prompt:")
        user_label.setProperty("class", "heading")
        input_layout.addWidget(user_label)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText(
            "Beschreibe hier was generiert werden soll..."
        )
        input_layout.addWidget(self.prompt_input)

        # Generate Button
        self.generate_button = QPushButton("🚀 Code Generieren")
        self.generate_button.setProperty("class", "primary")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.clicked.connect(self.generate_code)
        input_layout.addWidget(self.generate_button)

        parent_splitter.addWidget(input_group)

    def setup_output_section(self, parent_splitter):
        """Setup output section"""
        output_group = QGroupBox("💻 Generierter Code")
        output_layout = QVBoxLayout(output_group)

        # Tab widget for different views
        self.output_tabs = QTabWidget()

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
        self.output_tabs.addTab(self.multi_file_widget, "🏗️ Multi-File Generator")

        # Plugin Manager Tab
        self.plugin_manager_widget = PluginManagerWidget()
        self.plugin_manager_widget.plugins_changed.connect(self._on_plugins_changed)
        self.output_tabs.addTab(self.plugin_manager_widget, "🔌 Plugin-Manager")

        output_layout.addWidget(self.output_tabs)

        # Action buttons
        self.setup_output_buttons(output_layout)

        parent_splitter.addWidget(output_group)

    def setup_output_buttons(self, parent_layout):
        """Setup output action buttons"""
        button_layout = QHBoxLayout()

        self.copy_button = QPushButton("📋 Kopieren")
        self.copy_button.setProperty("class", "success")
        self.copy_button.setEnabled(False)
        self.copy_button.clicked.connect(self.copy_output)
        button_layout.addWidget(self.copy_button)

        self.save_button = QPushButton("💾 Speichern")
        self.save_button.setEnabled(False)
        self.save_button.clicked.connect(self.save_output)
        button_layout.addWidget(self.save_button)

        button_layout.addStretch()

        self.clear_button = QPushButton("🗑️ Leeren")
        self.clear_button.clicked.connect(self.clear_output)
        button_layout.addWidget(self.clear_button)

        parent_layout.addLayout(button_layout)

    def setup_connections(self):
        """Setup signal connections"""
        self.api_key_input.textChanged.connect(self.save_settings)
        self.model_combo.currentTextChanged.connect(self.save_settings)
        self.template_combo.currentTextChanged.connect(self.save_settings)

        # Status bar connections
        self.status_bar.theme_toggle_requested.connect(self.toggle_theme)

    def populate_models(self):
        """Populate model dropdown"""
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
        """Populate template dropdown"""
        try:
            template_service = TemplateService()
            templates = template_service.list_templates()

            self.template_combo.addItem("🚫 Kein Template", "")

            for template in templates:
                display_name = template.replace(".j2", "").replace("_", " ").title()
                self.template_combo.addItem(f"📄 {display_name}", template)

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Templates: {e}")
            self.template_combo.addItem("❌ Fehler beim Laden", "")

    def _on_plugins_changed(self):
        """Handler wenn Plugins geändert werden"""
        self.logger.info("Plugins wurden geändert, Templates werden aktualisiert")
        # Template-Dropdown neu laden
        QTimer.singleShot(500, self.populate_templates)

    def generate_code(self):
        """Start code generation"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.status_bar.show_error("API Key ist erforderlich!")
            return

        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            self.status_bar.show_error("Prompt ist erforderlich!")
            return

        # UI setup
        self.generate_button.setEnabled(False)
        self.status_bar.show_progress("Generiere Code...")
        self.clear_output()

        # Start generation thread
        model = self.model_combo.currentText()
        system_prompt = self.system_prompt_input.toPlainText()
        template_name = self.template_combo.currentData()

        self.current_thread = CodeGeneratorThread(
            api_key=api_key,
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

        # Update API status
        self.status_bar.update_api_status(True, model.split("/")[0])

    def on_generation_complete(self, result):
        """Handle successful code generation"""
        self.output_text.setPlainText(result)
        self.code_preview.set_code(result, "python")

        # Enable buttons
        self.copy_button.setEnabled(True)
        self.save_button.setEnabled(True)

        # Auto-copy if enabled
        if self.auto_copy_checkbox.isChecked():
            self.copy_output()
            self.status_bar.show_success("Code generiert und kopiert!")
        else:
            self.status_bar.show_success("Code erfolgreich generiert!")

        # Switch to preview tab
        self.output_tabs.setCurrentIndex(1)

    def on_generation_error(self, error_message):
        """Handle generation error"""
        self.status_bar.show_error(f"Generierung fehlgeschlagen: {error_message}")
        QMessageBox.critical(
            self, "Fehler", f"Fehler bei der Codegenerierung:\n{error_message}"
        )

    def on_thread_finished(self):
        """Handle thread completion"""
        self.generate_button.setEnabled(True)
        self.status_bar.hide_progress()
        self.current_thread = None

    def copy_output(self):
        """Copy generated code to clipboard"""
        if self.output_tabs.currentIndex() == 0:
            content = self.output_text.toPlainText()
        else:
            content = self.code_preview.get_code()

        if content.strip():
            QApplication.clipboard().setText(content)
            self.status_bar.show_success("Code kopiert!")
        else:
            self.status_bar.show_error("Kein Code zum Kopieren!")

    def save_output(self):
        """Save generated code to file"""
        from PySide6.QtWidgets import QFileDialog

        content = self.output_text.toPlainText()
        if not content.strip():
            self.status_bar.show_error("Kein Code zum Speichern!")
            return

        filename, _ = QFileDialog.getSaveFileName(
            self, "Code speichern", "", "Python Files (*.py);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                self.status_bar.show_success(f"Gespeichert: {Path(filename).name}")
            except Exception as e:
                self.status_bar.show_error(f"Speichern fehlgeschlagen: {e}")

    def clear_output(self):
        """Clear output area"""
        self.output_text.clear()
        self.code_preview.clear()
        self.copy_button.setEnabled(False)
        self.save_button.setEnabled(False)

    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.theme_manager.toggle_theme()

        # Update theme button
        current_theme = self.theme_manager.get_current_theme_name()
        icon = "☀️" if current_theme == "dark" else "🌙"
        self.theme_toggle_btn.setText(f"{icon} Theme")

    def apply_theme(self):
        """Apply current theme"""
        # Theme is applied automatically by ThemeManager
        pass

    def save_settings(self):
        """Save window settings"""
        self.settings.setValue("api_key", self.api_key_input.text())
        self.settings.setValue("model", self.model_combo.currentText())
        self.settings.setValue("template", self.template_combo.currentData())
        self.settings.setValue("streaming", self.streaming_checkbox.isChecked())
        self.settings.setValue("auto_copy", self.auto_copy_checkbox.isChecked())

    def load_settings(self):
        """Load window settings"""
        self.api_key_input.setText(self.settings.value("api_key", ""))
        self.model_combo.setCurrentText(
            self.settings.value("model", "openai/gpt-4-turbo")
        )

        template = self.settings.value("template", "")
        if template:
            index = self.template_combo.findData(template)
            if index >= 0:
                self.template_combo.setCurrentIndex(index)

        self.streaming_checkbox.setChecked(
            self.settings.value("streaming", True, type=bool)
        )
        self.auto_copy_checkbox.setChecked(
            self.settings.value("auto_copy", False, type=bool)
        )

    def closeEvent(self, event):
        """Handle window close"""
        if self.current_thread and self.current_thread.isRunning():
            self.current_thread.terminate()
            self.current_thread.wait()

        self.save_settings()
        event.accept()
