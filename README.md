# Julius Caesar RAG System

A Retrieval-Augmented Generation (RAG) system for answering questions about Shakespeare's "Julius Caesar" using Google Gemini, ChromaDB, and FastAPI.

---

## Quick Start

### One Command to Start Everything:

```bash
python start.py
```

That's it! The script will:
- Check all requirements
- Start backend API (port 8000)
- Start frontend UI (port 3000)
- Open your browser automatically

---

## Project Structure

```
NLP_ADV2/
├── app/
│   ├── etl.ipynb                    # Data preprocessing & chunking
│   ├── indexingVectorstore.ipynb    # Vector database indexing
│   ├── evaluation.ipynb             # RAGAS evaluation metrics
│   └── main.py                      # FastAPI backend
├── frontend/
│   ├── index.html                   # Web UI
│   ├── Dockerfile                   # Frontend container
│   └── nginx.conf                   # Nginx configuration
├── data/
│   └── julius-caesar.pdf            # Source document
├── chroma_db/                       # Vector database (auto-generated)
├── chunks.jsonl                     # Processed text chunks
├── Dockerfile                       # Backend container
├── docker-compose.yml               # Service orchestration
├── start.py                         # One-command startup script
├── run_local.sh                     # Local execution script
├── run_docker.sh                    # Docker execution script
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables (API key)
├── README.md                        # This file
├── FLOW_EXPLANATION.md              # Detailed system flow
└── EVALUATION_GUIDE.md              # Evaluation metrics guide
```

---

## Features

- **RAG Pipeline**: Retrieval-Augmented Generation with ChromaDB
- **LLM**: Google Gemini 2.5 Flash for answer generation
- **Embeddings**: BAAI/bge-base-en-v1.5 (768 dimensions)
- **Vector DB**: ChromaDB for semantic search
- **API**: FastAPI backend with CORS support
- **Frontend**: Beautiful web UI with chat interface
- **Evaluation**: 5 RAGAS metrics for quality assessment
- **Docker**: Full containerization support

---

## Installation & Setup

### Prerequisites

- Python 3.9+
- Google API Key (for Gemini)

### Local Setup

1. **Clone the repository**
```bash
cd /Users/prabhav.pandey_int/Desktop/NLP_ADV2
```

2. **Create virtual environment** (if not exists)
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
echo "GOOGLE_API_KEY=your-api-key-here" > .env
```

5. **Run the system**
```bash
python start.py
```

---

## Running the System

### Method 1: One Command (Easiest)

```bash
python start.py
```

### Method 2: Manual Local Setup

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
export GOOGLE_API_KEY="your-key"
python app/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python3 -m http.server 3000
```

Then open: http://localhost:3000

### Method 3: Using Shell Scripts

**Local:**
```bash
./run_local.sh
```

**Docker:**
```bash
./run_docker.sh
```

### Method 4: Docker Compose

```bash
docker-compose up --build
```

Then open: http://localhost:3000

---

## System Flow

### 1. Data Preprocessing (`etl.ipynb`)
- Load PDF document
- Extract text
- Clean and normalize
- Split into chunks
- Save to `chunks.jsonl`

### 2. Vector Indexing (`indexingVectorstore.ipynb`)
- Load chunks from `chunks.jsonl`
- Generate embeddings using BAAI/bge-base-en-v1.5
- Store in ChromaDB
- Create searchable index

### 3. Query Processing (`main.py`)
- User asks a question
- Generate query embedding
- Retrieve top-k similar chunks from ChromaDB
- Pass chunks + question to Gemini
- Generate concise answer (2-3 sentences)
- Return answer with source citations

### 4. Evaluation (`evaluation.ipynb`)
- Test with 8 questions
- Measure 5 RAGAS metrics:
  - Faithfulness
  - Answer Relevancy
  - Context Precision
  - Context Recall
  - Answer Correctness
- Generate performance report

---

## API Endpoints

### `GET /`
Health check endpoint

**Response:**
```json
{
  "status": "ok",
  "message": "Shakespeare RAG API (Gemini) is running."
}
```

### `POST /query`
Query the RAG system

**Request:**
```json
{
  "query": "Who is Brutus?"
}
```

