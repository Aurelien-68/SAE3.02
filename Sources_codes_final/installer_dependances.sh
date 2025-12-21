#!/bin/bash

# Se placer dans le dossier du script (équivalent de %~dp0)
cd "$(dirname "$0")" || exit 1

# Lancer le script Python
python3 dependances.py

# Pause (équivalent de "pause")
read -p "Appuyez sur Entrée pour continuer..."
