__module_name__ = "main"

import os
import sys
import warnings

# Setup environment to suppress warnings before any other imports
os.environ["TORCH_WARN"] = "0"
os.environ["PYTORCH_DISABLE_TORCH_FUNCTION_WARN"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# Fix for PyTorch 2.7+ compatibility with Streamlit file watcher
os.environ["STREAMLIT_DISABLE_WATCHDOG_WARNING"] = "1"
os.environ["STREAMLIT_FILE_WATCHER_TYPE"] = "none"

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=UserWarning, message=".*torch.*")

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Apply PyTorch compatibility fixes before importing Streamlit
try:
    from utils.torch_compatibility import apply_streamlit_fixes

    apply_streamlit_fixes()
    from utils.logging_method import setup_logger

    logger = setup_logger(
        log_file=os.path.join(project_root, "logs", "app.log"),
        level="INFO",
        timezone_str="Asia/Kolkata",
    )
except ImportError:
    print("Warning: Could not import torch compatibility fixes")

import streamlit as st

st.set_page_config(
    page_title="DoqToq",
    page_icon=":material/folder_open:",
    layout="centered",
    initial_sidebar_state="collapsed",
)
from app.chat import render_chat_interface
from app.config import init_session_state
from app.sidebar import render_sidebar
from app.styles import inject_custom_css
from app.uploader import handle_upload
from app.utils import load_svg_icon
from backend.rag_engine import DocumentRAG

inject_custom_css()
render_sidebar()

# Initialize session state
init_session_state()

# Only log application start once per session
if "app_started_logged" not in st.session_state:
    logger.info(
        f"{__module_name__} - Application started with session state: {st.session_state}"
    )
    st.session_state.app_started_logged = True

document_icon_path = os.path.join(project_root, "assets", "scroll-light.svg")
document_icon_b64 = load_svg_icon(document_icon_path)

if document_icon_b64:
    title_html = f"""
    <div style="display: flex; align-items: center; margin-bottom: 0.1rem;">
        <img src="data:image/svg+xml;base64,{document_icon_b64}"
             style="width: 40px; height: 40px; margin-right: 12px;"
             alt="DoqToq logo">
        <h1 class="doqtoq-title" style="margin: 0;">
            DoqToq
        </h1>
    </div>
    <div class="doqtoq-subtitle" style="display: flex; align-items: center; font-size: 1.2rem; color: #666; margin-top: -0.7rem;">
        Documents that talk ‒ DoqToq
    </div>
    """
    st.markdown(title_html, unsafe_allow_html=True)
    st.markdown('<div style="height: 64px;"></div>', unsafe_allow_html=True)
else:
    # Fallback to emoji if icon can't be loaded
    st.markdown('<h1 class="doqtoq-title">📄 DoqToq</h1>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload a PDF, TXT, JSON or Markdown document", type=["pdf", "txt", "json", "md"]
)

# Only log file upload when it's actually a new file or changed
current_file_name = uploaded_file.name if uploaded_file else "No file uploaded"
last_logged_file = st.session_state.get("last_logged_file", None)

if last_logged_file != current_file_name:
    logger.info(f"{__module_name__} - File uploaded: {current_file_name}")
    st.session_state.last_logged_file = current_file_name

