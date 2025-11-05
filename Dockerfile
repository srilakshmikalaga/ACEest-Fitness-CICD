# Use a lightweight Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Flask application
COPY app/ app/

# Expose Flask port
EXPOSE 5000

# Run Flask app (using web_app.py)
CMD ["python", "app/web_app.py"]
