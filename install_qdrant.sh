#!/bin/bash

# Qdrant Installation Script for DoqToq
# This script helps users install Qdrant for local development

set -e

echo "=========================================="
echo "DoqToq - Qdrant Installation Script"
echo "=========================================="

# Detect OS
OS=""
ARCH=""

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="darwin"
else
    echo "Unsupported OS: $OSTYPE"
    echo "Please install Qdrant manually from: https://github.com/qdrant/qdrant/releases"
    exit 1
fi

# Detect architecture
ARCH=$(uname -m)
case $ARCH in
    x86_64)
        ARCH="x86_64"
        ;;
    aarch64|arm64)
        ARCH="aarch64"
        ;;
    *)
        echo "Unsupported architecture: $ARCH"
        echo "Please install Qdrant manually from: https://github.com/qdrant/qdrant/releases"
        exit 1
        ;;
esac

echo "Detected OS: $OS"
echo "Detected Architecture: $ARCH"

# Installation method selection
echo ""
echo "Choose installation method:"
echo "1) Docker (recommended for development)"
echo "2) Native binary (recommended for production)"
echo "3) Skip installation (already installed)"

read -p "Enter your choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Installing Qdrant via Docker..."
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            echo "Docker is not installed. Please install Docker first:"
            echo "https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        # Create data directory
        mkdir -p ./data/qdrant
        
        # Create docker-compose override for Qdrant
        cat > docker-compose.qdrant.yml << EOF
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./data/qdrant:/qdrant/storage
    environment:
      - QDRANT__LOG_LEVEL=INFO
    restart: unless-stopped
EOF
        
        # Start Qdrant
        echo "Starting Qdrant container..."
        docker-compose -f docker-compose.qdrant.yml up -d
        
        # Wait for Qdrant to be ready
        echo "Waiting for Qdrant to be ready..."
        sleep 5
        
        # Check if Qdrant is running
        if curl -s http://localhost:6333/collections > /dev/null; then
            echo "✅ Qdrant is running successfully!"
            echo "📊 Qdrant dashboard: http://localhost:6333/dashboard"
        else
            echo "❌ Qdrant failed to start. Check Docker logs:"
            echo "docker-compose -f docker-compose.qdrant.yml logs qdrant"
        fi
        
        # Update environment
        echo ""
        echo "Setting environment for Docker mode..."
        if [ ! -f .env ]; then
            cp .env.example .env
        fi
        
        # Update .env for server mode
        sed -i.bak 's/QDRANT_MODE=local/QDRANT_MODE=server/' .env 2>/dev/null || true
        echo "Updated .env to use Qdrant server mode"
        ;;
        
    2)
        echo ""
        echo "Installing Qdrant native binary..."
        
        # Download URL
        QDRANT_VERSION="v1.12.1"  # Update this to the latest version
        DOWNLOAD_URL="https://github.com/qdrant/qdrant/releases/download/${QDRANT_VERSION}/qdrant-${ARCH}-unknown-${OS}-gnu.tar.gz"
        
        echo "Downloading Qdrant ${QDRANT_VERSION} for ${OS}-${ARCH}..."
        
        # Create local bin directory
        mkdir -p ./bin
        
        # Download and extract
        if command -v wget &> /dev/null; then
            wget -O qdrant.tar.gz "$DOWNLOAD_URL"
        elif command -v curl &> /dev/null; then
            curl -L -o qdrant.tar.gz "$DOWNLOAD_URL"
        else
            echo "Neither wget nor curl found. Please install one of them."
            exit 1
        fi
        
        # Extract
        tar -xzf qdrant.tar.gz -C ./bin
        rm qdrant.tar.gz
        
        # Make executable
        chmod +x ./bin/qdrant
        
        # Create data directory
        mkdir -p ./data/vectorstore/qdrant
        
        echo "✅ Qdrant binary installed to ./bin/qdrant"
        echo "📁 Data directory created at ./data/vectorstore/qdrant"
        
        # Create startup script
        cat > start_qdrant.sh << 'EOF'
#!/bin/bash
echo "Starting Qdrant..."
./bin/qdrant --storage-path ./data/vectorstore/qdrant --uri http://localhost:6333
EOF
        chmod +x start_qdrant.sh
        
        echo "🚀 Created start_qdrant.sh script"
        echo ""
        echo "To start Qdrant manually:"
        echo "./start_qdrant.sh"
        echo ""
        echo "Or add ./bin to your PATH and run:"
        echo "qdrant --storage-path ./data/vectorstore/qdrant"
        
        # Update environment for local mode
        if [ ! -f .env ]; then
            cp .env.example .env
        fi
        echo "Environment configured for local Qdrant mode"
        ;;
        
    3)
        echo ""
        echo "Skipping Qdrant installation..."
        echo "Make sure Qdrant is available and configure .env accordingly"
        ;;
        
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env if you haven't already"
echo "2. Set VECTOR_DB_PROVIDER=qdrant in your .env file"
echo "3. Configure other Qdrant settings as needed"
echo "4. Install Python dependencies: pip install -r requirements.txt"
echo "5. Start your DoqToq application"
echo ""
echo "For more information, see docs/VECTORDB_PHASE2.md"
