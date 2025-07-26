# pylint: disable=wrong-import-position
import logging
import os
import sys

from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR
from chromadb import Client

# Fix for pysqlite3 usage
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

from sqlite3 import Connection

# Setup base directory for imports
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as exc:
    logging.error("Failed to set up main directory path: %s", exc)
    sys.exit(1)

from src import get_db_conn, get_vdb_client
from src.database import clear_table
from src.infra import setup_logging

logger = setup_logging(name="ROUTE-STORAG-MANAGEMANT")

storage_management_route = APIRouter(
    prefix="/api/v1/storage",
    tags=["Storage-Management"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)

@storage_management_route.post("")
async def storage_management(
    do_reset_table_db: bool = False,
    do_reset_collection_vdb: bool = False,
    do_reset_chunks_table: bool = False,
    do_reset_chunks_collection: bool = False,
    layers_all: bool = False,
    conn: Connection = Depends(get_db_conn),
    vdb: Client = Depends(get_vdb_client)
):
    """
    Reset storage components based on provided parameters.
    """
    try:
        logger.info("Received storage reset request.")
        results = {
            "chunks": False,
            "query_responses": False,
            "vector_db_collections_reset": False,
            "chunks_collection_reset": False
        }

        if layers_all:
            do_reset_table_db = True
            do_reset_collection_vdb = True
            do_reset_chunks_table = True
            do_reset_chunks_collection = True
            logger.info("All reset layers activated due to layers_all=True")

        # Reset full main DB tables
        if do_reset_table_db:
            try:
                clear_table(conn, "chunks")
                clear_table(conn, "query_responses")
                results["chunks"] = True
                results["query_responses"] = True
                logger.info("Cleared both 'chunks' and 'query_responses' tables.")
            except Exception as e:
                logger.error(f"Error resetting main database tables: {e}")

        # Reset just chunks table
        elif do_reset_chunks_table:  # `elif` to avoid double-reset if already handled
            try:
                clear_table(conn, "chunks")
                results["chunks"] = True
                logger.info("Cleared 'chunks' table only.")
            except Exception as e:
                logger.error(f"Error clearing chunks table: {e}")

        # Reset entire vector DB
        if do_reset_collection_vdb:
            try:
                collections = vdb.list_collections()
                for collection in collections:
                    vdb.delete_collection(collection.name)
                results["vector_db_collections_reset"] = True
                logger.info("All vector DB collections deleted.")
            except Exception as e:
                logger.error(f"Error resetting vector DB collections: {e}")

        # Reset just chunks collection
        elif do_reset_chunks_collection:
            try:
                vdb.delete_collection("chunks")  # adjust name if different
                results["chunks_collection_reset"] = True
                logger.info("Chunks collection in vector DB deleted.")
            except Exception as e:
                logger.warning(f"Chunks collection may not exist: {e}")
                results["chunks_collection_reset"] = False

        return {
            "success": True,
            "message": "Storage reset completed successfully.",
            "results": results
        }

    except Exception as e:
        logger.error(f"Unhandled error during reset: {e}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Storage reset failed: {str(e)}"
        )
