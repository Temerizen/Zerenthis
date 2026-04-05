import sys
import json
import requests
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QLineEdit, QSpinBox, QMessageBox, QGroupBox
)

BASE_URL = "https://semantiqai-backend-production-bcab.up.railway.app"

class ZerenthisApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zerenthis Control Center")
        self.setMinimumSize(1100, 750)
        self.build_ui()

    def build_ui(self):
        root = QVBoxLayout()

        title = QLabel("ZERENTHIS CONTROL CENTER")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 28px; font-weight: bold; padding: 10px;")
        root.addWidget(title)

        form = QGroupBox("Money Loop Input")
        form_layout = QVBoxLayout()

        self.topic = QLineEdit()
        self.topic.setPlaceholderText("Topic")
        self.topic.setText("Faceless Content Cashflow Kit")

        self.niche = QLineEdit()
        self.niche.setPlaceholderText("Niche")
        self.niche.setText("Content Monetization")

        self.checkout = QLineEdit()
        self.checkout.setPlaceholderText("Checkout link")
        self.checkout.setText("")

        self.price = QSpinBox()
        self.price.setRange(1, 9999)
        self.price.setValue(29)

        form_layout.addWidget(QLabel("Topic"))
        form_layout.addWidget(self.topic)
        form_layout.addWidget(QLabel("Niche"))
        form_layout.addWidget(self.niche)
        form_layout.addWidget(QLabel("Checkout Link"))
        form_layout.addWidget(self.checkout)
        form_layout.addWidget(QLabel("Price"))
        form_layout.addWidget(self.price)
        form.setLayout(form_layout)
        root.addWidget(form)

        button_row = QHBoxLayout()

        self.run_btn = QPushButton("RUN MONEY LOOP")
        self.run_btn.clicked.connect(self.run_loop)

        self.health_btn = QPushButton("CHECK HEALTH")
        self.health_btn.clicked.connect(self.check_health)

        button_row.addWidget(self.run_btn)
        button_row.addWidget(self.health_btn)
        root.addLayout(button_row)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        root.addWidget(self.output)

        self.setLayout(root)
        self.setStyleSheet("""
            QWidget { background: #0b1020; color: #e6f1ff; font-family: Segoe UI; }
            QGroupBox { border: 1px solid #2a3555; border-radius: 8px; margin-top: 10px; padding: 10px; font-weight: bold; }
            QLineEdit, QTextEdit, QSpinBox {
                background: #121933; border: 1px solid #2a3555; border-radius: 6px; padding: 8px; color: #e6f1ff;
            }
            QPushButton {
                background: #1f6feb; border: none; border-radius: 8px; padding: 10px 14px; font-weight: bold;
            }
            QPushButton:hover { background: #388bfd; }
        """)

    def check_health(self):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=20)
            self.output.setPlainText(json.dumps(r.json(), indent=2))
        except Exception as e:
            QMessageBox.critical(self, "Health Error", str(e))

    def run_loop(self):
        payload = {
            "topic": self.topic.text().strip(),
            "niche": self.niche.text().strip(),
            "price": int(self.price.value()),
            "checkout_link": self.checkout.text().strip()
        }
        try:
            r = requests.post(f"{BASE_URL}/api/full-cycle", json=payload, timeout=120)
            self.output.setPlainText(json.dumps(r.json(), indent=2))
        except Exception as e:
            QMessageBox.critical(self, "Run Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ZerenthisApp()
    window.show()
    sys.exit(app.exec_())
