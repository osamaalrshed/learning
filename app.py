from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)


def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    task TEXT NOT NULL,
                    done INTEGER NOT NULL DEFAULT 0
                )
            """)


init_db()


@app.route("/")
def index():
    with get_db() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM todos ORDER BY id DESC")
            todos = cur.fetchall()
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    task = request.form.get("task", "").strip()
    if task:
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO todos (task) VALUES (%s)", (task,))
    return redirect(url_for("index"))


@app.route("/toggle/<int:todo_id>")
def toggle(todo_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE todos SET done = 1 - done WHERE id = %s", (todo_id,))
    return redirect(url_for("index"))


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
