# pylint: disable=wrong-import-position
import logging
import os
import sys

import networkx as nx
import numpy as np
import plotly.graph_objects as go
from fastapi import APIRouter, Depends, HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR

# Fix for pysqlite3 usage
__import__("pysqlite3")
sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")

# Setup base directory for imports
try:
    MAIN_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    sys.path.append(MAIN_DIR)
except (ImportError, OSError) as exc:
    logging.error("Failed to set up main directory path: %s", exc)
    sys.exit(1)

from src import get_vdb_collection
from src.infra import setup_logging

logger = setup_logging(name="ROUTE-UI-GRAPH")

graph_ui_route = APIRouter(
    prefix="/api/v1/graph_ui",
    tags=["Graph-UI"],
    responses={HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return float(np.dot(vec1, vec2) / (norm1 * norm2))


@graph_ui_route.get("")
async def graph_plotly3d(
    vdb=Depends(get_vdb_collection),
    max_nodes: int = 100,
    similarity_threshold: float = 0.75,
):
    """
    Generate a 3D semantic graph from ChromaDB chunks using cosine similarity.

    Args:
        vdb: Vector database collection instance.
        max_nodes: Maximum number of chunks to include in the graph.
        similarity_threshold: Threshold to connect nodes based on similarity.

    Returns:
        JSON Plotly graph for frontend rendering.

    Raises:
        HTTPException: If data fetch fails or no chunks are found.
    """
    logger.info("Starting graph_plotly3d with max_nodes=%d and similarity_threshold=%.2f",
                max_nodes, similarity_threshold)

    try:
        results = vdb.get(include=["embeddings", "documents", "metadatas"])
        all_chunks = [
            {
                "id": results["ids"][i],
                "embedding": results["embeddings"][i],
                "text": results["documents"][i],
                "metadata": results["metadatas"][i],
            }
            for i in range(len(results["ids"]))
        ]
        logger.info("Fetched %d chunks from vector DB", len(all_chunks))
    except Exception as exc:
        logger.exception("Failed to fetch chunks from vector DB")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch chunks from vector DB"
        )

    if not all_chunks:
        logger.warning("No chunks found in vector DB.")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No chunks found")

    chunks = all_chunks[:max_nodes]

    graph = nx.Graph()
    for chunk in chunks:
        graph.add_node(chunk["id"], label="chunk", text=chunk["text"][:100])

    for i, c1 in enumerate(chunks):
        emb1 = np.array(c1["embedding"])
        for j in range(i + 1, len(chunks)):
            emb2 = np.array(chunks[j]["embedding"])
            sim = cosine_similarity(emb1, emb2)
            if sim > similarity_threshold:
                graph.add_edge(c1["id"], chunks[j]["id"], weight=sim)

    if graph.number_of_nodes() == 0:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No nodes to display")

    pos = nx.spring_layout(graph, dim=3, seed=42)

    # Edge trace
    edge_x, edge_y, edge_z = [], [], []
    for source, target in graph.edges():
        x0, y0, z0 = pos[source]
        x1, y1, z1 = pos[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode="lines",
        line=dict(width=1, color="gray"),
        hoverinfo="none"
    )

    # Node trace
    node_x, node_y, node_z = [], [], []
    node_text, node_color, node_size = [], [], []
    degrees = dict(graph.degree())
    max_degree = max(degrees.values()) if degrees else 1

    for node in graph.nodes():
        x, y, z = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_z.append(z)
        degree = degrees[node]
        node_text.append(f"Node ID: {node}<br>Degree: {degree}<br>Text: {graph.nodes[node]['text']}")
        node_color.append("blue")
        node_size.append(5 + 10 * (degree / max_degree))

    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode="markers",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=1, color="black"),
            opacity=0.8,
        ),
        hoverinfo="text",
        text=node_text,
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            title="Chunks Semantic Graph (ChromaDB)",
            margin=dict(l=0, r=0, t=50, b=0),
            scene=dict(
                xaxis=dict(showbackground=False),
                yaxis=dict(showbackground=False),
                zaxis=dict(showbackground=False),
            ),
            showlegend=False,
            hovermode="closest",
        ),
    )

    logger.info("Graph visualization generated successfully.")
    # Convert the figure to a dictionary instead of JSON string
    fig_dict = fig.to_dict()

    # Add validation to ensure we have graph data
    if not fig_dict.get('data') or len(fig_dict['data']) == 0:
        logger.warning("Generated empty graph data")
        return {
            "data": [{
                "type": "scatter3d",
                "x": [], "y": [], "z": [],
                "mode": "markers",
                "marker": {"size": 1}
            }],
            "layout": fig_dict.get('layout', {})
        }

    return fig_dict
