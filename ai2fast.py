#Copyright (c)2023 btCode::Orange. All rights reserved.
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import LlamaCpp
from langchain.vectorstores import Qdrant
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains.question_answering import load_qa_chain
import langchain
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, UploadFile, HTTPException, Depends, File
from typing import List


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Fix for some new weird "no attribute 'verbose'" bug
langchain.verbose = False

# Callback just to stream output to stdout. Useful for debugging.
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = LlamaCpp(
    model_path="./llama-2-7b-chat.Q4_K_M.gguf",
    stop=["### Human:"],
    callback_manager=callback_manager,
    verbose=True,
    n_ctx=4000,
    n_batch=512, n_gpu_layers=100, n_threads=6,
)

chain = load_qa_chain(llm, chain_type="stuff")

knowledge_base = None  # This will store our Qdrant instance after processing the PDF

@app.post("/upload/")
async def upload_pdf(files: List[UploadFile] = File(...)):
    global knowledge_base
    all_texts = ""

    for file in files:
        pdf_reader = PdfReader(file.file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        all_texts += text
        
    # Split the text into chunks
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=1000, chunk_overlap=200, length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Use SentenceTransformerEmbeddings for embedding
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create in-memory Qdrant instance
    knowledge_base = Qdrant.from_texts(
        chunks,
        embeddings,
        location=":memory:",
        collection_name="doc_chunks",
    )

    return {"status": "PDF processed and ready for querying"}

@app.get("/query/")
async def query_pdf(question: str):
    global knowledge_base
    if not knowledge_base:
        raise HTTPException(status_code=400, detail="Please upload a PDF first")

    docs = knowledge_base.similarity_search(question, k=4)

    # Calculating prompt (takes time and can optionally be removed)
    question = "You always answer the with markdown formatting. You will be penalized if you do not answer with markdown when it would be possible." + "The markdown formatting you support: headings, bold, italic, links, tables, lists, code blocks, and blockquotes."+ "You do not support images and never include images. You will be penalized if you render images. You will base your answer on the provided documents only. You will be penalized if you base your answer on anything other than the provided documents. Answer this question: " + question

    prompt_len = chain.prompt_length(docs=docs, question=question)
    if prompt_len > llm.n_ctx:
        return {
            "error": "Prompt length is more than n_ctx. This will likely fail. Increase model's context, reduce chunk's sizes or question length, or retrieve fewer docs."
        }

    # Get the response
    response = chain.run(input_documents=docs, question=question)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
