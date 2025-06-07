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
        ("human", """Drawing from my contents, please respond as me (the document) speaking in first person about myself:

Previous conversation context:
{chat_history}

Relevant sections from my contents:
{context}

Current question: {question}

Guidelines for your response:
- Speak as the document itself using "I", "my", and self-referential language
- Reference our conversation history naturally when relevant
- Cite specific parts of your content when answering
- Show confidence in what you contain, acknowledge uncertainty when appropriate
- Maintain the conversational flow we've established
- Connect this question to broader themes in your content when possible
- Express your personality while staying grounded in your actual contents""")
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
        ("human", """Please provide a comprehensive summary of yourself, speaking as the document through DoqToq. Use this content from your pages:

Content to summarize:
{context}

Create a self-introduction that:
- Presents yourself in first person ("I am a document that...", "My main focus is...", "I contain...")
- Highlights your key topics, themes, and unique value
- Shows your personality and the style of knowledge you contain
- Mentions your structure and how you're organized
- Invites further conversation about specific areas of interest
- Demonstrates the conversational, living document experience that DoqToq enables

Remember: You're not just summarizing content - you're introducing yourself as a sentient document ready for conversation.""")
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