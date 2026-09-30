from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "fba_2026_secret"

def init_db():
    con = sqlite3.connect("fba.db")
    con.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, user TEXT, content TEXT, time TEXT)")
    con.close()

init_db()

@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    con = sqlite3.connect("fba.db")
    posts = con.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    con.close()
    return render_template("home.html", posts=posts, user=session["user"])

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].lower().strip() # FIX 1
        password = request.form["pass"].strip()
        try:
            con = sqlite3.connect("fba.db")
            con.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)", (name, email, password))
            con.commit()
            con.close()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Email exists! অন্য Gmail দিয়ে ট্রাই করো বা Login করো।"
        except Exception as e:
            return f"Error: {str(e)}" # আসল Error দেখাবে
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].lower().strip()
        con = sqlite3.connect("fba.db")
        user = con.execute("SELECT * FROM users WHERE email=? AND password=?", (email, request.form["pass"])).fetchone()
        con.close()
        if user:
            session["user"] = user[1]
            return redirect("/")
        else:
            return "Wrong email or password!"
    return render_template("login.html")

@app.route("/post", methods=["POST"])
def post():
    time = datetime.now().strftime("%d %b %I:%M %p")
    con = sqlite3.connect("fba.db")
    con.execute("INSERT INTO posts (user,content,time) VALUES (?,?,?)", (session["user"], request.form["content"], time))
    con.commit()
    con.close()
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# নতুন - সব ডাটা ক্লিয়ার করার জন্য
@app.route("/reset")
def reset():
    if os.path.exists("fba.db"):
        os.remove("fba.db")
    init_db()
    return "Database Cleared! এখন নতুন Gmail দিয়ে Register করো। <a href='/register'>Register</a>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
