#!/bin/bash

# Se placer dans le dossier du script (équivalent de %~dp0)
cd "$(dirname "$0")" || exit 1

echo "=============================="
echo " Installation des dépendances "
echo "        macOS (Homebrew)      "
echo "=============================="
echo

# Vérifier Homebrew
if ! command -v brew >/dev/null 2>&1; then
    echo "❌ Homebrew n'est pas installé."
    echo "➡️  Installe-le depuis https://brew.sh"
    exit 1
fi

# Mettre à jour Homebrew
brew update

# Installer Python si absent
brew install python || true

# Lancer le script Python
python3 dependances.py

# Pause (équivalent de pause / read)
read -p "Appuyez sur Entrée pour continuer..."
