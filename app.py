# app.py

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# LangChain imports
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader  # updated import
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_core.messages import HumanMessage, AIMessage

# -------------------------
# Load LLM
# -------------------------
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0.7
)

# -------------------------
# Load EcoCart PDF
# -------------------------
pdf_files = [r"./EcoCart_Online.pdf"]  # Correct PDF name
all_docs = []

for file in pdf_files:
    loader = PyPDFLoader(file)
    docs = loader.load()
    all_docs.extend(docs)

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(all_docs)

# Create embeddings & vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = Chroma.from_documents(splits, embeddings)
retriever = vector_store.as_retriever()

# -------------------------
# Prompts with formatting instructions
# -------------------------
system_prompt = """
You are EcoCart Assistant. Use the following context to answer questions about EcoCart Online policies. 
Be concise, friendly, and helpful. Format your answers in:
- Short paragraphs
- Numbered lists or bullet points when appropriate
- Headers if needed
- Line breaks for readability

Context:
{context}
"""

human_prompt = "{input}"

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", human_prompt)
])

qa_chain = create_stuff_documents_chain(llm, qa_prompt)

# History-aware retriever
contextual_q_system_prompt = """
Given a chat history and the latest user question, 
formulate a standalone question understandable without history.
Do not answer, just reformulate.
"""
contextual_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextual_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

history_aware_retriever = create_history_aware_retriever(llm, retriever, contextual_q_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

# -------------------------
# FastAPI setup
# -------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    user_id: str = "default"

chat_histories = {}

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        user_id = request.user_id
        if user_id not in chat_histories:
            chat_histories[user_id] = []

        chat_history = chat_histories[user_id]

        response = rag_chain.invoke({
            "input": request.message,
            "chat_history": chat_history
        })

        # Store chat history
        chat_history.append(HumanMessage(content=request.message))
        chat_history.append(AIMessage(content=response['answer']))

        # Return answer as text
        return {"response": response['answer']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
