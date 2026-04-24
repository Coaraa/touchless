from fastapi import FastAPI, HTTPException
import sys
import os
import subprocess

# BASE_DIR sera le dossier 'py_scripts/static_model/'
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(CURRENT_DIR)
PYSCRIPT_DIR = os.path.join(BASE_DIR, "py_scripts")

app = FastAPI()

@app.get("/")
async def Welcome():
    return {"message": "Hello from FastAPI!"}

@app.get("/static/run")
def run():

    script_path = os.path.join(PYSCRIPT_DIR, "static_model/model_run.py")
    subprocess.Popen([sys.executable, script_path])
    return {"message": "Lancement du modele statique !"}

@app.get("/static/capture")
def run():

    val1 = "Grab"
    script_path = os.path.join(PYSCRIPT_DIR, "static_model/data_capture.py")

    try:
        # .run() attend que le processus se termine
        result = subprocess.run(
            [sys.executable, script_path, val1],
            check=False  # On gère l'erreur manuellement via le returncode
        )

        # En général, 0 = Succès ou Fermeture normale (ESC)
        if result.returncode == 0:
            return {"status": "success", "message": "Capture terminée normalement."}
        else:
            return {"status": "error", "message": f"Le script a quitté avec le code {result.returncode}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dynamic/run")
def run():

    script_path = os.path.join(PYSCRIPT_DIR, "dynamic_model/dynamic_model_run.py")
    subprocess.Popen([sys.executable, script_path])
    return {"message": "Lancement du modele dynamique !"}

@app.get("/dynamic/capture")
def run():

    val1 = "Grab"
    script_path = os.path.join(PYSCRIPT_DIR, "dynamic_model/data_capture_dynamic.py")
    subprocess.Popen([sys.executable, script_path, val1])
    return {"message": "Lancement de la capture des mouvements !"}
