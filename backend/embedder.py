__module_name__ = "embedder"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain.embeddings.base import Embeddings
from typing import Literal, Dict, Any, List
import os
from dotenv import load_dotenv

load_dotenv()

EmbeddingProvider = Literal["huggingface", "mistral"]

# Predefined model configurations for different providers
EMBEDDING_MODELS = {
    "huggingface": {
        "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
        "bge-small-en-v1.5": "BAAI/bge-small-en-v1.5",
        "bge-base-en-v1.5": "BAAI/bge-base-en-v1.5",
        "bge-large-en-v1.5": "BAAI/bge-large-en-v1.5"
    },
    "mistral": {
        "mistral-embed": "mistral-embed"
    }
}

class MistralEmbeddings(Embeddings):
    """Custom Mistral embeddings wrapper for LangChain compatibility."""
    
    def __init__(self, model: str = "mistral-embed", api_key: str = None, **kwargs):
        """
        Initialize Mistral embeddings.
        
        Args:
            model: The Mistral model to use
            api_key: Mistral API key (if not provided, will use MISTRAL_API_KEY env var)
            **kwargs: Additional parameters
        """
        try:
            from mistralai import Mistral
        except ImportError:
            raise ImportError("mistralai package not found. Please install it with: pip install mistralai")
        
        self.model = model
        self.api_key = api_key or os.getenv("MISTRAL_API_KEY")
        
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY not found. Please set it in your .env file or pass it as api_key parameter.")
        
        self.client = Mistral(api_key=self.api_key)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                inputs=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise RuntimeError(f"Failed to embed documents with Mistral: {str(e)}")
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                inputs=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            raise RuntimeError(f"Failed to embed query with Mistral: {str(e)}")

def get_embedding_model(
    provider: EmbeddingProvider = "huggingface",
    model_name: str = "all-MiniLM-L6-v2",
    **kwargs
):
    """
    Get an embedding model from various providers.
    
    Args:
        provider: The embedding provider to use
        model_name: The model name (short name from EMBEDDING_MODELS)
        **kwargs: Additional parameters for the embedding model
    
    Returns:
        Configured embedding model instance
    """
    if provider == "huggingface":
        return _get_huggingface_embeddings(model_name, **kwargs)
    elif provider == "mistral":
        return _get_mistral_embeddings(model_name, **kwargs)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")

def _get_huggingface_embeddings(model_name: str, **kwargs):
    """Get HuggingFace BGE embeddings."""
    full_model_name = EMBEDDING_MODELS["huggingface"].get(model_name, model_name)
    
    default_kwargs = {
        "model_name": full_model_name,
        "model_kwargs": {"device": "cpu"},  # Can be overridden
        "encode_kwargs": {"normalize_embeddings": True}
    }
    default_kwargs.update(kwargs)
    
    return HuggingFaceEmbeddings(**default_kwargs)

def _get_mistral_embeddings(model_name: str, **kwargs):
    """Get Mistral embeddings."""
    full_model_name = EMBEDDING_MODELS["mistral"].get(model_name, model_name)
    
    default_kwargs = {
        "model": full_model_name
    }
    default_kwargs.update(kwargs)
    
    return MistralEmbeddings(**default_kwargs)

def list_available_models(provider: EmbeddingProvider = None) -> Dict[str, Dict[str, str]]:
    """
    List all available embedding models.
    
    Args:
        provider: Optional provider to filter by
    
    Returns:
        Dictionary of available models by provider
    """
    if provider:
        return {provider: EMBEDDING_MODELS.get(provider, {})}
    return EMBEDDING_MODELS

def get_model_info(provider: EmbeddingProvider, model_name: str) -> Dict[str, Any]:
    """
    Get information about a specific embedding model.
    
    Args:
        provider: The embedding provider
        model_name: The model name
    
    Returns:
        Dictionary with model information
    """
    models = EMBEDDING_MODELS.get(provider, {})
    if model_name not in models:
        return {"error": f"Model {model_name} not found for provider {provider}"}
    
    info = {
        "provider": provider,
        "model_name": model_name,
        "full_model_path": models[model_name],
        "requires_api_key": provider == "mistral",
    }
    
    # Add provider-specific information
    if provider == "huggingface":
        info.update({
            "type": "BGE (Beijing Academy of AI)",
            "local": True,
            "gpu_recommended": "bge-large" in model_name
        })
    elif provider == "mistral":
        info.update({
            "type": "Mistral AI",
            "local": False,
            "api_based": True
        })
    
    return info

# Backward compatibility
def get_embedding_model_legacy(model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
    """Legacy function for backward compatibility."""
    return HuggingFaceEmbeddings(model_name=model_name)
