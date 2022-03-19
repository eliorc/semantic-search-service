import os

from sentence_transformers import SentenceTransformer


def get_embedder() -> SentenceTransformer:
    """
    Returns a SentenceTransformer model.
    """
    return SentenceTransformer(os.environ["SIMILARITY_MODEL"], device='cpu')
