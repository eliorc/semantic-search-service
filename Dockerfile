FROM python:3.8-slim

ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

ENV SIMILARITY_MODEL="sentence-transformers/paraphrase-MiniLM-L6-v2"

RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir poetry==1.1.12

WORKDIR /opt/app
COPY . .

RUN poetry config virtualenvs.create false && \
    poetry install

# Download the model to prevent download on first startup
RUN poetry run python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('$SIMILARITY_MODEL', device='cpu')"

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0"]
