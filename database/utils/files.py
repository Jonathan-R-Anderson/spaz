import os
import json

def _load_json_file(path):
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def _save_json_file(path, data):
    with open(path, 'w') as f:
        json.dump(data, f)


def _allowed_file(filename):
    return True

