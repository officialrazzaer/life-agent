from flask import Flask, request, jsonify
import os
import uuid
from src.db.vector_store import ChromaDBManager

app = Flask(__name__)

# Use environment variable or default directory for ChromaDB
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

# Initialize ChromaDBManager
chroma = ChromaDBManager(persist_directory=CHROMA_PERSIST_DIRECTORY, collection_name="my_life_logs")

@app.route('/add_embedding', methods=['POST'])
def add_embedding():
    data = request.json
    # Required fields: embedding (list of floats), user_id (str), log_id (str), text (str), date (str)
    embedding = data.get('embedding')
    user_id = data.get('user_id')
    log_id = data.get('log_id', str(uuid.uuid4()))  # Generate a UUID if not provided
    text = data.get('text', '')
    date = data.get('date', None)

    if not embedding or not user_id or not text:
        return jsonify({"error": "Missing required fields: embedding, user_id, text"}), 400

    # Store the text as the document, embedding as metadata (ChromaDB stores embeddings internally)
    meta = {
        "user_id": user_id,
        "log_id": log_id
    }
    if date is not None:
        meta["date"] = date

    chroma.add_documents(
        documents=[text],
        metadatas=[meta],
        ids=[log_id]
    )
    return jsonify({"status": "ok", "log_id": log_id})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True) 