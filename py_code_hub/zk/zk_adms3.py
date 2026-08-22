import time
from quart import Quart, request, jsonify, Response

app = Quart(__name__)

# =====================================================================
# IN-MEMORY STORES (Replace with PostgreSQL, MySQL, or MongoDB in production)
# =====================================================================

# Command Queue: {"SN": [{"id": "1001", "cmd": "...", "raw": "C:1001:..."}]}
COMMAND_QUEUE = {}

# Command Status Tracking: {"1001": {"sn": "...", "status": "PENDING", ...}}
COMMAND_RESULTS = {}

# Device Registry/Heartbeat Tracker: {"SN": {"last_seen": timestamp, ...}}
DEVICES = {}

# Stored Attendance Records
ATTENDANCE_LOGS = []

COMMAND_COUNTER = 1000  # Auto-incrementing command ID


def make_text_response(content: str, status: int = 200) -> Response:
    content = content.replace("\r\n", "\n").replace("\n", "\r\n")
    if not content.endswith("\r\n"):
        content += "\r\n"
    return Response(content, status=status, mimetype="text/plain; charset=utf-8")


def parse_kv_line(line: str) -> dict:
    """Helper to parse tab-separated key=value lines from rtlog/rtstate."""
    data = {}
    for item in line.split("\t"):
        if "=" in item:
            k, v = item.split("=", 1)
            data[k.strip()] = v.strip()
    return data


# =====================================================================
# REST API FOR YOUR FRONTEND / ADMIN PANEL
# =====================================================================

@app.route("/api/commands/enqueue", methods=["POST"])
async def api_enqueue_command():
    """Enqueue a command for a specific ZKTeco device."""
    global COMMAND_COUNTER
    data = await request.get_json()

    sn = data.get("sn")
    action = data.get("action")
    payload = data.get("payload", {})

    if not sn or not action:
        return jsonify({"error": "Missing required fields 'sn' or 'action'"}), 400

    COMMAND_COUNTER += 1
    cmd_id = str(COMMAND_COUNTER)

    # Build ZKTeco Command Strings
    if action == "UPDATE_USER":
        pin = payload.get("pin")
        name = payload.get("name", "")
        card = payload.get("card", "0")
        group = payload.get("group", 1)
        pri = payload.get("Privilege", 0)  # 0=Normal, 14=Admin
        # adms_cmd = f"DATA UPDATE USERINFO PIN={pin} Name={name} Card={card} Pri={pri}"
        adms_cmd = (
            f"C:{cmd_id}:DATA UPDATE USERINFO "
            f"PIN={pin}\t"
            f"Name={name}\t"
            f"Privilege={pri}\t"
            f"Card={card}\t"
            f"Grp={group}"
        )

    elif action == "DELETE_USER":
        pin = payload.get("pin")
        adms_cmd = f"DATA DELETE USERINFO PIN={pin}"

    elif action == "REBOOT":
        adms_cmd = "REBOOT"

    elif action == "CLEAR_LOG":
        adms_cmd = "CLEAR LOG"

    elif action == "CHECK":
        adms_cmd = "CHECK"

    elif action == "CUSTOM":
        adms_cmd = payload.get("raw_cmd", "")

    else:
        return jsonify({"error": f"Unsupported action '{action}'"}), 400

    formatted_cmd = f"C:{cmd_id}:{adms_cmd}"

    # Queue command
    if sn not in COMMAND_QUEUE:
        COMMAND_QUEUE[sn] = []

    COMMAND_QUEUE[sn].append({"id": cmd_id, "action": action, "raw": formatted_cmd})

    # Track command
    COMMAND_RESULTS[cmd_id] = {
        "id": cmd_id,
        "sn": sn,
        "command": formatted_cmd,
        "status": "PENDING",
        "return_code": None,
        "created_at": int(time.time()),
        "executed_at": None,
    }

    print(f"[API] Queued command {cmd_id} for SN {sn}: {formatted_cmd}")
    return jsonify({"success": True, "command_id": cmd_id, "sn": sn, "formatted_cmd": formatted_cmd}), 201


@app.route("/api/commands/status/<cmd_id>", methods=["GET"])
async def api_get_command_status(cmd_id):
    """Check execution status of a command."""
    result = COMMAND_RESULTS.get(cmd_id)
    if not result:
        return jsonify({"error": "Command ID not found"}), 404
    return jsonify(result), 200


@app.route("/api/attendance", methods=["GET"])
async def api_get_attendance():
    """Retrieve all parsed attendance records."""
    return jsonify({"count": len(ATTENDANCE_LOGS), "data": ATTENDANCE_LOGS}), 200


@app.route("/api/devices", methods=["GET"])
async def api_get_devices():
    """Get active devices and their online status."""
    return jsonify({"devices": DEVICES}), 200


# =====================================================================
# ZKTECO ADMS PUSH PROTOCOL ENDPOINTS
# =====================================================================

@app.route("/iclock/registry", methods=["GET", "POST"])
async def handle_registry():
    """1. Device Initial Registration / Handshake."""
    sn = request.args.get("SN", "UNKNOWN")
    DEVICES[sn] = {"last_seen": int(time.time()), "status": "ONLINE"}
    print(f"[*] /iclock/registry handshake from SN: {sn}")

    body = (
        f"RegistryCode={sn}\n"
        "ServerVersion=1.0.0\n"
        "ServerName=Quart-ADMS-Server\n"
        "PushProtVer=3.1.2\n"
        "ErrorDelay=60\n"
        "Delay=30\n"
        "TransTimes=00:00;23:59\n"
        "TransInterval=1\n"
        "Realtime=1\n"
        "Encrypt=0"
    )
    return make_text_response(body)


