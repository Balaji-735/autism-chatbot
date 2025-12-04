# Autism Chatbot - RAG System

A full-stack RAG (Retrieval-Augmented Generation) chatbot application for querying autism-related documents. Built with Python (FastAPI + LangChain + ChromaDB) backend and Next.js 14 frontend.

## Architecture

- **Backend**: FastAPI server with LangChain, ChromaDB, and Ollama
- **Frontend**: Next.js 14 App Router with TypeScript, Tailwind CSS, and shadcn/ui
- **Vector Database**: ChromaDB for storing document embeddings
- **LLM**: Ollama (Mistral model)
- **Embeddings**: Ollama (nomic-embed-text model)

## Prerequisites

1. **Python 3.8+** with pip
2. **Node.js 18+** with npm
3. **Ollama** installed and running locally
   - Install from [https://ollama.ai](https://ollama.ai)
   - Run: `ollama pull mistral` and `ollama pull nomic-embed-text`
4. **PDF documents** in the `data/` directory

## Backend Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Populate the database with PDFs:
```bash
python populate_database.py
```

3. Start the FastAPI server:
```bash
python api_server.py
```

The API server will run on `http://localhost:8000`

### Backend API Endpoints

- `GET /` - API information
- `GET /health` - Health check endpoint
- `POST /api/query` - Query the RAG system
  ```json
  {
    "question": "Your question here"
  }
  ```
- `GET /api/pdf?file=<path>` - Serve PDF files from the data directory
  - Returns the PDF file for viewing/downloading
  - Security: Only files within the `data/` directory are accessible

## Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file (optional, defaults to `http://localhost:8000`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The frontend will run on `http://localhost:3000`

## Project Structure

```
.
├── api_server.py           # FastAPI backend server
├── query_data.py           # RAG query logic
├── populate_database.py    # Database population script
├── get_embedding_function.py  # Embedding function configuration
├── requirements.txt        # Python dependencies
├── data/                   # PDF documents directory
├── chroma/                 # ChromaDB storage
└── frontend/               # Next.js frontend application
    ├── app/                # Next.js App Router
    ├── components/         # React components
    ├── lib/                # Utilities and API client
    └── package.json        # Node.js dependencies
```

## Usage

1. Make sure Ollama is running with the required models
2. Start the backend API server
3. Start the frontend development server
4. Open `http://localhost:3000` in your browser
5. Start asking questions about the documents in the `data/` directory

## Development

### Backend Development

- API server: `python api_server.py`
- Reset database: `python populate_database.py --reset`
- Test queries: `python query_data.py`

### Frontend Development

- Development server: `npm run dev`
- Build for production: `npm run build`
- Start production server: `npm start`

## Features

- ✅ RAG-based question answering
- ✅ Source citations with relevance scores
- ✅ **Clickable PDF links** - View source documents directly
- ✅ Beautiful, responsive chat interface
- ✅ Real-time query processing
- ✅ Error handling and loading states
- ✅ Document metadata display
- ✅ Backend health monitoring

## Technology Stack

### Backend
- FastAPI
- LangChain
- ChromaDB
- Ollama

### Frontend
- Next.js 14 (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui
- Lucide React (icons)

## License

MIT
