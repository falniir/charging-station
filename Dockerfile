# Use an official Python runtime as a parent image
FROM python:3.12

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl

# Install Node.js (LTS version) and Bun
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g bun

# Install Pipenv
RUN pip install pipenv

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pipenv install django

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run Django development server
CMD ["pipenv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]
