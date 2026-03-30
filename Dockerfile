FROM python:3.10-slim

# Dépendances système pour librosa et pydub
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Port par défaut pour Flask
EXPOSE 5000

ENV FLASK_APP=app/main.py
ENV FLASK_RUN_HOST=0.0.0.0

CMD ["python", "app/main.py"]
