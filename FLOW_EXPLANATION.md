# RAG System Flow Explanation

## Complete Pipeline Overview

This document explains how the RAG (Retrieval-Augmented Generation) system works from start to finish.

---

## Phase 1: ETL (Extract, Transform, Load)

**File**: `app/etl.ipynb`

### What It Does:
1. **Extract**: Reads the PDF file (`data/julius-caesar.pdf`)
2. **Transform**: Splits the text into chunks by Act and Scene
3. **Load**: Saves chunks to `chunks.jsonl`

### Input:
- `data/julius-caesar.pdf` (Shakespeare's Julius Caesar)

### Output:
- `chunks.jsonl` (18 chunks, one per scene)

### Chunk Structure:
```json
{
  "text": "ACT 1\nSCENE 1\n[full scene text]...",
  "act": 1,
  "scene": 1
}
```

### Why Chunking?
- The play is too large to process at once
- Each scene is a logical unit of meaning
- Smaller chunks = better search results

---

## Phase 2: Indexing (Vector Embeddings)

**File**: `app/indexingVectorstore.ipynb`

### What It Does:
1. **Load**: Reads chunks from `chunks.jsonl`
2. **Embed**: Converts each text chunk into a 768-dimensional vector
3. **Store**: Saves vectors + text + metadata in ChromaDB

### Input:
- `chunks.jsonl` (18 text chunks)

### Output:
- `chroma_db/` (vector database with 18 documents)

### Embedding Model:
- **Model**: `BAAI/bge-base-en-v1.5`
- **Dimension**: 768
- **Purpose**: Converts text to numbers that capture meaning

### How It Works:
```
Text: "Brutus is an honorable man"
  ↓ (embedding model)
Vector: [0.23, -0.45, 0.67, ... 768 numbers total]
```

### ChromaDB Storage:
For each chunk, stores:
- **Vector**: 768 numbers representing meaning
- **Text**: Original scene text
- **Metadata**: Act number, scene number, source

---

## Phase 3: Query & Retrieval (API Server)

**File**: `app/main.py`

### What It Does:
1. **Load Models**: Loads embedding model, ChromaDB, and Gemini LLM
2. **Serve API**: Provides `/query` endpoint
3. **Process Queries**: Converts questions to vectors, searches, and generates answers

### When You Ask a Question:

#### Step 1: Convert Question to Vector
```
Question: "Who is Brutus?"
  ↓ (embedding model)
Query Vector: [0.12, -0.34, 0.56, ... 768 numbers]
```

#### Step 2: Search ChromaDB
```
Find top 3 most similar vectors:
1. Act 4, Scene 2 (similarity: 0.89)
2. Act 5, Scene 1 (similarity: 0.85)
3. Act 3, Scene 2 (similarity: 0.82)
```

#### Step 3: Retrieve Original Text
```
Get the full text of those 3 scenes
```

#### Step 4: Send to Gemini
```
Prompt:
"You are a helpful assistant answering questions about Julius Caesar.

Rules:
1. Answer ONLY from the provided context
2. Keep answers SHORT and CLEAR (2-3 sentences max)
3. Be direct and concise

Question: Who is Brutus?

Context:
[Full text of Act 4, Scene 2]
---
[Full text of Act 5, Scene 1]
---
[Full text of Act 3, Scene 2]

Answer briefly:"
```

#### Step 5: Return Answer
```json
{
  "answer": "Brutus is a character who leads an army alongside Cassius. He states he slew Caesar because he was ambitious and he loved Rome more.",
  "sources": [
    {
      "chunk": "[Act 4, Scene 2 text]",
      "metadata": {"act": 4, "scene": 2}
    },
    ...
  ]
}
```

### API Endpoints:
- `GET /` - Health check
- `POST /query` - Ask a question

---

## Phase 4: Evaluation (Testing)

**File**: `app/evaluation.ipynb`

### What It Does:
1. **Test Questions**: Sends 3 test questions to the API
2. **Check Results**: Verifies sources are retrieved and answers are generated
3. **Calculate Success Rate**: Shows percentage of successful queries

### Test Questions:
1. "Who is Brutus?"
2. "What does the Soothsayer say to Caesar?"
3. "Why does Brutus kill Caesar?"

### Metrics:
- **Vector Search**: Did it find relevant passages?
- **Answer Generation**: Did Gemini generate an answer?
- **Success Rate**: Percentage of working queries

---

## Complete Flow Diagram

```
┌─────────────────────────┐
│  julius-caesar.pdf      │
└───────────┬─────────────┘
            │
            ▼
    ┌───────────────┐
    │  etl.ipynb    │ (Chunking)
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ chunks.jsonl  │ (18 chunks)
    └───────┬───────┘
            │
            ▼
┌───────────────────────────┐
│ indexingVectorstore.ipynb │ (Embedding + Indexing)
└───────────┬───────────────┘
            │
            ▼
    ┌───────────────┐
    │  chroma_db/   │ (Vector Database)
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │   main.py     │ (FastAPI Server)
    └───────┬───────┘
            │
            ▼
    ┌───────────────┐
    │ User Question │
    └───────┬───────┘
            │
            ▼
┌───────────────────────────┐
│  1. Convert to vector     │
│  2. Search ChromaDB       │
│  3. Retrieve 3 chunks     │
│  4. Send to Gemini        │
│  5. Generate answer       │
└───────────┬───────────────┘
            │
            ▼
    ┌───────────────┐
    │    Answer     │
    │  + Sources    │
    └───────────────┘
```

---

## Key Technologies

### 1. **Sentence Transformers**
- Converts text to vectors
- Model: `BAAI/bge-base-en-v1.5`
- Output: 768-dimensional vectors

### 2. **ChromaDB**
- Vector database
- Stores embeddings + text + metadata
- Fast similarity search

### 3. **Google Gemini**
- Large Language Model
- Model: `gemini-2.5-flash`
- Generates natural language answers

### 4. **FastAPI**
- Python web framework
- Provides REST API
- Handles HTTP requests

---

## How Vector Search Works

### Similarity Calculation:
```
Question Vector:  [0.1, 0.5, 0.3, ...]
Chunk 1 Vector:   [0.2, 0.4, 0.3, ...]  → Similarity: 0.89 (High!)
Chunk 2 Vector:   [0.8, 0.1, 0.9, ...]  → Similarity: 0.23 (Low)
Chunk 3 Vector:   [0.1, 0.6, 0.2, ...]  → Similarity: 0.95 (Highest!)
```

The system returns the chunks with the highest similarity scores.

---

## Why This Approach?

### 1. **Accurate**
- Finds relevant passages based on meaning, not just keywords
- Vector search understands context

### 2. **Fast**
- ChromaDB searches millions of vectors in milliseconds
- Pre-computed embeddings = quick retrieval

### 3. **Scalable**
- Can handle large documents
- Easy to add more texts

### 4. **Transparent**
- Returns sources with each answer
- Users can verify the information

---

## Running the System

### Step 1: ETL
```bash
jupyter notebook app/etl.ipynb
# Run all cells
```

### Step 2: Indexing
```bash
jupyter notebook app/indexingVectorstore.ipynb
# Run all cells
```

### Step 3: Start API
```bash
export GOOGLE_API_KEY="your-api-key"
python app/main.py
```

### Step 4: Test
```bash
jupyter notebook app/evaluation.ipynb
# Run all cells
```

Or query directly:
```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is Brutus?"}'
```

---

## Summary

1. **ETL**: Splits PDF into 18 scene chunks
2. **Indexing**: Converts chunks to 768-dim vectors, stores in ChromaDB
3. **Querying**: Searches vectors, retrieves text, generates answer with Gemini
4. **Evaluation**: Tests the system with sample questions

The entire system is designed to answer questions about Julius Caesar by finding relevant passages and generating concise, accurate answers.
