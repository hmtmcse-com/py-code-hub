from datetime import datetime
from zk import ZK, const


def manage_zk_device():
    # -------------------------------------------------------------
    # 1. Configuration & Initial Setup
    # -------------------------------------------------------------
    DEVICE_IP = '10.0.100.51'  # Change to your device IP
    PORT = 4370                 # Default ZKTeco communication port
    PASSWORD = 0                # Communication password/key (0 if unset)

    # Initialize ZK instance
    zk = ZK(
        DEVICE_IP,
        port=PORT,
        timeout=5,
        password=PASSWORD,
        force_udp=False,
        ommit_ping=False
    )

    conn = None

    try:
        # ---------------------------------------------------------
        # 2. Connect to Device
        # ---------------------------------------------------------
        print(f"Connecting to ZKTeco device at {DEVICE_IP}:{PORT}...")
        conn = zk.connect()
        print(" Connected successfully!\n")

        # ---------------------------------------------------------
        # 3. Disable Device During Operations
        # ---------------------------------------------------------
        conn.disable_device()
        print("[Status] Device disabled for modifications.")

        # Print Device Specs
        print(f"Firmware Version : {conn.get_firmware_version()}")
        print(f"Device Name      : {conn.get_device_name()}")
        print(f"Serial Number    : {conn.get_serialnumber()}")
        print("-" * 65)

        # ---------------------------------------------------------
        # 4. Sync Device Real-Time Clock
        # ---------------------------------------------------------
        print("Syncing device internal clock to server time...")
        conn.set_time(datetime.now())
        print(f" Device time updated to: {conn.get_time()}\n")

        # ---------------------------------------------------------
        # 5. Access Control Group / Time Rule Setup
        # ---------------------------------------------------------
        # Set to desired Group ID (e.g., '1' for 24/7, '2' for custom time shift)
        GROUP_ID = '2'

        # ---------------------------------------------------------
        # 6. User Creation Setup
        # ---------------------------------------------------------
        new_uid = 105                        # Unique sequence integer
        new_user_id = '1005'                 # Display ID string
        user_name = 'Alice Smith'            # Full name
        user_password = '4321'               # Keypad access code
        user_privilege = const.USER_DEFAULT  # Standard user
        card_num = 0                         # RFID Card number (0 if none)

        print(f"Adding user '{user_name}' (ID: {new_user_id}) assigned to Group '{GROUP_ID}'...")

        # Save / Update User on Device (user_tz removed)
        conn.set_user(
            uid=new_uid,
            name=user_name,
            privilege=user_privilege,
            password=user_password,
            group_id=GROUP_ID,
            user_id=new_user_id,
            card=card_num
        )
        print(" User created and assigned to group time rule successfully!\n")

        # ---------------------------------------------------------
        # 7. Fetch & Verify User List
        # ---------------------------------------------------------
        print("Fetching current user list from device...")
        users = conn.get_users()

        print(f"{'UID':<6} | {'User ID':<10} | {'Name':<20} | {'Role':<8} | {'Group'}")
        print("-" * 65)

        user_verified = False
        for user in users:
            role = "Admin" if user.privilege == const.USER_ADMIN else "User"
            grp = getattr(user, 'group_id', 'N/A')
            print(f"{user.uid:<6} | {user.user_id:<10} | {user.name:<20} | {role:<8} | Group: {grp}")

            if str(user.user_id) == str(new_user_id):
                user_verified = True

        print("-" * 65)
        if user_verified:
            print(f" Verification complete: User '{user_name}' actively registered.")

    except Exception as e:
        print(f" Connection Error: {e}")

    finally:
        # ---------------------------------------------------------
        # 8. Re-enable Device & Safely Disconnect
        # ---------------------------------------------------------
        if conn:
            conn.enable_device()
            print("\n[Status] Device re-enabled for operation.")
            conn.disconnect()
            print("[Status] Connection safely closed.")


if __name__ == "__main__":
    manage_zk_device()