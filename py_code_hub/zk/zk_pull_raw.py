import json
import base64
import struct
from zk import ZK

# ==========================================
# DEVICE CONFIGURATION
# ==========================================
DEVICE_IP = "10.0.12.161"  # IP address of your SpeedFace-V5L
DEVICE_PORT = 4370  # Default ZKTeco socket port
COMM_KEY = 123456  # Set your terminal Comm Key / Password here (Default is 0)
OUTPUT_FILE = "speedface_backup.json"

# Internal ZK Binary Command Protocols
CMD_DATA_WRTQ = 1500  # Raw database query command


def get_persbdata_templates(conn):
    """
    Queries the device's internal 'persbdata' table to pull Visible Light
    Face vector data directly from the terminal hardware.
    """
    face_templates = {}
    try:
        # Request table structure: persbdata (Stores Visible Light Face Data)
        table_name = b"persbdata\x00"
        res = conn.send_command(CMD_DATA_WRTQ, table_name)

        if res.status and res.data:
            raw_data = res.data
            print(f"-> Retreived {len(raw_data)} bytes from PersBData table.")

            # Walk through the binary buffer to map user IDs to face templates
            offset = 0
            while offset < len(raw_data):
                if len(raw_data[offset:]) < 12:
                    break

                pin_length = raw_data[offset]
                if pin_length == 0 or pin_length > 32:
                    offset += 1
                    continue

                try:
                    user_id = raw_data[offset + 1: offset + 1 + pin_length].decode('utf-8', errors='ignore')
                    chunk_size = struct.unpack('<H', raw_data[offset + 1 + pin_length: offset + 3 + pin_length])[0]
                    tmpl_bytes = raw_data[offset + 3 + pin_length: offset + 3 + pin_length + chunk_size]

                    if user_id and tmpl_bytes:
                        face_templates[user_id] = base64.b64encode(tmpl_bytes).decode('utf-8')

                    offset += (3 + pin_length + chunk_size)
                except Exception:
                    offset += 1

    except Exception as e:
        print(f"-> PersBData Buffer extraction notice: {e}")

    return face_templates


def pull_and_save_data():
    # Initialize connection passing the specified COMM_KEY password
    zk = ZK(
        DEVICE_IP,
        port=DEVICE_PORT,
        timeout=10,
        password=COMM_KEY,  # <--- Password applied here
        force_udp=False
    )
    conn = None

    try:
        print(f"Connecting to SpeedFace-V5L ({DEVICE_IP}:{DEVICE_PORT}) with Password: {COMM_KEY}...")
        conn = zk.connect()
        conn.disable_device()  # Lock device display during extraction
        print("Connected successfully!")

        # 1. Extract User Profiles
        print("Fetching user list...")
        users = conn.get_users()
        print(f"Found {len(users)} user profiles.")

        # 2. Extract Visible Light Face Templates via Raw Protocols
        print("Fetching Visible Light face templates...")
        vl_templates = get_persbdata_templates(conn)

        # 3. Extract standard legacy templates (Fingerprints / Badges if present)
        standard_templates = []
        try:
            standard_templates = conn.get_templates()
        except Exception:
            pass

        backup_payload = []

        # 4. Map and build JSON structure
        for user in users:
            user_id_str = str(user.user_id)
            user_entry = {
                "uid": user.uid,
                "user_id": user_id_str,
                "name": user.name,
                "privilege": user.privilege,
                "password": user.password,
                "group_id": str(user.group_id),
                "card": user.card,
                "face_template_vl": None,
                "other_templates": []
            }

            # Link Visible Light Face Template if found
            if user_id_str in vl_templates:
                user_entry["face_template_vl"] = vl_templates[user_id_str]

            # Link fingerprint or badge templates if found
            for tmpl in standard_templates:
                if tmpl.uid == user.uid:
                    raw_bytes = tmpl.template if isinstance(tmpl.template, bytes) else tmpl.template.encode('latin1')
                    user_entry["other_templates"].append({
                        "fid": tmpl.fid,
                        "size": tmpl.size,
                        "template_base64": base64.b64encode(raw_bytes).decode('utf-8')
                    })

            backup_payload.append(user_entry)

        # 5. Save locally to file
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(backup_payload, f, indent=4)

        print("\n" + "=" * 40)
        print(f"SUCCESS: Exported {len(backup_payload)} users!")
        print(f"Saved locally to: '{OUTPUT_FILE}'")
        print("=" * 40)

    except Exception as e:
        print(f"\nERROR: Failed to pull data: {e}")
        print("Tip: Verify that the IP and Comm Key match the settings in: Menu -> Comm. Settings -> Ethernet/WiFi")
    finally:
        if conn:
            conn.enable_device()  # Unlock terminal screen
            conn.disconnect()
            print("Disconnected from terminal.")


if __name__ == "__main__":
    pull_and_save_data()