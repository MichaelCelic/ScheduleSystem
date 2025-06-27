from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from .schema import schema
from .database import init_db

app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()

gql_app = GraphQLRouter(schema)
app.include_router(gql_app, prefix="/graphql") 