"""Dark Theme für AI CodeGen Pro"""

from PySide6.QtGui import QColor, QPalette

from .base_theme import BaseTheme


class DarkTheme(BaseTheme):
    """Professionelles dunkles Theme"""

    @property
    def name(self) -> str:
        return "dark"

    @property
    def colors(self):
        return {
            "primary": "#2D2D2D",
            "secondary": "#3D3D3D",
            "accent": "#4A9EFF",
            "success": "#28A745",
            "warning": "#FFC107",
            "error": "#DC3545",
            "text": "#FFFFFF",
            "text_secondary": "#CCCCCC",
            "background": "#1E1E1E",
            "background_light": "#2D2D2D",
            "border": "#4A9EFF",
        }

    @property
    def fonts(self):
        return {
            "default": {"family": "Arial", "size": 10},
            "heading": {"family": "Arial", "size": 12, "weight": "bold"},
            "code": {"family": "Consolas", "size": 10},
        }

    def get_stylesheet(self) -> str:
        """Dark Theme Stylesheet - flake8 kompatibel"""
        return """
/* === MAIN WINDOW === */
QMainWindow {
    background-color: #1E1E1E;
    color: #FFFFFF;
    font-family: Arial;
    font-size: 10pt;
}

/* === BUTTONS === */
QPushButton {
    background-color: #3D3D3D;
    color: #FFFFFF;
    border: 1px solid #4A9EFF;
    padding: 8px 16px;
    border-radius: 6px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4A9EFF;
    border-color: #4A9EFF;
}

QPushButton:pressed {
    background-color: #2D2D2D;
}

QPushButton[class="primary"] {
    background-color: #4A9EFF;
    border-color: #4A9EFF;
}

QPushButton[class="success"] {
    background-color: #28A745;
    border-color: #28A745;
}

/* === TEXT INPUTS === */
QTextEdit, QLineEdit {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border: 1px solid #4A9EFF;
    padding: 8px;
    border-radius: 4px;
    selection-background-color: #4A9EFF;
}

QTextEdit:focus, QLineEdit:focus {
    border-color: #4A9EFF;
    border-width: 2px;
}

/* === COMBO BOXES === */
QComboBox {
    background-color: #2D2D2D;
    color: #FFFFFF;
    border: 1px solid #4A9EFF;
    padding: 6px 12px;
    border-radius: 4px;
}

/* === GROUP BOXES === */
QGroupBox {
    background-color: #2D2D2D;
    border: 2px solid #4A9EFF;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 12px;
    font-weight: bold;
}

QGroupBox::title {
    color: #FFFFFF;
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 8px 0 8px;
}

/* === TABS === */
QTabWidget::pane {
    border: 1px solid #4A9EFF;
    background-color: #2D2D2D;
}

QTabBar::tab {
    background-color: #3D3D3D;
    color: #FFFFFF;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #4A9EFF;
    color: white;
}

QTabBar::tab:hover {
    background-color: #2D2D2D;
}

/* === STATUS BAR === */
QStatusBar {
    background-color: #3D3D3D;
    color: #FFFFFF;
    border-top: 1px solid #4A9EFF;
}

QStatusBar QLabel {
    color: #FFFFFF;
    padding: 4px 8px;
}

QStatusBar QLabel[class="success"] {
    color: #28A745;
}

QStatusBar QLabel[class="warning"] {
    color: #FFC107;
}

QStatusBar QLabel[class="error"] {
    color: #DC3545;
}

/* === PROGRESS BAR === */
QProgressBar {
    background-color: #2D2D2D;
    border: 1px solid #4A9EFF;
    border-radius: 8px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #4A9EFF;
    border-radius: 6px;
}

/* === CHECKBOXES === */
QCheckBox {
    color: #FFFFFF;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #4A9EFF;
    border-radius: 3px;
    background-color: #2D2D2D;
}

QCheckBox::indicator:checked {
    background-color: #4A9EFF;
    border-color: #4A9EFF;
}

/* === LABELS === */
QLabel {
    color: #FFFFFF;
}

QLabel[class="heading"] {
    font-weight: bold;
    font-size: 12pt;
    color: #4A9EFF;
}

QLabel[class="secondary"] {
    color: #CCCCCC;
}

/* === SCROLLBARS === */
QScrollBar:vertical {
    background-color: #3D3D3D;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #4A9EFF;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4A9EFF;
}
"""

    def get_palette(self) -> QPalette:
        """Qt Palette für das Dark Theme"""
        palette = QPalette()

        # Window colors
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))

        # Base colors (for input fields)
        palette.setColor(QPalette.ColorRole.Base, QColor(45, 45, 45))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))

        # Button colors
        palette.setColor(QPalette.ColorRole.Button, QColor(61, 61, 61))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))

        # Highlight colors
        palette.setColor(QPalette.ColorRole.Highlight, QColor(74, 158, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))

        return palette
