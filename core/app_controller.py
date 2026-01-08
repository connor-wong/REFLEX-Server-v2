# core/app_controller.py
from PySide6.QtWidgets import QStackedWidget

class AppController(QStackedWidget):
    def __init__(self, boot_widget, vision_widget):
        super().__init__()
        self.addWidget(boot_widget)
        self.addWidget(vision_widget)

        self.boot_widget = boot_widget
        self.vision_widget = vision_widget

        self.current_mode = 0
        self.set_mode(0)  # Start in boot mode

    def set_mode(self, mode: int):
        if mode == self.current_mode:
            return

        # Pause old mode
        if self.current_mode == 1:
            self.vision_widget.pause_vision()

        self.current_mode = mode

        # Show new screen
        self.setCurrentIndex(mode)  # 0 = boot, 1 = vision

        # Resume new mode
        if mode == 1:
            self.vision_widget.resume_vision()