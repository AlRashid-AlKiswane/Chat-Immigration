# src/chroma/insert.py
from typing import List, Optional
from chromadb import Client
from chromadb.errors import ChromaError
from src.infra import setup_logging

logger = setup_logging(name="VECTORE-DB")

def insert_documents(
    client: Client,
    collection_name: str,
    ids: List[str],
    embeddings: List[List[float]],
    documents: List[str],
    metadatas: Optional[List[dict]] = None
) -> bool:
    """
    Insert documents, embeddings, and metadata into a ChromaDB collection.
    """
    try:
        if len(ids) != len(documents) or len(ids) != len(embeddings):
            raise ValueError("IDs, documents, and embeddings must be same length")

        if metadatas and len(metadatas) != len(ids):
            raise ValueError("Metadata length must match documents")

        collection = client.get_or_create_collection(name=collection_name)

        collection.add(
            ids=[str(i) for i in ids],
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas if metadatas else None
        )

        return True

    except ChromaError as ce:
        logger.error("ChromaDB error: %s", ce)
        return False
    except Exception as e:
        logger.error("Unexpected error in insert_documents: %s", e)
        return False
