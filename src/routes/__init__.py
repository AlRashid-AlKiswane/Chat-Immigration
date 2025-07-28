from .route_upload_docs import upload_route
from .route_docs_to_chunks import docs_to_chunks_route
from .route_chunks_to_embedding import embedding_route
from .route_llms_config import llms_route
from .route_llm_generate import llm_generation_route
from .route_crawling import web_crawling_route
from .route_monitoring import monitoring_route
from .route_logs import logs_router
from .route_live_rag import live_rag_route
from .route_scraping_taples import tables_crawling_route
from .route_history_management import history_router
from .route_graph_ui import graph_ui_route
from .route_storge_mangamnet import storage_management_route
from .route_auth_routes import auth_route
from .route_user_answer_input import answers_input_user_route

__all__ = [
    "upload_route",
    "docs_to_chunks_route",
    "embedding_route",
    "llms_route",
    "llm_generation_route",
    "web_crawling_route",
    "monitoring_route",
    "logs_router",
    "live_rag_route",
    "tables_crawling_route",
    "history_router",
    "graph_ui_route",
    "storage_management_route",
    "auth_route",
    "answers_input_user_route"
    ]
