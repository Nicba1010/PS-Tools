#!/usr/bin/env bash

plat=$(echo "$(uname)" | tr '[:upper:]' '[:lower:]')
echo "$plat"

gcc xor.c sha1.c -shared -std=c99 -O3 -o "./utils/xor.$plat.lib"
pyinstaller --onefile --add-data "./utils/xor.$plat.lib":"utils" --add-data "./format/pkg/naming_exceptions.txt";"format/pkg" pstools.py