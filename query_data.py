import argparse
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main():
    # Prepare the DB once at startup.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    model = OllamaLLM(model="mistral")

    print("Interactive RAG Query System. Type 'quit' or 'exit' to stop.")

    while True:
        query_text = input("Enter your question: ").strip()
        if query_text.lower() in ['quit', 'exit']:
            print("Exiting...")
            break
        if not query_text:
            continue
        response_text = query_rag(query_text, db, model)
        print(f"\n{response_text}")


def query_rag(query_text: str, db, model):
    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    response_text = model.invoke(prompt)

    return response_text


if __name__ == "__main__":
    main()
