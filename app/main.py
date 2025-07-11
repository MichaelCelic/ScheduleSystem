from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from .schema import schema
from .database import init_db
from .seed_data import seed_database

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()
    # Seed the database with frontend data
    try:
        seed_database()
    except Exception as e:
        print(f"Warning: Could not seed database: {e}")

gql_app = GraphQLRouter(schema)
app.include_router(gql_app, prefix="/graphql") 