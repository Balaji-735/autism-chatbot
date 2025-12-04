# Understanding RAG Relevance Scores

## What is the Score?

The **score** displayed with each source is a **cosine distance** metric that measures how similar the document chunk is to your query.

## How It Works

1. **Your question** is converted to a vector (embedding) using the `nomic-embed-text` model
2. **Document chunks** in the database are also stored as vectors (embeddings)
3. **ChromaDB** calculates the cosine distance between your query vector and each document vector
4. The system returns the **top 5 most similar chunks** (lowest scores = best matches)

## Score Interpretation

### Score Ranges

- **0.0 - 0.3**: 🎯 **Excellent match** - Highly relevant content
- **0.3 - 0.5**: ✅ **Good match** - Relevant content with some connection
- **0.5 - 1.0**: ⚡ **Fair match** - Somewhat relevant but may be tangential
- **1.0+**: ❌ **Poor match** - Not very relevant (rarely shown in top 5)

### Important Notes

- **Lower scores = Better matches** (closer vectors = more similar content)
- **Higher scores = Worse matches** (further vectors = less similar content)
- **Score of 0** = Perfect match (identical vectors - very rare)
- **Score of 1** = No similarity (orthogonal vectors)
- **Score of 2** = Opposite meaning (very rare)

## Example Scores from Your Query

Based on your example:
- **Score: 0.330** - Excellent match (first result)
- **Score: 0.349** - Excellent match (second result)  
- **Score: 0.372** - Good match (third result)

All three scores are quite low, indicating **strong relevance** to your query. The system uses these top matches to generate the answer.

## Why Use Distance Instead of Similarity?

ChromaDB uses **cosine distance** (not similarity) because:
- It's more efficient for ranking in vector databases
- Distance metrics work better with certain indexing algorithms
- It's the standard metric used by most vector databases

**Distance** and **similarity** are inversely related:
- Distance = 0 → Similarity = 1.0 (100% similar)
- Distance = 1 → Similarity = 0.0 (0% similar)

## How the RAG System Uses Scores

1. Retrieves top 5 chunks (lowest scores)
2. Combines them into context
3. Sends context + your question to the LLM (Mistral)
4. LLM generates an answer based on the provided context

The lower the scores of the retrieved chunks, the more relevant the context, leading to better answers.

## Tips for Better Results

- **Ask specific questions** - More specific queries get lower scores (better matches)
- **Use relevant keywords** - Include domain-specific terms from your documents
- **Check source scores** - If all scores are > 0.7, your question may not match well with the documents
- **Review sources** - The displayed source content helps verify relevance

## Technical Details

- **Embedding Model**: `nomic-embed-text` (via Ollama)
- **Vector Database**: ChromaDB
- **Distance Metric**: Cosine distance
- **Top K**: 5 chunks retrieved per query
- **Chunk Size**: 800 characters with 80 character overlap

For more information, see the [system architecture documentation](./system_architecture.md).


