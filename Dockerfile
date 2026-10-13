# Basis-Image: schlankes Python 3.12 (Debian-Slim, kleiner als das volle Image)
FROM python:3.12-slim

# Arbeitsverzeichnis im Container; alle folgenden Befehle laufen hier
WORKDIR /app

# Zuerst nur die Abhängigkeitsliste kopieren. So bleibt der pip-Schritt
# gecacht, solange sich requirements.txt nicht ändert (im Jenkins-Log
# sichtbar als "Using cache")
COPY requirements.txt .

# Python-Pakete (z. B. Flask, psycopg2) installieren;
# --no-cache-dir hält das Image klein
RUN pip install --no-cache-dir -r requirements.txt

# Erst danach den eigenen Code kopieren, denn der ändert sich am häufigsten
COPY app.py .
COPY webapp.py .

# HTML-Templates für das Flask-Dashboard
COPY templates ./templates

# Startbefehl: app.py (Monitoring-Schleife) läuft im Hintergrund (&),
# webapp.py (Flask-Dashboard auf Port 5000) im Vordergrund.
# -u schaltet die Pufferung aus, damit die Ausgabe sofort in "docker logs" erscheint
CMD ["sh", "-c", "python -u app.py & python -u webapp.py"]
