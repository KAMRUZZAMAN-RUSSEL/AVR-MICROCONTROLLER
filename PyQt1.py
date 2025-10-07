import sys
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QFileDialog, QTextEdit
)
from PyQt5.QtGui import QColor

class AvrBurner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AVR Burner - PyQt")
        self.setGeometry(200, 200, 600, 500)

        layout = QVBoxLayout()

        # Chip select
        chip_layout = QHBoxLayout()
        chip_layout.addWidget(QLabel("AVR Chip select:"))
        self.chip_combo = QComboBox()
        self.chip_combo.addItems(["m16", "m32", "m328p"])
        chip_layout.addWidget(self.chip_combo)
        layout.addLayout(chip_layout)

        # COM port select
        com_layout = QHBoxLayout()
        com_layout.addWidget(QLabel("COM Port select:"))
        self.port_combo = QComboBox()
        self.port_combo.addItems(["COM4", "COM3", "COM5"])
        com_layout.addWidget(self.port_combo)
        layout.addLayout(com_layout)

        # Fuse read button
        self.read_fuse_btn = QPushButton("Fuse Bites Read")
        self.read_fuse_btn.clicked.connect(self.read_fuses)
        layout.addWidget(self.read_fuse_btn)

        # Fuse set manually
        layout.addWidget(QLabel("Fuse Bites Set Manually:"))
        fuse_layout = QHBoxLayout()
        self.efuse_edit = QLineEdit(); self.efuse_edit.setPlaceholderText("Efuse")
        self.lfuse_edit = QLineEdit(); self.lfuse_edit.setPlaceholderText("Lfuse")
        self.hfuse_edit = QLineEdit(); self.hfuse_edit.setPlaceholderText("Hfuse")
        fuse_layout.addWidget(QLabel("Efuse:")); fuse_layout.addWidget(self.efuse_edit)
        fuse_layout.addWidget(QLabel("Lfuse:")); fuse_layout.addWidget(self.lfuse_edit)
        fuse_layout.addWidget(QLabel("Hfuse:")); fuse_layout.addWidget(self.hfuse_edit)
        layout.addLayout(fuse_layout)

        # HEX file upload
        self.hex_label = QLabel("HEX File: Not selected")
        self.hex_button = QPushButton("Select HEX File")
        self.hex_button.clicked.connect(self.select_hex)
        layout.addWidget(self.hex_label)
        layout.addWidget(self.hex_button)

        # Burn button
        self.burn_btn = QPushButton("Burn")
        self.burn_btn.clicked.connect(self.burn_hex)
        layout.addWidget(self.burn_btn)

        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        # Log
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)
        self.hex_file = None

    def select_hex(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select HEX File", "", "HEX Files (*.hex)")
        if file:
            self.hex_file = file
            self.hex_label.setText(f"HEX File: {file}")

    def run_avrdude(self, cmd):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            self.log_output.append(result.stdout)
            if result.stderr:
                self.log_output.append(result.stderr)
            return result.stdout + result.stderr
        except Exception as e:
            self.log_output.append(f"❌ Error: {e}")
            return None

    def read_fuses(self):
        chip = self.chip_combo.currentText()
        port = self.port_combo.currentText()
        avrdude_cmd = [
            r"C:\Users\Admin\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino17\bin\avrdude.exe",
            "-C", r"C:\Users\Admin\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino17\etc\avrdude.conf",
            "-c", "arduino", "-P", port, "-b", "19200", "-p", chip,
            "-U", "lfuse:r:-:h", "-U", "hfuse:r:-:h", "-U", "efuse:r:-:h"
        ]
        output = self.run_avrdude(avrdude_cmd)
        if output:
            lfuse, hfuse, efuse = "??", "??", "??"
            for line in output.splitlines():
                if "lfuse" in line: lfuse = line.split()[2]
                if "hfuse" in line: hfuse = line.split()[2]
                if "efuse" in line: efuse = line.split()[2]
            self.efuse_edit.setText(efuse)
            self.lfuse_edit.setText(lfuse)
            self.hfuse_edit.setText(hfuse)
            self.status_label.setText(f"✅ Fuses OK (E:{efuse}, H:{hfuse}, L:{lfuse})")
            self.status_label.setStyleSheet("color: green;")

    def burn_hex(self):
        if not self.hex_file:
            self.status_label.setText("⚠ Please select HEX file first!")
            self.status_label.setStyleSheet("color: red;")
            return

        chip = self.chip_combo.currentText()
        port = self.port_combo.currentText()
        avrdude_cmd = [
            r"C:\Users\Admin\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino17\bin\avrdude.exe",
            "-C", r"C:\Users\Admin\AppData\Local\Arduino15\packages\arduino\tools\avrdude\6.3.0-arduino17\etc\avrdude.conf",
            "-c", "arduino", "-P", port, "-b", "19200", "-p", chip,
            "-U", f"flash:w:{self.hex_file}:i"
        ]
        output = self.run_avrdude(avrdude_cmd)
        if "bytes of flash verified" in output:
            self.status_label.setText("✅ Burn Successful!")
            self.status_label.setStyleSheet("color: green;")
        else:
            self.status_label.setText("❌ Burn Failed!")
            self.status_label.setStyleSheet("color: red;")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AvrBurner()
    window.show()
    sys.exit(app.exec_())
