import os
import sys
import logging
import pathlib
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

# --- Setup project base path ---
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as e:
    logging.critical("[Startup Critical] Failed to set project base path.", exc_info=True)
    sys.exit(1)

# --- Local Imports ---
from src.embeddings import HuggingFaceModel, OpenAIEmbeddingModel
from src.database import (
    get_sqlite_engine,
    init_chunks_table,
    init_user_info_table,
    init_query_response_table,
    get_chroma_client,
)
from src.routes import (
    auth_route,
    upload_route,
    tables_crawling_route,
    web_crawling_route,
    docs_to_chunks_route,
    embedding_route,
    live_rag_route,
    llms_route,
    llm_generation_route,
    history_router,
    graph_ui_route,
    monitoring_route,
    logs_router,
    storage_management_route,
)
from src.history import ChatHistoryManager
from src.helpers import get_settings, Settings
from src.infra import setup_logging

# --- Constants ---
BASE_DIR = pathlib.Path(__file__).parent.resolve()
WEB_DIR = BASE_DIR / "web"

# --- Logging and Settings ---
logger = setup_logging(name="MAIN")
logger.info("Loading application settings...")

try:
    app_settings: Settings = get_settings()
    logger.debug(f"App settings loaded: {app_settings.dict()}")
except Exception:
    logger.critical("[Startup Critical] Failed to load app settings.", exc_info=True)
    sys.exit(1)

# --- FastAPI Lifespan Events ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown lifecycle of the app."""
    logger.info("Starting Immigration Chatbot API...")

    try:
        app.state.conn = get_sqlite_engine()
        logger.info("SQLite connection established.")
    except Exception:
        logger.critical("Failed to initialize SQLite engine.", exc_info=True)
        raise HTTPException(status_code=500, detail="SQLite init failed")

    for name, func in {
        "chunks_table": init_chunks_table,
        "user_info_table": init_user_info_table,
        "query_response_table": init_query_response_table,
    }.items():
        try:
            func(conn=app.state.conn)
            logger.info(f"{name.replace('_', ' ').title()} initialized.")
        except Exception:
            logger.error(f"{name} initialization failed.", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Init failed: {name}")

    try:
        app.state.embedding = OpenAIEmbeddingModel()
        logger.info("Embedding model initialized.")
    except Exception:
        logger.error("Embedding model initialization failed.", exc_info=True)
        raise HTTPException(status_code=500, detail="Embedding model init failed")

    try:
        vdb_client = get_chroma_client()
        collection = vdb_client.get_or_create_collection(name="chunks")
        app.state.vdb_client = vdb_client
        app.state.vdb_collection = collection
        logger.info("ChromaDB client initialized.")
    except Exception:
        logger.error("ChromaDB client initialization failed.", exc_info=True)
        raise HTTPException(status_code=500, detail="ChromaDB init failed")

    try:
        app.state.chat_manager = ChatHistoryManager()
        logger.info("Chat manager initialized.")
    except Exception:
        logger.warning("Failed to initialize chat manager.", exc_info=True)

    yield  # --- APPLICATION RUNNING ---

    # Shutdown
    try:
        if getattr(app.state, "conn", None):
            app.state.conn.close()
            logger.info("SQLite connection closed.")
    except Exception:
        logger.warning("Error closing SQLite connection.", exc_info=True)

    try:
        if getattr(app.state, "vdb_client", None):
            app.state.vdb_client.reset()
            logger.info("ChromaDB client shut down.")
    except Exception:
        logger.warning("Error shutting down ChromaDB client.", exc_info=True)

    logger.info("Application shutdown complete.")

# --- Create FastAPI App ---
app = FastAPI(
    title="Canada Express Entry Chatbot",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Include API Routes ---
app.include_router(auth_route)
app.include_router(upload_route)
app.include_router(tables_crawling_route)
app.include_router(web_crawling_route)
app.include_router(docs_to_chunks_route)
app.include_router(embedding_route)
app.include_router(live_rag_route)
app.include_router(llms_route)
app.include_router(llm_generation_route)
app.include_router(history_router)
app.include_router(graph_ui_route)
app.include_router(monitoring_route)
app.include_router(logs_router)
app.include_router(storage_management_route)

# --- Serve Static HTML UI ---
auth_html_path = WEB_DIR / "auth.html"

if auth_html_path.exists():
    @app.get("/", response_class=HTMLResponse)
    async def serve_auth_ui():
        try:
            with open(auth_html_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            logger.error("Failed to load auth.html", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to load auth UI.")
    logger.info("Main UI route '/' is serving auth.html.")
else:
    logger.warning("auth.html not found in web directory. '/' route disabled.")

# --- Mount /static for any assets like CSS/JS/images ---
if (WEB_DIR / "static").exists():
    app.mount("/static", StaticFiles(directory=str(WEB_DIR / "static")), name="static")
    logger.info("Static files mounted at '/static'.")
