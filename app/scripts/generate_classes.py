import json
from pathlib import Path
from typing import Any

STORAGE = Path("storage")

def load_json(name: str) -> dict[str, Any]:
    path = STORAGE / name
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def infer_type(value: Any) -> str:
    if isinstance(value, str):
        return "str"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, dict):
        return "Dict[str, Any]"
    if isinstance(value, list):
        # On part du principe que c’est une liste de strings
        return "List[str]"
    return "Any"

def generate_dataclass(name: str, fields: dict[str, Any]) -> str:
    lines = [f"@dataclass", f"class {name}:"]
    if not fields:
        lines.append("    pass")
    else:
        for field_name, value in fields.items():
            lines.append(f"    {field_name}: {infer_type(value)}")
    return "\n".join(lines)

def main():
    # Chargement JSON
    resources = load_json("resources.json")
    recipes = load_json("recipes.json")
    professions = load_json("professions.json")

    # Sélection d’un exemple pour inférer les structures
    sample_resource = next(iter(resources.values()))
    sample_recipe = next(iter(recipes.values()))
    sample_prof = next(iter(professions.values()))

    output_file = Path("generated/generated_models.py")

    # Construction du fichier final
    content = [
        "from dataclasses import dataclass",
        "from typing import List, Dict, Any",
        "",
        generate_dataclass("Resource", sample_resource),
        "",
        generate_dataclass("Recipe", sample_recipe),
        "",
        generate_dataclass("Profession", sample_prof),
        ""
    ]

    output_file.write_text("\n".join(content), encoding="utf-8")
    print(f"✔ Classes générées dans {output_file}")

if __name__ == "__main__":
    main()
