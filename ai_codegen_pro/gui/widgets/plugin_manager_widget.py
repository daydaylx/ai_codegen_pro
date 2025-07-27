"""Plugin-Manager Widget für die GUI"""

from typing import Any, Dict

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...plugins.manager import PluginManager
from ...utils.logger_service import LoggerService


class PluginListItem(QListWidgetItem):
    """Custom List Item für Plugins"""

    def __init__(self, plugin_id: str, plugin_info: Dict[str, Any]):
        super().__init__()
        self.plugin_id = plugin_id
        self.plugin_info = plugin_info

        metadata = plugin_info["metadata"]
        status = "✅ Aktiv" if plugin_info["enabled"] else "⭕ Inaktiv"

        self.setText(f"{metadata.name} v{metadata.version} - {status}")

        if plugin_info["enabled"]:
            self.setForeground(Qt.GlobalColor.darkGreen)


class PluginManagerWidget(QWidget):
    """Widget für Plugin-Management"""

    plugins_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService().get_logger(__name__)
        self.plugin_manager = PluginManager()

        self._setup_ui()
        self._setup_connections()
        self._refresh_plugin_list()

    def _setup_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()

        title_label = QLabel("Plugin-Manager")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.refresh_btn = QPushButton("🔄 Aktualisieren")
        self.refresh_btn.setMaximumWidth(150)
        header_layout.addWidget(self.refresh_btn)

        layout.addLayout(header_layout)

        # Main Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Plugin-Liste
        list_group = QGroupBox("Verfügbare Plugins")
        list_layout = QVBoxLayout(list_group)

        self.plugin_list = QListWidget()
        self.plugin_list.setMinimumWidth(300)
        list_layout.addWidget(self.plugin_list)

        # Plugin-Buttons
        button_layout = QHBoxLayout()

        self.enable_btn = QPushButton("✅ Aktivieren")
        self.enable_btn.setEnabled(False)
        button_layout.addWidget(self.enable_btn)

        self.disable_btn = QPushButton("⭕ Deaktivieren")
        self.disable_btn.setEnabled(False)
        button_layout.addWidget(self.disable_btn)

        self.auto_enable_cb = QCheckBox("Auto-Start")
        self.auto_enable_cb.setEnabled(False)
        button_layout.addWidget(self.auto_enable_cb)

        list_layout.addLayout(button_layout)
        splitter.addWidget(list_group)

        # Plugin-Details
        details_group = QGroupBox("Plugin-Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(200)
        details_layout.addWidget(self.details_text)

        # Template-Vorschau
        templates_label = QLabel("Verfügbare Templates:")
        templates_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        details_layout.addWidget(templates_label)

        self.templates_list = QListWidget()
        self.templates_list.setMaximumHeight(150)
        details_layout.addWidget(self.templates_list)

        splitter.addWidget(details_group)
        splitter.setSizes([400, 500])

        layout.addWidget(splitter)

    def _setup_connections(self):
        """Verbindet Signals mit Slots"""
        self.refresh_btn.clicked.connect(self._refresh_plugin_list)
        self.plugin_list.currentItemChanged.connect(self._on_plugin_selected)
        self.enable_btn.clicked.connect(self._enable_plugin)
        self.disable_btn.clicked.connect(self._disable_plugin)

    def _refresh_plugin_list(self):
        """Aktualisiert die Plugin-Liste"""
        self.plugin_list.clear()

        try:
            self.plugin_manager.reload_plugins()
            available_plugins = self.plugin_manager.get_available_plugins()

            for plugin_id, plugin_info in available_plugins.items():
                item = PluginListItem(plugin_id, plugin_info)
                self.plugin_list.addItem(item)

            self.logger.info(f"{len(available_plugins)} Plugins geladen")

        except Exception as e:
            self.logger.error(f"Fehler beim Laden der Plugins: {e}")
            QMessageBox.critical(self, "Fehler", f"Plugins konnten nicht geladen werden:\n{e}")

    def _on_plugin_selected(self, current_item, previous_item):
        """Handler für Plugin-Auswahl"""
        if not current_item:
            self._clear_details()
            return

        plugin_item = current_item
        plugin_info = plugin_item.plugin_info
        metadata = plugin_info["metadata"]

        # Details anzeigen
        details_html = f"""
        <h3>{metadata.name}</h3>
        <p><b>Version:</b> {metadata.version}</p>
        <p><b>Autor:</b> {metadata.author}</p>
        <p><b>Beschreibung:</b> {metadata.description}</p>
        <p><b>Status:</b> {'✅ Aktiv' if plugin_info['enabled'] else '⭕ Inaktiv'}</p>
        """

        if metadata.dependencies:
            details_html += f"<p><b>Abhängigkeiten:</b> {', '.join(metadata.dependencies)}</p>"

        self.details_text.setHtml(details_html)

        # Templates anzeigen
        self._show_plugin_templates(plugin_item.plugin_id)

        # Buttons aktivieren/deaktivieren
        self._update_buttons(plugin_info)

    def _show_plugin_templates(self, plugin_id: str):
        """Zeigt Templates eines Plugins an"""
        self.templates_list.clear()

        try:
            active_plugins = self.plugin_manager.get_active_plugins()

            if plugin_id in active_plugins:
                plugin = active_plugins[plugin_id]

                from ...plugins.base import TemplatePlugin

                if isinstance(plugin, TemplatePlugin):
                    templates = plugin.get_templates()

                    for template_name in templates.keys():
                        self.templates_list.addItem(f"📄 {template_name}")
                else:
                    self.templates_list.addItem("ℹ️ Kein Template-Plugin")
            else:
                self.templates_list.addItem("⭕ Plugin nicht aktiv")

        except Exception as e:
            self.logger.warning(f"Fehler beim Laden der Templates für {plugin_id}: {e}")
            self.templates_list.addItem("❌ Fehler beim Laden")

    def _update_buttons(self, plugin_info: Dict[str, Any]):
        """Aktualisiert Button-Status"""
        is_enabled = plugin_info["enabled"]
        config = plugin_info.get("config", {})

        self.enable_btn.setEnabled(not is_enabled)
        self.disable_btn.setEnabled(is_enabled)

        self.auto_enable_cb.setEnabled(True)
        self.auto_enable_cb.blockSignals(True)
        self.auto_enable_cb.setChecked(config.get("auto_enable", False))
        self.auto_enable_cb.blockSignals(False)

    def _clear_details(self):
        """Leert die Detail-Ansicht"""
        self.details_text.clear()
        self.templates_list.clear()
        self.enable_btn.setEnabled(False)
        self.disable_btn.setEnabled(False)
        self.auto_enable_cb.setEnabled(False)

    def _enable_plugin(self):
        """Aktiviert das ausgewählte Plugin"""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            return

        plugin_id = current_item.plugin_id
        auto_enable = self.auto_enable_cb.isChecked()

        try:
            if self.plugin_manager.enable_plugin(plugin_id, auto_enable=auto_enable):
                QMessageBox.information(self, "Erfolg", f"Plugin '{plugin_id}' wurde aktiviert!")
                self._refresh_plugin_list()
                self.plugins_changed.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Fehler",
                    f"Plugin '{plugin_id}' konnte nicht aktiviert werden.",
                )

        except Exception as e:
            self.logger.error(f"Fehler beim Aktivieren von {plugin_id}: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Aktivieren:\n{e}")

    def _disable_plugin(self):
        """Deaktiviert das ausgewählte Plugin"""
        current_item = self.plugin_list.currentItem()
        if not current_item:
            return

        plugin_id = current_item.plugin_id

        try:
            if self.plugin_manager.disable_plugin(plugin_id):
                QMessageBox.information(self, "Erfolg", f"Plugin '{plugin_id}' wurde deaktiviert!")
                self._refresh_plugin_list()
                self.plugins_changed.emit()
            else:
                QMessageBox.warning(
                    self,
                    "Fehler",
                    f"Plugin '{plugin_id}' konnte nicht deaktiviert werden.",
                )

        except Exception as e:
            self.logger.error(f"Fehler beim Deaktivieren von {plugin_id}: {e}")
            QMessageBox.critical(self, "Fehler", f"Fehler beim Deaktivieren:\n{e}")

    def get_plugin_manager(self) -> PluginManager:
        """Gibt den Plugin-Manager zurück"""
        return self.plugin_manager
