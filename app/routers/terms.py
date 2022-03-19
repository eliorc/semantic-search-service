from typing import List, Optional

import peewee as pw
from fastapi import APIRouter, UploadFile, Request, Query
from pydantic import BaseModel, Field

from app import db
from app.db import db as db_client

# Documentation
tags = [{"name": "terms", "descriptions": "Operation with terms"}]

# Routing
router = APIRouter(
    prefix="/terms")


class Term(BaseModel):
    """ Term model"""
    text: str = Field(..., description="Term text")


class Terms(BaseModel):
    """ Terms model """
    terms: List[Term] = Field(..., description="List of terms")


class QueryResult(Term):
    """ Query result model """
    match: float = Field(..., description="Match percentage")


@router.post("/upload_file", summary="Upload file with terms")
async def upload_file(file: UploadFile) -> dict:
    """
    Upload file with terms.

    File's structure must be one term per line
    """

    # Get file contents
    contents = file.file.read().decode().split("\n")

    # Convert to data source to match the DB model
    data_source = [{"text": term.strip()} for term in contents if term.strip()]

    # Insert to DB
    with db_client.atomic():
        for term_batch in pw.chunked(data_source, 100):
            db.Term.insert_many(term_batch).on_conflict_ignore().execute()

    return {"message": "File uploaded"}


@router.post("/insert", summary="Insert terms")
async def insert(terms: Terms) -> dict:
    """
    Insert terms.

    Terms must be in the form of a list of terms
    """

    # Convert to data source to match the DB model
    data_source = [{"text": term} for term in terms if term]

    # Insert to DB
    with db_client.atomic():
        for term_batch in pw.chunked(data_source, 100):
            db.Term.insert_many(term_batch).on_conflict_ignore().execute()

    return {"message": "Terms inserted"}


@router.post("/delete", summary="Delete terms")
async def delete(terms: Terms) -> dict:
    """
    Delete terms.

    Terms must be in the form of a list of terms
    """

    # Delete from DB
    with db_client.atomic():
        db.Term.delete().where(db.Term.text.in_(terms)).execute()

    return {"message": "Terms deleted"}


@router.get("/query", summary="Query terms")
async def query(request: Request,
                term: str = Query(..., summary="Query text"),
                n: Optional[int] = Query(5, summary="Number of matches to find")) -> List[QueryResult]:
    """
    Query terms.
    """

    # Embed query
    query_embedding = request.app.state.embedder.encode([term])

    # Look for nearest neighbors
    distances, indices = request.app.state.nearest_neighbors.kneighbors(query_embedding, n)

    # Convert distances to percentages
    matches = 1 - distances[0]
    matches *= 100

    # Convert indices to labels
    labels = [request.app.state.index2term[i] for i in indices[0]]

    # Return results
    result = [QueryResult(text=label, match=match) for label, match in zip(labels, matches)]

    return result
