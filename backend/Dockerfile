# Dockerfile

FROM python:3.10-slim

# Set workdir
WORKDIR /app

# Copy files
COPY app /app
COPY requirements.txt /app
COPY serviceAccountKey.json /app/serviceAccountKey.json

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Flask port
EXPOSE 5000

# Run the app
CMD ["python", "app.py"]
