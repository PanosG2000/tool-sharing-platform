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

    # Πίνακας εργαλείων
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
    """)

    # Πίνακας αιτημάτων δανεισμού
    connection.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tool_id INTEGER NOT NULL,
            borrower TEXT NOT NULL,
            days INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY (tool_id) REFERENCES tools (id)
        )
    """)

    # Προσθήκη αρχικών εργαλείων μόνο αν ο πίνακας είναι άδειος
    count = connection.execute(
        "SELECT COUNT(*) FROM tools"
    ).fetchone()[0]

    if count == 0:
        tools = [
            (
                "Τρυπάνι Bosch",
                "Ηλεκτρικό τρυπάνι για εργασίες στο σπίτι.",
                1
            ),
            (
                "Χλοοκοπτικό",
                "Χλοοκοπτικό για εργασίες κήπου.",
                1
            ),
            (
                
                "Σκάλα αλουμινίου",
                "Πτυσσόμενη σκάλα αλουμινίου.",
                1
            )
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

    if tool is None:
        connection.close()
        return "Το εργαλείο δεν βρέθηκε.", 404

    if request.method == "POST":
        borrower = request.form["borrower"]
        days = request.form["days"]

        connection.execute(
            """
            INSERT INTO requests (tool_id, borrower, days)
            VALUES (?, ?, ?)
            """,
            (tool_id, borrower, days)
        )

        connection.commit()
        connection.close()

        return render_template(
            "request_success.html",
            tool=tool,
            borrower=borrower,
            days=days
        )

    connection.close()

    return render_template(
        "request_tool.html",
        tool=tool
    )

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
@app.route("/requests")
def requests():
    connection = get_db_connection()

    requests = connection.execute("""
        SELECT requests.*, tools.name AS tool_name
        FROM requests
        JOIN tools ON requests.tool_id = tools.id
        ORDER BY requests.id DESC
    """).fetchall()

    connection.close()

    return render_template("requests.html", requests=requests)

@app.route("/requests/<int:request_id>/<action>", methods=["POST"])
def update_request(request_id, action):
    if action not in ["approve", "reject"]:
        return "Μη έγκυρη ενέργεια.", 400

    status = "approved" if action == "approve" else "rejected"

    connection = get_db_connection()

    connection.execute(
        "UPDATE requests SET status = ? WHERE id = ?",
        (status, request_id)
    )

    connection.commit()
    connection.close()

    return render_template(
        "request_updated.html",
        status=status
    )

if __name__ == "__main__":
    init_db()
    app.run(debug=True)