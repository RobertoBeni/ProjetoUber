FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install system dependencies, including geospatial libraries for PostGIS
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    binutils \
    libproj-dev \
    gdal-bin \
    python3-gdal \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . /app/

# Expose port
EXPOSE 8000

# Default command to run ASGI application with daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
