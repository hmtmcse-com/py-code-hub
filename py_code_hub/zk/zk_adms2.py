import time
from quart import Quart, request, Response

app = Quart(__name__)

# Temporary in-memory queue for commands to dispatch to devices: { "DEVICE_SN": ["C:1:CHECK", ...] }
COMMAND_QUEUE = {}


def make_text_response(content: str, status: int = 200) -> Response:
    """Helper to ensure all ADMS responses have proper text/plain content-type
    and end with an explicit newline (\n) required by ZKTeco firmware.
    """
    if not content.endswith("\n"):
        content += "\n"
    return Response(content, status=status, mimetype="text/plain; charset=utf-8")


@app.route("/iclock/registry", methods=["GET", "POST"])
async def handle_registry():
    """1. Device Initial Registration
    Device sends its SN and expects configuration back.
    """
    sn = request.args.get("SN", "UNKNOWN")
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
    """2. Options Exchange & Log Uploads
    GET: Handles handshake/options requests.
    POST: Receives attendance (ATTLOG), user info, and operational logs.
    """
    sn = request.args.get("SN", "UNKNOWN")

    # --- GET: Handshake / Option Request ---
    if request.method == "GET":
        options = request.args.get("options")
        print(f"[*] /iclock/cdata GET (options={options}) from SN: {sn}")

        current_timestamp = int(time.time())
        body = (
            f"GET OPTION FROM: {sn}\n"
            f"Stamp={current_timestamp}\n"
            f"OpStamp={current_timestamp}\n"
            "ErrorDelay=60\n"
            "Delay=30\n"
            "TransTimes=00:00;23:59\n"
            "TransInterval=1\n"
            "Realtime=1\n"
            "Encrypt=0"
        )
        return make_text_response(body)

    # --- POST: Log / Data Push ---
    table = request.args.get("table", "UNKNOWN")
    raw_data = await request.get_data(as_text=True)

    lines = [line.strip() for line in raw_data.splitlines() if line.strip()]
    count = len(lines)

    print(f"[+] /iclock/cdata POST from SN: {sn} | Table: {table} | Records: {count}")

    # Process logs (e.g., ATTLOG, OPERLOG, USERINFO)
    for line in lines:
        print(f"    --> {line}")

    # Return "OK: <count>" so the device marks the logs as successfully transmitted
    return make_text_response(f"OK: {count}")


@app.route("/iclock/getrequest", methods=["GET"])
async def handle_getrequest():
    """3. Command Polling / Heartbeat
    Device polls this endpoint periodically (defined by 'Delay') to fetch pending commands.
    """
    sn = request.args.get("SN", "UNKNOWN")

    # Check if there are commands queued for this device
    if sn in COMMAND_QUEUE and COMMAND_QUEUE[sn]:
        command = COMMAND_QUEUE[sn].pop(0)
        print(f"[>] Sending command to SN {sn}: {command}")
        return make_text_response(command)

    # Return plain "OK" when no commands are pending
    return make_text_response("OK")


@app.route("/iclock/devicecmd", methods=["POST"])
async def handle_devicecmd():
    """4. Command Result Receipt
    Device posts back the execution result of commands pulled from /iclock/getrequest.
    """
    sn = request.args.get("SN", "UNKNOWN")
    raw_data = await request.get_data(as_text=True)

    print(f"[<] Command Result from SN: {sn} | Payload: {raw_data.strip()}")
    # Example payload: ID=101&Return=0&CMD=DATA UPDATE USERINFO

    return make_text_response("OK")


@app.route("/iclock/querydata", methods=["POST"])
async def handle_querydata():
    """5. Biometric Templates & Table Query Uploads
    Device uploads requested template data (fingerprints, faces, palm).
    """
    sn = request.args.get("SN", "UNKNOWN")
    cmd_id = request.args.get("cmdid", "0")
    raw_data = await request.get_data(as_text=True)

    print(f"[+] /iclock/querydata POST from SN: {sn} (cmdid={cmd_id})")
    print(f"    --> {raw_data.strip()}")

    return make_text_response("OK")


if __name__ == "__main__":
    # Standard Quart development runner
    # Ensure port matches the ADMS server setting configured on your device (default: 80 or 8080)
    app.run(host="0.0.0.0", port=8000, debug=True)