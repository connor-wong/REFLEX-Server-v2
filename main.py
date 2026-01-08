# main.py
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QTimer

# Widgets
from components.boot.boot_widget import BootWidget
from components.vision.vision_wiget import VisionWidget

# Config
from config import WINDOW_WIDTH, WINDOW_HEIGHT

# Core
from core.app_controller import AppController

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("REFLEX UI")
        self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setStyleSheet("background-color: #101010;")

        # Create widgets
        boot = BootWidget()
        vision = VisionWidget()

        # Controller manages switching and pausing
        self.controller = AppController(boot, vision)
        self.setCentralWidget(self.controller)

        # Switch to vision after 3 seconds
        QTimer.singleShot(3000, lambda: self.controller.set_mode(1))

app = QApplication([])
app.setStyle("Fusion")

window = MainWindow()
window.show()

app.exec()