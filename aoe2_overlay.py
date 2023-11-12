# Game overlay application for Age of Empires II (AoE2)
import sys
import pathlib
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from aoe2.aoe2_game_overlay import AoE2GameOverlay

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AoE2GameOverlay(app=app, directory_main=str(pathlib.Path(__file__).parent.resolve()))

    # timer to call the functions related to mouse and keyboard inputs
    timer_mouse = QTimer()
    timer_mouse.timeout.connect(window.timer_mouse_keyboard_call)
    timer_mouse.setInterval(window.settings.mouse_call_ms)
    timer_mouse.start()

    # timer to call the functions related to match data
    timer_match_data = QTimer()
    timer_match_data.timeout.connect(window.timer_match_data_call)
    timer_match_data.setInterval(window.settings.match_data_call_ms)
    timer_match_data.start()

    exit_event = app.exec()
    sys.exit(exit_event)
