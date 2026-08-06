from documents_loader import embedding_function
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from dotenv import load_dotenv
import os

load_dotenv()
CHROMA_PATH = os.getenv("CHROMA_PATH")
PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""
model      = OllamaLLM(model = "mistral")
embed_func = embedding_function()

db = Chroma(
    persist_directory  = CHROMA_PATH,
    embedding_function = embed_func
)

def query_rag(question: str):
    results = db.similarity_search_with_score(question, k = 5)
    context = "\n\n---\n\n".join(
        doc.page_content
        for doc, _ in results
    )
    prompt  = ChatPromptTemplate.from_template(
        PROMPT_TEMPLATE
    ).format(
        context  = context,
        question = question
    )
    # sources = [doc.metadata.get("id", None) for doc, _score in results]

    sources = [
        {
            "source": doc.metadata.get("source", "unknown"),
            "page": doc.metadata.get("page", "unknown")
        }
        for doc, _score in results
    ]

    response_text = model.invoke(prompt)

    return {
        "answer": response_text,
        "sources": sources
    }

