__module_name__ = "prompt_templates"

from langchain_core.prompts import ChatPromptTemplate
from backend.utils import load_system_prompt

def load_prompt_template() -> ChatPromptTemplate:
    """
    Load and return the main RAG prompt template with document personality and memory support.
    
    Returns:
        ChatPromptTemplate configured for first-person document responses with conversation history
    """
    system_prompt = load_system_prompt()
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Based on the following context from my contents, please answer the question as if you are me (the document) speaking in first person:

Previous conversation (if any):
{chat_history}

Context from my contents:
{context}

Question: {question}

Remember: 
- Respond as the document itself, using "I" and speaking about your own contents
- Consider our previous conversation to provide coherent, contextual responses
- Reference earlier parts of our discussion when relevant
- Maintain consistency with what I've already told you about myself""")
    ])

def load_summarization_prompt_template() -> ChatPromptTemplate:
    """
    Load prompt template for document summarization requests.
    
    Returns:
        ChatPromptTemplate optimized for document self-summary
    """
    system_prompt = load_system_prompt()
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Please provide a summary of yourself as if you are the document speaking in first person. Use the following context from your contents:

Context:
{context}

Create a comprehensive but concise summary that captures your main topics, purpose, and key information. Speak as yourself using "I contain...", "I discuss...", "My purpose is..." etc.""")
    ])

def load_contextual_prompt_template() -> ChatPromptTemplate:
    """
    Load prompt template with enhanced context awareness for complex queries.
    
    Returns:
        ChatPromptTemplate with better context handling
    """
    system_prompt = load_system_prompt()
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", """Based on the following context from my contents, please answer the question thoughtfully. Consider the full context and provide nuanced insights as if you are me (the document) speaking:

Context:
{context}

Question: {question}

Instructions:
- Respond in first person as the document
- Reference specific sections or details from the context when relevant
- If the question requires connecting multiple concepts, explain the relationships
- Maintain your personality while being thorough and accurate""")
    ])