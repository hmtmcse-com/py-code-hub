import asyncio
from quart import Quart, request, Response

app = Quart(__name__)

# Stores pending commands per device SN
# Key: SN (str) -> Value: asyncio.Queue of command strings
command_queues = {}
cmd_counter = 1000


def get_next_cmd_id() -> int:
    global cmd_counter
    cmd_counter += 1
    return cmd_counter


# ----------------------------------------------------------------------
# ADMS Hardware Endpoints
# ----------------------------------------------------------------------

@app.route("/iclock/registry", methods=["GET", "POST"])
@app.route("/iclock/registry.aspx", methods=["GET", "POST"])
async def registry():

    print("\n" + "=" * 70)
    print("ADMS REGISTRY")
    print("METHOD:", request.method)
    print("ARGS:", dict(request.args))

    body = await request.get_data()

    print("BODY:")
    print(body.decode("utf-8", errors="ignore"))
    print("=" * 70)

    sn = request.args.get("SN")

    if sn:
        command_queues.setdefault(sn, asyncio.Queue())

    return Response(
        "OK",
        status=200,
        mimetype="text/plain"
    )

# @app.route("/iclock/cdata", methods=["GET", "POST"])
# @app.route("/iclock/cdata.aspx", methods=["GET", "POST"])
# async def cdata():
#     """Receives initial connection pings, attendance logs (ATTLOG),
#     and face templates (BIODATA) pushed back after enrollment.
#     """
#     sn = request.args.get("SN", "UNKNOWN")
#     table = request.args.get("table", "")
#     print(request.args)
#
#     if request.method == "POST":
#         data = await request.get_data()
#         body_str = data.decode("utf-8", errors="ignore")
#
#         if table == "ATTLOG":
#             print(f"[{sn}] New Attendance Records:\n{body_str}")
#         elif table == "BIODATA":
#             print(f"[{sn}] New Biometric Face Template Enrolled:\n{body_str}")
#         else:
#             print(f"[{sn}] Received data for table '{table}':\n{body_str}")
#
#         return Response("OK", status=200, mimetype="text/plain")
#
#     # Initial GET configuration handshake from device
#     return Response("OK", status=200, mimetype="text/plain")


@app.route('/iclock/cdata', methods=['GET'])
def handle_cdata_get():
    sn = request.args.get('SN', '')
    options = request.args.get('options', '')

    if options == 'all' or 'options' in request.args:
        # Must start with GET OPTION FROM: <SN>
        body = (
            f"GET OPTION FROM: {sn}\n"
            "Stamp=1710000000\n"
            "OpStamp=1710000000\n"
            "ErrorDelay=60\n"
            "Delay=30\n"
            "TransTimes=00:00;23:59\n"
            "TransInterval=1\n"
            "Realtime=1\n"
            "Encrypt=0\n"
        )
        return Response(body, status=200, mimetype='text/plain')

    return Response("OK", status=200, mimetype='text/plain')

@app.route('/iclock/registry', methods=['GET', 'POST'])
def handle_registry():
    sn = request.args.get('SN', 'UNKNOWN')

    # Needs key-value config, NOT just "OK"
    body = (
        f"RegistryCode={sn}\n"
        "ServerVersion=1.0.0\n"
        "ServerName=ADMS Server\n"
        "PushProtVer=3.1.2\n"
        "ErrorDelay=60\n"
        "Delay=30\n"
        "Realtime=1\n"
    )

    return Response(body, status=200, mimetype='text/plain')


# @app.route("/iclock/getrequest", methods=["GET"])
# @app.route("/iclock/getrequest.aspx", methods=["GET"])
# async def get_request():
#     """Polled continuously by SpeedFace-V5L to pull pending server commands."""
#     sn = request.args.get("SN")
#     if not sn:
#         return Response("BAD REQUEST", status=400)
#
#     # Initialize a queue for this device if it's the first connection
#     if sn not in command_queues:
#         command_queues[sn] = asyncio.Queue()
#
#     queue = command_queues[sn]
#
#     # Pop and dispatch next queued command if available
#     if not queue.empty():
#         cmd = await queue.get()
#         print(f"[{sn}] Dispatching command to terminal: {cmd.strip()}")
#         return Response(cmd, status=200, mimetype="text/plain")
#
#     return Response("OK", status=200, mimetype="text/plain")


@app.route("/iclock/devicecmd", methods=["POST"])
@app.route("/iclock/devicecmd.aspx", methods=["POST"])
async def device_cmd_result():
    """Receives command execution feedback (e.g., ID=1001&Return=0) from terminal."""
    sn = request.args.get("SN", "UNKNOWN")
    data = await request.get_data()
    result_str = data.decode("utf-8", errors="ignore")
    print(f"[{sn}] Command Execution Result:\n{result_str}")
    return Response("OK", status=200, mimetype="text/plain")


# ----------------------------------------------------------------------
# Application API Endpoints (For your Web App / Client)
# ----------------------------------------------------------------------

@app.route("/api/enroll_face", methods=["POST"])
async def trigger_enrollment():
    """Queues a command sequence to create/update a user and launch on-screen face enrollment.

    Expected JSON Payload:
    {
        "sn": "SYZ8243802548",
        "user_id": "101",
        "name": "John Doe"
    }
    """
    payload = await request.get_json()
    sn = payload.get("sn")
    user_id = str(payload.get("user_id", ""))
    name = payload.get("name", f"User_{user_id}")

    if not sn or not user_id:
        return {"error": "Both 'sn' and 'user_id' are required"}, 400

    if sn not in command_queues:
        command_queues[sn] = asyncio.Queue()

    # Step 1: Create or Update User profile on device
    cid_user = get_next_cmd_id()
    user_cmd = f"C:{cid_user}:DATA UPDATE USERINFO PIN={user_id}\tName={name}\tPrivilege=0\n"
    await command_queues[sn].put(user_cmd)

    # Step 2: Trigger visible light face camera enrollment screen (Type=9)
    cid_enroll = get_next_cmd_id()
    enroll_cmd = f"C:{cid_enroll}:ENROLL_BIO PIN={user_id}\tType=9\n"
    await command_queues[sn].put(enroll_cmd)

    return {
        "status": "queued",
        "device_sn": sn,
        "user_id": user_id,
        "queued_commands": [user_cmd.strip(), enroll_cmd.strip()],
    }, 200


@app.route("/api/delete_user", methods=["POST"])
async def delete_user():
    """Queues a command to delete a user and their biometric templates."""
    payload = await request.get_json()
    sn = payload.get("sn")
    user_id = str(payload.get("user_id", ""))

    if not sn or not user_id:
        return {"error": "Both 'sn' and 'user_id' are required"}, 400

    if sn not in command_queues:
        command_queues[sn] = asyncio.Queue()

    cid = get_next_cmd_id()
    del_cmd = f"C:{cid}:DATA DELETE USERINFO PIN={user_id}\n"
    await command_queues[sn].put(del_cmd)

    return {"status": "queued", "device_sn": sn, "command": del_cmd.strip()}, 200


if __name__ == "__main__":
    # Host on 0.0.0.0 so network hardware can reach port 8000
    app.run(host="0.0.0.0", port=8000, debug=True)