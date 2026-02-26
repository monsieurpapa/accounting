# /home/ubuntu/accounting_project/docker/django/Dockerfile

# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install system dependencies
# libpq-dev is needed for psycopg2
# build-essential might be needed for some packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Copy requirements first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project source code
# Ensure .dockerignore is set up correctly in the project root if needed
COPY ./src /app/

# Copy entrypoint script (optional but recommended)
# COPY ./docker/django/entrypoint.sh /entrypoint.sh
# RUN chmod +x /entrypoint.sh

# Collect static files (optional - can be done in entrypoint or manually)
# RUN python manage.py collectstatic --noinput

# Expose port Gunicorn will run on
EXPOSE 8000

# Define default command to run Gunicorn
# Replace 'config.wsgi:application' with your actual WSGI application path
# Consider using an entrypoint script to run migrations first
# ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]

