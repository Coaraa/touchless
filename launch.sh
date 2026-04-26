#!/bin/bash

# Chemin vers l'activation du venv
VENV_PATH="./venv/bin/activate"

if [ -f "$VENV_PATH" ]; then
    echo "[System] Activation du venv Python..."
    source "$VENV_PATH"
else
    echo "[Error] venv introuvable dans $VENV_PATH"
    exit 1
fi

trap "kill 0" EXIT

echo "--- Lancement des services ---"

uvicorn API.main:app --reload --port 8000 &
PID_API=$! # On récupère l'ID du processus Python

cargo run --release &
PID_RUST=$! # On récupère l'ID du processus Rust

echo "--- Monitoring (Ctrl+C pour arrêter) ---"

# Tant que les deux PID existent
while kill -0 $PID_API 2>/dev/null && kill -0 $PID_RUST 2>/dev/null; do
    sleep 1
done

echo "[System] Un des services s'est arrêté. Fermeture du script..."

kill $PID_API $PID_RUST 2>/dev/null

wait 2>/dev/null

echo "[System] Tout est arrêté proprement."
