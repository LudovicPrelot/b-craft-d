# app/scripts/fix_bugs.py

from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

def fix_http_imports():
    """Corrige les imports HTTPException incorrects"""
    print("🔧 Correction des imports HTTPException...")
    
    files_to_fix = [
        "routes/api/admin/professions.py",
        "routes/api/user/professions.py",
        "routes/api/user/recipes.py",
        "routes/api/user/resources.py",
    ]
    
    fixed = 0
    for rel_path in files_to_fix:
        file_path = BASE_DIR / rel_path
        if not file_path.exists():
            print(f"  ⚠️  Fichier introuvable: {rel_path}")
            continue
        
        content = file_path.read_text(encoding='utf-8')
        
        if "from http.client import HTTPException" in content:
            content = content.replace(
                "from http.client import HTTPException",
                "from fastapi import HTTPException"
            )
            file_path.write_text(content, encoding='utf-8')
            print(f"  ✅ Corrigé: {rel_path}")
            fixed += 1
        else:
            print(f"  ℹ️  Déjà correct: {rel_path}")
    
    print(f"✅ {fixed} fichier(s) corrigé(s)\n")

def fix_admin_init_duplicate():
    """Supprime le doublon router.include_router(resources_router)"""
    print("🔧 Correction du doublon dans admin/__init__.py...")
    
    file_path = BASE_DIR / "routes/api/admin/__init__.py"
    
    if not file_path.exists():
        print("  ⚠️  Fichier introuvable")
        return
    
    content = file_path.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    # Détecte et supprime les doublons
    seen = {}
    new_lines = []
    
    for line in lines:
        stripped = line.strip()
        
        # Si c'est un include_router, vérifie les doublons
        if 'router.include_router' in stripped:
            if stripped in seen:
                print(f"  🗑️  Suppression doublon: {stripped}")
                continue  # Skip cette ligne
            seen[stripped] = True
        
        new_lines.append(line)
    
    file_path.write_text('\n'.join(new_lines), encoding='utf-8')
    print("  ✅ Doublons supprimés\n")

def fix_inventory_comment():
    """Corrige le commentaire incorrect dans inventory.py"""
    print("🔧 Correction du commentaire dans inventory.py...")
    
    file_path = BASE_DIR / "routes/api/user/inventory.py"
    
    if not file_path.exists():
        print("  ⚠️  Fichier introuvable")
        return
    
    content = file_path.read_text(encoding='utf-8')
    
    if "# app/routes/api/user/devices.py" in content:
        content = content.replace(
            "# app/routes/api/user/devices.py",
            "# app/routes/api/user/inventory.py"
        )
        file_path.write_text(content, encoding='utf-8')
        print("  ✅ Commentaire corrigé\n")
    else:
        print("  ℹ️  Déjà correct\n")

def fix_loot_comment():
    """Corrige le commentaire incorrect dans loot.py"""
    print("🔧 Correction du commentaire dans admin/loot.py...")
    
    file_path = BASE_DIR / "routes/api/admin/loot.py"
    
    if not file_path.exists():
        print("  ⚠️  Fichier introuvable")
        return
    
    content = file_path.read_text(encoding='utf-8')
    
    if "# app/routes/api/admin/users.py" in content:
        content = content.replace(
            "# app/routes/api/admin/users.py",
            "# app/routes/api/admin/loot.py"
        )
        file_path.write_text(content, encoding='utf-8')
        print("  ✅ Commentaire corrigé\n")
    else:
        print("  ℹ️  Déjà correct\n")

def main():
    print("=" * 70)
    print("🔧 CORRECTION DES BUGS DE STRUCTURE")
    print("=" * 70)
    print()
    
    fix_http_imports()
    fix_admin_init_duplicate()
    fix_inventory_comment()
    fix_loot_comment()
    
    print("=" * 70)
    print("✅ TOUTES LES CORRECTIONS APPLIQUÉES !")
    print("=" * 70)
    print()
    print("📋 Prochaines étapes :")
    print("  1. Redémarre ton serveur")
    print("  2. Teste les routes /api/admin/professions")
    print("  3. Vérifie les logs")
    print("  4. Implémente le générateur CRUD (optionnel)")

if __name__ == "__main__":
    main()