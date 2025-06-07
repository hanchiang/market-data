# Dockerfile - Configuration for building the market data application container

# Pull the official Python slim image as the base image
# Using slim variant to reduce image size while keeping necessary tools
FROM python:3.12-slim-bullseye as base

# Set the working directory inside the container
# All subsequent commands will be executed in this directory
WORKDIR /app

# Set environment variables to disable Python bytecode generation and enable unbuffered output
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing .pyc files
# PYTHONUNBUFFERED: Ensures Python output is sent straight to terminal (helps with logging)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies and Poetry in a single layer for optimization
# - build-essential: Provides compilers and development tools for building packages
# - curl: Used for downloading resources
# - git: Required for cloning repositories
# - openssh-client: Provides SSH utilities like ssh-keyscan
# The symbolic link ensures Poetry is in the system PATH
RUN apt update && apt install -y --no-install-recommends \
    build-essential curl git openssh-client && \
    curl -sSL https://install.python-poetry.org | python3 && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Copy dependency files for Poetry to install dependencies
# This is done before copying the rest of the app for better layer caching
COPY pyproject.toml poetry.lock ./

# Set up SSH for accessing private repositories
# The known_hosts file is populated with GitHub's host key to avoid prompts
RUN mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts

# Copy the private SSH key for accessing private repositories
# The key is used to authenticate with private Git repositories
COPY secret/id_rsa /root/.ssh/id_rsa
RUN chmod 600 /root/.ssh/id_rsa

# Install Python dependencies using Poetry without creating a virtual environment
# virtualenvs.create false: Install packages directly in system Python
# --no-root: Don't install the project itself as a package
# The SSH key is removed immediately after dependencies are installed for security
RUN poetry config virtualenvs.create false && \
    poetry install --no-root && \
    rm -rf /root/.ssh/id_rsa

# Copy the application code into the container
# This is done after dependency installation to leverage Docker's build cache
COPY . .

# Remove the secret directory to ensure no sensitive files remain in the image
# This is a security best practice to avoid exposing credentials in the final image
RUN rm -rf "$(pwd)/secret"

# Set the PYTHONPATH environment variable to include the current working directory
# This ensures Python can find modules in the project
ENV PYTHONPATH "${PYTHONPATH}:$(pwd)"

# Use the base image to create a development image with Uvicorn as the entry point
# This creates a separate target for development use
FROM base as dev

# Start the Uvicorn server with hot-reload for development
# --reload: Enable auto-reload on code changes
# --host 0.0.0.0: Allow connections from any IP
# --app-dir: Specify the directory containing the app
CMD ["uvicorn", "--reload", "--host", "0.0.0.0", "--app-dir", "src/server", "main:app"]