#!/bin/bash

cd "$(dirname "$0")"
python3 master.py -p 12000
read -p "Appuyez sur Entrée pour continuer..."
