import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout

CONFIG_PATH = os.path.join("settings", "config.json")

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ajustes do FeelGaze")
        self.setFixedSize(300, 200)

        self.sensitivity = 6.0
        self.fixation_time = 1.2

        self.load_settings()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Sensibilidade
        self.sens_label = QLabel(f"Sensibilidade: {self.sensitivity:.1f}")
        sens_inc = QPushButton("+")
        sens_dec = QPushButton("–")
        sens_inc.clicked.connect(self.increase_sensitivity)
        sens_dec.clicked.connect(self.decrease_sensitivity)
        sens_row = QHBoxLayout()
        sens_row.addWidget(sens_dec)
        sens_row.addWidget(self.sens_label)
        sens_row.addWidget(sens_inc)

        # Tempo de fixação
        self.fix_label = QLabel(f"Fixação: {self.fixation_time:.1f}s")
        fix_inc = QPushButton("+")
        fix_dec = QPushButton("–")
        fix_inc.clicked.connect(self.increase_fixation)
        fix_dec.clicked.connect(self.decrease_fixation)
        fix_row = QHBoxLayout()
        fix_row.addWidget(fix_dec)
        fix_row.addWidget(self.fix_label)
        fix_row.addWidget(fix_inc)

        # Aplicar
        apply_button = QPushButton("Aplicar")
        apply_button.clicked.connect(self.save_and_close)

        layout.addLayout(sens_row)
        layout.addLayout(fix_row)
        layout.addWidget(apply_button)

        self.setLayout(layout)

    def increase_sensitivity(self):
        self.sensitivity = min(10.0, self.sensitivity + 0.1)
        self.sens_label.setText(f"Sensibilidade: {self.sensitivity:.1f}")

    def decrease_sensitivity(self):
        self.sensitivity = max(0.1, self.sensitivity - 0.1)
        self.sens_label.setText(f"Sensibilidade: {self.sensitivity:.1f}")

    def increase_fixation(self):
        self.fixation_time = min(3.0, self.fixation_time + 0.1)
        self.fix_label.setText(f"Fixação: {self.fixation_time:.1f}s")

    def decrease_fixation(self):
        self.fixation_time = max(0.3, self.fixation_time - 0.1)
        self.fix_label.setText(f"Fixação: {self.fixation_time:.1f}s")

    def save_and_close(self):
        os.makedirs("settings", exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump({
                "sensitivity": self.sensitivity,
                "fixation_time": self.fixation_time
            }, f, indent=2)
        self.close()

    def load_settings(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
                self.sensitivity = float(data.get("sensitivity", 6.0))
                self.fixation_time = float(data.get("fixation_time", 1.2))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SettingsWindow()
    win.show()
    sys.exit(app.exec_())
