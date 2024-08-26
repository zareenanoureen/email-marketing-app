FROM python:3.12.3-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libc-dev \
        make \
        python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements.txt and install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy the project files
COPY . .

# Expose the port the app runs on
EXPOSE 80

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]