import os
import base64
import sqlite3
from quart import Quart, request, jsonify, session
from argon2 import PasswordHasher
from argon2.low_level import hash_secret_raw, Type
from cryptography.fernet import Fernet

# ---------------- CONFIG ----------------
app = Quart(__name__)
app.secret_key = "dev-secret-key"  # change in prod
DB_FILE = "vault.db"

ph = PasswordHasher()  # Argon2id default

# ---------------- DATABASE ----------------
def db():
    return sqlite3.connect(DB_FILE)

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE,
            password_hash TEXT,
            vault_salt BLOB
        );

        CREATE TABLE IF NOT EXISTS vault_items (
            id INTEGER PRIMARY KEY,
            owner_id INTEGER,
            encrypted_secret BLOB
        );

        CREATE TABLE IF NOT EXISTS vault_shares (
            id INTEGER PRIMARY KEY,
            vault_item_id INTEGER,
            shared_with INTEGER,
            encrypted_item_key BLOB
        );
        """)

init_db()

# ---------------- CRYPTO ----------------
def derive_vault_key(password: str, salt: bytes) -> bytes:
    key = hash_secret_raw(
        secret=password.encode(),
        salt=salt,
        time_cost=3,
        memory_cost=64 * 1024,  # 64MB
        parallelism=2,
        hash_len=32,
        type=Type.ID
    )
    return base64.urlsafe_b64encode(key)

def encrypt(data: bytes, key: bytes) -> bytes:
    return Fernet(key).encrypt(data)

def decrypt(data: bytes, key: bytes) -> bytes:
    return Fernet(key).decrypt(data)

# ---------------- AUTH ----------------
@app.post("/register")
async def register():
    data = await request.json
    salt = os.urandom(16)
    password_hash = ph.hash(data["password"])

    with db() as con:
        con.execute(
            "INSERT INTO users (email, password_hash, vault_salt) VALUES (?, ?, ?)",
            (data["email"], password_hash, salt)
        )

    return {"status": "registered"}

@app.post("/login")
async def login():
    data = await request.json

    with db() as con:
        user = con.execute(
            "SELECT id, password_hash, vault_salt FROM users WHERE email=?",
            (data["email"],)
        ).fetchone()

    if not user:
        return {"error": "invalid"}, 401

    try:
        ph.verify(user[1], data["password"])
    except:
        return {"error": "invalid"}, 401

    session["user_id"] = user[0]
    session["vault_key"] = derive_vault_key(data["password"], user[2]).decode()

    return {"status": "logged_in"}

# ---------------- VAULT ----------------
@app.post("/vault/add")
async def add_secret():
    data = await request.json
    vault_key = session.get("vault_key").encode()

    # generate per-item key
    item_key = Fernet.generate_key()

    encrypted_secret = encrypt(data["secret"].encode(), item_key)
    encrypted_item_key = encrypt(item_key, vault_key)

    with db() as con:
        cur = con.execute(
            "INSERT INTO vault_items (owner_id, encrypted_secret) VALUES (?, ?)",
            (session["user_id"], encrypted_secret)
        )
        item_id = cur.lastrowid

        con.execute(
            "INSERT INTO vault_shares (vault_item_id, shared_with, encrypted_item_key) VALUES (?, ?, ?)",
            (item_id, session["user_id"], encrypted_item_key)
        )

    return {"vault_item_id": item_id}

@app.get("/vault/<int:item_id>")
async def read_secret(item_id):
    vault_key = session.get("vault_key").encode()

    with db() as con:
        row = con.execute("""
            SELECT v.encrypted_secret, s.encrypted_item_key
            FROM vault_items v
            JOIN vault_shares s ON v.id = s.vault_item_id
            WHERE v.id=? AND s.shared_with=?
        """, (item_id, session["user_id"])).fetchone()

    if not row:
        return {"error": "no access"}, 403

    item_key = decrypt(row[1], vault_key)
    secret = decrypt(row[0], item_key)

    return {"secret": secret.decode()}

# ---------------- SHARING ----------------
@app.post("/vault/share")
async def share_secret():
    data = await request.json
    vault_key = session.get("vault_key").encode()

    with db() as con:
        target = con.execute(
            "SELECT id, vault_salt FROM users WHERE email=?",
            (data["email"],)
        ).fetchone()

        share = con.execute("""
            SELECT encrypted_item_key
            FROM vault_shares
            WHERE vault_item_id=? AND shared_with=?
        """, (data["vault_item_id"], session["user_id"])).fetchone()

    if not target or not share:
        return {"error": "invalid"}, 400

    item_key = decrypt(share[0], vault_key)
    target_vault_key = derive_vault_key(data["target_password"], target[1])
    encrypted_for_target = encrypt(item_key, target_vault_key)

    with db() as con:
        con.execute(
            "INSERT INTO vault_shares (vault_item_id, shared_with, encrypted_item_key) VALUES (?, ?, ?)",
            (data["vault_item_id"], target[0], encrypted_for_target)
        )

    return {"status": "shared"}

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
