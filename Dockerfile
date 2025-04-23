# syntax=docker/dockerfile:1

# Inkplate Dashboard Server
# Hosted on server at: http://0.0.0.0:10465

# Use an official Python runtime as a base image
FROM selenium/standalone-chrome:124.0

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/
ENV TZ="America/Los_Angeles"

# Create a non-privileged user that the app will run under.
# Create a user and group with a specific ID
USER root
RUN groupadd -r appuser &&  \
    useradd -r  \
    --gid appuser  \
    --home-dir /home/appuser  \
    --shell /sbin/nologin  \
    appuser

### Get Python set up in Selenium container

# Set up python3.11
RUN apt-get update && apt-get install -y software-properties-common
RUN apt-get install -y python3.11 python3.11-venv python3.11-distutils python3-pip

# Replace 'python' command with 'python3.11'
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1


### Actually set up our Flask app now

# Set the working directory in the container
WORKDIR /app

# Install virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN python -m pip install --upgrade pip

# Install any needed packages specified in requirements.txt
COPY requirements.txt .
COPY wheel ./wheel
RUN pip install --ignore-installed --no-cache-dir -r requirements.txt

# Copy the app directory contents into the container at /app
COPY ./app .

# Change the ownership of the /app directory to the new user
RUN chown -R appuser:appuser /app
# Give access to Selinium's home
RUN chown -R appuser:appuser /home/seluser

# Switch to the non-root user
USER appuser

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD flask --app . run --host 0.0.0.0 --port 5000
