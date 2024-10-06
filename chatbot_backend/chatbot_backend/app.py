from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import faiss
from transformers import AutoTokenizer, AutoModel
import torch
import json
import logging
import os

# Configure logging
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(log_dir, 'chatbot_backend.log')
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "https://dreamy-rugelach-f54aa3.netlify.app", "https://chatbot-homepage-app-07jsvjdl.devinapps.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load the processed data
embeddings = np.load("/home/ubuntu/chatbot_project/embeddings.npy")
faiss_index = faiss.read_index("/home/ubuntu/chatbot_project/faiss_index.bin")

# Load the text snippets
with open("/home/ubuntu/chatbot_project/text_snippets.json", "r", encoding="utf-8") as f:
    text_snippets = json.load(f)

# Log information about text_snippets and FAISS index
logger.info(f"Number of entries in text_snippets: {len(text_snippets)}")
logger.info(f"Size of FAISS index: {faiss_index.ntotal}")

# Load the BERT model and tokenizer
model_name = "bert-base-german-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

def filter_valid_indices(indices):
    valid = [idx % len(text_snippets) for idx in indices]
    logger.info(f"Filtering indices: input={indices}, output={valid}")
    return valid

def get_answer(question, conversation_history):
    try:
        logger.info(f"Processing question: {question}")
        logger.info(f"Conversation history: {conversation_history}")

        # Combine the current question with the conversation history
        context = " ".join([msg["text"] for msg in conversation_history[-3:]] + [question])
        context_embedding = get_embedding(context)
        logger.info(f"Context embedding shape: {context_embedding.shape}")

        k = 50  # Increase k to have a better chance of finding valid indices
        distances, indices = faiss_index.search(context_embedding.reshape(1, -1), k=k)
        logger.info(f"FAISS search results - distances: {distances}, indices: {indices}")

        valid_indices = filter_valid_indices(indices[0])
        logger.info(f"Valid indices: {valid_indices}")

        # Get the relevant text snippets
        relevant_texts = [text_snippets[str(idx)] for idx in valid_indices[:5]]  # Use top 5 valid indices
        logger.info(f"Relevant texts: {relevant_texts}")

        if not relevant_texts:
            logger.warning("No relevant texts found")
            return "I'm sorry, I couldn't find any relevant information to answer your question."

        # Combine the relevant texts
        combined_text = " ".join(relevant_texts)
        logger.info(f"Combined text (first 100 chars): {combined_text[:100]}...")

        # Generate a simple answer based on the combined text and conversation history
        answer = f"Based on the context of our conversation and the relevant information: {combined_text[:500]}..."
        logger.info(f"Generated answer (first 100 chars): {answer[:100]}...")
        return answer
    except Exception as e:
        logger.error(f"Error in get_answer: {str(e)}")
        return "I'm sorry, there was an error processing your question. Please try again."

class Question(BaseModel):
    text: str
    conversation_history: list

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/ask")
async def ask_question(question: Question):
    if not question.text:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    answer = get_answer(question.text, question.conversation_history)
    return {"question": question.text, "answer": answer}
