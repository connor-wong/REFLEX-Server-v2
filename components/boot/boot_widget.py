# boot/boot_widget.py
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import os

class BootWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #000000;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setAlignment(Qt.AlignCenter)

        # Boot Title
        # title = QLabel("REFLEX SYSTEM\nBooting up...")
        # title.setAlignment(Qt.AlignCenter)
        # title.setStyleSheet("""
        #     background-color: #000000;
        #     color: white;
        #     font-size: 48px;
        #     font-weight: bold;
        #     font-family: 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
        #     padding: 40px;
        #     border-radius: 20px;
        # """)

         # Boot Logo
        bootscreen_logo = QLabel()
        bootscreen_logo_path = os.path.join(os.path.dirname(__file__), "assets/Frame 1.png")
        bootscreen_logo_pixmap = QPixmap(bootscreen_logo_path)

        if bootscreen_logo_pixmap.isNull():
            print(f"Error: Image not found or cannot be loaded at {bootscreen_logo_path}")
        else:
            scaled_pixmap = bootscreen_logo_pixmap.scaled(
                500, 500,  # width, height in pixels
                Qt.KeepAspectRatio,  # maintains the original aspect ratio
                Qt.SmoothTransformation  # provides smooth scaling
            )
            bootscreen_logo.setPixmap(scaled_pixmap)
            bootscreen_logo.setAlignment(Qt.AlignCenter)

        # Boot Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0) 
        self.progress_bar.setTextVisible(False) 
        self.progress_bar.setFixedHeight(8)    
        self.progress_bar.setFixedWidth(500)   

        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 4px;
                background-color: #2A2A2A;
            }
            QProgressBar::chunk {
                background-color: #D0D0D0; 
                border-radius: 4px;
            }
        """)

        # layout.addWidget(title)
        layout.addWidget(bootscreen_logo)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignCenter)

    def update_progress(self, value: int):
        """Call this to update the progress bar (0-100)"""
        self.progress_bar.setValue(value)