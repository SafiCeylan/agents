import os
import chromadb
from datetime import datetime
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

class LongTermMemory:
    """
    LongTermMemory handles persistent storage and retrieval using ChromaDB.
    """
    def __init__(self, collection_name="agent_memory", persist_directory="./data/chroma"):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def add_memory(self, text, metadata=None):
        """Adds a piece of information to the memory."""
        base_meta = {"timestamp": datetime.now().isoformat(), "type": "general"}
        if metadata:
            base_meta.update(metadata)
        self.vector_store.add_texts(texts=[text], metadatas=[base_meta])

    def save_market_snapshot(self, symbol: str, data: str, source: str = "Kishi"):
        """
        Tau'nun emriyle Kishi veya Ghost'un getirdiği verileri
        zaman damgalı olarak ChromaDB'ye kaydeder.
        Bu sayede sist hem anı hem süreci hatırlar.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        text = (
            f"[{timestamp}] {source} raporu | Sembol: {symbol.upper()}\n"
            f"{data}"
        )
        metadata = {
            "type": "market_snapshot",
            "symbol": symbol.upper(),
            "source": source,
            "timestamp": timestamp,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        self.vector_store.add_texts(texts=[text], metadatas=[metadata])
        return timestamp

    def search_memory(self, query, k=3):
        """Searches for relevant information in the memory."""
        results = self.vector_store.similarity_search(query, k=k)
        return results

    def search_market_history(self, symbol: str, k: int = 5):
        """Belirli bir sembol için geçmiş piyasa anlık görüntülerini getirir."""
        query = f"{symbol.upper()} piyasa fiyat analizi raporu"
        results = self.vector_store.similarity_search(
            query,
            k=k,
            filter={"symbol": symbol.upper()}
        )
        return results

    def clear_memory(self):
        """Deletes all memories in the current collection."""
        self.vector_store.delete_collection()
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )
