from flask import Flask, render_template, request, redirect, session
import sqlite3, os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "fba-secret-key-2026"
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def init_db():
    con = sqlite3.connect("fba.db")
    con.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, email TEXT PRIMARY KEY, pass TEXT)")
    con.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, content TEXT, media TEXT, time TEXT, likes TEXT DEFAULT '', comments TEXT DEFAULT '')")
    con.commit(); con.close()
init_db()

@app.route("/")
def home():
    if "user" not in session: return redirect("/login")
    con = sqlite3.connect("fba.db")
    con.row_factory = sqlite3.Row
    posts = con.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    con.close()
    return render_template("home.html", user=session["user"], posts=posts)

@app.route("/editor")
def editor():
    if "user" not in session: return redirect("/login")
    return render_template("editor.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form.get("email"); pwd=request.form.get("pass")
        con=sqlite3.connect("fba.db"); cur=con.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND pass=?",(email,pwd))
        user=cur.fetchone(); con.close()
        if user:
            session["user"]=user[0]; return redirect("/")
        return "Login Failed! Wrong Email/Password"
    return render_template("login.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form.get("name"); email=request.form.get("email"); pwd=request.form.get("pass")
        try:
            con=sqlite3.connect("fba.db")
            con.execute("INSERT INTO users VALUES (?,?,?)",(name,email,pwd))
            con.commit(); con.close()
            return redirect("/login")
        except: return "Email already exists!"
    return render_template("register.html")

@app.route("/post", methods=["POST"])
def post():
    content=request.form.get("content","").strip(); media=""
    file=request.files.get("file")
    if file and file.filename:
        filename=secure_filename(file.filename)
        path=os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path); media="/"+path
    elif request.form.get("media"): media=request.form.get("media").strip()
    if not content and not media: return redirect("/")
    time=datetime.now().strftime("%d %b at %I:%M %p")
    con=sqlite3.connect("fba.db")
    con.execute("INSERT INTO posts (user,content,media,time) VALUES (?,?,?,?)",(session["user"],content,media,time))
    con.commit(); con.close(); return redirect("/")

@app.route("/logout")
def logout(): session.clear(); return redirect("/login")

@app.route("/reset")
def reset():
    if os.path.exists("fba.db"): os.remove("fba.db")
    init_db(); return redirect("/register")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
