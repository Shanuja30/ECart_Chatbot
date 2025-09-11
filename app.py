# app.py
# FastAPI version of EcoCart AI Chatbot with Memory & System Instruction

import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

# Suppress HuggingFace tokenizer parallelism warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from groq import Groq

# ----------------- Load Environment Variables -----------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("Please set your GROQ_API_KEY in the .env file!")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# ----------------- Load PDF & Create Vector DB -----------------
pdf_file = "EcoCart_Online.pdf"
loader = PyPDFLoader(pdf_file)
pages = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
docs = text_splitter.split_documents(pages)

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    collection_name="ecocart_policies",
    persist_directory="./chroma_ecocart"
)

print(f"✅ PDF loaded ({len(pages)} pages) and Vector DB ready ({len(docs)} chunks).")

# ----------------- FastAPI App -----------------
app = FastAPI(title="EcoCart AI Chatbot")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Request Model -----------------
class QuestionRequest(BaseModel):
    question: str

# ----------------- Conversation Memory -----------------
conversation_memory = []  # Stores previous user/AI messages

# ----------------- API Endpoint -----------------
@app.post("/ask")
async def ask_question(req: QuestionRequest):
    query = req.question.strip()

    # Handle greetings
    greetings = ["hi", "hello", "hey", "hey there", "helllo"]
    if query.lower() in greetings:
        return {"answer": "👋 Hi! You can ask me about EcoCart policies."}

    # Retrieve relevant chunks
    results = vectordb.similarity_search(query, k=3)
    if not results or all(len(r.page_content.strip()) == 0 for r in results):
        return {"answer": "❌ Sorry, I don't have information about that. Try asking about EcoCart policies."}

    context = "\n".join([r.page_content for r in results])

    # Include memory
    memory_text = ""
    if conversation_memory:
        memory_text = "\nPrevious conversation:\n" + "\n".join(
            [f"User: {m['user']}\nAI: {m['ai']}" for m in conversation_memory]
        )

    # Prepare user message
    user_message = f"{memory_text}\n\nContext:\n{context}\n\nQuestion:\n{query}"

    # Generate AI response
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are EcoCart AI, a helpful assistant. "
                        "Answer briefly, clearly, and in a friendly tone. "
                        "Use bullet points or 2–3 short sentences. "
                        "Do not write long paragraphs unless necessary."
                    ),
                },
                {"role": "user", "content": user_message},
            ],
            model="llama-3.3-70b-versatile",
        )
        ai_response = chat_completion.choices[0].message.content

        # Save memory
        conversation_memory.append({"user": query, "ai": ai_response})

        return {"answer": ai_response}

    except Exception as e:
        return {"answer": f"❌ Error generating AI response: {e}"}
