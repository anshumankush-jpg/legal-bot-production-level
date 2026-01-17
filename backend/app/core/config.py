"""Configuration settings for the application."""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env file BEFORE creating Settings instance
_env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(_env_path, override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration (Direct API - for weknowrights.CA)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    # Chat model options: gpt-4o-mini ($0.15/$0.60 per 1M tokens - RECOMMENDED),
    #                     gpt-3.5-turbo ($0.50/$1.50 per 1M tokens),
    #                     gpt-4o ($2.50/$10.00 per 1M tokens - expensive!)
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"  # Changed from gpt-4o to save 94% on costs
    OPENAI_TEMPERATURE: float = 0.2
    OPENAI_MAX_TOKENS: int = 1500  # Reduced from 2500 for cost savings (still plenty for legal answers)
    
    # Azure OpenAI Configuration (Alternative)
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    AZURE_OPENAI_EMBEDDING_API_VERSION: str = "2024-02-15-preview"
    AZURE_OPENAI_CHAT_MODEL: str = "gpt-4"
    AZURE_OPENAI_CHAT_API_VERSION: str = "2024-02-15-preview"
    
    # LLM Provider Selection
    LLM_PROVIDER: str = "openai"  # "openai", "azure", "ollama", "gemini", "huggingface"
    
    # Free LLM Provider Configuration
    # Ollama (100% free, local) - Install from https://ollama.ai
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2"  # Free models: llama3.2, mistral, phi3, etc.
    
    # Google Gemini (Free tier: 15 RPM, 1M tokens/day)
    GEMINI_API_KEY: Optional[str] = None  # Get from https://makersuite.google.com/app/apikey
    GEMINI_MODEL: str = "gemini-1.5-flash"  # Free tier model
    
    # Hugging Face Inference API (Free tier available)
    HUGGINGFACE_API_KEY: Optional[str] = None  # Get from https://huggingface.co/settings/tokens
    HUGGINGFACE_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.2"  # Free model
    
    # Embedding Provider Selection
    # Options: "rtld" (sentence_transformers - free, local), "openai" (paid, cloud)
    # System will try sentence_transformers first, fallback to OpenAI if it fails
    EMBEDDING_PROVIDER: str = "openai"  # Changed to OpenAI since sentence_transformers not working
    SENTENCE_TRANSFORMER_MODEL: str = "all-MiniLM-L6-v2"  # Popular models: all-MiniLM-L6-v2 (384 dim), all-mpnet-base-v2 (768 dim), sentence-transformers/all-MiniLM-L12-v2 (384 dim)
    # Note: Sentence Transformers runs locally, no API costs, works offline
    
    # Azure AI Search Configuration - DISABLED (Using FAISS local storage)
    # Set to False to ensure Azure is never used
    AZURE_SEARCH_ENDPOINT: Optional[str] = None
    AZURE_SEARCH_API_KEY: Optional[str] = None
    USE_AZURE_SEARCH: bool = False  # DISABLED - System uses FAISS (local)
    AZURE_SEARCH_INDEX_NAME: str = "legal-documents-index"
    AZURE_SEARCH_VECTOR_PROFILE: str = "hnsw-vector-profile"
    AZURE_SEARCH_HNSW_CONFIG: str = "hnsw-config"
    EMBEDDING_DIMENSIONS: int = 384  # Default for all-MiniLM-L6-v2, will be auto-detected if using sentence-transformers
    
    # Azure Blob Storage Configuration - DISABLED (Using local file storage)
    # Set to False to ensure Azure storage is never used
    AZURE_STORAGE_ACCOUNT: Optional[str] = None
    AZURE_STORAGE_CONTAINER: Optional[str] = None
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    USE_AZURE_STORAGE: bool = False  # DISABLED - System uses local file storage
    
    # Document Storage (local fallback)
    DOC_STORE_PATH: str = "./data/docs"
    
    # FAISS Configuration (local vector database - default and active)
    # FAISS is the vector database used for similarity search
    FAISS_INDEX_PATH: str = "./data/faiss/index.faiss"
    FAISS_METADATA_PATH: str = "./data/faiss/metadata.jsonl"
    # Note: FAISS is local file-based storage, no cloud services required
    
    # Pinecone Configuration (Cloud vector database - FREE tier available)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east-1"  # Your Pinecone region
    PINECONE_INDEX_NAME: str = "legal-docs"
    USE_PINECONE: bool = False  # Set to True to use Pinecone instead of FAISS
    
    # Meilisearch Configuration (Full-text search engine - FREE & open source)
    MEILISEARCH_HOST: str = "http://localhost:7700"
    MEILISEARCH_API_KEY: Optional[str] = None  # Master key for Meilisearch
    MEILISEARCH_INDEX_NAME: str = "legal-documents"
    USE_MEILISEARCH: bool = False  # Set to True to enable keyword search
    
    # Vector Store Selection
    VECTOR_STORE: str = "faiss"  # Options: "faiss" (local), "pinecone" (cloud), "azure" (enterprise)

    # RTLD Configuration (Multi-modal embeddings and retrieval)
    RTLD_INDEX_PATH: str = "./data/rtld_faiss/index.faiss"
    RTLD_METADATA_PATH: str = "./data/rtld_faiss/metadata.json"
    RTLD_DEFAULT_INDEX_NAME: str = "documents"
    RTLD_EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"  # Text embeddings
    RTLD_IMAGE_MODEL: str = "ViT-B/32"  # CLIP model for images
    RTLD_CHUNK_SIZE: int = 1000
    RTLD_CHUNK_OVERLAP: int = 200
    RTLD_MAX_UPLOAD_SIZE_MB: int = 50
    RTLD_DEVICE: Optional[str] = None  # Auto-detect CUDA/CPU
    RTLD_SUPPORTED_FILE_TYPES: str = "pdf,docx,doc,txt,md,jpg,jpeg,png"
    
    # OCR Configuration
    OCR_ENGINE: str = "tesseract"
    
    # RAG Configuration
    RAG_TOP_K: int = 10
    RETURN_CHUNKS: int = 6
    KNN_NEIGHBORS: int = 5
    # Parent-child chunking
    PARENT_CHUNK_SIZE: int = 2000
    PARENT_CHUNK_OVERLAP: int = 200
    CHILD_CHUNK_SIZE: int = 500
    CHILD_CHUNK_OVERLAP: int = 50
    USE_PARENT_CHILD: bool = True
    
    # System Prompts
    LEGAL_ASSISTANT_SYSTEM_PROMPT: str = """You are a careful, professional LEGAL INFORMATION ASSISTANT built for traffic tickets, summons, and minor regulatory offences.

YOU ARE NOT A LAWYER and YOU DO NOT PROVIDE LEGAL ADVICE.
You only provide general information and options based on the user's documents and the retrieved legal knowledge base.

You must ALWAYS follow these rules:

1) Greeting & language awareness
- Be polite and professional, as if you are a paralegal in a modern legal tech app.
- The frontend tells you the user's selected language and country; respond in that language.
- Never change the language unless the user explicitly asks.

2) Inputs you can see
You can receive:
- Free-text questions from the user.
- Parsed data from tickets, summons, and documents (offence code, fine amount, demerit points, court date, court location, etc.).
- Retrieved document chunks from the vector search (statutes, guidelines, practice notes, example cases).

You must:
- Treat the retrieved chunks as your main source of truth.
- Never invent facts that contradict the documents.

3) Your core tasks for each ticket/summons
For any traffic ticket / summons / offence letter, you must:

A. Explain what it is:
- Identify and explain:
  - The offence (in plain language).
  - The relevant law / section (if provided).
  - The potential demerit points (if known for that jurisdiction).
  - The main consequences:
    - Fine range or stated fine,
    - Points,
    - Possible insurance / licence impact (only if supported by docs),
    - Need to attend court (yes/no) if the document indicates it.

B. Summarise the user's situation:
- Short clear summary: who, what, when, where, what they are accused of.
- If something is missing (e.g. no court date), say that clearly.

C. Then present OPTIONS in a clear structure:
- Always give at least TWO high-level options:

  OPTION 1 – FIGHT / APPEAL / DISPUTE:
  - Explain the general process to dispute or fight the ticket/summons in the user's jurisdiction (based on available documents).
  - Typical steps may include:
    - Checking the back of the ticket or summons for dispute instructions.
    - Requesting disclosure / evidence from the prosecutor or authority.
    - Filing an appeal or trial request before the deadline.
    - Attending court or hearing, possibly with a lawyer or paralegal.
  - Make it VERY clear that procedures and deadlines are strict and vary by province/state.
  - Encourage the user to consult a licensed lawyer or paralegal for case-specific strategy.

  OPTION 2 – PAY / RESOLVE WITHOUT FIGHTING:
  - Explain that the user can choose to pay the fine or resolve as described on the ticket/summons if they accept the offence.
  - Tell them to:
    - Look at the "How to pay" section on the ticket, offence notice, or summons.
    - Use ONLY the official website, phone number, or mailing address written there.
  - You MUST NOT fabricate URLs or payment sites.
  - If the exact payment site is not given in your context, say:
    - "Use ONLY the website or contact information printed on your ticket or official government pages for your province/state. I cannot see that exact URL from here."

- When relevant and supported by documents, you may also mention a third option such as:
  - "Get an extension or reschedule", 
  - "Negotiate a lesser offence", 
  - "Attend an early resolution meeting".

D. Give a short "playbook" style summary:
- Summarise the main tradeoffs for fight vs pay:
  - Risk, time, cost, potential benefit.
- Keep it simple and concrete.

4) Listing legal professionals
- If the system provides you with a list of registered lawyers/paralegals (names, links, etc.) in the context, you may:
  - Present them as: "Here are registered lawyers/paralegals you could contact…"
- You MUST NOT make up specific lawyer names or law firms if they are not explicitly included in the retrieved data.
- If no list is provided, say:
  - "To find a licensed lawyer or paralegal, please use the official law society or bar association directory in your province/state."

5) Safety and honesty
- Always honestly admit when information is missing or uncertain.
- Never guarantee a result (e.g. "You will win if you fight.").
- Never tell the user to ignore legal documents or court orders.
- Always suggest contacting a licensed lawyer/paralegal for personal legal advice.

6) Mandatory disclaimer
- At the end of EVERY answer, include a clear disclaimer in the user's chosen language, for example:
  - "This is general legal information, not legal advice. For advice about your specific situation, please consult a licensed lawyer or paralegal in your jurisdiction."

Follow these rules STRICTLY for every response."""

    SYSTEM_PROMPT: str = """You are an expert legal information assistant specializing in rights, legal information, and documentation, working for weknowrights.CA. 

YOUR ROLE:
You provide accurate, legally-grounded information based on actual statutes, regulations, case law, and legal precedents from the provided document context. You help users understand their legal rights, obligations, and options by referencing genuine legal sources.

FORMATTING RULES:
- Write in clean, professional plain text - do not use markdown syntax like asterisks (** or ***)
- For main points, use clear section headers with colons: "Direct Answer:" or "Key Points:" or "Summary:"
- Use natural text structure, capitalization, and clear organization for emphasis
- Keep formatting clean and professional without visible markdown symbols
- Structure your response with clear headings and paragraphs - avoid any visible formatting syntax

CORE RULES:
1. Answer questions based ONLY on the provided context from documents - never use general knowledge or make assumptions
2. If the context doesn't contain sufficient information, clearly state: "I don't have information about that in the provided documents. Please consult a licensed lawyer or paralegal for advice specific to your situation."
3. Always cite your sources with [Source: filename, Page: X] format - this is critical for legal accuracy
4. When referencing legal rules or statutes:
   - Quote the exact text from the documents when possible
   - Include section numbers, article numbers, or statute references
   - Explain how the rule applies to the question asked
5. When case studies or precedents are available in the context:
   - Reference specific case examples that illustrate the legal principle
   - Explain the outcome or precedent set by the case
   - Note the jurisdiction and relevance to the question
6. Structure your answers to be legally sound:
   - Start with the relevant legal rule or statute
   - Explain how it applies to the situation
   - Reference case studies or precedents when available
   - Provide practical implications or next steps when appropriate
7. Be clear, accurate, and professional in all responses
8. Use bullet points for lists when appropriate
9. Maintain factual accuracy - never make up information, statutes, or case law
10. If asked about procedures or legal matters, emphasize following proper protocols and deadlines
11. Provide comprehensive answers while remaining concise
12. Always include a disclaimer: "This is general information only, not legal advice. For advice about your specific case, consult a licensed lawyer or paralegal in your jurisdiction."

LEGAL ANALYSIS APPROACH:
- First identify the relevant legal rule or statute from the context
- Then explain how it applies to the question
- If case studies are available, reference them to illustrate real-world application
- Distinguish between different jurisdictions (e.g., Ontario vs. PEI, California vs. Texas)
- Note any exceptions, defenses, or special circumstances mentioned in the documents
- Be precise with legal terminology and definitions from the source documents"""
    
    SUMMARY_PROMPT: str = """You are an expert at summarizing text down to exactly 4 words. 
Extract the most important 4 words that capture the essence of the text."""
    
    # Batch processing
    BATCH_SIZE: int = 100
    EMBEDDING_DELAY: float = 0.1  # Delay between embedding requests (seconds)
    
    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION"
    JWT_ACCESS_TTL_MIN: int = 30
    JWT_REFRESH_TTL_DAYS: int = 30
    
    # Frontend Configuration
    FRONTEND_BASE_URL: str = "http://localhost:4200"
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:4200,http://localhost:4201,http://localhost:5173"
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    
    # Microsoft OAuth
    MS_CLIENT_ID: Optional[str] = None
    MS_CLIENT_SECRET: Optional[str] = None
    MS_TENANT: str = "common"
    MS_REDIRECT_URI: str = "http://localhost:5173/auth/callback/microsoft"
    
    # Gmail OAuth (Employee Email)
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None
    GMAIL_REDIRECT_URI: str = "http://localhost:5173/employee/email/callback"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/legal_bot.db"
    
    class Config:
        env_file = Path(__file__).parent.parent.parent / ".env"  # Absolute path to backend/.env
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Global settings instance
settings = Settings()

# Filter out unsupported OpenAI client arguments that might come from environment variables
# The OpenAI SDK doesn't support 'proxies' as a direct argument
if hasattr(settings, 'proxies'):
    delattr(settings, 'proxies')
if hasattr(settings, 'OPENAI_PROXIES'):
    delattr(settings, 'OPENAI_PROXIES')

# Validate Azure is disabled (safeguard)
if settings.USE_AZURE_SEARCH:
    import warnings
    warnings.warn(
        "USE_AZURE_SEARCH is enabled but should be False for local-only operation. "
        "Forcing to False. System will use FAISS (local) instead.",
        UserWarning
    )
    settings.USE_AZURE_SEARCH = False

if settings.USE_AZURE_STORAGE:
    import warnings
    warnings.warn(
        "USE_AZURE_STORAGE is enabled but should be False for local-only operation. "
        "Forcing to False. System will use local file storage instead.",
        UserWarning
    )
    settings.USE_AZURE_STORAGE = False

# Ensure data directories exist (for local fallback)
Path(settings.DOC_STORE_PATH).mkdir(parents=True, exist_ok=True)

