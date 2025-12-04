# System Architecture Diagram for Autism-Chatbot Project

This document contains the system architecture diagram in Mermaid format. You can copy the code below and paste it into a Mermaid renderer (e.g., https://mermaid.live/) to visualize the diagram.

## Diagram Layout (Vertical Flowchart)

Title: "RAG Workflow (Vertical)" at the top.

Diagram Elements (Vertical Flow):

Top Box:

Label: "Data Ingestion (Offline)"
Shape: Rectangle (Header)
Arrow Down to:

Label: "Load PDFs\nfrom data/"
Shape: Rectangle
Arrow Down to:

Label: "Chunk Text\n(800 chars, 80 overlap)"
Shape: Rectangle
Arrow Down to:

Label: "Embed Chunks\n(nomic-embed-text)"
Shape: Rectangle
Arrow Down to:

Label: "Store in ChromaDB"
Shape: Rectangle (Database Icon)
Arrow Down to:

Label: "Query Phase (Runtime)"
Shape: Rectangle (Header)
Arrow Down to:

Label: "User Query"
Shape: Rectangle (Input)
Arrow Down to:

Label: "Embed Query\n(nomic-embed-text)"
Shape: Rectangle
Arrow Down to:

Label: "Search ChromaDB\n(Top 5 Chunks)"
Shape: Rectangle
Arrow Down to:

Label: "Build Prompt\n(Context + Query)"
Shape: Rectangle
Arrow Down to:

Label: "Generate Response\n(Mistral LLM)"
Shape: Rectangle
Arrow Down to:

Label: "Output Answer"
Shape: Rectangle (Output)
Arrow Back Up from Output to User Query:

Label: "Loop"
Shape: Curved Arrow (Loop)

## Description of Components

- **Data Ingestion Pipeline**:
  - PDFs from the `data/` directory are loaded and split into chunks.
  - Chunks are embedded using Ollama's nomic-embed-text model.
  - Embeddings are stored in ChromaDB for persistence.

- **Query Pipeline**:
  - User queries are embedded and searched against the vector DB.
  - Top relevant contexts are retrieved and fed into the Mistral LLM via a prompt template.
  - The LLM generates a response based on the context.

- **Key Technologies**:
  - Embedding: Ollama (nomic-embed-text)
  - LLM: Ollama (mistral)
  - Vector DB: ChromaDB
  - Libraries: LangChain ecosystem

- **External Dependencies**:
  - Ollama server must be running locally for embeddings and LLM inference.

This diagram provides a high-level overview of the RAG system's flow.
