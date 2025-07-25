from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTextEdit, QPlainTextEdit,
    QScrollArea, QListWidget, QFrame, QGridLayout, QStackedWidget,
    QSlider, QSpinBox, QGroupBox, QCheckBox, QSplitter, QDialog,
    QDialogButtonBox, QFileDialog, QMessageBox, QInputDialog,
    QMenuBar, QAction, QListWidgetItem, QTreeWidget, QTreeWidgetItem,
    QProgressBar, QToolButton, QRadioButton, QButtonGroup
)

from PySide6.QtGui import QIcon, QTextCursor, QPixmap, QPainter, QFont
from PySide6.QtCore import Qt, QThread, Signal, Slot, QTimer, QPropertyAnimation, QEasingCurve

import sys
import os
import json
from pathlib import Path
from datetime import datetime

CONFIG_PATH = Path.home() / ".ai_codegen_pro_config.json"

class CustomCard(QFrame):
    def __init__(self, title="", content_widget=None):
        super().__init__()
        self.setObjectName("customCard")
        layout = QVBoxLayout(self)
        if title:
            header = QLabel(title)
            header.setObjectName("cardHeader")
            layout.addWidget(header)
        if content_widget:
            layout.addWidget(content_widget)

class StatusDisplay(QFrame):
    def __init__(self):
        super().__init__()
        self.setObjectName("statusDisplay")
        layout = QHBoxLayout(self)
        self.status = QLabel("Bereit")
        self.model = QLabel("Modell: -")
        self.tokens = QLabel("Tokens: 0")
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.status)
        layout.addStretch()
        layout.addWidget(self.progress)
        layout.addWidget(self.model)
        layout.addWidget(self.tokens)

class PromptEditor(QFrame):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        toolbar = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.addItems(["Leer", "Debug", "Docs", "Tests"])
        self.btn_vars = QPushButton("Variablen")
        self.btn_format = QPushButton("Format")
        self.btn_save = QPushButton("Speichern")

        toolbar.addWidget(QLabel("Vorlage:"))
        toolbar.addWidget(self.combo)
        toolbar.addWidget(self.btn_vars)
        toolbar.addWidget(self.btn_format)
        toolbar.addWidget(self.btn_save)
        toolbar.addStretch()
        layout.addLayout(toolbar)

        self.editor = QTextEdit()
        self.editor.setPlaceholderText("Prompt eingeben...")
        layout.addWidget(self.editor)

        quick = QHBoxLayout()
        for label in ["Erklären", "Optimieren", "Testen", "Dokumentieren"]:
            quick.addWidget(QPushButton(label))
        quick.addStretch()
        layout.addLayout(quick)

class ModelSettings(QFrame):
    def __init__(self):
        super().__init__()
        layout = QGridLayout(self)

        layout.addWidget(QLabel("Modell:"), 0, 0)
        self.combo = QComboBox()
        self.refresh = QPushButton("🔄")
        h_model = QHBoxLayout()
        h_model.addWidget(self.combo)
        h_model.addWidget(self.refresh)
        layout.addLayout(h_model, 0, 1)

        layout.addWidget(QLabel("Temperatur:"), 1, 0)
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(70)
        h_temp = QHBoxLayout()
        h_temp.addWidget(self.temp_slider)
        h_temp.addWidget(QLabel("0.7"))
        layout.addLayout(h_temp, 1, 1)

        layout.addWidget(QLabel("Max Tokens:"), 2, 0)
        self.max_tokens = QSpinBox()
        self.max_tokens.setRange(100, 8000)
        self.max_tokens.setValue(2000)
        layout.addWidget(self.max_tokens, 2, 1)

        box = QGroupBox("Erweiterte Optionen")
        vbox = QVBoxLayout(box)
        self.chk_stream = QCheckBox("Streaming")
        self.chk_mem = QCheckBox("Kontext speichern")
        self.chk_safe = QCheckBox("Safety aktiv")
        vbox.addWidget(self.chk_stream)
        vbox.addWidget(self.chk_mem)
        vbox.addWidget(self.chk_safe)
        layout.addWidget(box, 3, 0, 1, 2)

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"Fehler beim Speichern: {e}")

def load_config():
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden: {e}")
    return {}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Alternative AI CodeGen GUI")
    central = QWidget()
    layout = QVBoxLayout(central)

    layout.addWidget(StatusDisplay())
    layout.addWidget(PromptEditor())
    layout.addWidget(ModelSettings())

    window.setCentralWidget(central)
    window.resize(900, 700)
    window.show()
    sys.exit(app.exec())
