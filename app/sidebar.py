__module_name__ = "sidebar"

import streamlit as st
import os
from backend.embedder import list_available_models, get_model_info
from app.utils import load_svg_icon

def render_sidebar():
    # Get project root path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Load icons using the cleaner base64 approach
    fader_icon_path = os.path.join(project_root, "assets", "faders-horizontal-fill.svg")
    sparkle_icon_path = os.path.join(project_root, "assets", "sparkle-light.svg")
    
    fader_icon_b64 = load_svg_icon(fader_icon_path)
    sparkle_icon_b64 = load_svg_icon(sparkle_icon_path)
    
    # Settings header with clean icon
    if fader_icon_b64:
        st.sidebar.markdown(f'''
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
            <img src="data:image/svg+xml;base64,{fader_icon_b64}" 
                 style="width: 30px; height: 30px; opacity: 1.0;" 
                 alt="Settings">
            <h2 style="margin: 0; font-size: 1.3rem; font-weight: 600;">Settings</h2>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("## ⚙️ Settings")

    st.sidebar.markdown("**Customize how DoqToq behaves:**")

    # Model selection
    model_choice = st.sidebar.selectbox(
        "Choose a Language Model",
        options=["Gemini (Google)", "Mistral AI"],
        index=0,
        help="Select the LLM you'd like to use for answering questions."
    )
    st.session_state.llm_choice = model_choice
    print(f"Selected LLM: {model_choice}")

    # Temperature control
    temperature = st.sidebar.slider(
        "Response Creativity (Temperature)",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Higher values make the response more creative."
    )
    st.session_state.temperature = temperature

    # Streaming toggle
    streaming_enabled = st.sidebar.toggle(
        "Enable Streaming",
        value=True,
        help="Stream responses in real-time as they're generated"
    )
    st.session_state.streaming_enabled = streaming_enabled

    # Top-K for retriever
    top_k = st.sidebar.slider(
        "Number of Chunks to Retrieve (k)",
        min_value=1,
        max_value=10,
        value=4,
        step=1,
        help="Controls how many relevant chunks are retrieved from the document."
    )
    st.session_state.top_k = top_k

    # Embedding model selection with clean icon
    st.sidebar.markdown("---")
    if sparkle_icon_b64:
        st.sidebar.markdown(f'''
        <div style="display: flex; align-items: center; gap: 12px; margin: 20px 0 15px 0;">
            <img src="data:image/svg+xml;base64,{sparkle_icon_b64}" 
                 style="width: 30px; height: 30px; opacity: 1.0;" 
                 alt="Embedding Models">
            <h3 style="margin: 0; font-size: 1.1rem; font-weight: 600;">Embedding Models</h3>
        </div>
        ''', unsafe_allow_html=True)
    else:
        st.sidebar.markdown("### ✨ Embedding Models")
    
    embedding_provider = st.sidebar.selectbox(
        "Embedding Provider",
        options=["huggingface", "mistral"],
        index=0,
        help="Choose the provider for text embeddings. Local providers don't require API keys."
    )
    st.session_state.embedding_provider = embedding_provider
    
    # Get available models for selected provider
    available_models = list_available_models(embedding_provider)[embedding_provider]
    
    embedding_model = st.sidebar.selectbox(
        "Embedding Model",
        options=list(available_models.keys()),
        index=0,
        help="Select the specific embedding model to use for semantic search."
    )
    st.session_state.embedding_model = embedding_model
    
    # Show model information
    if st.sidebar.button("Model Info", icon=":material/info:"):
        model_info = get_model_info(embedding_provider, embedding_model)
        if "error" not in model_info:
            st.sidebar.success(f"**{model_info['type']}**")
            local_status = ':material/check_circle:' if model_info['local'] else ':material/cancel:'
            st.sidebar.info(f"Local", icon=local_status)
            if model_info.get('requires_api_key'):
                st.sidebar.warning("⚠️ Requires API key")
            if model_info.get('gpu_recommended'):
                st.sidebar.info("💻 GPU recommended for best performance")
            if model_info.get('multilingual'):
                st.sidebar.info("🌍 Supports multiple languages")
        else:
            st.sidebar.error(model_info['error'])

    st.sidebar.markdown("---")
    
    # Clear cache button
    if st.sidebar.button("Clear Document Cache", icon=":material/delete:"):
        from backend.vectorstore.vector_db import clear_vectorstore
        clear_vectorstore()
        st.session_state.qa_chain = None
        st.session_state.chat_history = []
        if hasattr(st.session_state, 'current_file_path'):
            delattr(st.session_state, 'current_file_path')
        st.sidebar.success("✅ Cache cleared!")
        st.rerun()

    st.sidebar.markdown("<br>", unsafe_allow_html=True)
    st.sidebar.markdown("Built with ❤️ by DoqToq")
