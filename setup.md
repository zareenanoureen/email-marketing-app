# Setup Instructions for Dockerized Django Project
## Prerequisites

Ensure you have Docker and Docker Compose installed on your server.
Clone the repository to your server.
## Installation

Navigate to the project directory:
    ```bash
    cd ~/email-marketing-app/
    ```

Build and start the Docker containers:
    ```bash
    docker-compose up --build -d
    ```

Run database migrations:
    ```bash
    docker-compose exec django python manage.py makemigrations
    docker-compose exec django python manage.py migrate
    ```

Create a superuser for the Django admin:
    ```bash
    docker-compose exec django python manage.py createsuperuser
    ```

Access the application in your browser at `http://142.93.194.97:8000`.
## Additional Commands

To view logs:
    ```bash
    docker-compose logs -f
    ```

To stop the containers:
    ```bash
    docker-compose down
    ```

















