from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

DATABASE = "database.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Προσθήκη αρχικών εργαλείων μόνο αν ο πίνακας είναι άδειος
    count = connection.execute(
        "SELECT COUNT(*) FROM tools"
    ).fetchone()[0]

    if count == 0:
        tools = [
            ("Τρυπάνι Bosch", "Ηλεκτρικό τρυπάνι για εργασίες στο σπίτι.", 1),
            ("Χλοοκοπτικό", "Χλοοκοπτικό για εργασίες κήπου.", 1),
            ("Σκάλα αλουμινίου", "Πτυσσόμενη σκάλα αλουμινίου.", 1)
        ]

        connection.executemany(
            """
            INSERT INTO tools (name, description, available)
            VALUES (?, ?, ?)
            """,
            tools
        )

    connection.commit()
    connection.close()


@app.route("/")
def home():
    connection = get_db_connection()
    tools = connection.execute(
        "SELECT * FROM tools WHERE available = 1"
    ).fetchall()
    connection.close()

    return render_template("index.html", tools=tools)


@app.route("/add", methods=["GET", "POST"])
def add_tool():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]

        connection = get_db_connection()
        connection.execute(
            """
            INSERT INTO tools (name, description, available)
            VALUES (?, ?, 1)
            """,
            (name, description)
        )
        connection.commit()
        connection.close()

        return render_template("success.html", name=name)

    return render_template("add_tool.html")
@app.route("/request/<int:tool_id>", methods=["GET", "POST"])
def request_tool(tool_id):
    connection = get_db_connection()

    tool = connection.execute(
        "SELECT * FROM tools WHERE id = ?",
        (tool_id,)
    ).fetchone()

    connection.close()

    if tool is None:
        return "Το εργαλείο δεν βρέθηκε.", 404

    if request.method == "POST":
        return render_template(
            "request_success.html",
            tool=tool
        )

    return render_template(
        "request_tool.html",
        tool=tool
    )


if __name__ == "__main__":
    init_db()
    app.run(debug=True)