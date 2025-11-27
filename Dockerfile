FROM python:3.11-slim-bullseye
WORKDIR /app

COPY requirements.txt requirements.txt
RUN python -m pip install --upgrade pip && python -m pip install -r requirements.txt
COPY . .

ENV PYTHONPATH=/app

CMD alembic upgrade head && python src/main.py && python scripts/clear_db.py && python scripts/seed_db.py