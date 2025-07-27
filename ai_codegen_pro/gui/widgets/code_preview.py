"""Code-Preview Widget mit Syntax-Highlighting"""

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...utils.logger_service import LoggerService


class CodePreviewWidget(QWidget):
    """Widget für Code-Preview mit Syntax-Highlighting"""

    code_modified = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService().get_logger(__name__)

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Initialisiert die Benutzeroberfläche"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_layout = QHBoxLayout()

        header_layout.addWidget(QLabel("Code-Preview:"))

        self.language_combo = QComboBox()
        self.language_combo.addItems(
            [
                "python",
                "javascript",
                "typescript",
                "html",
                "css",
                "sql",
                "json",
                "yaml",
                "markdown",
                "bash",
            ]
        )
        self.language_combo.setCurrentText("python")
        header_layout.addWidget(self.language_combo)

        header_layout.addStretch()

        self.copy_btn = QPushButton("📋 Kopieren")
        self.copy_btn.setMaximumWidth(120)
        header_layout.addWidget(self.copy_btn)

        layout.addLayout(header_layout)

        # Code-Editor
        self.code_edit = QTextEdit()
        self.code_edit.setFont(QFont("Consolas", 10))
        self.code_edit.setStyleSheet(
            """
            QTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 10px;
            }
        """
        )

        layout.addWidget(self.code_edit)

    def _setup_connections(self):
        """Verbindet Signals mit Slots"""
        self.copy_btn.clicked.connect(self._copy_code)
        self.code_edit.textChanged.connect(self._on_text_changed)

    def _copy_code(self):
        """Kopiert Code in die Zwischenablage"""
        self.code_edit.selectAll()
        self.code_edit.copy()
        self.logger.debug("Code in Zwischenablage kopiert")

    def _on_text_changed(self):
        """Handler für Text-Änderungen"""
        code = self.code_edit.toPlainText()
        self.code_modified.emit(code)

    def set_code(self, code: str, language: Optional[str] = None):
        """Setzt den Code-Inhalt"""
        if language:
            self.language_combo.setCurrentText(language)

        self.code_edit.blockSignals(True)
        self.code_edit.setPlainText(code)
        self.code_edit.blockSignals(False)

        self.logger.debug(f"Code gesetzt: {len(code)} Zeichen")

    def get_code(self) -> str:
        """Gibt den aktuellen Code zurück"""
        return self.code_edit.toPlainText()

    def clear(self):
        """Leert den Preview-Bereich"""
        self.code_edit.clear()

    def set_read_only(self, read_only: bool):
        """Setzt Read-Only Modus"""
        self.code_edit.setReadOnly(read_only)
