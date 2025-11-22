# app.py
"""
Flask web app for bcrypt-based password hashing demo.
Features:
- Register (bcrypt hashes stored in JSON)
- Login (bcrypt verification)
- Compare page (show SHA-256 unsalted vs bcrypt demonstration)
- Rainbow demo (search a small sample rainbow table)
This file is intentionally simple for learning.
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import bcrypt
import json
import os
import hashlib

# ---------- Configuration ----------
USERS_FILE = "users_sample.json"      # commit-safe sample file (real users.json should be ignored)
RAINBOW_FILE = "rainbow_sample.txt"   # sample rainbow table (safe to commit)
app = Flask(__name__)
app.secret_key = "replace-with-a-random-secret-for-production"  # used by Flask flash messaging

# ---------- Utility functions ----------
def load_json(path):
    """Load JSON from path or return empty dict."""
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    """Write JSON to path."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ---------- Routes ----------
@app.route("/")
def index():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("register"))

        users = load_json(USERS_FILE)
        if username in users:
            flash("Username already exists. Choose another.", "warning")
            return redirect(url_for("register"))

        # bcrypt handles salt internally with gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

        # store as string for JSON
        users[username] = {"bcrypt_hash": hashed.decode("utf-8")}
        save_json(USERS_FILE, users)

        flash("Registration successful! You can log in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        users = load_json(USERS_FILE)
        record = users.get(username)
        if not record:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

        stored_hash = record.get("bcrypt_hash", "").encode("utf-8")
        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            flash(f"Login successful — welcome, {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/compare", methods=["GET", "POST"])
def compare():
    """
    Educational: Show unsalted SHA-256 vs bcrypt.
    - Unsalted: deterministic SHA-256(password)
    - bcrypt: has salt inside the hash; two bcrypt hashes for same password differ
    """
    result = None
    if request.method == "POST":
        pw = request.form.get("password", "")
        # unsalted SHA-256 (for demonstration only)
        unsalted = hashlib.sha256(pw.encode("utf-8")).hexdigest()
        # two bcrypt examples (different salts)
        b1 = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        b2 = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        result = {"unsalted": unsalted, "bcrypt1": b1, "bcrypt2": b2}
    return render_template("compare.html", result=result)

@app.route("/rainbow", methods=["GET", "POST"])
def rainbow():
    """
    Demonstration: read small rainbow_sample.txt that contains lines "password | bcrypt_hash"
    We'll search for an exact bcrypt hash or compute the SHA-256 of a plaintext and compare
    against a precomputed UNSALTED SHA-256 table stored internally (for demo).
    """
    probe = {}
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        # load bcrypt rainbow table (exact matches only)
        bcrypt_table = {}
        if os.path.exists(RAINBOW_FILE):
            with open(RAINBOW_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(" | ")
                    if len(parts) == 2:
                        plaintext, h = parts
                        bcrypt_table[h] = plaintext

        # if user pasted a 60+ char bcrypt hash, check direct lookup
        if target.startswith("$2") and len(target) >= 60:
            probe["type"] = "bcrypt_hash"
            probe["target"] = target
            probe["found"] = bcrypt_table.get(target)
        else:
            # treat as plaintext: show its unsalted SHA-256 and whether it's in a tiny demo SHA table
            probe["type"] = "plaintext"
            probe["plaintext"] = target
            probe["sha256"] = hashlib.sha256(target.encode("utf-8")).hexdigest()
            # small built-in unsalted sample mapping for demo (common passwords)
            sample_sha_map = {
                hashlib.sha256(p.encode("utf-8")).hexdigest(): p
                for p in ["password","123456","qwerty","letmein","12345678","abc123"]
            }
            probe["sha_cracked"] = sample_sha_map.get(probe["sha256"])
    return render_template("rainbow.html", probe=probe)

# ---------- Run ----------
if __name__ == "__main__":
    # ensure sample files exist so templates don't error when reading them in UI
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, {})
    if not os.path.exists(RAINBOW_FILE):
        # create a small demo rainbow file if missing
        with open(RAINBOW_FILE, "w", encoding="utf-8") as f:
            f.write("password | " + bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8") + "\n")
            f.write("123456 | " + bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8") + "\n")
    app.run(debug=True)
