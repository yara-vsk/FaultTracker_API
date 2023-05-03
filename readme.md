# FastAPI project

## General info
* Users can registration and authentication;
* Users can create "fault" (upload images and description) via HTTP request;
* Users can list, update and delete their "fault";
* Users can get report on email with all "fault";
* Users can get "fault's" image;

## How to set up the project

* Create docker containers for the project by running $ docker compose build;
* Start the application by launching the containers $ docker compose up;

## Technologies
* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* alembic
* Pydantic
* Pytest
* redis
* Celery
* Flower