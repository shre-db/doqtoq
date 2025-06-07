__module_name__ = "llm_wrapper"

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai.chat_models import ChatMistralAI
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

def get_google_chat_model(model_name: str = "gemini-1.5-flash", temperature: float = 0.7, streaming: bool = False) -> ChatGoogleGenerativeAI:
    """
    Returns a Gemini chat model using the Google Generative AI API.
    """
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY not found. Check your .env file.")
    try:
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=GOOGLE_API_KEY,
            temperature=temperature,
            top_p=1.0,
            streaming=streaming,
        )
    except Exception as e:
        raise ValueError(f"Failed to initialize Google chat model: {str(e)}")

def get_mistral_chat_model(model_name: str = "mistral-medium", temperature: float = 0.7, streaming: bool = False) -> ChatMistralAI:
    """
    Returns a Mistral chat model using the Mistral API.
    Valid model names: mistral-tiny, mistral-small, mistral-medium
    """
    if not MISTRAL_API_KEY:
        raise ValueError("MISTRAL_API_KEY not found. Check your .env file.")
    try:
        return ChatMistralAI(
            model=model_name,
            api_key=MISTRAL_API_KEY,
            temperature=temperature,
            top_p=1.0,
            streaming=streaming,
        )
    except Exception as e:
        raise ValueError(f"Failed to initialize Mistral chat model: {str(e)}")