**Response:**
```json
{
  "answer": "Brutus is a Roman senator...",
  "sources": [
    {
      "chunk": "Text from the play...",
      "metadata": {
        "source": "Act 1, Scene 2",
        "chunk_id": 5
      }
    }
  ]
}
```

---

## Evaluation Metrics

The system uses **RAGAS** framework with 5 metrics:

1. **Faithfulness (0-1)**: No hallucinations, factually accurate
2. **Answer Relevancy (0-1)**: Answers the question directly
3. **Context Precision (0-1)**: Retrieved chunks are relevant
4. **Context Recall (0-1)**: All needed info is retrieved
5. **Answer Correctness (0-1)**: Matches ground truth

**Score Interpretation:**
- 0.8-1.0: Excellent
- 0.6-0.8: Good
- 0.4-0.6: Fair
- 0.0-0.4: Needs Improvement

See `EVALUATION_GUIDE.md` for detailed information.

---

## Sample Questions

Try asking:
- "Who is Brutus?"
- "What does the Soothsayer say to Caesar?"
- "Why does Brutus kill Caesar?"
- "What happens at Caesar's funeral?"
- "Who is Cassius?"
- "What is the relationship between Caesar and Brutus?"
- "What role does Mark Antony play?"
- "What are Caesar's last words?"

---

## Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000,3000 | xargs kill
```

### Backend Not Starting
```bash
# Check if API key is set
echo $GOOGLE_API_KEY

# Restart backend
source venv/bin/activate
export GOOGLE_API_KEY="your-key"
python app/main.py
```

### ChromaDB Empty
```bash
# Re-run indexing notebook
jupyter notebook app/indexingVectorstore.ipynb
```

### Module Not Found
```bash
pip install -r requirements.txt
```

---

## Docker Setup

### Build and Run

```bash
# Using docker-compose
docker-compose up --build

# Or manually
docker build -t rag-backend .
docker run -p 8000:8000 -e GOOGLE_API_KEY="your-key" rag-backend
```

### Environment Variables

Create `.env` file:
```
GOOGLE_API_KEY=your-google-api-key-here
```

---

## Development

### Running Notebooks

```bash
cd app
jupyter notebook
```

### Testing API

```bash
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is Brutus?"}'
```

### Running Evaluation

```bash
cd app
jupyter notebook evaluation.ipynb
# Run all cells
```

---

## Technology Stack

- **Backend**: FastAPI, Python 3.9
- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: BAAI/bge-base-en-v1.5
- **Vector DB**: ChromaDB
- **Frontend**: HTML, CSS, JavaScript
- **Evaluation**: RAGAS framework
- **Containerization**: Docker, Docker Compose

---

## Key Files

- **`start.py`**: One-command startup script with monitoring
- **`app/main.py`**: FastAPI backend with RAG logic
- **`app/etl.ipynb`**: Data preprocessing pipeline
- **`app/indexingVectorstore.ipynb`**: Vector database setup
- **`app/evaluation.ipynb`**: System evaluation with metrics
- **`frontend/index.html`**: Web interface
- **`FLOW_EXPLANATION.md`**: Detailed system architecture
- **`EVALUATION_GUIDE.md`**: Metrics and interpretation

---

## Performance

- **Embedding Model**: 768-dimensional vectors
- **Retrieval**: Top-3 chunks per query
- **Response Time**: ~2-3 seconds per query
- **Accuracy**: Measured by RAGAS metrics
- **Database**: 18 chunks from Julius Caesar

---

## License

This project is for educational purposes.

---

## Support

For issues or questions:
1. Check `FLOW_EXPLANATION.md` for system details
2. Check `EVALUATION_GUIDE.md` for metrics
3. Review troubleshooting section above
4. Check API logs in terminal

---

## Quick Commands Reference

```bash
# Start everything
python start.py

# Stop services
lsof -ti:8000,3000 | xargs kill

# Run locally
./run_local.sh

# Run with Docker
./run_docker.sh

# Test API
curl http://localhost:8000/

# Open frontend
open http://localhost:3000
```

---

**Enjoy exploring Julius Caesar with AI!** 🎭
