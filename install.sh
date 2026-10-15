#!/usr/bin/env bash
# Installe kalicheck dans /usr/local/bin (commande: kalicheck)
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 est requis." >&2
    exit 1
fi

chmod +x "$DIR/kalicheck.py"
sudo ln -sf "$DIR/kalicheck.py" /usr/local/bin/kalicheck
echo "Installé. Lance simplement : kalicheck"
echo "(le lien pointe vers ce dossier : ne le supprime pas)"
