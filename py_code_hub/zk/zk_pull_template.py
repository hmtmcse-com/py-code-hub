import json
import base64
from zk import ZK, const

# --- DEVICE CONFIGURATION ---
DEVICE_IP = "10.0.12.161"  # IP of your SpeedFace-V5L
DEVICE_PORT = 4370  # Default ZKTeco Communication Port
OUTPUT_FILE = "speedface_backup.json"


def pull_and_save_backup():
    zk = ZK(DEVICE_IP, port=DEVICE_PORT, timeout=10, password=123456, force_udp=False)
    conn = None

    try:
        print(f"Connecting to SpeedFace terminal at {DEVICE_IP}:{DEVICE_PORT}...")
        conn = zk.connect()
        conn.disable_device()  # Lock device interactions during pull

        print("Connected! Extracting user profiles...")
        users = conn.get_users()
        print(f"Found {len(users)} total users on terminal.")

        # Pull all biometric templates directly from local storage
        print("Fetching template payloads...")
        templates = conn.get_templates()

        backup_payload = []

        for user in users:
            user_entry = {
                "uid": user.uid,
                "user_id": str(user.user_id),
                "name": user.name,
                "privilege": user.privilege,
                "password": user.password,
                "group_id": str(user.group_id),
                "card": user.card,
                "templates": []
            }

            # Link templates to this user
            for tmpl in templates:
                if tmpl.uid == user.uid:
                    # Convert raw binary payload into Base64 for safe JSON writing
                    raw_bytes = tmpl.template
                    if isinstance(raw_bytes, str):
                        raw_bytes = raw_bytes.encode('latin1')

                    encoded_template = base64.b64encode(raw_bytes).decode('utf-8')

                    user_entry["templates"].append({
                        "size": tmpl.size,
                        "uid": tmpl.uid,
                        "fid": tmpl.fid,  # Finger/Face ID index slot
                        "valid": tmpl.valid,
                        "template_base64": encoded_template
                    })

            backup_payload.append(user_entry)

        # Write data structure locally
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(backup_payload, f, indent=4)

        print(f"\nSUCCESS: Backup created with {len(backup_payload)} users!")
        print(f"Saved to local file: '{OUTPUT_FILE}'")

    except Exception as e:
        print(f"\nERROR: Failed to pull data from terminal: {e}")
    finally:
        if conn:
            conn.enable_device()
            conn.disconnect()
            print("Disconnected from terminal.")


if __name__ == "__main__":
    pull_and_save_backup()