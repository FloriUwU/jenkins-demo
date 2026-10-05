import os
import socket
import time
import psycopg2


HOST = "google.de"
PORT = 443


def check_service(host, port):
    start_time = time.time()

    try:
        connection = socket.create_connection((host, port), timeout=5)
        connection.close()

        response_time = int((time.time() - start_time) * 1000)

        return "UP", response_time

    except Exception:
        return "DOWN", None


def save_result(host, port, status, response_time):
    connection = psycopg2.connect(
        host=os.environ["DB_HOST"],
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"]
    )

    cursor = connection.cursor()

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

    cursor.execute("""
        INSERT INTO monitoring_results
        (host, port, status, response_time_ms)
        VALUES (%s, %s, %s, %s)
    """, (host, port, status, response_time))

    connection.commit()

    cursor.close()
    connection.close()


print("NetWatch gestartet")
print(f"Prüfe {HOST}:{PORT} alle 60 Sekunden")

while True:
    status, response_time = check_service(HOST, PORT)

    print(f"Status: {status}")

    if response_time is not None:
        print(f"Antwortzeit: {response_time} ms")

    save_result(HOST, PORT, status, response_time)

    print("Ergebnis wurde in der Datenbank gespeichert.")
    print("Warte 60 Sekunden...")

    time.sleep(60)
# Automatischer Jenkins-Polling-Test
