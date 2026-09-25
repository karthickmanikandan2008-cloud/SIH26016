from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("land.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS lands (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            land_id TEXT,
            survey_no TEXT,
            village TEXT,
            district TEXT,
            area REAL,
            owner TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/")
def dashboard():

    search = request.args.get("search", "")
    status_filter = request.args.get("status", "")

    conn = sqlite3.connect("land.db")

    query = """
        SELECT land_id, survey_no, village,
               district, area, owner, status
        FROM lands
        WHERE 1=1
    """

    values = []

    if search:
        query += """
            AND (
                land_id LIKE ?
                OR survey_no LIKE ?
                OR village LIKE ?
                OR district LIKE ?
                OR owner LIKE ?
            )
        """

        search_value = "%" + search + "%"

        values.extend([
            search_value,
            search_value,
            search_value,
            search_value,
            search_value
        ])

    if status_filter:
        query += " AND status = ?"
        values.append(status_filter)

    lands = conn.execute(query, values).fetchall()

    total_lands = len(lands)

    approved = sum(
        1 for land in lands
        if land[6] == "Approved"
    )

    pending = sum(
        1 for land in lands
        if land[6] == "Pending"
    )

    completed = sum(
        1 for land in lands
        if land[6] == "Completed"
    )

    conn.close()

    return render_template(
        "dashboard.html",
        lands=lands,
        total_lands=total_lands,
        approved=approved,
        pending=pending,
        completed=completed,
        search=search,
        status_filter=status_filter
    )


@app.route("/update-status/<land_id>", methods=["POST"])
def update_status(land_id):

    new_status = request.form["status"]

    conn = sqlite3.connect("land.db")

    conn.execute("""
        UPDATE lands
        SET status = ?
        WHERE land_id = ?
    """, (new_status, land_id))

    conn.commit()
    conn.close()

    return "Status updated successfully!"


@app.route("/add-land", methods=["GET", "POST"])
def add_land():

    if request.method == "POST":

        land_id = request.form["land_id"]
        survey_no = request.form["survey_no"]
        village = request.form["village"]
        district = request.form["district"]
        area = request.form["area"]
        owner = request.form["owner"]
        status = request.form["status"]

        conn = sqlite3.connect("land.db")

        conn.execute("""
            INSERT INTO lands
            (land_id, survey_no, village, district, area, owner, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            land_id,
            survey_no,
            village,
            district,
            area,
            owner,
            status
        ))

        conn.commit()
        conn.close()

        return "Land successfully saved!"

    return render_template("add_land.html")


if __name__ == "__main__":
    app.run(debug=True)