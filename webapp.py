from flask import Flask, render_template
import os
import psycopg2

app = Flask(__name__)


def get_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )


@app.route("/")
def dashboard():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT host, port, status, response_time_ms, checked_at
        FROM monitoring_results
        ORDER BY checked_at DESC
        LIMIT 20
    """)

    results = cursor.fetchall()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE status = 'UP') AS up_count,
            COUNT(*) FILTER (WHERE status = 'DOWN') AS down_count
        FROM monitoring_results
    """)

    statistics = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        "index.html",
        results=results,
        statistics=statistics
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