@app.route("/iclock/cdata", methods=["GET", "POST"])
async def handle_cdata():
    """2. Options Handshake & Attendance/State Data Logging."""
    sn = request.args.get("SN", "UNKNOWN")
    DEVICES[sn] = {"last_seen": int(time.time()), "status": "ONLINE"}

    # --- GET: Device Option Sync ---
    if request.method == "GET":
        options = request.args.get("options")
        print(f"[*] /iclock/cdata GET options request from SN: {sn}")
        current_ts = int(time.time())
        body = (
            f"GET OPTION FROM: {sn}\n"
            f"Stamp={current_ts}\n"
            f"OpStamp={current_ts}\n"
            "ErrorDelay=60\n"
            "Delay=30\n"
            "TransTimes=00:00;23:59\n"
            "TransInterval=1\n"
            "Realtime=1\n"
            "Encrypt=0"
        )
        return make_text_response(body)

    # --- POST: Log Ingestion ---
    table = request.args.get("table", "UNKNOWN")
    raw_data = await request.get_data(as_text=True)
    lines = [line.strip() for line in raw_data.splitlines() if line.strip()]

    # A. Handle Access Control Real-Time Logs (rtlog)
    if table == "rtlog":
        for line in lines:
            rec = parse_kv_line(line)
            event_code = rec.get("event")

            # Event 0 or 3 = Verification Success / Access Granted
            if event_code in ["0", "3"]:
                log_entry = {
                    "sn": sn,
                    "user_id": rec.get("pin"),
                    "timestamp": rec.get("time"),
                    "in_out_status": rec.get("inoutstatus", "0"),  # 0=In, 1=Out
                    "verify_type": rec.get("verifytype"),  # 15=Face, 1=FP, 2=Card
                    "card_no": rec.get("cardno", "0"),
                    "raw_event": event_code,
                }
                ATTENDANCE_LOGS.append(log_entry)
                print(
                    f"[+] [SUCCESS LOG] User: {log_entry['user_id']} | Time: {log_entry['timestamp']} | Type: {log_entry['verify_type']}")
            else:
                print(f"[!] [ACCESS DENIED/ALARM] SN: {sn} | User: {rec.get('pin')} | Event: {event_code}")

    # B. Handle Traditional Attendance Logs (ATTLOG)
    elif table == "ATTLOG":
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                user_id = parts[0]
                timestamp = f"{parts[1]} {parts[2]}" if len(parts) > 2 else parts[1]
                in_out = parts[3] if len(parts) > 3 else "0"

                log_entry = {
                    "sn": sn,
                    "user_id": user_id,
                    "timestamp": timestamp,
                    "in_out_status": in_out,
                    "type": "ATTLOG"
                }
                ATTENDANCE_LOGS.append(log_entry)
                print(f"[+] [ATTLOG] User: {user_id} | Time: {timestamp}")

    # C. Handle Door/Hardware State (rtstate)
    elif table == "rtstate":
        for line in lines:
            state_data = parse_kv_line(line)
            print(
                f"[*] [HARDWARE STATE] SN: {sn} | Sensor: {state_data.get('sensor')} | Door: {state_data.get('door')}")

    return make_text_response(f"OK: {len(lines)}")


@app.route("/iclock/getrequest", methods=["GET"])
async def handle_getrequest():
    """3. Device Heartbeat & Command Polling."""
    sn = request.args.get("SN", "UNKNOWN")
    DEVICES[sn] = {"last_seen": int(time.time()), "status": "ONLINE"}
    print(sn)

    # Dispatch pending commands if queue is not empty
    if sn in COMMAND_QUEUE and len(COMMAND_QUEUE[sn]) > 0:
        cmd_obj = COMMAND_QUEUE[sn].pop(0)
        cmd_id = cmd_obj["id"]

        if cmd_id in COMMAND_RESULTS:
            COMMAND_RESULTS[cmd_id]["status"] = "DISPATCHED"

        print(f"[>] Dispatched command to SN {sn}: {cmd_obj['raw']}")
        return make_text_response(cmd_obj["raw"])

    # Default response when no commands are pending
    return make_text_response("OK")


@app.route("/iclock/devicecmd", methods=["POST"])
async def handle_devicecmd():
    """4. Command Result Receipt."""
    sn = request.args.get("SN", "UNKNOWN")
    raw_data = await request.get_data(as_text=True)

    print(f"[<] Command Result from SN: {sn} | Raw: {raw_data.strip()}")

    # Parse response format: ID=1001&Return=0&CMD=DATA UPDATE USERINFO
    params = {}
    for part in raw_data.strip().split("&"):
        if "=" in part:
            k, v = part.split("=", 1)
            params[k] = v

    cmd_id = params.get("ID")
    return_code = params.get("Return")

    if cmd_id and cmd_id in COMMAND_RESULTS:
        COMMAND_RESULTS[cmd_id]["return_code"] = return_code
        COMMAND_RESULTS[cmd_id]["status"] = "SUCCESS" if return_code == "0" else "FAILED"
        COMMAND_RESULTS[cmd_id]["executed_at"] = int(time.time())

    return make_text_response("OK")


@app.route("/iclock/querydata", methods=["POST"])
async def handle_querydata():
    """5. Biometric Templates Upload Processing."""
    sn = request.args.get("SN", "UNKNOWN")
    raw_data = await request.get_data(as_text=True)
    print(f"[+] /iclock/querydata from SN {sn}: {raw_data.strip()[:100]}...")
    return make_text_response("OK")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)