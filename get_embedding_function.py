from langchain_ollama import OllamaEmbeddings
import os
# from langchain_community.embeddings.bedrock import BedrockEmbeddings


def get_embedding_function():
    # embeddings = BedrockEmbeddings(
    #     credentials_profile_name="default", region_name="us-east-1"
    # )
    # Get Ollama base URL from environment, default to localhost
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url=ollama_base_url)
    return embeddings
