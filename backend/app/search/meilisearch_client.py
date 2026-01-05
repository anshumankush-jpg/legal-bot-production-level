"""Meilisearch client for full-text keyword search."""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    import meilisearch
    MEILISEARCH_AVAILABLE = True
except ImportError:
    MEILISEARCH_AVAILABLE = False
    logger.warning("Meilisearch not installed. Run: pip install meilisearch")


class MeilisearchClient:
    """Meilisearch client for fast keyword search."""
    
    def __init__(self, host: str = "http://localhost:7700", api_key: Optional[str] = None, index_name: str = "legal-documents"):
        """
        Initialize Meilisearch client.
        
        Args:
            host: Meilisearch server URL
            api_key: Optional API key (master key)
            index_name: Name of the search index
        """
        if not MEILISEARCH_AVAILABLE:
            raise ImportError("Meilisearch is not installed. Run: pip install meilisearch")
        
        self.host = host
        self.index_name = index_name
        
        try:
            # Initialize client
            self.client = meilisearch.Client(host, api_key)
            
            # Create or get index
            self.index = self.client.index(self.index_name)
            
            # Configure searchable attributes
            self._configure_index()
            
            logger.info(f"✅ Meilisearch initialized: {index_name} at {host}")
        except Exception as e:
            logger.error(f"Failed to connect to Meilisearch: {e}")
            logger.info("Make sure Meilisearch is running. Start with: meilisearch or docker run -p 7700:7700 getmeili/meilisearch:latest")
            raise
    
    def _configure_index(self):
        """Configure index settings for legal documents."""
        try:
            # Set searchable attributes (fields to search in)
            self.index.update_searchable_attributes([
                'content',
                'title',
                'filename',
                'offense_code',
                'statute',
                'case_name',
                'jurisdiction'
            ])
            
            # Set filterable attributes (for filtering results)
            self.index.update_filterable_attributes([
                'jurisdiction',
                'country',
                'province',
                'category',
                'document_type',
                'offense_code'
            ])
            
            # Set sortable attributes
            self.index.update_sortable_attributes([
                'created_at',
                'relevance_score'
            ])
            
            logger.info("✅ Meilisearch index configured")
        except Exception as e:
            logger.warning(f"Could not configure index: {e}")
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Add documents to Meilisearch index.
        
        Args:
            documents: List of document dictionaries (must have 'id' field)
            
        Returns:
            Task info from Meilisearch
        """
        try:
            # Ensure all documents have an 'id' field
            for i, doc in enumerate(documents):
                if 'id' not in doc:
                    doc['id'] = f"doc_{i}"
            
            task = self.index.add_documents(documents)
            logger.info(f"✅ Added {len(documents)} documents to Meilisearch (task: {task.task_uid})")
            return task
        except Exception as e:
            logger.error(f"Error adding documents to Meilisearch: {e}")
            raise
    
    def search(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[str] = None,
        attributes_to_retrieve: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for documents using keyword search.
        
        Args:
            query: Search query string
            limit: Number of results to return
            filters: Optional filter string (e.g., "jurisdiction = Ontario")
            attributes_to_retrieve: List of attributes to return
            
        Returns:
            List of matching documents
        """
        try:
            search_params = {
                'limit': limit
            }
            
            if filters:
                search_params['filter'] = filters
            
            if attributes_to_retrieve:
                search_params['attributesToRetrieve'] = attributes_to_retrieve
            
            results = self.index.search(query, search_params)
            
            logger.info(f"Found {len(results['hits'])} results for query: '{query}'")
            return results['hits']
        except Exception as e:
            logger.error(f"Error searching Meilisearch: {e}")
            return []
    
    def delete_all(self):
        """Delete all documents from the index."""
        try:
            self.index.delete_all_documents()
            logger.info("🗑️ Deleted all documents from Meilisearch")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def delete_by_ids(self, ids: List[str]):
        """Delete specific documents by ID."""
        try:
            self.index.delete_documents(ids)
            logger.info(f"🗑️ Deleted {len(ids)} documents from Meilisearch")
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        try:
            stats = self.index.get_stats()
            return {
                "number_of_documents": stats.number_of_documents,
                "is_indexing": stats.is_indexing,
                "field_distribution": stats.field_distribution
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {"error": str(e)}
    
    def hybrid_search(
        self,
        query: str,
        semantic_results: List[Dict[str, Any]],
        limit: int = 10,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining keyword and semantic results.
        
        Args:
            query: Search query
            semantic_results: Results from vector search (Pinecone/FAISS)
            limit: Number of final results
            keyword_weight: Weight for keyword search (0-1)
            semantic_weight: Weight for semantic search (0-1)
            
        Returns:
            Combined and re-ranked results
        """
        # Get keyword search results
        keyword_results = self.search(query, limit=limit * 2)
        
        # Create score dictionaries
        keyword_scores = {doc['id']: idx for idx, doc in enumerate(keyword_results)}
        semantic_scores = {doc.get('id', doc.get('metadata', {}).get('id')): idx for idx, doc in enumerate(semantic_results)}
        
        # Combine results
        all_ids = set(keyword_scores.keys()) | set(semantic_scores.keys())
        
        combined_results = []
        for doc_id in all_ids:
            # Calculate combined score (lower is better for ranking)
            keyword_rank = keyword_scores.get(doc_id, len(keyword_results))
            semantic_rank = semantic_scores.get(doc_id, len(semantic_results))
            
            combined_score = (keyword_weight * keyword_rank) + (semantic_weight * semantic_rank)
            
            # Get document data
            doc = None
            for kw_doc in keyword_results:
                if kw_doc['id'] == doc_id:
                    doc = kw_doc
                    break
            
            if not doc:
                for sem_doc in semantic_results:
                    sem_id = sem_doc.get('id', sem_doc.get('metadata', {}).get('id'))
                    if sem_id == doc_id:
                        doc = sem_doc.get('metadata', sem_doc)
                        break
            
            if doc:
                doc['hybrid_score'] = combined_score
                doc['keyword_rank'] = keyword_rank
                doc['semantic_rank'] = semantic_rank
                combined_results.append(doc)
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x['hybrid_score'])
        
        logger.info(f"Hybrid search: {len(combined_results)} combined results")
        return combined_results[:limit]
