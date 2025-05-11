# Dockerfile
FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Add CA certificates
RUN apt-get update && apt-get install -y ca-certificates git && apt-get clean

# Expose ports
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]