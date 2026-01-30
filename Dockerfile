FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

# Listen on all interfaces so the container can receive traffic from host (port 80 -> 3000)
CMD ["python", "-c", "from app import app; app.run(host='0.0.0.0', port=3000)"]
