# boot/boot_widget.py
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class BootWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""background-color: #000000; color: white;""")

        layout = QVBoxLayout(self)
        label = QLabel("REFLEX SYSTEM\nBooting up...")
        label.setAlignment(Qt.AlignCenter)
        # label.setStyle("""font-size: 48px; font-weight: bold;""")
        layout.addWidget(label)