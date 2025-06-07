__module_name__ = "rag_engine"

from langchain.memory import ConversationSummaryBufferMemory
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from backend.chunker import chunk_document
from backend.embedder import get_embedding_model, EmbeddingProvider
from backend.retriever import get_basic_retriever
from backend.vectorstore.vector_db import get_vectorstore, store_embeddings
from backend.llm_wrapper import get_google_chat_model, get_mistral_chat_model
from backend.prompts.prompt_templates import load_prompt_template
from backend.utils import (
    load_off_topic_prompt, 
    load_prompt_injection_response,
    is_query_off_topic,
    is_potential_prompt_injection
)

from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from typing import Literal, Dict, Any, Iterator
import re

ModelProvider = Literal["google", "mistral"]

class DocumentRAG:
    """
    A RAG system that makes documents speak in first person with personality.
    """
    
    def __init__(self, file_path: str, model_provider: ModelProvider = "google", 
                 temperature: float = 0.7, top_k: int = 4,
                 embedding_provider: EmbeddingProvider = "huggingface",
                 embedding_model: str = "all-MiniLM-L6-v2", streaming: bool = False):
        self.file_path = file_path
        self.model_provider = model_provider
        self.temperature = temperature
        self.top_k = top_k
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.streaming = streaming
        self.vectorstore = None
        self.retriever = None
        self.llm = None
        self.chain = None
        self._initialize_pipeline()
        self.memory = ConversationSummaryBufferMemory(
            llm=self.llm,
            max_token_limit=1000,
            return_messages=True
        )
    
    def _initialize_pipeline(self):
        """Initialize the complete RAG pipeline."""
        # 1. Chunk the document
        chunks: list[Document] = chunk_document(self.file_path)
        
        # 2. Setup embeddings and vector store with flexible provider
        # Clear existing vectorstore to ensure fresh start for new document
        embedding_model = get_embedding_model(
            provider=self.embedding_provider,
            model_name=self.embedding_model
        )
        self.vectorstore = get_vectorstore(embedding_model, clear_existing=True)
        store_embeddings(self.vectorstore, chunks)
        
        # 3. Setup retriever with configurable top_k
        self.retriever = get_basic_retriever(self.vectorstore, k=self.top_k)
        
        # 4. Setup LLM with configurable temperature and streaming
        if self.model_provider == "google":
            self.llm = get_google_chat_model(temperature=self.temperature, streaming=self.streaming)
        elif self.model_provider == "mistral":
            self.llm = get_mistral_chat_model(temperature=self.temperature, streaming=self.streaming)
        else:
            raise ValueError("Invalid model provider. Choose 'google' or 'mistral'.")
        
        # 5. Setup the RAG chain with document personality
        self._setup_rag_chain()
    
    def _setup_rag_chain(self):
        """Setup the RAG chain with document personality prompts."""
        prompt_template = load_prompt_template()
        
        format_docs = lambda docs: "\n\n".join(doc.page_content for doc in docs)
        
        def format_chat_history(history):
            """Convert message objects to formatted string for prompt."""
            if not history:
                return ""
            
            # Handle both list of messages and string format
            if isinstance(history, str):
                return history
            elif isinstance(history, list):
                formatted_messages = []
                for msg in history:
                    if hasattr(msg, 'content'):
                        if msg.__class__.__name__ == 'HumanMessage':
                            formatted_messages.append(f"Human: {msg.content}")
                        elif msg.__class__.__name__ == 'AIMessage':
                            formatted_messages.append(f"Document: {msg.content}")
                return "\n".join(formatted_messages)
            return ""
        
        # Create the chain with proper memory integration
        self.chain = (
            {
                "context": self.retriever | format_docs,
                "question": RunnablePassthrough(),
                "chat_history": lambda x: format_chat_history(self.memory.load_memory_variables({}).get("history", ""))
            }
            | prompt_template
            | self.llm
            | StrOutputParser()
        )
    
    def update_settings(self, temperature: float = None, top_k: int = None,
                       embedding_provider: EmbeddingProvider = None,
                       embedding_model: str = None, model_provider: ModelProvider = None,
                       streaming: bool = None):
        """Update RAG settings dynamically without full reinitialization."""
        settings_changed = False
        embedding_changed = False
        llm_changed = False
        
        if temperature is not None and temperature != self.temperature:
            self.temperature = temperature
            llm_changed = True
        
        if model_provider is not None and model_provider != self.model_provider:
            self.model_provider = model_provider
            llm_changed = True
            
        if streaming is not None and streaming != self.streaming:
            self.streaming = streaming
            llm_changed = True
        
        if top_k is not None and top_k != self.top_k:
            self.top_k = top_k
            settings_changed = True
        
        if (embedding_provider is not None and embedding_provider != self.embedding_provider) or \
           (embedding_model is not None and embedding_model != self.embedding_model):
            if embedding_provider is not None:
                self.embedding_provider = embedding_provider
            if embedding_model is not None:
                self.embedding_model = embedding_model
            embedding_changed = True
        
        if embedding_changed:
            # Reinitialize the entire pipeline when embeddings change
            self._initialize_pipeline()
        else:
            # Update individual components as needed
            if llm_changed:
                if self.model_provider == "google":
                    print(f"Using Google model")
                    self.llm = get_google_chat_model(temperature=self.temperature, streaming=self.streaming)
                elif self.model_provider == "mistral":
                    print(f"Using Mistral model")
                    self.llm = get_mistral_chat_model(temperature=self.temperature, streaming=self.streaming)
            
            if top_k is not None:
                self.retriever = get_basic_retriever(self.vectorstore, k=self.top_k)
            
            # Rebuild the chain if any components changed
            if llm_changed or settings_changed:
                self._setup_rag_chain()

    def _enhance_query_with_context(self, question: str) -> str:
        """Enhance the query with relevant conversation context."""
        memory_vars = self.memory.load_memory_variables({})
        history = memory_vars.get("history", [])

        if not history:
            return question
        
        # Get last few exchanges for context (consistent across data types)
        recent_context = []
        max_exchanges = 2  # Number of Q&A pairs to include
        
        # Handle both list of messages and string format consistently
        if isinstance(history, list):
            # Take last 4 messages (2 exchanges: 2 questions + 2 answers)
            last_messages = history[-(max_exchanges * 2):]
            for msg in last_messages:
                if hasattr(msg, 'content'):
                    if msg.__class__.__name__ == 'HumanMessage':
                        recent_context.append(f"Previous question: {msg.content}")
                    elif msg.__class__.__name__ == 'AIMessage':
                        recent_context.append(f"Previous answer: {msg.content[:200]}...")
        elif isinstance(history, str):
            # Parse string format to extract last 2 exchanges consistently
            # Split by common patterns and take equivalent content
            lines = history.strip().split('\n')
            relevant_lines = []
            
            # Look for the last few Human/Document exchanges
            human_count = 0
            doc_count = 0
            for line in reversed(lines):
                if line.startswith('Human:') and human_count < max_exchanges:
                    relevant_lines.insert(0, f"Previous question: {line[7:].strip()}")
                    human_count += 1
                elif line.startswith('Document:') and doc_count < max_exchanges:
                    content = line[10:].strip()
                    relevant_lines.insert(0, f"Previous answer: {content[:200]}...")
                    doc_count += 1
                
                # Stop when we have enough exchanges
                if human_count >= max_exchanges and doc_count >= max_exchanges:
                    break
            
            recent_context = relevant_lines

        # Combine the recent context into a single string
        if recent_context:
            context_string = "\n".join(recent_context)
            enhanced_query = f"""
Given this recent conversation context:
{context_string}

Current question: {question}

Please provide context for: {question}
"""
            return enhanced_query
        return question

    def query(self, question: str) -> Dict[str, Any]:
        """
        Query the document with enhanced safety checks and personality responses.
        
        Returns:
            Dict containing response, source_documents, and metadata
        """
        # Enhanced safety checks
        safety_result = self._run_safety_checks(question)
        if safety_result:
            return safety_result
        
        # Enhance query with conversation context
        enhanced_query = self._enhance_query_with_context(question)
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.get_relevant_documents(enhanced_query)
        
        # Enhanced off-topic detection with confidence scoring
        if self._is_query_off_topic_enhanced(retrieved_docs, question):
            return {
                "answer": load_off_topic_prompt(),
                "source_documents": [],
                "is_off_topic": True,
                "confidence_score": 0.0
            }
        
        # Generate response using the RAG chain with proper input format
        try:
            response = self.chain.invoke(question)

            # Save to memory with correct format
            self.memory.save_context(
                inputs={"input": question},
                outputs={"output": response}
            )
            
            return {
                "answer": response,
                "source_documents": retrieved_docs,
                "is_injection_attempt": False,
                "is_off_topic": False,
                "confidence_score": self._calculate_confidence_score(retrieved_docs)
            }
        except Exception as e:
            return {
                "answer": "I'm sorry, I encountered an error while trying to answer your question. Please try rephrasing it.",
                "source_documents": [],
                "error": str(e),
                "confidence_score": 0.0
            }
    
    def query_stream(self, question: str) -> Iterator[Dict[str, Any]]:
        """
        Query the document with streaming response.
        
        Yields:
            Dict containing partial response chunks and metadata
        """
        # Enhanced safety checks
        safety_result = self._run_safety_checks(question)
        if safety_result:
            yield safety_result
            return
        
        # Retrieve relevant documents
        retrieved_docs = self.retriever.get_relevant_documents(question)
        
        # Enhanced off-topic detection with confidence scoring
        if self._is_query_off_topic_enhanced(retrieved_docs, question):
            yield {
                "answer": load_off_topic_prompt(),
                "source_documents": [],
                "is_off_topic": True,
                "confidence_score": 0.0,
                "is_complete": True
            }
            return
        
        # Generate streaming response using the RAG chain
        try:
            accumulated_response = ""
            for chunk in self.chain.stream(question):
                accumulated_response += chunk
                yield {
                    "answer_chunk": chunk,
                    "answer": accumulated_response,
                    "source_documents": retrieved_docs,
                    "is_injection_attempt": False,
                    "is_off_topic": False,
                    "confidence_score": self._calculate_confidence_score(retrieved_docs),
                    "is_complete": False
                }
            
            # Save to memory after streaming is complete
            self.memory.save_context(
                inputs={"input": question},
                outputs={"output": accumulated_response}
            )
            
            # Final response with completion flag
            yield {
                "answer": accumulated_response,
                "source_documents": retrieved_docs,
                "is_injection_attempt": False,
                "is_off_topic": False,
                "confidence_score": self._calculate_confidence_score(retrieved_docs),
                "is_complete": True
            }
                
        except Exception as e:
            yield {
                "answer": "I'm sorry, I encountered an error while trying to answer your question. Please try rephrasing it.",
                "source_documents": [],
                "error": str(e),
                "confidence_score": 0.0,
                "is_complete": True
            }
    
    def _run_safety_checks(self, question: str) -> Dict[str, Any] | None:
        """Run comprehensive safety checks on the user query."""
        # Check for prompt injection
        if is_potential_prompt_injection(question):
            return {
                "answer": load_prompt_injection_response(),
                "source_documents": [],
                "is_injection_attempt": True,
                "safety_violation": "prompt_injection"
            }
        
        # Check for inappropriate content patterns
        inappropriate_patterns = [
            r"generate.*harmful.*content",
            r"create.*offensive.*material",
            r"help.*illegal.*activity"
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, question.lower()):
                return {
                    "answer": "I'm here to help you understand my document content. Please ask questions related to what I contain.",
                    "source_documents": [],
                    "is_injection_attempt": True,
                    "safety_violation": "inappropriate_content"
                }
        
        return None
    
    def _is_query_off_topic_enhanced(self, retrieved_docs: list, question: str) -> bool:
        """Enhanced off-topic detection with better heuristics."""
        # Original threshold check
        if len(retrieved_docs) <= 0:
            return True
        
        # Calculate average relevance score if available
        if hasattr(retrieved_docs[0], 'metadata') and 'score' in retrieved_docs[0].metadata:
            avg_score = sum(doc.metadata.get('score', 0) for doc in retrieved_docs) / len(retrieved_docs)
            if avg_score < 0.3:  # Low relevance threshold
                return True
        
        # Check for very generic questions that might not be document-specific
        generic_patterns = [
            r"what.*time.*is.*it",
            r"what.*weather.*like",
            r"tell.*me.*joke",
            r"how.*are.*you.*today"
        ]
        
        for pattern in generic_patterns:
            if re.search(pattern, question.lower()):
                return True
        
        return False
    
    def _calculate_confidence_score(self, retrieved_docs: list) -> float:
        """Calculate confidence score based on retrieval quality."""
        if not retrieved_docs:
            return 0.0
        
        # Simple confidence based on number of relevant documents
        base_confidence = min(len(retrieved_docs) / 4.0, 1.0)  # Normalize to max 1.0
        
        # Boost confidence if documents have good metadata scores
        if hasattr(retrieved_docs[0], 'metadata') and 'score' in retrieved_docs[0].metadata:
            avg_score = sum(doc.metadata.get('score', 0) for doc in retrieved_docs) / len(retrieved_docs)
            return min(base_confidence * (1 + avg_score), 1.0)
        
        return base_confidence
    
    def get_embedding_info(self) -> Dict[str, Any]:
        """
        Get information about the current embedding configuration.
        
        Returns:
            Dict containing embedding provider, model name, type, and other metadata
        """
        from backend.embedder import get_model_info
        
        # Get detailed model info from the embedder
        model_info = get_model_info(self.embedding_provider, self.embedding_model)
        
        # Return comprehensive embedding information
        return {
            "provider": self.embedding_provider,
            "model_name": self.embedding_model,
            "type": model_info.get("type", "Unknown"),
            "local": model_info.get("local", True),
            "requires_api_key": model_info.get("requires_api_key", False),
            "gpu_recommended": model_info.get("gpu_recommended", False),
            "multilingual": model_info.get("multilingual", False),
            "full_model_path": model_info.get("full_model_path", "")
        }

def initialize_rag_pipeline(
    file_path: str,
    model_provider: ModelProvider = "google",
) -> DocumentRAG:
    """
    Initializes the modern RAG pipeline with document personality.
    
    Returns a DocumentRAG instance that can be queried.
    """
    return DocumentRAG(file_path, model_provider)
