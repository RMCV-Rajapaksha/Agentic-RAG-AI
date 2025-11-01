"""
Pipeline Module

This module contains the ingestion pipeline creation and execution logic.
"""

from .pipeline import (
    create_embedding_model,
    create_ingestion_pipeline,
    ingest_documents,
)

__all__ = [
    "create_embedding_model",
    "create_ingestion_pipeline",
    "ingest_documents",
]
