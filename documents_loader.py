import pytesseract
from langchain_core.documents import Document
import os, fitz
from PIL import Image
from dotenv import load_dotenv
import hashlib

from langchain_experimental.text_splitter import SemanticChunker
from langchain_ollama import OllamaEmbeddings
# from langchain_aws import BedrockEmbeddings

load_dotenv()
DATA_PATH = os.getenv("DATA_PATH")

# Function to LOAD the documents (OCR/text)
def load_documents() -> list[Document]:
  documents = []

  for filename in os.listdir(DATA_PATH):
    if filename.endswith(".pdf"):
      path = os.path.join(DATA_PATH, filename)
      doc  = fitz.open(path)

      # Loop to check if text/image are present
      for i, page in enumerate(doc): 
        text = page.get_text().strip()
        # Image detected
        if not text:
          pix  = page.get_pixmap()
          img  = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
          text = pytesseract.image_to_string(img)
        documents.append(Document(
          page_content = text,
          metadata = {
            "source": path,
            "page": i,
            "document_hash": file_hash(path)
          }
        ))
  return documents

def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)

    return h.hexdigest()

# Function that return the EMBEDDING FUNCTION
def embedding_function():
  # embeddings = BedrockEmbeddings(
  #   credentials_profile_name = "default",
  #   region_name              = "eu-west-1"
  # )
  # embeddings = OllamaEmbeddings(model = "mxbai-embed-large")
  embeddings = OllamaEmbeddings(model = "bge-m3")
  return embeddings

# Function to SPLIT into CHUNKS
def split_documents(documents: list[Document]) -> list[Document]:
  text_splitter = SemanticChunker(
    embeddings                  = embedding_function(),
    breakpoint_threshold_type   = "percentile",
    breakpoint_threshold_amount = 95
  )
  return text_splitter.split_documents(documents)