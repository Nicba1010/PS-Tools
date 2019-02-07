#!/usr/bin/env bash

echo "$(uname)"

if [ "$(uname)" == "Darwin" ]
then
    gcc ./utils/xor.c -shared -std=c99 -O3 -o ./utils/xor.mac.lib
    pyinstaller --onefile --add-data "./utils/xor.mac.lib":. pstools.py
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]
then
    gcc ./utils/xor.c -shared -std=c99 -O3 -o ./utils/xor.nix.lib
    pyinstaller --onefile --add-data "./utils/xor.nix.lib":. pstools.py
fi