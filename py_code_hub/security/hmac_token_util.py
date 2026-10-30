import base64
import hashlib
import hmac
import secrets
import struct
import time


class HMACTokenUtil:

    @classmethod
    def create_token(cls, secret: str, expires_in: int = 300) -> str:
        if not secret:
            raise ValueError("Secret is required")

        if expires_in <= 0:
            raise ValueError("expires_in must be positive")

        expires_at = int(time.time()) + expires_in

        if expires_at > 0xFFFFFFFF:
            raise ValueError("Expiration exceeds supported range")

        payload = struct.pack(">I", expires_at) + secrets.token_bytes(12)

        signature = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256
        ).digest()[:16]

        token = base64.urlsafe_b64encode(
            payload + signature
        ).rstrip(b"=").decode("ascii")

        return token

    @classmethod
    def validate_token(cls, token: str, secret: str) -> bool:
        if not token or not secret:
            return False

        try:
            if len(token) != 43:
                return False

            encoded = token.encode("ascii")

            data = base64.b64decode(
                encoded + b"=",
                altchars=b"-_",
                validate=True
            )

            if len(data) != 32:
                return False

            payload = data[:16]
            signature = data[16:]

            expected_signature = hmac.new(
                secret.encode("utf-8"),
                payload,
                hashlib.sha256
            ).digest()[:16]

            if not hmac.compare_digest(signature, expected_signature):
                return False

            expires_at = struct.unpack(">I", payload[:4])[0]

            if time.time() >= expires_at:
                return False

            return True

        except (ValueError, UnicodeError, struct.error, TypeError):
            return False


APP_SECRET = "some-key-xyz"

# Create token (valid for 5 minutes)
token = HMACTokenUtil.create_token(
    secret=APP_SECRET,
    expires_in=300
)
print(token)

# Validate token
is_valid = HMACTokenUtil.validate_token(
    token=token,
    secret=APP_SECRET
)
print(is_valid)
