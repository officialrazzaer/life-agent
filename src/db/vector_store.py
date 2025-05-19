# src/db/vector_store.py
import chromadb
# from chromadb.config import Settings # Settings is deprecated, pass persist_directory directly
import os
from dotenv import load_dotenv

load_dotenv()

# Default path for ChromaDB persistence, can be overridden by environment variable
CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_PERSIST_DIRECTORY", "./chroma_db")

class ChromaDBManager:
    def __init__(self, persist_directory=CHROMA_PERSIST_DIRECTORY, collection_name="default_collection"):
        """
        Initializes the ChromaDB client.
        Args:
            persist_directory (str): The directory to persist ChromaDB data.
            collection_name (str): The default collection name to create or load.
        """
        # Ensure the persist directory exists
        if not os.path.exists(persist_directory):
            os.makedirs(persist_directory)
            print(f"Created ChromaDB persistence directory: {persist_directory}")

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection_name = collection_name
        self._collection = None  # Lazy load collection

    @property
    def collection(self):
        if self._collection is None:
            try:
                self._collection = self.client.get_collection(name=self.collection_name)
                print(f"Loaded existing ChromaDB collection: '{self.collection_name}'")
            except:
                self._collection = self.client.create_collection(name=self.collection_name)
                print(f"Created new ChromaDB collection: '{self.collection_name}'")
        return self._collection

    def get_or_create_collection(self, collection_name):
        """
        Gets an existing collection or creates it if it doesn't exist.
        Args:
            collection_name (str): The name of the collection.
        Returns:
            chromadb.api.models.Collection.Collection: The collection object.
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            print(f"Retrieved collection: {collection_name}")
        except Exception as e:
            # A more specific exception might be ValueError if using an older client
            # or if the collection truly doesn't exist. chromadb.errors.CollectionNotFoundException for newer ones.
            print(f"Collection '{collection_name}' not found, creating it. Original error: {e}")
            collection = self.client.create_collection(name=collection_name)
        return collection

    def add_documents(self, documents, metadatas=None, ids=None, collection_name=None):
        """
        Adds documents to the specified ChromaDB collection.
        Args:
            documents (list of str): The documents to add.
            metadatas (list of dict, optional): Metadata associated with each document.
            ids (list of str, optional): Unique IDs for each document.
            collection_name (str, optional): The name of the collection. Defaults to the instance's default collection.
        """
        target_collection_name = collection_name if collection_name else self.collection_name
        current_collection = self.get_or_create_collection(target_collection_name)
        
        if ids is None:
            # Generate simple sequential IDs if none are provided
            # Consider a more robust ID generation strategy for production
            start_id = current_collection.count() # Get current count to avoid collisions if possible
            ids = [f"doc_{start_id + i}" for i in range(len(documents))]
        
        current_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"Added {len(documents)} documents to collection '{target_collection_name}'.")

    def query_collection(self, query_texts, n_results=5, query_embeddings=None, collection_name=None, where=None, where_document=None, include=["metadatas", "documents", "distances"]):
        """
        Queries the specified ChromaDB collection.
        Args:
            query_texts (list of str, optional): The query texts.
            n_results (int): The number of results to return.
            query_embeddings (list of list of float, optional): The query embeddings.
            collection_name (str, optional): The name of the collection. Defaults to the instance's default collection.
            where (dict, optional): Filter results by metadata. Example: {"source": "email"}
            where_document (dict, optional): Filter results by document content. Example: {"$contains": "search_term"}
            include (list of str): A list of what to include in the results. Can be ["metadatas", "documents", "distances", "embeddings"].
        Returns:
            dict: The query results.
        """
        target_collection_name = collection_name if collection_name else self.collection_name
        current_collection = self.get_or_create_collection(target_collection_name)
        
        results = current_collection.query(
            query_texts=query_texts,
            query_embeddings=query_embeddings,
            n_results=n_results,
            where=where,
            where_document=where_document,
            include=include
        )
        return results

    def delete_collection(self, collection_name=None):
        """
        Deletes the specified ChromaDB collection.
        Args:
            collection_name (str, optional): The name of the collection. Defaults to the instance's default collection.
        """
        target_collection_name = collection_name if collection_name else self.collection_name
        self.client.delete_collection(name=target_collection_name)
        print(f"Collection '{target_collection_name}' deleted.")
        if target_collection_name == self.collection_name:
            self._collection = None # Reset cached collection if it was the default one

    def list_collections(self):
        """
        Lists all collections in the ChromaDB instance.
        Returns:
            list: A list of collection objects.
        """
        return self.client.list_collections()

    def delete_all_data(self):
        """
        Deletes all data in the current collection (shortcut for delete_collection and re-create).
        """
        self.delete_collection()
        # Re-create the collection for further use
        self._collection = self.client.create_collection(name=self.collection_name)
        print(f"All data deleted and collection '{self.collection_name}' re-created.")

    def delete_data_by_date(self, date_str):
        """
        Deletes all documents in the collection for a specific date (metadata 'date').
        Args:
            date_str (str): The date string to match (e.g., '2024-06-19').
        """
        results = self.collection.get(include=['metadatas', 'ids'])
        ids_to_delete = [
            doc_id for doc_id, meta in zip(results['ids'], results['metadatas'])
            if meta.get('date') == date_str
        ]
        if ids_to_delete:
            self.collection.delete(ids=ids_to_delete)
            print(f"Deleted {len(ids_to_delete)} documents for date {date_str}.")
        else:
            print(f"No documents found for date {date_str}.")

# Example Usage (optional - for testing this script directly)
if __name__ == '__main__':
    print(f"ChromaDB persistence directory: {CHROMA_PERSIST_DIRECTORY}")
    # Initialize with a default collection name
    chroma_manager = ChromaDBManager(collection_name="my_life_logs")

    # Using the default collection
    print(f"Default collection object: {chroma_manager.collection}")

    # Add documents to the default collection
    docs_to_add = [
        "Today was a good day. I went to the gym and had a productive work session.",
        "Feeling a bit tired after a long week of Jiu-Jitsu training.",
        "My investments in Solana are doing well."
    ]
    doc_ids = ["day1", "day2", "invest1"]
    doc_metadatas = [
        {"source": "daily_log", "date": "2024-07-28"},
        {"source": "jiujitsu_log", "date": "2024-07-27"},
        {"source": "finance_log", "date": "2024-07-28"}
    ]
    chroma_manager.add_documents(documents=docs_to_add, metadatas=doc_metadatas, ids=doc_ids)

    # Query the default collection
    query_results = chroma_manager.query_collection(query_texts=["What happened with Solana?"], n_results=1)
    print("Query results:", query_results)

    # List all collections
    print("Current collections:", chroma_manager.list_collections())

    # Create and use a different collection
    # custom_collection = chroma_manager.get_or_create_collection("my_custom_data")
    # print(f"Custom collection object: {custom_collection}")
    # chroma_manager.add_documents(
    #     documents=["Custom data point 1", "Another custom entry"],
    #     ids=["cust1", "cust2"],
    #     collection_name="my_custom_data"
    # )
    # custom_query_results = chroma_manager.query_collection(query_texts=["custom"], n_results=1, collection_name="my_custom_data")
    # print("Custom query results:", custom_query_results)

    # Delete a collection
    # chroma_manager.delete_collection(collection_name="my_custom_data")
    # print("Collections after deletion:", chroma_manager.list_collections())

    # To clear the default collection for a fresh start (if needed for testing)
    # chroma_manager.delete_collection() # This will delete 'my_life_logs'
    # print("Collections after deleting default:", chroma_manager.list_collections()) 
    # Re-initialize to create it again if needed for further tests
    # chroma_manager = ChromaDBManager(collection_name="my_life_logs")
    # print(f"Default collection object after re-init: {chroma_manager.collection}") 