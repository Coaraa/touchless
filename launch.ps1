# Activation du venv
$VENV_PATH = "py_scripts\venv\Scripts\Activate.ps1"

if (Test-Path $VENV_PATH) {
    Write-Host "[System] Activation du venv Python..."
    & $VENV_PATH
} else {
    Write-Host "[Error] venv introuvable dans $VENV_PATH"
    exit 1
}

Write-Host "--- Lancement des services ---"

# Lancement de FastAPI
$apiProcess = Start-Process uvicorn -ArgumentList "API.main:app","--reload","--port","8000" -PassThru

# Lancement du programme Rust
$rustProcess = Start-Process cargo -ArgumentList "run","--release" -PassThru

Write-Host "--- Monitoring (Ctrl+C pour arrêter) ---"

# Monitoring tant que les deux processus sont vivants
while ($apiProcess.HasExited -eq $false -and $rustProcess.HasExited -eq $false) {
    Start-Sleep -Seconds 1
}

Write-Host "[System] Un des services s'est arrêté. Fermeture du script..."

# Tentative d'arrêt propre
try { $apiProcess.Kill() } catch {}
try { $rustProcess.Kill() } catch {}

Write-Host "[System] Tout est arrêté proprement."
