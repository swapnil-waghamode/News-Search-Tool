
import os
import re
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_classic.chains import RetrievalQAWithSourcesChain
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_community.vectorstores import FAISS


# ---------------- CONFIGURATION ----------------

st.set_page_config(
    page_title="News Research Tool",
    page_icon="📈",
    layout="wide"
)

st.title(":green[News Research Tool 📈]")
st.sidebar.title("News Article URLs")

# Load .env from the same folder as this Python file
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")

# Stop if API key is missing
if not api_key:
    st.error("OPENAI_API_KEY not found. Check your .env file.")
    st.stop()

INDEX_DIR = Path(__file__).resolve().parent / "faiss_store_openai"


# ---------------- MODELS ----------------

llm = ChatOpenAI(
    api_key=api_key,
    model="gpt-4o-mini",
    temperature=0
)

embeddings = OpenAIEmbeddings(
    api_key=api_key,
    model="text-embedding-3-small"
)


# ---------------- URL INPUT ----------------

urls = [
    st.sidebar.text_input(f"Article URL {i + 1}", key=f"url_{i}")
    for i in range(3)
]

urls = [url.strip() for url in urls if url.strip()]

process_clicked = st.sidebar.button(
    "Process URLs",
    type="primary"
)


# ---------------- PROCESS ARTICLES ----------------

if process_clicked:

    if not urls:
        st.sidebar.warning("Please enter at least one article URL.")

    else:
        try:
            with st.spinner("Loading articles..."):

                loader = UnstructuredURLLoader(urls=urls)
                data = loader.load()

            if not data:
                st.error(
                    "No article content was loaded. "
                    "Try different URLs."
                )
                st.stop()

            with st.spinner("Splitting article text..."):

                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200
                )

                documents = splitter.split_documents(data)

            if not documents:
                st.error("No text was extracted from the articles.")
                st.stop()

            with st.spinner("Creating embeddings and saving index..."):

                vectorstore = FAISS.from_documents(
                    documents,
                    embeddings
                )

                vectorstore.save_local(str(INDEX_DIR))

            st.success(
                f"Successfully processed {len(urls)} URL(s) "
                f"into {len(documents)} text chunks."
            )

        except Exception as e:
            st.error(f"Error while processing articles: {e}")


# ---------------- ASK QUESTIONS ----------------

st.subheader("Ask a question about your articles")

query = st.text_input("Enter your question",
    placeholder= "What are the main points in these news articles?")

ask_clicked = st.button("Get Answer", type="primary")

if ask_clicked:

    if not query.strip():
        st.warning("Please enter a question.")

    elif not (INDEX_DIR / "index.faiss").exists():
        st.warning("Please process your article URLs first.")

    else:
        try:
            with st.spinner("Finding relevant information..."):

                vectorstore = FAISS.load_local(
                    str(INDEX_DIR),
                    embeddings,
                    allow_dangerous_deserialization=True
                )

                chain = RetrievalQAWithSourcesChain.from_llm(
                    llm=llm,
                    retriever=vectorstore.as_retriever(
                        search_kwargs={"k": 4}
                    )
                )

                result = chain.invoke({
                    "question": query
                })

            st.subheader("Answer")
            st.markdown(
                result.get("answer", "No answer generated.")
            )

            sources = result.get("sources", "").strip()

            if sources:
                st.subheader("Sources")

                for source in re.split(r",\s*|\n", sources):
                    if source.strip():
                        st.write(source.strip())

        except Exception as e:
            st.error(f"Error while answering your question: {e}")
