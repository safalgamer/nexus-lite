"""Vector database for episodic and semantic memory."""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

class NexusVectorDB:
    """Simple in-memory vector database with file persistence."""
    
    def __init__(self, config):
        self.config = config
        self.memories = []
        self.db_path = Path("./data/memories.jsonl")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._load_memories()
    
    async def initialize(self):
        """Initialize the vector database."""
        pass
    
    def _load_memories(self):
        """Load memories from disk."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            self.memories.append(json.loads(line))
            except Exception as e:
                print(f"Error loading memories: {e}")
    
    def add_memory(self, content: str, source: str = "thought"):
        """Add a memory to the database."""
        memory = {
            "timestamp": datetime.now().isoformat(),
            "content": content,
            "source": source
        }
        self.memories.append(memory)
        self._save_memory(memory)
    
    def _save_memory(self, memory: Dict):
        """Save a single memory to disk."""
        try:
            with open(self.db_path, 'a') as f:
                f.write(json.dumps(memory) + '\n')
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    def query(self, query: str, n_results: int = 5) -> List[str]:
        """Query memories (simple text-based for now)."""
        results = []
        query_terms = set(query.lower().split())
        
        for memory in self.memories[-100:]:  # Search recent memories
            content = memory.get("content", "").lower()
            # Simple matching
            if any(term in content for term in query_terms):
                results.append(memory.get("content", ""))
        
        return results[:n_results]
    
    async def shutdown(self):
        """Shutdown the vector database."""
        pass
