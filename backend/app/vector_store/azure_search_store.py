"""Azure AI Search vector store implementation with parent-child chunking."""
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import uuid

from azure.search.documents import SearchClient, SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    SearchFieldDataType,
    ComplexField,
    Field
)
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

from app.core.config import settings

logger = logging.getLogger(__name__)


class AzureSearchVectorStore:
    """Azure AI Search vector store with HNSW indexing and parent-child chunking."""
    
    def __init__(
        self,
        index_name: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Azure AI Search vector store.
        
        Args:
            index_name: Name of the search index
            endpoint: Azure AI Search endpoint
            api_key: Azure AI Search API key (optional if using managed identity)
        """
        self.index_name = index_name or settings.AZURE_SEARCH_INDEX_NAME
        self.endpoint = endpoint or settings.AZURE_SEARCH_ENDPOINT
        
        # Authentication
        if api_key or settings.AZURE_SEARCH_API_KEY:
            credential = AzureKeyCredential(api_key or settings.AZURE_SEARCH_API_KEY)
        else:
            # Use managed identity or default credential
            credential = DefaultAzureCredential()
        
        self.search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=credential
        )
        
        self.index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=credential
        )
        
        self.dimensions = settings.EMBEDDING_DIMENSIONS
        self.vector_profile = settings.AZURE_SEARCH_VECTOR_PROFILE
        self.hnsw_config = settings.AZURE_SEARCH_HNSW_CONFIG
        
        # Ensure index exists
        self._ensure_index()
    
    def _ensure_index(self):
        """Create index if it doesn't exist."""
        try:
            self.index_client.get_index(self.index_name)
            logger.info(f"Index {self.index_name} already exists")
        except Exception:
            logger.info(f"Creating index {self.index_name}")
            self._create_index()
    
    def _create_index(self):
        """Create Azure AI Search index with vector search configuration."""
        fields = [
            SimpleField(name="id", type=SearchFieldDataType.String, key=True),
            SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
            SimpleField(name="parent_id", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="child_id", type=SearchFieldDataType.String, filterable=True),
            SearchableField(name="subject", type=SearchFieldDataType.String),
            SimpleField(name="is_config", type=SearchFieldDataType.Boolean, filterable=True),
            SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
            SimpleField(name="page", type=SearchFieldDataType.Int32, filterable=True),
            SimpleField(name="organization", type=SearchFieldDataType.String, filterable=True),
            Field(
                name="vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=self.dimensions,
                vector_search_profile_name=self.vector_profile
            )
        ]
        
        vector_search = VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name=self.vector_profile,
                    algorithm_configuration_name=self.hnsw_config
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(
                    name=self.hnsw_config,
                    kind=VectorSearchAlgorithmKind.HNSW
                )
            ]
        )
        
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search
        )
        
        self.index_client.create_or_update_index(index)
        logger.info(f"Created/updated index {self.index_name}")
    
    def add_documents(
        self,
        documents: List[Dict],
        batch_size: Optional[int] = None
    ) -> List[str]:
        """
        Add documents to the index in batches.
        
        Args:
            documents: List of document dicts with required fields
            batch_size: Batch size for uploads (defaults to config)
            
        Returns:
            List of document IDs added
        """
        batch_size = batch_size or settings.BATCH_SIZE
        doc_ids = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            try:
                result = self.search_client.upload_documents(documents=batch)
                
                # Check for errors
                for r in result:
                    if r.succeeded:
                        doc_ids.append(r.key)
                    else:
                        logger.error(f"Failed to upload document {r.key}: {r.error_message}")
                
                logger.info(f"Uploaded batch {i//batch_size + 1} ({len(batch)} documents)")
            except Exception as e:
                logger.error(f"Error uploading batch: {e}")
                raise
        
        return doc_ids
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        search_text: Optional[str] = None,
        filters: Optional[str] = None,
        select: Optional[List[str]] = None
    ) -> List[Tuple[float, Dict]]:
        """
        Search for similar vectors.
        
        Args:
            query_vector: Query vector (list of floats)
            top_k: Number of results to return
            search_text: Optional text for hybrid search
            filters: Optional OData filter expression
            select: Optional list of fields to return
            
        Returns:
            List of tuples: (score, document_dict)
        """
        if select is None:
            select = ["id", "content", "source", "page", "subject", "parent_id", "child_id", "is_config"]
        
        vector_query = VectorizedQuery(
            vector=query_vector,
            k_nearest_neighbors=top_k,
            fields="vector"
        )
        
        try:
            results = self.search_client.search(
                search_text=search_text,  # None for vector-only, text for hybrid
                vector_queries=[vector_query],
                filter=filters,
                top=top_k,
                select=select
            )
            
            search_results = []
            for result in results:
                score = result.get("@search.score", 0.0)
                doc = dict(result)
                search_results.append((score, doc))
            
            logger.info(f"Search returned {len(search_results)} results")
            return search_results
            
        except Exception as e:
            logger.error(f"Error in search: {e}")
            raise
    
    def get_parent_context(self, parent_id: str) -> Optional[Dict]:
        """
        Retrieve parent chunk by ID.
        
        Args:
            parent_id: Parent chunk ID
            
        Returns:
            Parent document dict or None
        """
        try:
            result = self.search_client.get_document(key=parent_id)
            return dict(result)
        except Exception as e:
            logger.warning(f"Could not retrieve parent {parent_id}: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Get statistics about the index."""
        try:
            stats = self.search_client.get_document_count()
            return {
                'total_documents': stats,
                'dimension': self.dimensions,
                'index_name': self.index_name
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {
                'total_documents': 0,
                'dimension': self.dimensions,
                'index_name': self.index_name
            }


# Global singleton instance
_azure_search_store: Optional['AzureSearchVectorStore'] = None


def get_vector_store() -> AzureSearchVectorStore:
    """Get or create the global Azure Search vector store instance."""
    global _azure_search_store
    if _azure_search_store is None:
        _azure_search_store = AzureSearchVectorStore()
    return _azure_search_store

