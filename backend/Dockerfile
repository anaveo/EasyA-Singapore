FROM python:3.10-slim

# Install system dependencies required to build PyNaCl and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    python3-dev \
    cargo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy app folder contents into /app
COPY app /app

# Copy serviceAccountKey.json into /app
# COPY serviceAccountKey.json /app/serviceAccountKey.json

# Install dependencies
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run the app
ENV FLASK_APP=app.py
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
