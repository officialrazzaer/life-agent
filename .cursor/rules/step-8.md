### Step 8: Vector Search Implementation

Implement vector search functionality to enable semantic queries:

```python
# src/nlp/vector_search.py
from typing import List, Dict, Any
import numpy as np
from src.nlp.embeddings import EmbeddingGenerator
from src.db.vector_store import ChromaDBManager  # or QdrantManager

class VectorSearch:
    def __init__(self, vector_db_manager, embedding_generator):
        self.vector_db = vector_db_manager
        self.embedding_generator = embedding_generator

    def search(self, collection_name: str, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents in the vector database."""
        # Generate embedding for the query
        query_embedding = self.embedding_generator.generate_embedding(query_text)

        # Search the vector database
        results = self.vector_db.query_collection(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=n_results
        )

        return results

    def hybrid_search(self, query_text: str, structured_filters: Dict[str, Any] = None, n_results: int = 5):
        """Combine vector search with structured database filters."""
        # This would be implemented in Phase 2 to combine vector search with SQL queries
        pass
```

### Step 9: Data Extraction with GPT-4

Implement the GPT-4 data extraction module to parse natural language inputs into structured data:

```python
# src/nlp/extractors.py
import os
import openai
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.environ.get("OPENAI_API_KEY")

class GPTExtractor:
    def __init__(self, model="gpt-4"):
        self.model = model

    def extract_daily_log(self, text: str) -> Dict[str, Any]:
        """Extract structured data from daily log text."""
        prompt = f"""
        Extract the following information from this daily log entry.
        Return a JSON object with these fields:
        - mood_score (1-10)
        - energy_level (1-10)
        - stress_level (1-10)
        - sleep_hours (numeric)
        - sleep_quality (1-10)

        Daily log:
        {text}

        JSON:
        """

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a data extraction assistant that converts natural language into structured data."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        # Parse the JSON response
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            # Handle parsing errors
            return {}

    def extract_gym_log(self, text: str) -> Dict[str, Any]:
        """Extract structured data from gym log text."""
        # Similar implementation as extract_daily_log but with gym-specific fields
        pass

    # Implement similar methods for other log types
```
