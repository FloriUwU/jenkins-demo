"""
NetWatch – Monitoring-Skript

Prüft in einer Endlosschleife jede Minute, ob ein Dienst per TCP erreichbar ist,
und speichert das Ergebnis (UP/DOWN, Antwortzeit, Zeitpunkt) in PostgreSQL.
Das Flask-Dashboard (webapp.py) liest diese Daten und zeigt sie an.

Die Zugangsdaten zur Datenbank kommen aus Umgebungsvariablen
(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD). Im Code steht kein Passwort.
"""

import os            # Zugriff auf Umgebungsvariablen (Datenbank-Zugangsdaten)
import socket        # TCP-Verbindung zum überwachten Dienst aufbauen
import time          # Zeit messen und zwischen den Prüfungen warten
import psycopg2      # PostgreSQL-Treiber für Python


# Überwachtes Ziel; Host und Port sind fest im Code eingetragen
HOST = "google.de"
PORT = 443


def check_service(host, port):
    """Prüft, ob sich eine TCP-Verbindung zu host:port aufbauen lässt.

    Rückgabe:
        ("UP", Antwortzeit in ms)  bei erfolgreicher Verbindung
        ("DOWN", None)             bei Fehler oder Timeout
    """
    # Startzeitpunkt für die Messung der Verbindungszeit
    start_time = time.time()

    try:
        # Verbindung aufbauen; nach 5 Sekunden ohne Antwort gilt sie als gescheitert
        connection = socket.create_connection((host, port), timeout=5)
        connection.close()

        # Dauer des Verbindungsaufbaus in Millisekunden
        response_time = int((time.time() - start_time) * 1000)

        return "UP", response_time

    except Exception:
        # Jeder Fehler (nicht erreichbar, Timeout, DNS-Fehler) zählt als DOWN;
        # eine Antwortzeit gibt es dann nicht (wird als NULL gespeichert)
        return "DOWN", None


def save_result(host, port, status, response_time):
    """Speichert ein Prüfergebnis in der Tabelle monitoring_results."""
    # Verbindung zur Datenbank; die Zugangsdaten stammen aus den Umgebungsvariablen.
    # Fehlt eine davon, bricht das Programm mit einem KeyError ab (gewollt,
    # so fällt eine fehlende Konfiguration sofort auf)
    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

    cursor = connection.cursor()

    # Tabelle beim ersten Aufruf automatisch anlegen, danach ändert sich nichts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monitoring_results (
            id SERIAL PRIMARY KEY,
            host VARCHAR(255) NOT NULL,
            port INTEGER NOT NULL,
            status VARCHAR(20) NOT NULL,
            response_time_ms INTEGER,
            checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Ergebnis einfügen; die %s-Platzhalter werden vom Treiber sicher befüllt
    # (Schutz vor SQL-Injection). checked_at setzt die Datenbank automatisch
    cursor.execute("""
        INSERT INTO monitoring_results
        (host, port, status, response_time_ms)
        VALUES (%s, %s, %s, %s)
    """, (host, port, status, response_time))

    # Änderung festschreiben, sonst wird nichts gespeichert
    connection.commit()

    # Ressourcen wieder freigeben
    cursor.close()
    connection.close()


# ---------- Hauptprogramm ----------
# Diese Ausgaben erscheinen in "docker logs netwatch-app"
print("NetWatch gestartet")
print(f"Prüfe {HOST}:{PORT} alle 60 Sekunden")

# Endlosschleife: prüfen, speichern, eine Minute warten
while True:
    # Dienst prüfen
    status, response_time = check_service(HOST, PORT)

    print(f"Status: {status}")

    # Bei DOWN gibt es keine Antwortzeit
    if response_time is not None:
        print(f"Antwortzeit: {response_time} ms")

    # Ergebnis in die Datenbank schreiben. Hier gibt es keine Fehlerbehandlung:
    # ist die Datenbank nicht erreichbar, beendet der Fehler die Schleife
    save_result(HOST, PORT, status, response_time)

    print("Ergebnis wurde in der Datenbank gespeichert.")
    print("Warte 60 Sekunden...")

    # Prüfintervall: 60 Sekunden
    time.sleep(60)
# Automatischer Jenkins-Polling-Test
