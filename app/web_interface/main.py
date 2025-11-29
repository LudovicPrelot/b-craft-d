from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import json
import config
from pathlib import Path

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def load(file):
    return json.load(open(file, encoding="utf-8"))

def save(file, data):
    json.dump(data, open(file, "w", encoding="utf-8"), indent=4, ensure_ascii=False)

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ---------------- PROFESSION CRUD ----------------

@app.get("/professions")
async def get_professions(request: Request):
    data = load(config.PROFESSIONS_FILE)
    return templates.TemplateResponse("professions.html", {"request": request, "professions": data})

@app.post("/professions/add")
async def add_profession(id: str = Form(), name: str = Form()):
    data = load(config.PROFESSIONS_FILE)
    data[id] = {
        "id": id,
        "name": name,
        "resources_found": [],
        "allowed_recipes": [],
        "subclasses": []
    }
    save(config.PROFESSIONS_FILE, data)
    return RedirectResponse("/professions", status_code=303)
