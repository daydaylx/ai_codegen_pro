"""Professional Status Bar mit mehreren Zonen"""

from PySide6.QtWidgets import QStatusBar, QLabel, QProgressBar, QPushButton
from PySide6.QtCore import QTimer, Signal

from ...utils.logger_service import LoggerService


class ProfessionalStatusBar(QStatusBar):
    """Professional status bar mit mehreren Zonen"""

    theme_toggle_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = LoggerService().get_logger(__name__)
        self.setup_ui()

    def setup_ui(self):
        """Setup status bar zones"""
        # Main status message
        self.main_label = QLabel("Bereit")
        self.main_label.setProperty("class", "secondary")
        self.addWidget(self.main_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setMaximumHeight(16)
        self.addWidget(self.progress_bar)

        # Permanent widgets
        self.api_status_label = QLabel("🔴 API: Nicht verbunden")
        self.addPermanentWidget(self.api_status_label)

        # Theme toggle
        theme_btn = QPushButton("🌙")
        theme_btn.setToolTip("Theme wechseln")
        theme_btn.setMaximumWidth(30)
        theme_btn.clicked.connect(self.theme_toggle_requested.emit)
        self.addPermanentWidget(theme_btn)

        # Version
        version_label = QLabel("v1.0.0")
        self.addPermanentWidget(version_label)

    def show_message(
        self, message: str, timeout: int = 5000, style_class: str = "secondary"
    ):
        """Show temporary message"""
        self.main_label.setText(message)
        self.main_label.setProperty("class", style_class)

        if timeout > 0:
            QTimer.singleShot(timeout, lambda: self.set_ready())

    def show_success(self, message: str, timeout: int = 3000):
        """Show success message"""
        self.show_message(f"✅ {message}", timeout, "success")

    def show_error(self, message: str, timeout: int = 8000):
        """Show error message"""
        self.show_message(f"❌ {message}", timeout, "error")

    def show_info(self, message: str, timeout: int = 3000):
        """Show info message"""
        self.show_message(f"ℹ️ {message}", timeout, "secondary")

    def set_ready(self):
        """Set status to ready"""
        self.main_label.setText("Bereit")
        self.main_label.setProperty("class", "secondary")

    def show_progress(self, text: str = "Arbeite..."):
        """Show progress bar"""
        self.show_message(text, 0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)

    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)
        self.set_ready()

    def update_api_status(self, connected: bool, provider: str = ""):
        """Update API connection status"""
        if connected:
            text = f"🟢 API: {provider}" if provider else "🟢 API: Verbunden"
            self.api_status_label.setText(text)
            self.api_status_label.setProperty("class", "success")
        else:
            self.api_status_label.setText("🔴 API: Nicht verbunden")
            self.api_status_label.setProperty("class", "error")
