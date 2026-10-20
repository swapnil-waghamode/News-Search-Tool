# News Research Tool 📈

A simple Streamlit app that lets you ask questions about news articles. Paste up to three article URLs, and the app reads them, indexes the text, and answers your questions using OpenAI, with the sources listed.

## Features

- Load up to 3 news article URLs from the sidebar
- Split the articles into chunks and build a FAISS vector index
- Ask questions in plain English and get answers based only on the articles
- See the source URLs for each answer
- Index is saved locally, so you can ask more questions without reprocessing

## How It Works

1. **Load**: article text is fetched from the URLs you provide
2. **Split**: text is divided into overlapping chunks (1000 characters, 200 overlap)
3. **Embed**: each chunk is converted to a vector with OpenAI embeddings (`text-embedding-3-small`)
4. **Store**: vectors are saved in a local FAISS index (`faiss_store_openai/`)
5. **Answer**: your question retrieves the 4 most relevant chunks, and `gpt-4o-mini` writes the answer with sources

## Tech Stack

- Python 3.12
- Streamlit
- LangChain (`langchain-openai`, `langchain-classic`, `langchain-text-splitters`, `langchain-community`)
- FAISS (`faiss-cpu`)
- Unstructured
- OpenAI API

## Project Structure

```text
News Research Tool/
├── main.py                # Streamlit app
├── requirements.txt       # Python dependencies
├── .env                   # Your OpenAI API key (do not share)
└── faiss_store_openai/    # Saved vector index (created after processing URLs)
```

## Setup

### 1. Clone or download the project

```powershell
cd "D:\News Research Tool"
```

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

`requirements.txt`:

```text
langchain
langchain-classic
langchain-community
langchain-openai
langchain-text-splitters
python-dotenv
streamlit
unstructured
tiktoken
faiss-cpu
python-magic
python-magic-bin
openai
```

### 4. Add your OpenAI API key

Create a file named `.env` in the project folder (the file name must be exactly `.env`, saved as UTF-8) with this single line:

```text
OPENAI_API_KEY=your-api-key-here
```

Never commit this file or share your key publicly.

## Run the App

```powershell
streamlit run main.py
```

The app opens at http://localhost:8501.

## Usage

1. Enter one to three news article URLs in the sidebar.
2. Click **Process URLs** and wait for the success message.
3. Type a question and click **Get Answer**.
4. Read the answer and the sources below it.

## Troubleshooting

| Problem | Fix |
|---|---|
| `OPENAI_API_KEY not found` | Check that `.env` is in the same folder as `main.py`, is named exactly `.env` (not `.env.txt`), and is saved as UTF-8 |
| `Partitioning is not supported for the FileType.UNK file type` | The article could not be read (the site may block scrapers, or `libmagic` is not working). Try a different news site |
| `No article content was loaded` | None of the URLs returned readable text. Try other URLs |
| `Please process your article URLs first` | Click **Process URLs** before asking a question |
| `langchain-community` deprecation warning | Harmless. The package is no longer maintained but still works |

## Notes

- The saved index is loaded with `allow_dangerous_deserialization=True`. This is fine for an index you created yourself, but do not load index files from untrusted sources.
- Answers come only from the processed articles, so questions outside them may return "I don't know".
- Using the OpenAI API incurs costs. This app uses low-cost models.