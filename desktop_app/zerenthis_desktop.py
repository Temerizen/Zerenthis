import sys, json, urllib.request, os, webbrowser
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

BASE_URL = "https://semantiqai-backend-production-bcab.up.railway.app"

def get_json(url, method="GET", payload=None):
    data = None
    if payload:
        data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type":"application/json"}, method=method)
    return json.loads(urllib.request.urlopen(req).read().decode())

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zerenthis OS")
        self.resize(1000,700)

        layout = QVBoxLayout()

        title = QLabel("Zerenthis Control System")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size:24px; font-weight:bold;")
        layout.addWidget(title)

        self.output = QTextEdit()
        self.output.setReadOnly(True)

        btn_money = QPushButton("💰 Generate Product")
        btn_open = QPushButton("📄 Open Latest Product")
        btn_dash = QPushButton("📊 Refresh Dashboard")

        btn_money.clicked.connect(self.run_money)
        btn_open.clicked.connect(self.open_latest)
        btn_dash.clicked.connect(self.dashboard)

        layout.addWidget(btn_money)
        layout.addWidget(btn_open)
        layout.addWidget(btn_dash)
        layout.addWidget(self.output)

        self.setLayout(layout)

    def dashboard(self):
        data = get_json(BASE_URL + "/api/dashboard")
        self.output.setText(json.dumps(data, indent=2))

    def run_money(self):
        data = get_json(BASE_URL + "/api/command", "POST", {"command":"money"})
        self.output.setText(json.dumps(data, indent=2))

    def open_latest(self):
        path = os.path.abspath("C:/Zerenthis/backend/outputs")
        files = sorted(os.listdir(path), reverse=True)
        if files:
            webbrowser.open(os.path.join(path, files[0]))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec_())
