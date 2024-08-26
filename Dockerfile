FROM python:3.12.3-slim

ENV PYTHONBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc libc-dev make libffi-dev libssl-dev libxml2-dev libxslt-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ADD . /app

COPY requirements.txt requirements.txt

# Upgrade pip and install requirements
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .

EXPOSE 80

CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
