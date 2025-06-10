"""
Utility script to suppress common warnings and setup environment variables
for running the DoqToq application.
"""

import os
import warnings
import sys

def setup_environment():
    """Setup environment variables to suppress warnings."""
    # Suppress PyTorch C++ warnings that occur during Streamlit file watching
    os.environ["TORCH_WARN"] = "0"
    os.environ["PYTORCH_DISABLE_TORCH_FUNCTION_WARN"] = "1"
    
    # Suppress other common warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning, module="torch")
    
    # Set up additional environment variables for better performance
    os.environ["TOKENIZERS_PARALLELISM"] = "false"  # Prevents huggingface tokenizer warnings
    
if __name__ == "__main__":
    setup_environment()
    print("Environment configured successfully!")
