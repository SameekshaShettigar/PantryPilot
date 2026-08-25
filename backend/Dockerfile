# Base Image: Python 3.11 lightweight slim Linux image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set active working directory inside container
WORKDIR /app

# Install system utilities required for PostgreSQL client drivers and curl healthchecks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependencies manifest first to utilize Docker layer caching
COPY requirements.txt /app/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy full application codebase into container
COPY . /app

# Expose internal container port
EXPOSE 8000

# Runtime Command: Bind Uvicorn to 0.0.0.0 so Docker network routing can access it
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
