#!/bin/sh
# Herramientas de comprobación de docs/ingenieria/08_PLAN_DE_PRUEBAS.md § 4.4, en ~/.cache/lorraine-tools/,
# sin tocar el sistema. Las usa tools/comprobar.py. Volver a ejecutarlo no baja lo que ya está.
#   - ODF Validator 0.13.0 (ODF Toolkit, Apache 2), un .jar para el Java del sistema
#   - OOXML-Validator 2.1.6 (MIT), la versión para Linux con su propio .NET dentro
#   - un venv con openpyxl y python-docx
set -e
D="${LORRAINE_TOOLS:-$HOME/.cache/lorraine-tools}"
mkdir -p "$D"

JAR="$D/odfvalidator-0.13.0-jar-with-dependencies.jar"
if [ ! -f "$JAR" ]; then
    curl -fL -o "$JAR.part" "https://repo1.maven.org/maven2/org/odftoolkit/odfvalidator/0.13.0/odfvalidator-0.13.0-jar-with-dependencies.jar"
    mv "$JAR.part" "$JAR"
fi

OX="$D/ooxml-validator"
if [ ! -d "$OX" ]; then
    curl -fL -o "$D/ooxml-validator.zip" "https://github.com/mikeebowen/OOXML-Validator/releases/download/v2.1.6/linux-x64.zip"
    mkdir -p "$OX.part" && unzip -q "$D/ooxml-validator.zip" -d "$OX.part" && mv "$OX.part" "$OX"
    rm "$D/ooxml-validator.zip"
fi

if [ ! -x "$D/venv/bin/python" ]; then
    python3 -m venv "$D/venv"
    "$D/venv/bin/pip" install -q openpyxl python-docx
fi
echo "herramientas en $D"
