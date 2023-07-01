# FastAPI project

## General info

<img alt="img.png" height="526,8" src="img.png" width="377,4"/>

* Users can registration and authentication;
* Users can create "project";
* Users can create project "faults"  (upload images and description) assigned to created project via HTTP request;
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