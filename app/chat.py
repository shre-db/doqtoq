__module_name__ = "chat"

import streamlit as st
import os
import time
from streamlit_chat import message
from utils import load_svg_icon

def get_default_avatar():
    document_path = os.path.join(os.path.dirname(__file__), "..", "assets", "scroll-light.svg")
    user_path = os.path.join(os.path.dirname(__file__), "..", "assets", "user-light.svg")
    return document_path, user_path


def render_chat_interface():
    # Display chat history first (before processing any new input)
    document_avatar, user_avatar = get_default_avatar()
    
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

    if user_input:
        # Check if streaming is enabled
        streaming_enabled = st.session_state.get("streaming_enabled", True)
        
        # Display the new user message immediately
        with st.chat_message("user", avatar=user_avatar):
            st.write(user_input)
        
        if streaming_enabled:
            # Handle streaming response
            with st.chat_message("assistant", avatar=document_avatar):
                message_placeholder = st.empty()
                full_response = ""
                source_docs = []
                response_metadata = {}
                
                # Stream the response
                for chunk_data in st.session_state.qa_chain.query_stream(user_input):
                    if chunk_data.get("answer_chunk"):
                        full_response += chunk_data["answer_chunk"]
                        # Update the message placeholder with accumulated text
                        message_placeholder.markdown(full_response + "▌")
                    
                    # Handle completed response
                    if chunk_data.get("is_complete"):
                        final_answer = chunk_data.get("answer", full_response)
                        message_placeholder.markdown(final_answer)
                        source_docs = chunk_data.get("source_documents", [])
                        response_metadata = chunk_data
                        break
                
                # Handle different response types after streaming is complete
                if response_metadata.get("is_injection_attempt"):
                    st.warning("Security: Please ask questions about the document content.", icon=":material/warning:")
                elif response_metadata.get("is_off_topic"):
                    st.info("This question seems outside the document's scope.", icon=":material/info:")
                elif response_metadata.get("error"):
                    st.error("❌ An error occurred while processing your question.")
                else:
                    # Show source information for successful queries
                    if source_docs:
                        with st.expander("Source Information", icon=":material/newsstand:", expanded=False):
                            st.write(f"Found {len(source_docs)} relevant sections in the document.")
            
            # Add both messages to chat history after streaming is complete
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("doc", final_answer))
            
        else:
            # Use the original non-streaming query method
            result = st.session_state.qa_chain.query(user_input)
            
            # Handle different response types based on safety checks
            if result.get("is_injection_attempt"):
                reply = result["answer"]
                st.warning("Security: Please ask questions about the document content.", icon=":material/warning:")
            elif result.get("is_off_topic"):
                reply = result["answer"]
                st.info("This question seems outside the document's scope.", icon=":material/info:")
            elif result.get("error"):
                reply = result["answer"]
                st.error("An error occurred while processing your question.", icon=":material/error:")
            else:
                reply = result["answer"]
                # Show source information for successful queries
                if result["source_documents"]:
                    with st.expander("Source Information", expanded=False, icon=":material/newsstand:"):
                        st.write(f"Found {len(result['source_documents'])} relevant sections in the document.")

            # Display the response immediately
            with st.chat_message("assistant", avatar=document_avatar):
                st.write(reply)

            # Add messages to chat history
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("doc", reply))
            
            # Force a rerun to update the display with the new history
            st.rerun()
