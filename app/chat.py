__module_name__ = "chat"

import logging
logger = logging.getLogger(__name__)

import streamlit as st
import os
import time
from streamlit_chat import message
from app.utils import load_svg_icon, load_png_icon
from app.streaming_queue import handle_streamed_response

def get_default_avatar():
    document_path = os.path.join(os.path.dirname(__file__), "..", "assets", "scroll-light.svg")
    user_path = os.path.join(os.path.dirname(__file__), "..", "assets", "user-light.svg")
    return document_path, user_path

def get_quill():
    """Load and return the PNG Quill icon"""
    quill_path = os.path.join(os.path.dirname(__file__), "..", "assets", "quill.png")
    return load_png_icon(quill_path)
    
def render_chat_interface():
    # Display chat history first (before processing any new input)
    document_avatar, user_avatar = get_default_avatar()
    quill_icon = get_quill()

    for role, msg in st.session_state.chat_history:
        is_user = role == "user"
        if is_user:
            with st.chat_message("user", avatar=user_avatar):
                st.write(msg)
        else:
            with st.chat_message("assistant", avatar=document_avatar):
                st.write(msg)
    
    # Handle new user input
    user_input = st.chat_input("Ask something about the document...")
    logger.info(
        f"{__module_name__} - User input received."
    )

    if user_input:
        # Check if streaming is enabled
        streaming_enabled = st.session_state.get("streaming_enabled", True)
        
        # Display the new user message immediately
        with st.chat_message("user", avatar=user_avatar):
            st.write(user_input)
            logger.info(
                f"{__module_name__} - User input displayed."
            )
        
        if streaming_enabled:
            logger.info(
                f"{__module_name__} - Streaming enabled."
            )
            # Handle streaming response
            with st.chat_message("assistant", avatar=document_avatar):
                message_placeholder = st.empty()
                full_response = ""
                source_docs = []
                response_metadata = {}
                
                # Get streaming configuration from session state
                streaming_delay = st.session_state.get("streaming_delay", 0.02)
                streaming_mode = st.session_state.get("streaming_mode", "character")
                
                if streaming_delay == 0 or streaming_mode == "instant":
                    logger.info(
                        f"{__module_name__} - Using instant streaming mode with no delay."
                    )
                    # No delay - stream directly as before for maximum performance
                    for chunk_data in st.session_state.qa_chain.query_stream(user_input):
                        if chunk_data.get("answer_chunk"):
                            full_response += chunk_data["answer_chunk"]
                            message_placeholder.markdown(
                                full_response + f"<img src='data:image/png;base64,{quill_icon}' style='width: 40px; height: 40px; display: inline; vertical-align: bottom; transform: translateY(-5px);'>", 
                                unsafe_allow_html=True
                            )
                        
                        # Handle completed response
                        if chunk_data.get("is_complete"):
                            final_answer = chunk_data.get("answer", full_response)
                            source_docs = chunk_data.get("source_documents", [])
                            response_metadata = chunk_data
                            
                            # Store similarity metrics if available
                            if chunk_data.get("similarity_metrics"):
                                st.session_state['similarity_metrics'] = chunk_data["similarity_metrics"]
                            break
                else:
                    logger.info(
                        f"{__module_name__} - Using queue-based streaming with delay: {streaming_delay}s"
                    )
                    # Use new queue-based streaming with shock absorber pattern
                    stream_source = st.session_state.qa_chain.query_stream(user_input)
                    
                    # Handle streaming with queue-based approach
                    result = handle_streamed_response(
                        stream_source=stream_source,
                        message_placeholder=message_placeholder,
                        quill_icon=quill_icon,
                        streaming_mode=streaming_mode,
                        streaming_delay=streaming_delay,
                        debug=True  # Enable debugging to see raw LLM response structure
                    )
                    
                    # Extract results from the queue-based streaming
                    full_response = result.get("final_text", "")
                    final_answer = result.get("answer", full_response)
                    source_docs = result.get("source_documents", [])
                    response_metadata = result
                    
                    # Store similarity metrics in session state if available
                    if result.get("similarity_metrics"):
                        st.session_state['similarity_metrics'] = result["similarity_metrics"]
                
                # Final cleanup - remove the quill icon and show final answer
                final_answer = response_metadata.get("answer", full_response)
                message_placeholder.markdown(final_answer)
                logger.info(
                    f"{__module_name__} - Final answer displayed."
                )
                
                # Handle different response types after streaming is complete
                if response_metadata.get("is_injection_attempt"):
                    st.warning("Security: Please ask questions about the document content.", icon=":material/warning:")
                    logger.warning(
                        f"{__module_name__} - Injection attempt detected in user query."
                    )
                elif response_metadata.get("is_off_topic"):
                    st.info("This question seems outside the document's scope.", icon=":material/info:")
                    logger.info(
                        f"{__module_name__} - User query is off-topic."
                    )
                elif response_metadata.get("error"):
                    st.error(f"❌ An error occurred while processing your question.")
                    logger.error(
                        f"{__module_name__} - Error occurred while processing user query: {response_metadata.get('error')}"
                    )
                    # Show detailed error in an expander for debugging
                    with st.expander("Error Details (for debugging)", expanded=False):
                        st.code(str(response_metadata.get("error")))
                else:
                    # Show source information for successful queries
                    if source_docs:
                        # Get meaningful similarity metrics from session state
                        similarity_metrics = st.session_state.get('similarity_metrics', {})
                        high_relevance_count = similarity_metrics.get('high_similarity_count', len(source_docs))
                        total_docs = similarity_metrics.get('total_docs', len(source_docs))
                        logger.info(
                            f"{__module_name__} - Source information: {high_relevance_count} high relevance out of {total_docs} total."
                        )
                        with st.expander("Source Information", icon=":material/newsstand:", expanded=False):
                            if similarity_metrics:
                                st.write(f"Found **{high_relevance_count} highly relevant** sections out of {total_docs} retrieved.")
                                
                                # Show detailed breakdown
                                medium_count = similarity_metrics.get('medium_similarity_count', 0)
                                low_count = similarity_metrics.get('low_similarity_count', 0)
                                
                                if medium_count > 0 or low_count > 0:
                                    # Create colored tags for relevance breakdown
                                    st.markdown(f"""
                                    <span style='background-color: #28a745; color: white; padding: 4px 8px; border-radius: 5px; font-size: 0.8em; font-weight: regular; display: inline-flex; align-items: center; justify-content: center; line-height: 1; margin-right: 6px;'>High: {high_relevance_count}</span>
                                    <span style='background-color: #ffc107; color: black; padding: 4px 8px; border-radius: 5px; font-size: 0.8em; font-weight: regular; display: inline-flex; align-items: center; justify-content: center; line-height: 1; margin-right: 6px;'>Medium: {medium_count}</span>
                                    <span style='background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 5px; font-size: 0.8em; font-weight: regular; display: inline-flex; align-items: center; justify-content: center; line-height: 1;'>Low: {low_count}</span>
                                    """, unsafe_allow_html=True)
                                        
                                # Show score details in plain text instead of nested expander
                                st.markdown("")
                                st.markdown("##### Score Details")
                                st.markdown(f"""
                                - **Relevance Threshold:** < `{similarity_metrics.get('relevance_threshold', 0.8)}` (cosine distance)
                                - **Best Score:** `{similarity_metrics.get('min_score', 'N/A'):.3f}`
                                - **Worst Score:** `{similarity_metrics.get('max_score', 'N/A'):.3f}`
                                - **Average Score:** `{similarity_metrics.get('avg_score', 'N/A'):.3f}`
                                """)
                                logger.info(
                                    f"{__module_name__} - Score details: "
                                    f"threshold={similarity_metrics.get('relevance_threshold', 0.8)}, "
                                    f"best={similarity_metrics.get('min_score', 'N/A'):.3f}, "
                                    f"worst={similarity_metrics.get('max_score', 'N/A'):.3f}, "
                                    f"average={similarity_metrics.get('avg_score', 'N/A'):.3f}"
                                )
                            else:
                                st.markdown(f"Found {len(source_docs)} relevant sections in the document.")
                                logger.info(
                                    f"{__module_name__} - Found {len(source_docs)} relevant sections in the document."
                                )

            # Add both messages to chat history after streaming is complete
            st.session_state.chat_history.append(("user", user_input))
            logger.info(
                f"{__module_name__} - User message added to chat history."
            )
            st.session_state.chat_history.append(("doc", final_answer))
            logger.info(
                f"{__module_name__} - Assistant reply added to chat history."
            )
            logger.info(
                f"{__module_name__} - User query processed successfully. --- END OF TURN ---"
            )
        else:
            logger.info(
                f"{__module_name__} - Streaming disabled, using non-streaming query."
            )
            # Use the original non-streaming query method
            result = st.session_state.qa_chain.query(user_input)
            
            # Store similarity metrics in session state if available
            if result.get("similarity_metrics"):
                st.session_state['similarity_metrics'] = result["similarity_metrics"]
            
            # Handle different response types based on safety checks
            if result.get("is_injection_attempt"):
                reply = result["answer"]
                st.warning("Security: Please ask questions about the document content.", icon=":material/warning:")
                logger.warning(
                    f"{__module_name__} - Injection attempt detected in user query."
                )
            elif result.get("is_off_topic"):
                reply = result["answer"]
                st.info("This question seems outside the document's scope.", icon=":material/info:")
                logger.info(
                    f"{__module_name__} - User query is off-topic."
                )
            elif result.get("error"):
                reply = result["answer"]
                st.error("An error occurred while processing your question.")
                # Show detailed error in an expander for debugging
                with st.expander("Error Details (for debugging)", expanded=False):
                    st.code(str(result.get("error")))
                logger.error(
                    f"{__module_name__} - Error occurred while processing user query: {response_metadata.get('error')}"
                )
            else:
                reply = result["answer"]
                # Show source information for successful queries
                if result["source_documents"]:
                    with st.expander("Source Information", expanded=False, icon=":material/newsstand:"):
                        # Use similarity metrics if available, otherwise fall back to simple count
                        similarity_metrics = st.session_state.get('similarity_metrics', {})
                        if similarity_metrics:
                            high_relevance_count = similarity_metrics.get('high_similarity_count', 0)
                            medium_relevance_count = similarity_metrics.get('medium_similarity_count', 0)
                            low_relevance_count = similarity_metrics.get('low_similarity_count', 0)
                            total_docs = len(result['source_documents'])
                            logger.info(
                                f"{__module_name__} - Source information: {high_relevance_count} high relevance, "
                                f"{medium_relevance_count} medium relevance, {low_relevance_count} low relevance out of {total_docs} total."
                            )
                            st.write(f"Found **{high_relevance_count} highly relevant** sections out of {total_docs} retrieved.")

                            # Show detailed breakdown
                            if medium_relevance_count > 0 or low_relevance_count > 0:
                                # Create colored tags for relevance breakdown with minimal gaps
                                st.markdown(f"""
                                <span style='background-color: #28a745; color: white; padding: 4px 8px; border-radius: 5px; font-size: 0.8em; font-weight: regular; display: inline-flex; align-items: center; justify-content: center; line-height: 1; margin-right: 4px;'>High: {high_relevance_count}</span>
                                <span style='background-color: #ffc107; color: black; padding: 4px 8px; border-radius: 5px; font-size: 0.8em; font-weight: regular; display: inline-flex; align-items: center; justify-content: center; line-height: 1; margin-right: 4px;'>Medium: {medium_relevance_count}</span>
                                <span style='background-color: #dc3545; color: white; padding: 4px 8px; border-radius: 5px; font-size: 0.8em; font-weight: regular; display: inline-flex; align-items: center; justify-content: center; line-height: 1;'>Low: {low_relevance_count}</span>
                                """, unsafe_allow_html=True)
                            # Add score details in plain text instead of nested expander
                            st.markdown("")
                            st.markdown("""
                            ##### Score Details
                            - **Relevance Threshold:** < `{:.3f}` (cosine distance)
                            - **Best Score:** `{:.3f}`
                            - **Worst Score:** `{:.3f}`
                            - **Average Score:** `{:.3f}`
                            """.format(
                                similarity_metrics.get('relevance_threshold', 0.8),
                                similarity_metrics.get('min_score', 0),
                                similarity_metrics.get('max_score', 0),
                                similarity_metrics.get('avg_score', 0)
                            ))
                            logger.info(
                                f"{__module_name__} - Score details: "
                                f"threshold={similarity_metrics.get('relevance_threshold', 0.8)}, "
                                f"best={similarity_metrics.get('min_score', 'N/A'):.3f}, "
                                f"worst={similarity_metrics.get('max_score', 'N/A'):.3f}, "
                                f"average={similarity_metrics.get('avg_score', 'N/A'):.3f}"
                            )
                        else:
                            # Fallback to original display if metrics unavailable
                            st.markdown(f"Found {len(result['source_documents'])} relevant sections in the document.")
                            logger.info(
                                f"{__module_name__} - Fallback display: Found {len(result['source_documents'])} relevant sections."
                            )

            # Display the response immediately
            with st.chat_message("assistant", avatar=document_avatar):
                st.write(reply)
            logger.info(
                f"{__module_name__} - Assistant reply displayed: {reply[:50]}..."  # Log first 50 chars for brevity
            )

            # Add messages to chat history
            st.session_state.chat_history.append(("user", user_input))
            logger.info(
                f"{__module_name__} - User message added to chat history."
            )
            st.session_state.chat_history.append(("doc", reply))
            logger.info(
                f"{__module_name__} - Assistant reply added to chat history."
            )
            logger.info(
                f"{__module_name__} - User query processed successfully. --- END OF TURN ---"
            )
            
            # Force a rerun to update the display with the new history
            logger.info(
                f"{__module_name__} - Rerunning Streamlit to update chat interface."
            )
            st.rerun()
