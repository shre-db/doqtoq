# Changelog

All notable changes to DoqToq will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- _No unreleased features yet_

### Changed
- _No unreleased changes yet_

### Fixed
- _No unreleased fixes yet_

## [0.1.0] - 2025-08-01

### Added
- **Qdrant Vector Database Support**: Complete Qdrant integration with automated installation
- **Vector Database Abstraction**: Unified interface supporting both ChromaDB and Qdrant
- **Database Factory Pattern**: Flexible database provider selection and configuration
- **Pydantic Configuration Management**: Type-safe configuration with environment-based setup
- **Database Migration System**: Seamless switching between vector database providers
- **Automated Qdrant Installation**: `install_qdrant.sh` script with Docker and native support
- **Docker Compose Profiles**: Qdrant service integration with profile-based deployment
- **Unified Directory Structure**: Standardized `./data/vectorstore/` organization
- **Enhanced Environment Configuration**: Comprehensive `.env.example` with database options
- **Vector Database Documentation**: Complete setup guides and design decision documentation
- **Manual Release Guide**: Comprehensive documentation for manual versioning and GitHub releases
- **Advanced Vector Database Configuration**: Local, server, and cloud deployment modes
- **gRPC Support**: High-performance gRPC option for Qdrant connections
- **Database Health Checks**: Built-in monitoring and status verification
- **Multi-LLM Support**: Google Gemini, Mistral AI, and Ollama integration
- **Document Personality System**: First-person conversational document responses
- **Real-time Streaming**: Customizable streaming responses with multiple speed options
- **Advanced RAG Pipeline**: ChromaDB and Qdrant vector database support
- **Universal Document Support**: PDF, TXT, JSON, and Markdown file processing
- **Interactive Streamlit Interface**: Professional web UI with custom styling
- **Conversation Memory**: Context-aware multi-turn conversations
- **Safety Features**: Off-topic detection, prompt injection protection, input validation
- **Similarity Scoring**: Visual relevance assessment with color-coded feedback
- **Comprehensive Testing**: Unit, integration, performance, and security test suites
- **CI/CD Pipeline**: Automated testing, security scanning, and quality checks
- **Docker Support**: Multiple containerization options (venv and conda)
- **Production Infrastructure**: Logging, monitoring, health checks, and deployment guides
- **LaTeX Math Rendering**: Mathematical expression support in responses
- **Code Syntax Highlighting**: Enhanced code block presentation
- **Emoji Enhancement**: Rich emoji integration in responses
- **Multithreaded Streaming**: Producer-consumer pattern for smooth response delivery

### Changed
- **Release Process**: Switched from automated semantic-release to manual GitHub releases for simplicity
- **CI/CD Pipeline**: Removed release automation, simplified to testing and quality checks only
- **Versioning Strategy**: Adopted manual version control with GitHub's native release system
- **Vector Database Architecture**: Refactored from single ChromaDB to pluggable architecture
- **Configuration System**: Migrated to Pydantic-based configuration management
- **Directory Structure**: Unified vector database storage under `./data/vectorstore/`
- **Environment Variables**: Enhanced `.env` structure with database provider options
- **Dependencies**: Updated `requirements.txt` with Qdrant and Pydantic dependencies
- **Docker Configuration**: Enhanced Docker Compose with multi-service support
- **Installation Process**: Improved setup scripts with database choice options

### Fixed
- **CI Pipeline Errors**: Resolved GitHub Actions workflow issues and job dependencies
- **Protobuf Compatibility**: Fixed protobuf version conflicts with PyTorch and Streamlit
- **LLM Wrapper Issues**: Corrected model selection and initialization problems
- **Prompt Injection Detection**: Enhanced security checks and off-topic handling
- **Embedding Model Configuration**: Fixed Mistral model selection and HuggingFace integration
- **Dependency Conflicts**: Resolved version compatibility issues across the stack

### Removed
- **Semantic Release Automation**: Removed `.releaserc.json` and automated release workflow
- **CI Release Job**: Eliminated release automation from GitHub Actions pipeline
- **Conventional Commit Requirements**: No longer enforcing commit message formats

---

*Note: This project uses manual versioning and GitHub releases. Version 0.1.0 is the initial release.*

## Release Information

This project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with manual release management via GitHub's release system.

### Release Process
- **Manual Versioning**: Releases are created manually through GitHub's web interface
- **Changelog Updates**: Version sections are manually maintained in this file
- **Release Notes**: GitHub releases reference this changelog for detailed information

### Version Types
- **Major (X.0.0)**: Breaking changes that require user intervention
- **Minor (0.X.0)**: New features that are backward compatible
- **Patch (0.0.X)**: Bug fixes and performance improvements

## Contributing to the Changelog

When contributing to DoqToq, please update this changelog following these guidelines:

### Categories
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

### Format
- Keep entries concise but descriptive
- Link to issues/PRs when relevant: `([#123](https://github.com/shre-db/doqtoq/issues/123))`
- Group related changes together
- Use past tense ("Added" not "Add")
- Start with a capital letter
- Don't end with a period

### Example Entry
```markdown
### Added
- New document format support for DOCX files ([#45](https://github.com/shre-db/doqtoq/issues/45))
- Real-time collaboration features
- Advanced search functionality with filters

### Fixed
- Memory leak in document processing ([#67](https://github.com/shre-db/doqtoq/issues/67))
- UI responsiveness on mobile devices
```
