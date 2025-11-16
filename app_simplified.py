import os
import importlib
import uvicorn
import chromadb
try:
    FastAPI = importlib.import_module("fastapi").FastAPI
except Exception:
    class FastAPI:
        def __init__(self, *args, **kwargs):
            pass
        def post(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator
        def get(self, *args, **kwargs):
            def decorator(func):
                return func
            return decorator

from pydantic import BaseModel

# For this simplified version, we'll use basic text similarity instead of heavy models
try:
    genai = importlib.import_module("google.generativeai")
except Exception:
    class _GenAIShim:
        def configure(self, *args, **kwargs):
            raise RuntimeError("google.generativeai is not installed")
        class GenerativeModel:
            def __init__(self, *args, **kwargs):
                raise RuntimeError("google.generativeai is not installed")
    genai = _GenAIShim()

# --- 1. Simplified Model Setup ---
try:
    print("🚀 Starting RAG API with simplified models...")
    
    # Configure Gemini (lightweight)
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set.")
    genai.configure(api_key=api_key)
    generation_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    print("✅ Gemini model configured")

    # Connect to ChromaDB (local)
    db_path = "./chroma_db"
    client = chromadb.PersistentClient(path=db_path)
    
    # Check if collection exists
    try:
        collection = client.get_collection(name="shakespeare_collection")
        print("✅ Connected to existing ChromaDB collection")
        # Get a sample to verify it has data
        sample = collection.peek(limit=1)
        if sample['documents']:
            print(f"✅ Collection has {len(sample['documents'])} documents ready")
        else:
            print("⚠️ Collection exists but is empty")
    except Exception as e:
        print(f"❌ ChromaDB collection not found: {e}")
        print("💡 You may need to run your data ingestion script first")
        # Create empty collection for testing
        collection = client.get_or_create_collection(name="shakespeare_collection")
    
    print("🎉 Basic setup complete! API is ready.")
    
except Exception as e:
    print(f"❌ Setup error: {e}")
    # Create minimal fallback
    collection = None
    generation_model = None

# --- 2. System Prompt ---
SYSTEM_PROMPT = """
You are an Expert Shakespearean Scholar. Your persona is academic, insightful, and clear.
Your target audience is an ICSE Class 10 student.

You MUST follow these rules:
1. Answer Only from Context: Use only the provided CONTEXT to answer the question.
2. Cite Evidence: Support your answer with textual evidence from the context.
3. Stay in Persona: Maintain an academic, helpful tone.
4. Handle "I don't know": If the answer isn't in the context, say so clearly.

Question: {question}

CONTEXT:
{context}

Provide your scholarly answer based only on this context.
"""

# --- 3. FastAPI App ---
app = FastAPI(title="Shakespeare RAG API", description="Simplified version for testing")

class QueryRequest(BaseModel):
    query: str

class Source(BaseModel):
    chunk: str
    metadata: dict

class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]

@app.get("/")
def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Shakespeare RAG API is running (simplified version)",
        "google_api_key": "Set" if os.getenv("GOOGLE_API_KEY") else "Not set",
        "chromadb": "Connected" if collection else "Not connected",
        "gemini": "Ready" if generation_model else "Not ready"
    }

@app.post("/query", response_model=QueryResponse)
def query_rag(request: QueryRequest):
    """Query the RAG system with simplified retrieval."""
    
    if not collection:
        return QueryResponse(
            answer="ChromaDB collection not available. Please check your data setup.",
            sources=[]
        )
    
    if not generation_model:
        return QueryResponse(
            answer="Gemini model not available. Please check your API key.",
            sources=[]
        )
    
    try:
        # Simple text search in ChromaDB (without embeddings for now)
        # This will work if you have documents in your collection
        results = collection.query(
            query_texts=[request.query],
            n_results=3
        )
        
        if not results['documents'] or not results['documents'][0]:
            return QueryResponse(
                answer="No relevant documents found in the database.",
                sources=[]
            )
        
        # Format context
        retrieved_chunks = results['documents'][0]
        retrieved_metadatas = results['metadatas'][0]
        
        context_string = "\n\n---\n\n".join(retrieved_chunks)
        
        # Generate answer using Gemini
        prompt = SYSTEM_PROMPT.format(
            question=request.query,
            context=context_string
        )
        
        response = generation_model.generate_content(prompt)
        final_answer = response.text
        
        # Format sources
        sources_list = []
        for i, (chunk, metadata) in enumerate(zip(retrieved_chunks, retrieved_metadatas)):
            sources_list.append(Source(
                chunk=chunk[:200] + "..." if len(chunk) > 200 else chunk,
                metadata=metadata or {}
            ))
        
        return QueryResponse(
            answer=final_answer,
            sources=sources_list
        )
        
    except Exception as e:
        return QueryResponse(
            answer=f"Error processing query: {str(e)}",
            sources=[]
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003)