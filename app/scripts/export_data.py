# scripts/export_data.py
import json
import config

def main(outfile='export_backup.json'):
    out = {}
    for p in [config.USERS_FILE, config.PROFESSIONS_FILE, config.RECIPES_FILE, config.REFRESH_TOKENS_FILE]:
        try:
            out[p.name] = json.loads(p.read_text(encoding='utf-8'))
        except Exception:
            out[p.name] = {}
    open(outfile, 'w', encoding='utf-8').write(json.dumps(out, indent=4, ensure_ascii=False))
    print("Exporté dans", outfile)

if __name__=="__main__":
    main()
