#!/bin/bash

# DoqToq Startup Script
# This script sets up the environment and starts the Streamlit application
# with proper warning suppression

# Set environment variables to suppress warnings
export TORCH_WARN=0
export PYTORCH_DISABLE_TORCH_FUNCTION_WARN=1
export TOKENIZERS_PARALLELISM=false

# Start the Streamlit application
echo "Starting DoqToq application..."
echo "The application will be available at: http://localhost:8501"
echo ""

streamlit run app/main.py --server.port 8501 --server.headless true
