# Use an official Python image as the base
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies required for dlib and face_recognition
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        libopenblas-dev \
        liblapack-dev \
        libx11-dev \
        libgtk-3-dev \
        libboost-python-dev \
        python3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project files
COPY . .

# Expose port 8000
EXPOSE 8000

# Command to start the server (adjust if your WSGI module is different)
CMD ["gunicorn", "face_auth.wsgi", "--bind", "0.0.0.0:8000"]