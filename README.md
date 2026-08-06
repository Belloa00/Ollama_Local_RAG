The content of this repo is a full local implementation of a RAG system, specifically using LLMs that are running inside Ollama.
In this guide I assume that you already have Ollama installed and running in a background terminal (launched using `ollama serve`).

# What is a RAG?
In simple terms, a RAG (Retrieval Augmented Generation) is a pipeline that uses the NLP power of an LLM to Generate a response based exclusively on a `Context` parsed. The `Context` is represented by the most attinent chunks of documents that are selected to be used when replying the user's question.

We can define the two macro components (almost three for this repo):
- <b>(Chunking)</b>: Here we use a technique called `semantic-chunking` instead of the usual `fixed-size` approach. Using this method we use Ollama to compute the embeddings of the chunked documents, compare them and group those sentences by similarity in chunks. 
- <b>Retrieval</b>: We retrieve the top 5 most similar chunks compared to the user's query.
- <b>Generation</b>: A final call to the local LLM parsing the retrieval (context) and the user's query, both inside a properly formatted `prompt template`

# Requirements
Make sure to have Python3 installed (I had a previous installation of Python 3.14.3) and start a new venv:
- Create the venv: 
```bash
python -m venv .venv
```
- Activate the venv:<br>

(Windows):
```bash
.\.venv\Scripts\activate
```
In case of problems, make sure to run: `Set-ExecutionPolicy Unrestricted -Scope Process` before activating the venv.
<br><br>
(Linux):
```bash
source .\.venv\bin\activate
```

- Run the following command:
```bash
pip install -r requirements.txt
```

- Make sure to create the folder `data` with all your documents in it.

## Populate the VectorDB
The first step is to populate the VectorDB (Chroma) with the embeddings of the documents inside `data`.
To start the step, simply run `python .\generate_embeddings.py`, check the Ollama terminal to see if the processing is running, and wait a bit. Note that this step takes some minutes.

## Submit your first query
The final step is to use the system, simply run `python .\send_query.py "What is the capital of India?"` and put between the `""` your query. The system will answer, also providing the sources for the material.