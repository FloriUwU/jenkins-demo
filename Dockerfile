FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY webapp.py .
COPY templates ./templates

CMD ["sh", "-c", "python -u app.py & python -u webapp.py"]
