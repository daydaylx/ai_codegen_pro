"""GUI Widget for Multi-File Project Generation"""

from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QLabel,
    QGroupBox,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QSplitter,
    QCheckBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ...core.multi_file_generator import MultiFileGenerator
from ...utils.logger_service import LoggerService


class MultiFileGeneratorWidget(QWidget):
    """Widget for multi-file project generation"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService().get_logger(__name__)
        self.generator = MultiFileGenerator()
        self.generated_files = {}

        self.setup_ui()
        self.setup_connections()
        self.populate_project_types()

    def setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("🏗️ Multi-File Project Generator")
        header_label.setProperty("class", "heading")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header_label)

        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left side - Configuration
        self.setup_config_panel(splitter)

        # Right side - Results
        self.setup_results_panel(splitter)

        splitter.setSizes([400, 600])
        layout.addWidget(splitter)

    def setup_config_panel(self, parent_splitter):
        """Setup configuration panel"""
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)

        # Project Type Selection
        type_group = QGroupBox("🎯 Projekt-Typ")
        type_layout = QFormLayout(type_group)

        self.project_type_combo = QComboBox()
        self.project_type_combo.currentTextChanged.connect(self.on_project_type_changed)
        type_layout.addRow("Typ:", self.project_type_combo)

        self.project_description = QTextEdit()
        self.project_description.setReadOnly(True)
        self.project_description.setMaximumHeight(80)
        type_layout.addRow("Beschreibung:", self.project_description)

        config_layout.addWidget(type_group)

        # Project Variables
        variables_group = QGroupBox("⚙️ Projekt-Variablen")
        self.variables_layout = QFormLayout(variables_group)
        config_layout.addWidget(variables_group)

        # Generate Button
        self.generate_button = QPushButton("🚀 Projekt Generieren")
        self.generate_button.setProperty("class", "primary")
        self.generate_button.setMinimumHeight(40)
        self.generate_button.clicked.connect(self.generate_project)
        config_layout.addWidget(self.generate_button)

        config_layout.addStretch()
        parent_splitter.addWidget(config_widget)

    def setup_results_panel(self, parent_splitter):
        """Setup results panel"""
        results_widget = QWidget()
        results_layout = QVBoxLayout(results_widget)

        # Results header
        results_header = QHBoxLayout()
        results_label = QLabel("📄 Generierte Dateien")
        results_label.setProperty("class", "heading")
        results_header.addWidget(results_label)
        results_header.addStretch()

        self.clear_results_button = QPushButton("🗑️ Leeren")
        self.clear_results_button.clicked.connect(self.clear_results)
        results_header.addWidget(self.clear_results_button)

        results_layout.addLayout(results_header)

        # Files table
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(2)
        self.files_table.setHorizontalHeaderLabels(["Datei", "Status"])

        header = self.files_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)

        self.files_table.itemSelectionChanged.connect(self.on_file_selected)
        results_layout.addWidget(self.files_table)

        # File preview
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 10))
        results_layout.addWidget(self.preview_text)

        parent_splitter.addWidget(results_widget)

    def setup_connections(self):
        """Setup signal connections"""
        pass

    def populate_project_types(self):
        """Populate project type dropdown"""
        project_types = self.generator.list_project_types()

        for project_type in project_types:
            project_info = self.generator.get_project_info(project_type)
            display_name = project_info.name if project_info else project_type
            self.project_type_combo.addItem(display_name, project_type)

        if project_types:
            self.on_project_type_changed(self.project_type_combo.currentText())

    def on_project_type_changed(self, display_name: str):
        """Handle project type change"""
        project_type = self.project_type_combo.currentData()
        if not project_type:
            return

        project_info = self.generator.get_project_info(project_type)
        if not project_info:
            return

        self.project_description.setPlainText(project_info.description)
        self.populate_variables_form(project_info.project_variables)

    def populate_variables_form(self, variables: Dict[str, Any]):
        """Populate variables form"""
        # Clear existing variables
        for i in reversed(range(self.variables_layout.count())):
            child = self.variables_layout.itemAt(i)
            if child:
                widget = child.widget()
                if widget:
                    widget.setParent(None)

        # Add new variables
        for var_name, default_value in variables.items():
            label = var_name.replace("_", " ").title() + ":"

            if isinstance(default_value, bool):
                checkbox = QCheckBox()
                checkbox.setChecked(default_value)
                checkbox.setObjectName(f"var_{var_name}")
                self.variables_layout.addRow(label, checkbox)
            else:
                line_edit = QLineEdit()
                line_edit.setText(str(default_value))
                line_edit.setObjectName(f"var_{var_name}")
                self.variables_layout.addRow(label, line_edit)

    def get_project_variables(self) -> Dict[str, Any]:
        """Get current project variables from form"""
        variables = {}

        for i in range(self.variables_layout.count()):
            item = self.variables_layout.itemAt(i)
            if item and item.fieldItem():
                field_widget = item.fieldItem().widget()
                if not field_widget or not hasattr(field_widget, "objectName"):
                    continue

                var_name = field_widget.objectName().replace("var_", "")

                if isinstance(field_widget, QCheckBox):
                    variables[var_name] = field_widget.isChecked()
                elif isinstance(field_widget, QLineEdit):
                    text = field_widget.text().strip()
                    variables[var_name] = text

        return variables

    def generate_project(self):
        """Start project generation"""
        project_type = self.project_type_combo.currentData()
        if not project_type:
            QMessageBox.warning(self, "Fehler", "Bitte Projekt-Typ auswählen!")
            return

        variables = self.get_project_variables()

        try:
            # Generate project files
            files = self.generator.generate_project_structure(project_type, variables)

            # Update UI
            self.generated_files = files
            self.update_files_table()

            QMessageBox.information(
                self,
                "Erfolg",
                f"Projekt erfolgreich generiert!\n{len(files)} Dateien erstellt.",
            )

        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Generierung fehlgeschlagen:\n{e}")

    def update_files_table(self):
        """Update files table with generated files"""
        self.files_table.setRowCount(len(self.generated_files))

        for row, (filename, content) in enumerate(self.generated_files.items()):
            self.files_table.setItem(row, 0, QTableWidgetItem(filename))
            self.files_table.setItem(row, 1, QTableWidgetItem("✅ Generiert"))

    def on_file_selected(self):
        """Handle file selection in table"""
        selected_items = self.files_table.selectedItems()
        if not selected_items:
            self.preview_text.clear()
            return

        row = selected_items[0].row()
        filename_item = self.files_table.item(row, 0)
        if not filename_item:
            return

        filename = filename_item.text()
        if filename in self.generated_files:
            content = self.generated_files[filename]
            self.preview_text.setPlainText(content)

    def clear_results(self):
        """Clear all results"""
        self.generated_files.clear()
        self.files_table.setRowCount(0)
        self.preview_text.clear()
