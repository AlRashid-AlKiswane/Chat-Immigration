"""
Main entry point for the Immigration Chatbot FastAPI application.

Handles application startup and shutdown events, sets up SQLite database tables,
and includes routes for file upload and document chunking.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

# Setup project base path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
    logging.debug(f"Project base path set to: {MAIN_DIR}")
except (ImportError, OSError) as e:
    logging.critical(
        "[Startup Critical] Failed to set up project base path. "
        f"Error: {str(e)}. System paths: {sys.path}",
        exc_info=True
    )
    sys.exit(1)

# pylint: disable=wrong-import-position
from src.logs import setup_logging
from src.helpers import get_settings, Settings
from src.routes import (
    upload_route,
    docs_to_chunks_route,
    embedding_route,
    llms_route,
    llm_generation_route,
    web_crawling_route
)
from src.database import (
    get_sqlite_engine,
    init_chunks_table,
    init_user_info_table,
    init_query_response_table,
    get_chroma_client
)
from src.embeddings import HuggingFaceModel, OpenAIEmbeddingModel

# Initialize logger and settings
logger = setup_logging()
logger.info("Initializing application settings...")

try:
    app_settings: Settings = get_settings()
    logger.debug(f"Application settings loaded successfully: {app_settings.dict()}")
except Exception as e:
    logger.critical(
        "[Startup Critical] Failed to load application settings. "
        f"Error: {str(e)}. Environment variables: {dict(os.environ)}",
        exc_info=True
    )
    sys.exit(1)

# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context to handle startup and shutdown events.
    Initializes and tears down database resources with comprehensive logging.
    """
    logger.info("Starting Immigration Chatbot API initialization...")

    # Initialize SQLite database
    try:
        logger.debug("Initializing SQLite engine...")
        app.state.conn = get_sqlite_engine()
        logger.info("SQLite engine initialized successfully")
    except Exception as db_err:
        logger.critical(
            "Failed to initialize SQLite engine. "
            f"Error type: {type(db_err).__name__}, Error: {str(db_err)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Database initialization failed"
        ) from db_err

    # Initialize database tables
    table_initializers = {
        "chunks_table": init_chunks_table,
        "user_info_table": init_user_info_table,
        "query_response_table": init_query_response_table
    }

    for table_name, initializer in table_initializers.items():
        try:
            logger.debug(f"Initializing {table_name}...")
            initializer(conn=app.state.conn)
            logger.info(f"{table_name.replace('_', ' ').title()} created successfully")
        except Exception as table_err:
            logger.error(
                f"Failed to initialize {table_name}. "
                f"Error type: {type(table_err).__name__}, Error: {str(table_err)}",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Database table {table_name} initialization failed"
            ) from table_err

    # Initialize embedding model
    try:
        logger.debug("Initializing embedding model...")
        model_name = app_settings.PROVIDER_EMBEDDING_MODEL

        if model_name == "LOCAL":
            logger.info("Using local HuggingFace embedding model")
            app.state.embedding = HuggingFaceModel(model_name=app_settings.EMBEDDING_MODEL)
            app.state.embedd_name = model_name
        elif model_name == "OPENAI":
            logger.info("Using OpenAI embedding model")
            app.state.embedding = OpenAIEmbeddingModel()
            app.state.embedd_name = model_name
        else:
            logger.warning(f"Unknown embedding model specified: {model_name}")
            app.state.embedding = None
            app.state.embedd_name = "NONE"

        if app.state.embedding:
            logger.info(f"Embedding model initialized: {model_name}")
        else:
            logger.warning("No valid embedding model configured")

    except Exception as embed_err:
        logger.error(
            "Failed to initialize embedding model. "
            f"Model: {model_name}, Error: {str(embed_err)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Embedding model initialization failed"
        ) from embed_err

    # Initialize ChromaDB client
    try:
        logger.debug("Initializing ChromaDB client...")
        app.state.vdb_client = get_chroma_client()
        logger.info("ChromaDB vector store client initialized successfully")
    except Exception as vdb_err:
        logger.error(
            "Failed to initialize ChromaDB client. "
            f"Error: {str(vdb_err)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Vector database initialization failed"
        ) from vdb_err

    # Initialize LLM (can be configured later)
    app.state.llm = None
    logger.warning(
        "LLM provider not initialized at startup. "
        "Please configure it via the /llms route before generating responses."
    )

    yield  # Application runs here

    # Shutdown procedures
    logger.info("Starting application shutdown...")

    try:
        conn = getattr(app.state, "conn", None)
        if conn:
            logger.debug("Closing database connection...")
            conn.close()
            logger.info("Database connection closed successfully")
        else:
            logger.warning("No active database connection found during shutdown")
    except Exception as shutdown_err:
        logger.error(
            "Error during database connection shutdown. "
            f"Error: {str(shutdown_err)}",
            exc_info=True
        )

    logger.info("Application shutdown completed")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Immigration Chatbot",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/", tags=["Root"])
def read_root():
    """Health check endpoint"""
    try:
        logger.debug("Root endpoint accessed")
        return {
            "status": "healthy",
            "version": app.version,
        }
    except Exception as root_err:
        logger.error(
            f"Error in root endpoint. Error: {str(root_err)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        ) from root_err

@app.get("/status", tags=["Monitoring"])
def get_status():
    """System status endpoint"""
    try:
        logger.debug("Status check requested")

        status = {
            "database": "connected" if hasattr(app.state, "conn") else "disconnected",
            "embedding": app.state.embedd_name if hasattr(app.state, "embedd_name") else "none",
            "llm": "configured" if hasattr(app.state, "llm") \
                and app.state.llm else "not configured",
            "vector_db": "connected" if hasattr(app.state, "vdb_client") else "disconnected"
        }

        logger.info(f"System status: {status}")
        return status
    except Exception as status_err:
        logger.error(
            f"Error in status endpoint. Error: {str(status_err)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail="Status check failed"
        ) from status_err



# Route registration with error handling
route_registrations = [
    (upload_route, "/upload", "File Upload"),
    (docs_to_chunks_route, "/chunking", "Document Chunking"),
    (embedding_route, "/embedding", "Embedding"),
    (llms_route, "/llms", "LLM Configuration"),
    (llm_generation_route, "/Generate", "LLM Generation"),
    (web_crawling_route, "/crawling", "Web Crawling")
]

for route, prefix, tag in route_registrations:
    try:
        logger.debug(f"Registering {tag.lower()} route...")
        app.include_router(
            route,
            prefix=prefix,
            tags=[tag]
        )
        logger.info(f"{tag} route registered successfully")
    except Exception as e:
        logger.critical(
            f"Failed to register {tag.lower()} route. "
            f"Error: {str(e)}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"{tag} route registration failed"
        ) from e

logger.info("All routes registered successfully")
