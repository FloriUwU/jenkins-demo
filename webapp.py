"""
NetWatch – Flask-Weboberfläche

Stellt das Dashboard auf Port 5000 bereit. Bei jedem Aufruf liest die Seite die
letzten Prüfungen und die Kennzahlen aus PostgreSQL und übergibt sie an das
HTML-Template templates/index.html.

Die Daten schreibt app.py, diese Datei liest sie nur.
Die Datenbank-Zugangsdaten kommen aus Umgebungsvariablen
(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD), im Code steht kein Passwort.
"""

# Flask: Webframework; render_template füllt ein HTML-Template mit Daten
from flask import Flask, render_template
import os          # Zugriff auf Umgebungsvariablen
import psycopg2    # PostgreSQL-Treiber für Python


# Flask-Anwendung anlegen
app = Flask(__name__)


def get_connection():
    """Öffnet eine neue Verbindung zur PostgreSQL-Datenbank.

    Fehlt eine der Umgebungsvariablen, bricht das mit einem KeyError ab.
    Ist die Datenbank nicht erreichbar oder das Passwort falsch, löst
    psycopg2 einen OperationalError aus.
    """
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )


# Diese Funktion wird beim Aufruf der Startseite (http://localhost:5000/) ausgeführt
@app.route("/")
def dashboard():
    connection = get_connection()
    cursor = connection.cursor()

    # Die 20 neuesten Prüfungen für die Tabelle "Letzte Prüfungen".
    # Spaltenreihenfolge (wichtig für das Template): [0] host, [1] port,
    # [2] status, [3] response_time_ms, [4] checked_at
    cursor.execute("""
        SELECT host, port, status, response_time_ms, checked_at
        FROM monitoring_results
        ORDER BY checked_at DESC
        LIMIT 20
    """)

    results = cursor.fetchall()

    # Kennzahlen über ALLE gespeicherten Prüfungen in einer einzigen Abfrage:
    # Gesamtzahl, Anzahl UP und Anzahl DOWN (COUNT ... FILTER zählt nur Zeilen,
    # auf die die Bedingung zutrifft)
    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE status = 'UP') AS up_count,
            COUNT(*) FILTER (WHERE status = 'DOWN') AS down_count
        FROM monitoring_results
    """)

    # Genau eine Ergebniszeile: (total, up_count, down_count)
    statistics = cursor.fetchone()

    # Verbindung wieder freigeben
    cursor.close()
    connection.close()

    # Template mit den Daten füllen und als HTML an den Browser schicken.
    # Es gibt hier keine Fehlerbehandlung: Ist die Datenbank nicht erreichbar,
    # antwortet Flask mit HTTP 500 (das hat in der Check-Stage der Pipeline
    # den Build fehlschlagen lassen)
    return render_template(
        "index.html",
        results=results,
        statistics=statistics
    )


# Wird nur ausgeführt, wenn die Datei direkt gestartet wird (python webapp.py),
# so wie es das Dockerfile tut
if __name__ == "__main__":
    # host="0.0.0.0": von außerhalb des Containers erreichbar, nicht nur lokal.
    # Das ist der eingebaute Flask-Entwicklungsserver, für den Dauerbetrieb
    # wäre ein Produktionsserver wie gunicorn üblich
    app.run(host="0.0.0.0", port=5000)
