from fastapi import FastAPI, Request, HTTPException
import uvicorn

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import google.generativeai as genai
from config import get_settings
from database import get_user_data, save_user_message
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import ConversationChain

from vectorstore import vector_db,setup_vectorstore
from query_parser import parse_insurance_query, get_search_terms
from decision_engine import process_claim_decision
from retriever import retriever, query_rag_system, retrieve_clauses, get_retrieval_context

# ====================================
# FASTAPI APPLICATION SETUP
# ====================================
app = FastAPI(
    title="ASK.AI chatbot",
    description="LangChain-powered Query chatbot with Gemini API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)

# Fix the CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8080", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Initialize chatbot
chatbot = QueryChatbot()

@app.on_event("startup")
async def startup_event():
    """Startup event to validate configuration"""
    if not Config.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable is required")
    print(f"🚀 ASK.AI Chatbot started successfully!")
    print(f"📚 Ready to help businesses grow!")

# ====================================
# FASTAPI ENDPOINTS
# ====================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API status"""
    return {
        "message": "🎓 Query Chatbot API is running!",
        "status": "active",
        "model": Config.MODEL_NAME,
        "context_messages": Config.MAX_CONTEXT_MESSAGES,
        "docs": "/docs",
        "health": "/health"
    }

@app.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_endpoint(chat_message: ChatMessage):
    """Main chat endpoint"""
    try:
        response = await chatbot.get_response(
            message=chat_message.message,
            user_id=chat_message.user_id
        )
        return ChatResponse(
            response=response,
            timestamp=datetime.now().isoformat(),
            user_id=chat_message.user_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



#@app.get("/history/{user_id}", tags=["History"])
#async def get_chat_history(user_id: str):
#    """Get conversation history for a specific user"""
#    history = chatbot.get_conversation_history(user_id)
#    return {
#       "user_id": user_id,
#        "history": history,
#       "total_messages": len(history)
#    }

#@app.delete("/history/{user_id}", tags=["History"])
#async def clear_chat_history(user_id: str):
#    """Clear conversation history for a specific user"""
#    success = chatbot.clear_user_memory(user_id)
#    return {
#        "user_id": user_id,
#        "cleared": success,
#        "message": "Conversation history cleared successfully!" if success else "No history found for user"
#    }

#@app.get("/users", tags=["Users"])
#async def get_active_users():
#    """Get list of all users with active conversations"""
 #   return {
 #       "active_users": list(chatbot.user_memories.keys()),
 #       "total_users": len(chatbot.user_memories)
 #   }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


def query_rag_system(question: str):
    # Parse and enhance query
    parsed_query = parse_insurance_query(question)
    search_terms = parsed_query["enhanced_search_phrases"]
    
    # Search using multiple enhanced terms
    all_results = []
    for term in search_terms[:3]:  # Use top 3 search phrases
        results = query_vectorstore(term, k=2)
        all_results.extend(results)
    
    # Remove duplicates and get top results
    unique_docs = list({doc.page_content: doc for doc in all_results}.values())[:5]
    
    # Generate context-aware answer
    context = "\n".join([doc.page_content for doc in unique_docs])
    
    # Your LLM generation logic here...
    return answer

def main_rag_query(question: str):
    return query_rag_system(question)


def process_insurance_query(query: str):
    # Get general RAG answer
    rag_answer = query_rag_system(query)
    
    # Get claim decision if query is about claims
    if "claim" in query.lower() or "surgery" in query.lower():
        decision = process_claim_decision(query)
        return {
            "answer": rag_answer,
            "decision": decision,
            "type": "claim_processing"
        }
    else:
        return {
            "answer": rag_answer,
            "type": "general_query"
        }

# ====================================
# RUN SERVER
# ====================================
if __name__ == "__main__":
    print("🎓 Starting Query.AI Chatbot Server...")
    print("📋 Make sure to set your GEMINI_API_KEY environment variable!")
    print(f"🌐 Server will run on http://{Config.HOST}:{Config.PORT}")
    
    uvicorn.run(
        "main:app",  # Replace "main" with your actual filename
        host=Config.HOST,
        port=Config.PORT,
        reload=True,
        # log_level="info"
    )


"""

# Example client code for testing

Example usage with requests:

import requests

# Send a chat message

response = requests.post("http://localhost:8000/chat", json={
    "message": "Explain photosynthesis to me",
    "user_id": "student_123"
})

print(response.json())

# Get chat history
history = requests.get("http://localhost:8000/history/student_123")
print(history.json())
"""
"""
output = rag_chain.invoke({"input": query})

print(output['answer'])





# Example usage
if __name__ == "__main__":
    # Test queries
    test_queries = [
        "I'm a 46-year-old male needing knee surgery in Pune. Does my 3-month policy cover this?",
        "What are the exclusions for dental procedures?",
        "Can I claim maternity benefits after 2 years of policy?",
        "Premium calculation for 35-year-old female in Mumbai"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        result = parse_insurance_query(query)
        print(f"Parsed: {json.dumps(result, indent=2)}")
        print(f"Search terms: {get_search_terms(query)}")





# Example usage
if __name__ == "__main__":
    test_query = "What are the policy exclusions for pre-existing conditions?"
    
    # Test retrieval
    relevant_docs = retrieve_clauses(test_query)
    print(f"Found {len(relevant_docs)} relevant documents")
    
    # Test full RAG
    answer = query_rag_system(test_query)
    print(f"Answer: {answer}")





# Example usage
if __name__ == "__main__":
    # Test case from your original file
    test_query = "46-year-old male needs knee surgery in Pune with 3 months policy duration"
    
    # Using extracted patient data
    patient_info = {
        "age": 46,
        "gender": "M",
        "procedure": "knee surgery",
        "location": "Pune", 
        "duration": 3
    }
    
    decision = process_claim_decision(test_query, patient_info)
    print("Decision Result:")
    print(json.dumps(decision, indent=2))
    
    print(f"\nSummary: {get_decision_summary(test_query, patient_info)}")



"""




