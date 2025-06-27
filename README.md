# HospitalScheduler

A hospital staff scheduling system using FastAPI, Strawberry GraphQL, SQLModel, and SQLite.

## Features
- Employee, Location, and Shift management
- Weekly schedule generation with business constraints
- GraphQL API for queries and mutations
- CLI commands for admin tasks
- Dockerized for easy deployment

## Requirements
- Python 3.10+
- Docker (optional)

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate  # On Windows
pip install -r requirements.txt
```

## Running the App

```bash
uvicorn app.main:app --reload
```

Visit http://localhost:8000/graphql for the GraphQL Playground.

## Docker

```bash
docker-compose up --build
```

## Testing

```bash
pytest
``` 