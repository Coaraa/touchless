from xml.etree.ElementTree import tostring

from fastapi import FastAPI, HTTPException
import sys
import os
import subprocess

from scipy.constants import value

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

@app.get("/static/capture/{geste}")
def run(geste: str):

# A FAIRE : modifier dynamiquement val1

    val1 = geste
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

@app.get("/static/train")
def run():

    script_path = os.path.join(PYSCRIPT_DIR, "static_model/model_train.py")

    try:
        # .run() attend que le processus se termine
        result1 = subprocess.run(
            [sys.executable, script_path],
            check=False  # On gère l'erreur manuellement via le returncode
        )

        result2 = subprocess.run(
            [sys.executable, script_path, "data/gesture_data.csv", "gesture_model_xgb_2h.pkl", "gesture_labels_2h.pkl"],
            check=False  # On gère l'erreur manuellement via le returncode
        )

        result = result1 or result2

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


@app.get("/dynamic/capture/{geste}")
def run(geste : str):

# A FAIRE : modifier dynamiquement val1

    val1 = geste
    script_path = os.path.join(PYSCRIPT_DIR, "dynamic_model/data_capture_dynamic.py")

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

@app.get("/dynamic/train")
def run():

    script_path = os.path.join(PYSCRIPT_DIR, "dynamic_model/dynamic_model_train.py")

    try:
        # .run() attend que le processus se termine
        result1 = subprocess.run(
            [sys.executable, script_path],
            check=False  # On gère l'erreur manuellement via le returncode
        )

        # En général, 0 = Succès ou Fermeture normale (ESC)
        if result1.returncode == 0:
            return {"status": "success", "message": "Capture terminée normalement."}
        else:
            return {"status": "error", "message": f"Le script a quitté avec le code {result1.returncode}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
