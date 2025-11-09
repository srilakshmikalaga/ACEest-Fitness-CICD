# Base image
FROM python:3.10-slim

# Working directory
WORKDIR /app

# Build argument: specify which file to include
ARG VERSION_FILE=app/ACEest_Fitness.py

# Copy the chosen version file
COPY ${VERSION_FILE} /app/ACEest_Fitness.py

# Install dependencies if needed
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Run the app
CMD ["python", "ACEest_Fitness.py"]