if uploaded_file:
    file_path = handle_upload(uploaded_file)

    # Check if this is a new document by comparing file paths
    current_file = getattr(st.session_state, "current_file_path", None)
    is_new_document = current_file != file_path

    # Reset session state for new document
    if is_new_document:
        st.session_state.qa_chain = None
        st.session_state.chat_history = []
        st.session_state.current_file_path = file_path
        st.info(f"New document detected: {uploaded_file.name}", icon=":material/docs:")

    if not st.session_state.qa_chain:
        with st.spinner("Reading and indexing your document..."):
            logger.info(f"{__module_name__} - Indexing started for file: {file_path}")
            # Get model provider from sidebar
            llm_choice = st.session_state.get("llm_choice", "Gemini (Google)")
            model_provider = (
                "google"
                if llm_choice == "Gemini (Google)"
                else "mistral" if llm_choice == "Mistral AI" else "ollama"
            )
            logger.info(
                f"{__module_name__} - Using model provider: {model_provider} (from choice: {llm_choice})"
            )
            # Get embedding settings from sidebar
            embedding_provider = st.session_state.get(
                "embedding_provider", "huggingface"
            )
            embedding_model = st.session_state.get(
                "embedding_model", "all-MiniLM-L6-v2"
            )
            temperature = st.session_state.get("temperature", 0.7)
            top_k = st.session_state.get("top_k", 4)
            streaming_enabled = st.session_state.get("streaming_enabled", True)

            st.session_state.qa_chain = DocumentRAG(
                file_path=file_path,
                model_provider=model_provider,
                temperature=temperature,
                top_k=top_k,
                embedding_provider=embedding_provider,
                embedding_model=embedding_model,
                streaming=streaming_enabled,
            )
            logger.info(
                f"{__module_name__} - Indexing completed for file: {file_path}, "
                f"model provider: {model_provider}, embedding provider: {embedding_provider}, "
                f"embedding model: {embedding_model}, temperature: {temperature}, top_k: {top_k}, "
                f"streaming: {streaming_enabled}"
            )

    # Update settings if they've changed
    if st.session_state.qa_chain:
        llm_choice = st.session_state.get("llm_choice", "Gemini (Google)")
        model_provider = (
            "google"
            if llm_choice == "Gemini (Google)"
            else "mistral" if llm_choice == "Mistral AI" else "ollama"
        )

        # Get current settings
        temperature = st.session_state.get("temperature", 0.7)
        top_k = st.session_state.get("top_k", 4)
        embedding_provider = st.session_state.get("embedding_provider", "huggingface")
        embedding_model = st.session_state.get("embedding_model", "all-MiniLM-L6-v2")
        streaming_enabled = st.session_state.get("streaming_enabled", True)

        # Create settings signature to detect actual changes
        current_settings = {
            "model_provider": model_provider,
            "temperature": temperature,
            "top_k": top_k,
            "embedding_provider": embedding_provider,
            "embedding_model": embedding_model,
            "streaming": streaming_enabled,
        }

        last_settings = st.session_state.get("last_logged_settings", {})

        # Only log and update if settings actually changed
        if current_settings != last_settings:
            logger.info(
                f"{__module_name__} - Updating settings for model provider: {model_provider} (from choice: {llm_choice})"
            )

            st.session_state.qa_chain.update_settings(
                temperature=temperature,
                top_k=top_k,
                embedding_provider=embedding_provider,
                embedding_model=embedding_model,
                model_provider=model_provider,
                streaming=streaming_enabled,
            )
            logger.info(
                f"{__module_name__} - Settings updated: temperature={temperature}, top_k={top_k}, "
                f"embedding_provider={embedding_provider}, embedding_model={embedding_model}, "
                f"model_provider={model_provider}, streaming={streaming_enabled}"
            )

            # Store current settings for next comparison
            st.session_state.last_logged_settings = current_settings
        else:
            # Settings haven't changed, just update without logging
            st.session_state.qa_chain.update_settings(
                temperature=temperature,
                top_k=top_k,
                embedding_provider=embedding_provider,
                embedding_model=embedding_model,
                model_provider=model_provider,
                streaming=streaming_enabled,
            )

        # Show current embedding info
        with st.expander(
            "Current Embedding Configuration",
            expanded=False,
            icon=":material/settings:",
        ):
            embedding_info = st.session_state.qa_chain.get_embedding_info()
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Provider:** {embedding_info['provider']}")
                st.write(f"**Model:** {embedding_info['model_name']}")
            with col2:
                st.write(f"**Type:** {embedding_info['type']}")
                st.write(
                    f"**Local:** {':material/check_circle:' if embedding_info['local'] else ':material/cancel:'}"
                )

    st.success(
        "Your document has awakened from hibernation, ready for your questions!",
        icon=":material/check_circle:",
    )

    # Only log document ready once per file
    if st.session_state.get("last_ready_file") != file_path:
        logger.info(f"{__module_name__} - Document ready for interaction: {file_path}")
        st.session_state.last_ready_file = file_path

    render_chat_interface()
else:
    st.info("Please upload a document to begin.")
