import sys
import subprocess
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

def run_cmd():
    subprocess.run("echo Hallo von CMD!", shell=True)

def run_powershell():
    subprocess.run(["powershell", "-Command", "Write-Output 'Hallo von PowerShell!'"], shell=True)

def show_ip():
    subprocess.run("ipconfig", shell=True)

class ModernGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Moderne Test GUI")
        self.setGeometry(100, 100, 400, 300)
        self.setStyleSheet("background-color: #1e1e1e;")
        
        layout = QVBoxLayout()
        
        label = QLabel("Befehlsauswahl")
        label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        label.setStyleSheet("color: #ffa500;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        btn_style = """
            QPushButton {
                background-color: #ff8c00;
                color: black;
                font-size: 14px;
                padding: 10px;
                border-radius: 5px;
                border: 2px solid #ffa500;
            }
            QPushButton:hover {
                background-color: #ff4500;
                color: white;
            }
            QPushButton:pressed {
                background-color: #b22222;
                border: 2px solid #ff6347;
            }
        """
        
        btn_cmd = QPushButton("CMD Befehl")
        btn_cmd.setStyleSheet(btn_style)
        btn_cmd.clicked.connect(run_cmd)
        layout.addWidget(btn_cmd)
        
        btn_powershell = QPushButton("PowerShell Befehl")
        btn_powershell.setStyleSheet(btn_style)
        btn_powershell.clicked.connect(run_powershell)
        layout.addWidget(btn_powershell)
        
        btn_ip = QPushButton("IP anzeigen")
        btn_ip.setStyleSheet(btn_style)
        btn_ip.clicked.connect(show_ip)
        layout.addWidget(btn_ip)
        
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ModernGUI()
    window.show()
    sys.exit(app.exec())
