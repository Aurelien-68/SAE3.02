import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QGridLayout
)

app = QApplication(sys.argv)

# --- Fenêtre ---
root = QWidget()
root.resize(350, 150)
root.setWindowTitle("Exercice 1 - Affichage interface")

# --- Layout ---
grid = QGridLayout()
root.setLayout(grid)

# --- Composants ---
label = QLabel("Saisir votre nom :")
text = QLineEdit()
btn_ok = QPushButton("OK")
result = QLabel("")

# --- Placement ---
grid.addWidget(label, 0, 0)
grid.addWidget(text, 1, 0)
grid.addWidget(btn_ok, 2, 0)
grid.addWidget(result, 3, 0)

# --- Action du bouton ---
def action_ok():
    nom = text.text()
    result.setText(f"Bonjour {nom} !")

btn_ok.clicked.connect(action_ok)

# --- Affichage ---
root.show()

if __name__ == "__main__":
    sys.exit(app.exec())
