from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton, 
                             QFrame, QLabel, QHBoxLayout, QSizePolicy)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

class CollapsiblePanel(QWidget):
    """Ein ausklappbares Panel für System- und Regel-Prompts."""
    def __init__(self, title, placeholder_text, parent=None):
        super().__init__(parent)
        self.is_collapsed = True

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.toggle_button = QPushButton(title)
        self.toggle_button.setStyleSheet("text-align: left; padding: 8px; font-weight: bold;")
        self.toggle_button.clicked.connect(self.toggle_panel)
        main_layout.addWidget(self.toggle_button)

        self.content_area = QFrame()
        self.content_area.setObjectName("collapsible_panel")
        content_layout = QVBoxLayout(self.content_area)
        content_layout.setContentsMargins(8, 8, 8, 8)
        
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText(placeholder_text)
        content_layout.addWidget(self.prompt_edit)

        button_layout = QHBoxLayout()
        self.update_button = QPushButton("Aktualisieren")
        self.reset_button = QPushButton("Zurücksetzen")
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.reset_button)
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(self.content_area)

        self.content_area.setMaximumHeight(0)
        self.animation = QPropertyAnimation(self.content_area, b"maximumHeight")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        
        self.reset_button.clicked.connect(self.prompt_edit.clear)

    def toggle_panel(self):
        self.is_collapsed = not self.is_collapsed
        start_height = self.content_area.height()
        end_height = 0 if self.is_collapsed else self.content_area.sizeHint().height()

        self.animation.setStartValue(start_height)
        self.animation.setEndValue(end_height)
        self.animation.start()
