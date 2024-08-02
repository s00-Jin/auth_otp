# Dockerfile.worker
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the contents of the project into the container
COPY ./ /app/

RUN pip install --no-cache-dir -r requirements.txt

# Create a non-privileged user
RUN useradd -ms /bin/sh celeryuser

# Switch to the non-privileged user
USER celeryuser

# Set the default command to run Celery
CMD ["celery", "-A", "config", "worker", "--loglevel=INFO"]
