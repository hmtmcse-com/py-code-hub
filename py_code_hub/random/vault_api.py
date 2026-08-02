import os
import base64
import sqlite3
import jwt
import datetime
from functools import wraps
from quart import Quart, request, jsonify
from argon2 import PasswordHasher

# ---------------- CONFIG ----------------
app = Quart(__name__)

DB_FILE = "vault.db"
JWT_SECRET = "CHANGE_THIS_SECRET"
JWT_ALG = "HS256"

ph = PasswordHasher()

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
            encrypted_secret TEXT,
            iv TEXT
        );

        CREATE TABLE IF NOT EXISTS vault_shares (
            id INTEGER PRIMARY KEY,
            vault_item_id INTEGER,
            shared_with INTEGER,
            encrypted_item_key TEXT
        );
        """)

init_db()

# ---------------- JWT ----------------
def create_token(user_id: int):
    return jwt.encode(
        {
            "sub": user_id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
        },
        JWT_SECRET,
        algorithm=JWT_ALG
    )

def auth_required(fn):
    @wraps(fn)
    async def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return {"error": "unauthorized"}, 401
        try:
            token = auth.replace("Bearer ", "")
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
            request.user_id = payload["sub"]
        except:
            return {"error": "unauthorized"}, 401
        return await fn(*args, **kwargs)
    return wrapper

# ---------------- AUTH API ----------------
@app.post("/auth/register")
async def register():
    data = await request.json
    salt = os.urandom(16)

    with db() as con:
        con.execute(
            "INSERT INTO users (email, password_hash, vault_salt) VALUES (?, ?, ?)",
            (data["email"], ph.hash(data["password"]), salt)
        )

    return {"status": "registered"}

@app.post("/auth/login")
async def login():
    data = await request.json

    with db() as con:
        user = con.execute(
            "SELECT id, password_hash, vault_salt FROM users WHERE email=?",
            (data["email"],)
        ).fetchone()

    if not user:
        return {"error": "invalid"}, 401

    ph.verify(user[1], data["password"])

    return {
        "access_token": create_token(user[0]),
        "vault_salt": base64.b64encode(user[2]).decode()
    }

# ---------------- VAULT API ----------------
@app.post("/vault")
@auth_required
async def create_secret():
    data = await request.json

    with db() as con:
        cur = con.execute(
            """
            INSERT INTO vault_items (owner_id, encrypted_secret, iv)
            VALUES (?, ?, ?)
            """,
            (request.user_id, data["encrypted_secret"], data["iv"])
        )
        item_id = cur.lastrowid

        con.execute(
            """
            INSERT INTO vault_shares (vault_item_id, shared_with, encrypted_item_key)
            VALUES (?, ?, ?)
            """,
            (item_id, request.user_id, data["encrypted_item_key"])
        )

    return {"id": item_id}

@app.get("/vault")
@auth_required
async def list_secrets():
    with db() as con:
        rows = con.execute("""
            SELECT v.id
            FROM vault_items v
            JOIN vault_shares s ON v.id = s.vault_item_id
            WHERE s.shared_with=?
        """, (request.user_id,)).fetchall()

    return {"items": [r[0] for r in rows]}

@app.get("/vault/<int:item_id>")
@auth_required
async def read_secret(item_id):
    with db() as con:
        row = con.execute("""
            SELECT encrypted_secret, iv, encrypted_item_key
            FROM vault_items v
            JOIN vault_shares s ON v.id = s.vault_item_id
            WHERE v.id=? AND s.shared_with=?
        """, (item_id, request.user_id)).fetchone()

    if not row:
        return {"error": "forbidden"}, 403

    return {
        "encrypted_secret": row[0],
        "iv": row[1],
        "encrypted_item_key": row[2]
    }

# ---------------- SHARING ----------------
@app.post("/vault/<int:item_id>/share")
@auth_required
async def share_secret(item_id):
    data = await request.json

    with db() as con:
        target = con.execute(
            "SELECT id FROM users WHERE email=?",
            (data["email"],)
        ).fetchone()

    if not target:
        return {"error": "user not found"}, 404

    with db() as con:
        con.execute(
            """
            INSERT INTO vault_shares (vault_item_id, shared_with, encrypted_item_key)
            VALUES (?, ?, ?)
            """,
            (item_id, target[0], data["encrypted_item_key"])
        )

    return {"status": "shared"}

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run()
