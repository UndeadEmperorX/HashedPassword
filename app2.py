from flask import Flask, render_template, request, redirect, url_for, flash
import bcrypt
import hashlib
import json
import os

app = Flask(__name__)
app.secret_key = "change-me-in-production"

USERS_FILE = "users.json"
RAINBOW_FILE = "rainbow_demo.txt"

def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return redirect(url_for("register"))

        users = load_json(USERS_FILE, {})

        if username in users:
            flash("User already exists. Try a different username.", "danger")
            return redirect(url_for("register"))

        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        users[username] = hashed
        save_json(USERS_FILE, users)

        flash("Registered successfully! You can log in now.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        users = load_json(USERS_FILE, {})
        stored_hash = users.get(username)

        ok = False
        if stored_hash:
            try:
                ok = bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("utf-8"))
            except ValueError:
                ok = False

        if ok:
            flash("Login successful!", "success")
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@app.route("/compare", methods=["GET", "POST"])
def compare():
    result = None
    if request.method == "POST":
        pw = request.form.get("password", "")

        unsalted = hashlib.sha256(pw.encode("utf-8")).hexdigest()
        b1 = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        b2 = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        result = {
            "unsalted": unsalted,
            "bcrypt1": b1,
            "bcrypt2": b2,
        }

    return render_template("compare.html", result=result)

def load_rainbow_table():
    table = []
    if not os.path.exists(RAINBOW_FILE):
        return table

    with open(RAINBOW_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "|" not in line:
                continue
            plain, bc = [x.strip() for x in line.split("|", 1)]
            sha = hashlib.sha256(plain.encode("utf-8")).hexdigest()
            table.append({
                "plaintext": plain,
                "bcrypt": bc,
                "sha256": sha,
            })
    return table

@app.route("/rainbow", methods=["GET", "POST"])
def rainbow():
    probe = None

    if request.method == "POST":
        target = request.form.get("target", "").strip()
        table = load_rainbow_table()
        probe_type = "plaintext"

        sha = hashlib.sha256(target.encode("utf-8")).hexdigest()
        sha_map = {row["sha256"]: row["plaintext"] for row in table}
        sha_cracked = sha_map.get(sha)

        if target.startswith("$2a$") or target.startswith("$2b$") or target.startswith("$2y$"):
            probe_type = "bcrypt"
            found_plain = None
            for row in table:
                if row["bcrypt"] == target:
                    found_plain = row["plaintext"]
                    break

            probe = {
                "type": "bcrypt",
                "target": target,
                "found": found_plain,
            }
        else:
            probe = {
                "type": "plaintext",
                "plaintext": target,
                "sha256": sha,
                "sha_cracked": sha_cracked,
            }

    return render_template("rainbow.html", probe=probe)

if __name__ == "__main__":
    if not os.path.exists(USERS_FILE):
        save_json(USERS_FILE, {})

    if not os.path.exists(RAINBOW_FILE):
        with open(RAINBOW_FILE, "w", encoding="utf-8") as f:
            f.write("password | " + bcrypt.hashpw(b"password", bcrypt.gensalt()).decode("utf-8") + "\n")
            f.write("123456 | " + bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode("utf-8") + "\n")

    app.run(debug=True)
