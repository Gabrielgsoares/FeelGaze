import sys
import math
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush
from PyQt5.QtWidgets import QApplication, QWidget

DURATION = 3000  # milissegundos

class ProgressCircle(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(100, 100)

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 110, 10)  # canto superior direito com margem

        self.progress = 0  # de 0 a 100
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(DURATION // 100)

        self.counter = 0

    def update_progress(self):
        self.counter += 1
        self.progress = min(100, self.counter)
        self.update()
        if self.progress >= 100:
            self.timer.stop()
            self.close()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Sombra
        shadow = QPen(QColor(0, 0, 0, 100), 8)
        painter.setPen(shadow)
        painter.drawEllipse(4, 4, 92, 92)

        # Círculo externo
        pen = QPen(QColor(0, 150, 255), 6)
        painter.setPen(pen)
        angle = 360 * self.progress / 100
        painter.drawArc(10, 10, 80, 80, -90 * 16, -int(angle * 16))

        # Centro transparente (desenhar nada)
        brush = QBrush(Qt.transparent)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(30, 30, 40, 40)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ProgressCircle()
    w.show()
    sys.exit(app.exec_())
