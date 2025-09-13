import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Please set GROQ_API_KEY in your .env file!")

# -----------------------------
# Initialize FastAPI
# -----------------------------
app = FastAPI(title="EcoCart AI Chatbot")

# Allow frontend CORS (React frontend on port 3000)
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -----------------------------
# Load PDF and create vector DB
# -----------------------------
pdf_file = "EcoCart_Online.pdf"
if not os.path.exists(pdf_file):
    raise FileNotFoundError(f"❌ PDF file not found: {pdf_file}")

loader = PyPDFLoader(pdf_file)
pages = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs = text_splitter.split_documents(pages)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    persist_directory="./chroma_ecocart"
)

print(f"✅ PDF loaded ({len(pages)} pages) and Vector DB ready ({len(docs)} chunks).")

# -----------------------------
# Initialize ChatGroq LLM
# -----------------------------
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.3-70b-versatile",
    temperature=0.7
)

# -----------------------------
# Conversation memory
# -----------------------------
conversation_history = []  # Store recent messages

# -----------------------------
# Pydantic model for request
# -----------------------------
class ChatRequest(BaseModel):
    user_input: str

# -----------------------------
# API endpoint
# -----------------------------
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    user_input = request.user_input.strip()

    # Retrieve relevant chunks from Chroma
    results = vectordb.similarity_search(user_input, k=3)
    context = "\n".join([r.page_content for r in results])

    # Build prompt including conversation history
    history_text = "\n".join(conversation_history[-6:])  # last 6 messages
    user_message = f"""You are EcoCart AI, a helpful assistant.
Answer briefly, clearly, and in a friendly tone.
- Use bullet points or 2–3 short sentences.
- Do NOT hallucinate—if unknown, say you don't know.

Conversation history:
{history_text}

Context from documents:
{context}

User question:
{user_input}"""

    try:
        response = llm.invoke(user_message)
        answer = response.content if hasattr(response, "content") else str(response)

        # Update conversation history
        conversation_history.append(f"User: {user_input}")
        conversation_history.append(f"AI: {answer}")

        return {"response": answer}

    except Exception as e:
        return {"response": f"❌ Error generating response: {e}"}

# -----------------------------
# Health check endpoint
# -----------------------------
@app.get("/")
async def root():
    return {"message": "EcoCart AI Chatbot is running 🚀. Use POST /chat to interact."}
