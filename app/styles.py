__module_name__ = "styles"

import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap');
            
            html, body {
                font-family: 'Segoe UI', sans-serif;
                background-color: #f7f9fc;
            }
            .stButton button {
                border-radius: 8px;
                background-color: #cfcfcf;
                color: black;
            }
            .stChatInput > div {
                border-radius: 10px;
                border: 1px solid #ddd;
            }
            h1 {
                font-family: 'Inter', 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
                color: #2c3e50;
                font-weight: 700;
                letter-spacing: -0.025em;
                line-height: 1.1;
            }
            
            /* Custom styling for the main title specifically */
            .doqtoq-title {
                font-family: 'Inter', 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
                font-weight: 700;
                font-size: 2.75rem;
                color: #1a365d;
                letter-spacing: -0.03em;
                background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                text-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    """, unsafe_allow_html=True)
