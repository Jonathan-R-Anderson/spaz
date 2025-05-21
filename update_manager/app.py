import os, tarfile, json, shutil, subprocess
from datetime import datetime

PROJECT_DIR = os.getenv("PROJECT_DIR", "/app")
BACKUP_DIR = "./rollback"
DEPLOYMENTS_FILE = "./deployments/contracts.json"

def archive_project():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"{timestamp}_backup.tar.gz")
    with tarfile.open(backup_path, "w:gz") as tar:
        tar.add(PROJECT_DIR, arcname=os.path.basename(PROJECT_DIR))
    print(f"[✔] Project archived to: {backup_path}")
    return backup_path

def push_update():
    print("[⟳] Updating project...")
    archive_project()
    subprocess.run(["./update_hooks/post_update.sh"])
    print("[✔] Update pushed.")

def rollback(backup_file):
    print(f"[⤺] Rolling back using {backup_file}...")
    shutil.rmtree(PROJECT_DIR, ignore_errors=True)
    with tarfile.open(os.path.join(BACKUP_DIR, backup_file), "r:gz") as tar:
        tar.extractall(path="/")
    print("[✔] Rollback completed.")

def track_contract(name, address, abi_path):
    with open(DEPLOYMENTS_FILE, "r+") as f:
        data = json.load(f)
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(abi_path) as abi_file:
            abi = json.load(abi_file)
        data[version] = {"name": name, "address": address, "abi": abi}
        f.seek(0)
        json.dump(data, f, indent=2)
    print(f"[✔] Tracked contract {name} at {address}")

# Main execution for CLI
if __name__ == "__main__":
    import sys
    cmd = sys.argv[1]
    if cmd == "update":
        push_update()
    elif cmd == "rollback" and len(sys.argv) > 2:
        rollback(sys.argv[2])
    elif cmd == "track" and len(sys.argv) > 4:
        track_contract(sys.argv[2], sys.argv[3], sys.argv[4])
    else:
        print("Usage: update | rollback <filename> | track <name> <address> <abi_path>")
