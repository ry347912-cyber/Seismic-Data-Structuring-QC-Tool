"""
RAG Pipeline for Seismic QC
Uses HuggingFace embeddings + ChromaDB + Groq/Llama3
as per HiDevs GenAI curriculum.
"""

import os
import json
from pathlib import Path


def build_rag_pipeline(docs_dir: str = "data/samples"):
    """
    Build a RAG pipeline over the seismic docs directory.
    Returns a callable chain: chain.invoke({"question": "..."})
    """
    try:
        from langchain_community.document_loaders import DirectoryLoader, TextLoader
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import Chroma
        from langchain_groq import ChatGroq
        from langchain.prompts import ChatPromptTemplate
        from langchain.chains import RetrievalQA
    except ImportError as e:
        raise ImportError(
            f"Missing dependency: {e}\n"
            "Install with: pip install -r requirements.txt"
        )

    # ── Step 1: Load documents ──────────────────────────────────────────
    loader = DirectoryLoader(docs_dir, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()
    print(f"[RAG] Loaded {len(documents)} documents")

    # ── Step 2: Chunk ───────────────────────────────────────────────────
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
    print(f"[RAG] Created {len(chunks)} chunks")

    # ── Step 3: Embed + store ───────────────────────────────────────────
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="outputs/chroma_db",
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    # ── Step 4: LLM (Groq / Llama3) ────────────────────────────────────
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise EnvironmentError("Set GROQ_API_KEY environment variable.")

    llm = ChatGroq(
        model="llama3-8b-8192",
        api_key=groq_api_key,
        temperature=0.1,
    )

    # ── Step 5: Prompt ──────────────────────────────────────────────────
    prompt = ChatPromptTemplate.from_template(
        """You are an expert geophysicist and seismic data analyst.
Use the retrieved seismic context below to answer the question.
If the answer is not in the context, say so — never hallucinate.

Context:
{context}

Question: {question}

Provide a concise, technically accurate answer."""
    )

    # ── Step 6: Chain ───────────────────────────────────────────────────
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff",
        chain_type_kwargs={"prompt": prompt},
    )
    print("[RAG] Pipeline ready.")
    return chain
