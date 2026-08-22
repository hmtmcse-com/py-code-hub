from zk import ZK


class SpeedFaceV5L:
    def __init__(
        self,
        ip: str,
        port: int = 4370,
        comm_key: int = 123456,
        timeout: int = 10,
    ):
        self.ip = ip
        self.port = port
        self.comm_key = comm_key
        self.timeout = timeout

        self.zk = ZK(
            self.ip,
            port=self.port,
            timeout=self.timeout,
            password=self.comm_key,
        )

        self.conn = None

    # ---------------------------------------------------------
    # Connection
    # ---------------------------------------------------------

    def connect(self):
        if self.conn:
            return self.conn

        self.conn = self.zk.connect()
        return self.conn

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()
            self.conn = None

    def enable(self):
        self.conn.enable_device()

    def disable(self):
        self.conn.disable_device()

    # ---------------------------------------------------------
    # Device information
    # ---------------------------------------------------------

    def get_device_info(self):
        self.connect()

        return {
            "name": self.conn.get_device_name(),
            "serial": self.conn.get_serialnumber(),
            "firmware": self.conn.get_firmware_version(),
            "platform": self.conn.get_platform(),
        }

    # ---------------------------------------------------------
    # Users
    # ---------------------------------------------------------

    def get_users(self):
        self.connect()
        return self.conn.get_users()

    def get_user(self, user_id: str):
        self.connect()

        users = self.conn.get_users()

        for user in users:
            if str(user.user_id) == str(user_id):
                return user

        return None

    def create_user(
        self,
        uid: int,
        user_id: str,
        name: str,
        privilege: int = 0,
        password: str = "",
        group_id: str = "",
    ):
        self.connect()

        self.conn.disable_device()

        try:
            self.conn.set_user(
                uid=uid,
                user_id=str(user_id),
                name=name,
                privilege=privilege,
                password=password,
                group_id=group_id,
            )
        finally:
            self.conn.enable_device()

    def delete_user(self, uid: int):
        self.connect()

        self.conn.disable_device()

        try:
            self.conn.delete_user(uid)
        finally:
            self.conn.enable_device()

    # ---------------------------------------------------------
    # Attendance
    # ---------------------------------------------------------

    def get_attendance(self):
        self.connect()
        return self.conn.get_attendance()

    def clear_attendance(self):
        self.connect()

        self.conn.disable_device()

        try:
            self.conn.clear_attendance()
        finally:
            self.conn.enable_device()

    # ---------------------------------------------------------
    # Device commands
    # ---------------------------------------------------------

    def restart(self):
        self.connect()
        self.conn.restart()

    def shutdown(self):
        self.connect()
        self.conn.shutdown()

    def clear_data(self):
        self.connect()

        self.conn.disable_device()

        try:
            self.conn.clear_data()
        finally:
            self.conn.enable_device()

    def enroll_face(self, uid: int):
        self.connect()

        self.conn.disable_device()

        try:
            # Start face enrollment on the terminal
            self.conn.enroll_user(uid)

        finally:
            self.conn.enable_device()


device = SpeedFaceV5L(
    ip="10.0.12.225",
    port=4370,
    comm_key=123456,
)
info = device.get_device_info()
print(info)

device.restart()


users = device.get_users()
for user in users:
    print(
        user.uid,
        user.user_id,
        user.name,
        user.privilege,
    )


# device.create_user(
#     uid=1001,
#     user_id="1001",
#     name="Touhid Mia",
# )
device.enroll_face(uid=1001)
print("Done")