from fastapi import FastAPI
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
    subprocess.Popen([sys.executable, script_path, val1])
    return {"message": "Lancement de la capture des mouvements !"}

@app.get("/dynamic/run")
def run():

    script_path = os.path.join(PYSCRIPT_DIR, "static_model/model_run.py")
    subprocess.Popen([sys.executable, script_path])
    return {"message": "Lancement du modele statique !"}

@app.get("/dynamic/capture")
def run():

    val1 = "Grab"
    script_path = os.path.join(PYSCRIPT_DIR, "static_model/data_capture.py")
    subprocess.Popen([sys.executable, script_path, val1])
    return {"message": "Lancement de la capture des mouvements !"}
