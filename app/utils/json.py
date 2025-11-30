# app/utils/json.py
from pathlib import Path
from typing import Any, Dict, Optional
import json, config


def load_json(path: str | Path) -> Optional[Any]:
    """
    Charge un fichier JSON et retourne l'objet Python.
    Si le fichier n'existe pas, retourne None.
    """
    p = Path(path)
    if not p.exists():
        return None
    try:
        with p.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Si le JSON est corrompu, remonter l'erreur pour debug
        raise


def save_json(path: str | Path, data: Any) -> None:
    """
    Sauvegarde atomiquement `data` (objet Python) en JSON à `path`.
    Utilise un fichier temporaire puis un replace pour éviter d'écraser en cours d'écriture.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + ".tmp")

    # write to tmp file
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    # atomic replace
    tmp.replace(p)

def load_users() -> Dict[str, Any]:
    return load_json(config.USERS_FILE) or {}

def save_users(d: Dict[str, Any]) -> None:
    save_json(config.USERS_FILE, d)