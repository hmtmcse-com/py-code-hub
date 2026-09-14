from dataclasses import dataclass
from ipaddress import IPv4Interface, IPv4Network
from pathlib import Path
import base64
import ipaddress
import secrets

import qrcode
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)


@dataclass(frozen=True)
class WireGuardServer:
    public_key: str
    address: str
    endpoint: str
    port: int = 51820
    dns: str = "1.1.1.1"


@dataclass(frozen=True)
class WireGuardClient:
    name: str
    private_key: str
    public_key: str
    address: str
    config: str


class WireGuardGenerator:

    def __init__(
        self,
        server: WireGuardServer,
        client_network: str,
    ):
        self.server = server
        self.client_network = IPv4Network(
            client_network,
            strict=False,
        )

    @staticmethod
    def _generate_key_pair() -> tuple[str, str]:
        private_key = X25519PrivateKey.generate()

        private_raw = private_key.private_bytes_raw()
        public_raw = private_key.public_key().public_bytes(
            Encoding.Raw,
            PublicFormat.Raw,
        )

        private_key_b64 = base64.b64encode(private_raw).decode()
        public_key_b64 = base64.b64encode(public_raw).decode()

        return private_key_b64, public_key_b64

    def _next_client_ip(self) -> str:
        hosts = list(self.client_network.hosts())

        if not hosts:
            raise ValueError("Client network has no usable addresses")

        return str(hosts[0])

    def create_client(
        self,
        name: str,
        client_ip: str | None = None,
        allowed_ips: str = "0.0.0.0/0",
    ) -> WireGuardClient:

        private_key, public_key = self._generate_key_pair()

        if client_ip is None:
            client_ip = self._next_client_ip()

        address = f"{client_ip}/32"

        config = f"""[Interface]
PrivateKey = {private_key}
Address = {address}
DNS = {self.server.dns}

[Peer]
PublicKey = {self.server.public_key}
Endpoint = {self.server.endpoint}:{self.server.port}
AllowedIPs = {allowed_ips}
PersistentKeepalive = 25
"""

        return WireGuardClient(
            name=name,
            private_key=private_key,
            public_key=public_key,
            address=address,
            config=config,
        )

    @staticmethod
    def save_config(
        client: WireGuardClient,
        directory: str = "wireguard",
    ) -> Path:

        path = Path(directory)
        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        config_file = path / f"{client.name}.conf"

        config_file.write_text(
            client.config,
            encoding="utf-8",
        )

        return config_file

    @staticmethod
    def generate_qr(
        client: WireGuardClient,
        directory: str = "wireguard",
    ) -> Path:

        path = Path(directory)
        path.mkdir(
            parents=True,
            exist_ok=True,
        )

        qr_file = path / f"{client.name}.png"

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )

        qr.add_data(client.config)
        qr.make(fit=True)

        image = qr.make_image()

        image.save(qr_file)

        return qr_file




# ============================================================
# Server configuration
# ============================================================

server = WireGuardServer(
    public_key="YOUR_SERVER_PUBLIC_KEY",
    address="10.99.0.1/24",
    endpoint="vpn.example.com",
    port=51820,
    dns="10.99.0.1",
)


# ============================================================
# Generator
# ============================================================

generator = WireGuardGenerator(
    server=server,
    client_network="10.99.0.0/24",
)


# ============================================================
# Create user
# ============================================================

client = generator.create_client(
    name="touhid-pc",
    client_ip="10.99.0.10",
    allowed_ips="10.99.0.0/24",
)


# ============================================================
# Generate files
# ============================================================

config_file = generator.save_config(
    client,
    directory="wireguard",
)

qr_file = generator.generate_qr(
    client,
    directory="wireguard",
)


# ============================================================
# Client information
# ============================================================

print("========================================")
print("WireGuard User")
print("========================================")

print("Name       :", client.name)
print("VPN IP     :", client.address)
print("Public Key :", client.public_key)
print("Private Key:", client.private_key)

print()
print("Config     :", config_file)
print("QR Code    :", qr_file)


# ============================================================
# MikroTik command
# ============================================================

print()
print("========================================")
print("MikroTik Command")
print("========================================")

print(
    f'/interface wireguard peers add '
    f'interface=wg-management '
    f'public-key="{client.public_key}" '
    f'allowed-address={client.address} '
    f'comment="{client.name}"'
)


# ============================================================
# Client configuration
# ============================================================

print()
print("========================================")
print("Client Configuration")
print("========================================")

print(client.config)