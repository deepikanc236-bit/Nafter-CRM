# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PORT 8000

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Download NLP data
RUN python -m textblob.download_corpora

# Copy project
COPY . /app/

# Run collectstatic
RUN python manage.py collectstatic --no-input

# Expose port
EXPOSE 8000

# Run the application
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
