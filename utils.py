import json
import os

ROLES_FILE = 'roles.json'

def load_roles():
    if os.path.exists(ROLES_FILE):
        with open(ROLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_roles(data):
    with open(ROLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)