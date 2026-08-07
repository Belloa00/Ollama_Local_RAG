from documents_loader import embedding_function, load_documents, split_documents
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os, shutil, argparse, hashlib
from dotenv import load_dotenv
import pickle

load_dotenv()
CHROMA_PATH = os.getenv("CHROMA_PATH")

def add_to_chromadb(chunks: list[Document]):
  db = Chroma(
    persist_directory  = CHROMA_PATH,
    embedding_function = embedding_function()
  )
  chunks_with_ids = calculate_chunk_ids(chunks)
  
  # Add or update the documents
  existing_items = db.get(include = [])
  existing_ids   = set(existing_items["ids"])
  print(f"Number of existing documents in DB: {len(existing_ids)}")

  # Add documents that don't exist in the DB
  new_chunks = []
  for chunk in chunks_with_ids:
     if chunk.metadata["id"] not in existing_ids:
        new_chunks.append(chunk)
  
  if len(new_chunks):
    print(f"Adding new documents: {len(new_chunks)}")
    #new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
    #db.add_documents(new_chunks, ids = new_chunk_ids)
    # Add documents in batches
    BATCH_SIZE = 64
    for i in range(0, len(new_chunks), BATCH_SIZE):
        batch = new_chunks[i:i + BATCH_SIZE]
        batch_ids = [c.metadata["id"] for c in batch]
        print(f"Batch {i//BATCH_SIZE + 1}")
        db.add_documents(batch, ids=batch_ids)
  else:
     print("No new documents to add")

def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

def calculate_chunk_ids(chunks):
    seen = {}

    for chunk in chunks:
        content = chunk.page_content.strip()

        chunk_hash = hashlib.sha256(
            content.encode("utf-8")
        ).hexdigest()

        document_hash = chunk.metadata["document_hash"]
    
        # Count identical chunks within the same document
        key = (document_hash, chunk_hash)
        occurrence = seen.get(key, 0)
        chunk_id = f"{document_hash}:{chunk_hash}:{occurrence}"
        seen[key] = occurrence + 1

        chunk.metadata["id"] = chunk_id

    return chunks
   
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action = "store_true", help = "Reset the database.")
    args = parser.parse_args()

    CACHE_FILE = "chunks.pkl"

    if args.reset:
        print("======= Clearing Database =======")
        clear_database()
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
    
    if os.path.exists(CACHE_FILE):
        print("Loading cached chunks")
        with open(CACHE_FILE, "rb") as f:
            chunks = pickle.load(f)
    else:
        print("Creating chunks")

        documents = load_documents()
        chunks = split_documents(documents)

        with open(CACHE_FILE, "wb") as f:
            pickle.dump(chunks, f)
    add_to_chromadb(chunks)

if __name__ == "__main__":
    main()