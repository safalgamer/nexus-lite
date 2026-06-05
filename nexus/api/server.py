"""FastAPI server stub."""
from fastapi import FastAPI

def create_app(config, model, metacognition, vector_db, evolution_engine):
    """Create the FastAPI app."""
    app = FastAPI()
    
    @app.get("/health")
    def health():
        return {"status": "ok"}
    
    return app
