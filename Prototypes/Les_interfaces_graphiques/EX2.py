import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QGridLayout, QMessageBox
)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Exercice 2 - Conversion Celsius / Kelvin")
        self.resize(350, 180)

        # ----- Widget principal -----
        root = QWidget()
        self.setCentralWidget(root)

        # ----- Layout -----
        grid = QGridLayout()
        root.setLayout(grid)

        # ----- Composants -----
        label_entree = QLabel("Température :")
        self.text = QLineEdit()

        self.combo = QComboBox()
        self.combo.addItems(["Celsius → Kelvin", "Kelvin → Celsius"])

        self.btn_convert = QPushButton("Convertir")
        self.result = QLabel("Résultat : ")

        # ----- Placement -----
        grid.addWidget(label_entree, 0, 0)
        grid.addWidget(self.text, 0, 1)

        grid.addWidget(self.combo, 1, 0, 1, 2)

        grid.addWidget(self.btn_convert, 2, 0, 1, 2)

        grid.addWidget(self.result, 3, 0, 1, 2)

        # ----- Signaux -----
        self.btn_convert.clicked.connect(self.convertir)
        self.combo.currentIndexChanged.connect(self.changement_unite)

    # ----- Traitement conversion -----
    def convertir(self):
        try:
            valeur = float(self.text.text())
        except ValueError:
            self._alerte("Erreur de saisie", "Veuillez entrer un nombre valide.")
            return

        mode = self.combo.currentText()

        # Celsius → Kelvin
        if mode == "Celsius → Kelvin":
            if valeur < -273.15:
                self._alerte("Température impossible",
                             "Impossible : en dessous du zéro absolu (-273,15 °C).")
                return
            resultat = valeur + 273.15
            self.result.setText(f"Résultat : {resultat:.2f} K")

        # Kelvin → Celsius
        else:
            if valeur < 0:
                self._alerte("Température impossible",
                             "Impossible : en dessous de 0 K (zéro absolu).")
                return
            resultat = valeur - 273.15
            self.result.setText(f"Résultat : {resultat:.2f} °C")

    # ----- Changement d’unité -----
    def changement_unite(self):
        self.result.setText("Résultat :")
        self.text.clear()

    # ----- Fenêtre d’alerte -----
    def _alerte(self, titre, message):
        msg = QMessageBox()
        msg.setWindowTitle(titre)
        msg.setText(message)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.exec()


# ----- MAIN -----
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
