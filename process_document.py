import PyPDF2
import spacy
from transformers import AutoTokenizer, AutoModel
import torch
import faiss
import numpy as np
import logging
import time

logging.basicConfig(level=logging.INFO)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for i, page in enumerate(reader.pages):
            text += page.extract_text()
            if (i + 1) % 10 == 0:
                logging.info(f"Processed {i + 1} pages")
    return text

def preprocess_text(text, nlp):
    logging.info("Preprocessing text")
    doc = nlp(text)
    return [token.text for token in doc if not token.is_stop and not token.is_punct]

def create_embeddings(tokens, model, tokenizer, batch_size=16):
    embeddings = []
    total_batches = len(tokens) // batch_size + (1 if len(tokens) % batch_size != 0 else 0)
    for i in range(0, len(tokens), batch_size):
        batch = tokens[i:i+batch_size]
        inputs = tokenizer(batch, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings.append(outputs.last_hidden_state.mean(dim=1).numpy())
        if (i // batch_size + 1) % 10 == 0:
            logging.info(f"Processed {i // batch_size + 1}/{total_batches} batches")
    return np.vstack(embeddings)

def create_faiss_index(embeddings):
    logging.info("Creating FAISS index")
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index

def main():
    start_time = time.time()
    pdf_path = "finanzdienstleistungen.pdf"

    logging.info("Loading German language model")
    nlp = spacy.load("de_core_news_sm")

    logging.info("Loading BERT model for German")
    model_name = "bert-base-german-cased"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name)

    logging.info("Extracting text from PDF")
    text = extract_text_from_pdf(pdf_path)

    logging.info("Preprocessing text")
    tokens = preprocess_text(text, nlp)

    logging.info("Creating embeddings in batches")
    embeddings = create_embeddings(tokens, model, tokenizer)

    logging.info("Creating FAISS index")
    index = create_faiss_index(embeddings)

    logging.info("Saving processed data")
    np.save("embeddings.npy", embeddings)
    faiss.write_index(index, "faiss_index.bin")

    end_time = time.time()
    logging.info(f"Document processed and RAG system set up successfully in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
