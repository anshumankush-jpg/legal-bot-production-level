EMBEDDING PIPELINE
==================

This folder contains the embedding pipeline for legal documents.

STRUCTURE:
----------
- canada_traffic/     : Processed Canadian traffic act documents
- canada_criminal/    : Processed Canadian criminal law documents
- usa_traffic/        : Processed US traffic law documents
- usa_criminal/       : Processed US criminal law documents
- embeddings_output/  : Generated embeddings (vectors, metadata)

SOURCE DATA:
-----------
- Canadian Traffic Acts: ../canada_traffic_acts/
- Canadian Criminal Law: ../canada criminal and federal law/
- US Traffic Laws: ../USA/ (traffic-related files)
- US Criminal Law: ../usa_criminal_law/

NEXT STEPS:
----------
1. Extract text from PDFs and HTML files
2. Clean and preprocess text
3. Chunk documents into manageable segments
4. Generate embeddings using your chosen model (OpenAI, Cohere, etc.)
5. Store embeddings with metadata (jurisdiction, document type, etc.)
