from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sklearn.neighbors import NearestNeighbors

from app.routers import terms
from app.db import db as db_client
from app import db
from model import get_embedder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


@app.on_event("startup")
async def startup():
    # Prerequisites
    app.state.nearest_neighbors = NearestNeighbors(n_neighbors=5, metric='cosine')
    app.state.embedder = get_embedder()
    app.state.index2term = dict()

    # Get all terms
    with db_client.atomic():
        terms = [term.text for term in db.Term.select()]

    if terms:
        # Save indices
        for i, term in enumerate(terms):
            app.state.index2term[i] = term

        # Build the nearest neighbors model
        app.state.nearest_neighbors.fit(app.state.embedder.encode(terms))


app.include_router(terms.router)
