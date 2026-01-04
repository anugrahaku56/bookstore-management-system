from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "bookstore_secret"

# ---------- DATABASE ----------
def get_db():
    conn = sqlite3.connect("books.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create tables
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    price TEXT,
    quantity TEXT
)
""")
conn.commit()
conn.close()

# ---------- LOGIN PAGE ----------
@app.route("/")
def login_page():
    return render_template("login.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()
    admin = conn.execute(
        "SELECT * FROM admin WHERE username=? AND password=?",
        (username, password)
    ).fetchone()
    conn.close()

    if admin:
        session["admin"] = username
        return redirect("/home")

    return redirect("/")

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        conn.execute(
            "INSERT INTO admin (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    return render_template("signup.html")

# ---------- HOME ----------
@app.route("/home")
def home():
    if "admin" not in session:
        return redirect("/")
    return render_template("index.html")

# ---------- ADD BOOK ----------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        price = request.form["price"]
        quantity = request.form["quantity"]

        conn = get_db()
        conn.execute(
            "INSERT INTO books VALUES (NULL, ?, ?, ?, ?)",
            (title, author, price, quantity)
        )
        conn.commit()
        conn.close()
        return redirect("/view")

    return render_template("add.html")

# ---------- VIEW + SEARCH ----------
@app.route("/view")
def view():
    if "admin" not in session:
        return redirect("/")

    search = request.args.get("search")
    conn = get_db()

    if search:
        books = conn.execute(
            "SELECT * FROM books WHERE title LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    else:
        books = conn.execute("SELECT * FROM books").fetchall()

    conn.close()
    return render_template("view.html", books=books)

# ---------- EDIT ----------
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    if "admin" not in session:
        return redirect("/")

    conn = get_db()

    if request.method == "POST":
        title = request.form["title"]
        author = request.form["author"]
        price = request.form["price"]
        quantity = request.form["quantity"]

        conn.execute("""
            UPDATE books
            SET title=?, author=?, price=?, quantity=?
            WHERE id=?
        """, (title, author, price, quantity, id))

        conn.commit()
        conn.close()
        return redirect("/view")

    book = conn.execute(
        "SELECT * FROM books WHERE id=?",
        (id,)
    ).fetchone()
    conn.close()

    return render_template("edit.html", book=book)

# ---------- DELETE ----------
@app.route("/delete/<int:id>")
def delete(id):
    if "admin" not in session:
        return redirect("/")

    conn = get_db()
    conn.execute("DELETE FROM books WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/view")

if __name__ == "__main__":
    app.run(debug=True)
