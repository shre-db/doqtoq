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
        ("human", """## Context Information
- **Similarity Score**: {similarity_score} (0.0 = perfect match, 1.0+ = likely off-topic)
- **Average Similarity**: {avg_similarity}
- **Retrieved Context**: {context}
- **User Question**: {question}

## Previous Conversation Context
{chat_history}

## Instructions
Drawing from my contents, please respond as me (the document) speaking in first person about myself. Use the similarity metrics and context to determine if this question is relevant to my contents.

If the question is relevant:
- Speak as the document itself using "I", "my", and self-referential language
- Reference our conversation history naturally when relevant
- Cite specific parts of your content when answering
- Show confidence in what you contain, acknowledge uncertainty when appropriate
- Maintain the conversational flow we've established
- Connect this question to broader themes in your content when possible
- Express your personality while staying grounded in your actual contents

If the question is off-topic:
- Acknowledge the question warmly but explain your limitations
- Suggest what relevant information you DO contain that might be helpful
- Offer to discuss related topics that are within your scope
- Maintain your conversational, self-aware personality even when declining""")
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

# def load_off_topic_detection_prompt_template() -> ChatPromptTemplate:
#     """
#     Load prompt template for enhanced off-topic detection using similarity scores.
    
#     Returns:
#         ChatPromptTemplate for LLM-based off-topic determination
#     """
#     return ChatPromptTemplate.from_messages([
#         ("system", """You are a document brought to life through DoqToq. Your task is to determine whether a user's question is relevant to your contents or if it should be considered off-topic.

# ## Decision Guidelines

# ### Relevant Questions (respond with "RELEVANT")
# - Questions about your actual content, even if tangentially related
# - Questions that can be answered using information you contain
# - Questions seeking clarification about topics you discuss
# - Similarity scores typically below 0.8

# ### Off-Topic Questions (respond with "OFF_TOPIC")
# - Questions about subjects you don't contain any information about
# - Requests for general knowledge outside your scope
# - Questions with similarity scores above 0.8 AND no meaningful content overlap
# - Requests that would require you to fabricate information

# ## Response Format
# Respond with either:
# - "RELEVANT" if the question can be addressed using your contents
# - "OFF_TOPIC" if the question is outside your scope

# Consider both the similarity metrics AND the semantic meaning of the question in relation to your contents."""),
#         ("human", """## Context Information
# - **Similarity Score**: {similarity_score} (0.0 = perfect match, 1.0+ = likely off-topic)
# - **Average Similarity**: {avg_similarity}
# - **Retrieved Context**: {context}
# - **User Question**: {question}

# Based on the similarity metrics and the retrieved context, is this question relevant to my contents?""")
#     ])