import chromadb
from sentence_transformers import SentenceTransformer

class DevOpsAssistant:
    """
    Retrieval-Augmented Generation (RAG) assistant for DevOps incident analysis.
    """
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        # Initializing lightweight vector store simulation
        self.model = SentenceTransformer(model_name)
        self.knowledge_base = [
            "Incident #101: Memory leak caused by cache overflow in Redis.",
            "Incident #102: Latency spike due to high unindexed DB queries.",
            "Deployment #55: Updated networking firewall rules."
        ]

    def query(self, alert_context):
        """
        Queries the knowledge base for relevant historical incidents.
        In a full implementation, this would use vector search via chromadb.
        """
        # For now, simple keyword matching for initialization
        matches = [kb for kb in self.knowledge_base if any(word in kb.lower() for word in alert_context.lower().split())]
        return matches if matches else ["No historical incidents match this context."]

if __name__ == "__main__":
    assistant = DevOpsAssistant()
    print(assistant.query("Redis memory leak"))
