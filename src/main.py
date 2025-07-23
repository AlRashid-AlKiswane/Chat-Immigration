import os
import sys
import logging
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

# Setup project base path
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("[Startup Critical] Failed to set project base path.", exc_info=True)
    sys.exit(1)

# Local imports after sys.path setup
from src.embeddings import HuggingFaceModel, OpenAIEmbeddingModel
from src.database import (
    get_sqlite_engine,
    init_chunks_table,
    init_user_info_table,
    init_query_response_table,
    get_chroma_client,
)
from src.routes import (
    upload_route,
    docs_to_chunks_route,
    embedding_route,
    llms_route,
    llm_generation_route,
    web_crawling_route,
    monitoring_route,
    logs_router,
    live_rag_route,
    tables_crawling_route,
    history_router,
)
from src.history import ChatHistoryManager
from src.helpers import get_settings, Settings
from src.infra import setup_logging

# Constants
BASE_DIR = pathlib.Path(__file__).parent.resolve()
WEB_DIR = BASE_DIR / "web"

# Initialize logging and settings
logger = setup_logging(name="MAIN")
logger.info("Loading application settings...")

try:
    app_settings: Settings = get_settings()
    logger.debug(f"App settings: {app_settings.dict()}")
except Exception as e:
    logger.critical("[Startup Critical] Failed to load app settings.", exc_info=True)
    sys.exit(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown."""
    logger.info("Starting Immigration Chatbot API...")

    # Database initialization
    try:
        app.state.conn = get_sqlite_engine()
        logger.info("SQLite connection established.")
    except Exception as e:
        logger.critical("Database engine initialization failed.", exc_info=True)
        raise HTTPException(status_code=500, detail="DB init failed")

    # Initialize tables
    for name, func in {
        "chunks_table": init_chunks_table,
        "user_info_table": init_user_info_table,
        "query_response_table": init_query_response_table,
    }.items():
        try:
            func(conn=app.state.conn)
            logger.info(f"{name.replace('_', ' ').title()} initialized.")
        except Exception as e:
            logger.error(f"{name} init failed.", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Init failed: {name}")

    # Embedding model
    try:
        provider = app_settings.PROVIDER_EMBEDDING_MODEL
        if provider == "LOCAL":
            app.state.embedding = HuggingFaceModel(model_name=app_settings.EMBEDDING_MODEL)
        elif provider == "OPENAI":
            app.state.embedding = OpenAIEmbeddingModel()
        logger.info(f"Embedding model: {provider}")
    except Exception as e:
        logger.error("Embedding model initialization failed.", exc_info=True)
        raise HTTPException(status_code=500, detail="Embedding model init failed")

    # ChromaDB client
    try:
        app.state.vdb_client = get_chroma_client()
        logger.info("ChromaDB client initialized.")
    except Exception as e:
        logger.error("ChromaDB init failed.", exc_info=True)
        raise HTTPException(status_code=500, detail="Vector DB init failed")

    # Chat manager
    app.state.chat_manager = ChatHistoryManager()
    logger.info("Chat manager initialized.")

    yield  # Run app

    # Shutdown
    try:
        if getattr(app.state, "conn", None):
            app.state.conn.close()
            logger.info("SQLite connection closed.")
    except Exception as e:
        logger.warning("Shutdown error.", exc_info=True)


# Create FastAPI app
app = FastAPI(
    title="Immigration Chatbot",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Register API routes
for route, prefix, tag in [
    (upload_route, "/api", "File Upload"),
    (docs_to_chunks_route, "/api", "Document Chunking"),
    (embedding_route, "/api", "Embedding"),
    (llms_route, "/api", "LLM Configuration"),
    (llm_generation_route, "/api", "LLM Generation"),
    (web_crawling_route, "/api", "Web Crawling"),
    (monitoring_route, "/api", "Monitoring"),
    (logs_router, "/api", "Logs"),
    (live_rag_route, "/api", "Live RAG"),
    (tables_crawling_route, "/api", "Table Crawling"),
    (history_router, "/api", "Chat History"),
]:
    try:
        app.include_router(route, prefix=prefix, tags=[tag])
        logger.info(f"{tag} route registered.")
    except Exception as e:
        logger.critical(f"Failed to register {tag} route.", exc_info=True)

# Serve static files for the frontend UI
if WEB_DIR.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")
    logger.info(f"Web UI mounted at '/'. Directory: {WEB_DIR}")
else:
    logger.warning(f"Web directory not found: {WEB_DIR}. Static UI not mounted.")
