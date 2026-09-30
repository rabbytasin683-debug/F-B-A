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
    if "user" not in session: return redirect("/login")
    con = sqlite3.connect("fba.db")
    posts = con.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    con.close()
    return render_template("home.html", posts=posts, user=session["user"])
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        try:
            con = sqlite3.connect("fba.db")
            con.execute("INSERT INTO users (name,email,password) VALUES (?,?,?)", (request.form["name"], request.form["email"], request.form["pass"]))
            con.commit(); con.close()
            return redirect("/login")
        except: return "Email exists!"
    return render_template("register.html")
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        con = sqlite3.connect("fba.db")
        user = con.execute("SELECT * FROM users WHERE email=? AND password=?", (request.form["email"], request.form["pass"])).fetchone()
        con.close()
        if user:
            session["user"] = user[1]
            return redirect("/")
        else: return "Wrong password!"
    return render_template("login.html")
@app.route("/post", methods=["POST"])
def post():
    time = datetime.now().strftime("%d %b %I:%M %p")
    con = sqlite3.connect("fba.db")
    con.execute("INSERT INTO posts (user,content,time) VALUES (?,?,?)", (session["user"], request.form["content"], time))
    con.commit(); con.close()
    return redirect("/")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
