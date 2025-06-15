# Changelog

All notable changes to DoqToq will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with pytest
- CI/CD pipeline with GitHub Actions
- Pre-commit hooks for code quality
- Security scanning with Bandit and Safety
- Performance testing framework
- Docker support (venv and conda)
- Development environment setup scripts
- Contributing guidelines and issue templates
- Security policy and vulnerability reporting
- Code coverage reporting
- Type checking with mypy
- Automated formatting with Black and isort
- Makefile for common development tasks

### Changed
- Enhanced documentation with setup instructions
- Improved error handling and logging
- Streamlined dependency management

### Security
- Added prompt injection detection and prevention
- Implemented input validation for file uploads
- Added security headers and configuration guidance

## [1.0.0] - TBD

### Added
- Initial release of DoqToq
- Multi-LLM support (Google Gemini, Mistral AI, Ollama)
- Document personality system with first-person responses
- Real-time streaming responses with customizable speed
- Advanced RAG pipeline with ChromaDB integration
- Support for PDF, TXT, JSON, and Markdown files
- Interactive Streamlit web interface
- Conversation memory and context awareness
- Off-topic detection and graceful handling
- Similarity scoring and relevance assessment
- Custom CSS styling and SVG icons
- Comprehensive prompt engineering system
- LaTeX math rendering support
- Code syntax highlighting
- Emoji-enhanced responses
- Docker containerization
- Environment-based configuration
- Logging and debugging capabilities

### Features by Category

#### Core RAG Engine
- Document chunking and embedding
- Vector similarity search
- Context-aware retrieval
- Multi-provider LLM integration
- Streaming response generation

#### User Interface
- Drag-and-drop file upload
- Real-time chat interface
- Configurable sidebar controls
- Responsive design
- Custom theming

#### AI Capabilities
- Document personality injection
- First-person conversational responses
- Context-aware question answering
- Off-topic query detection
- Prompt injection protection

#### Developer Experience
- Modular architecture
- Comprehensive logging
- Error handling
- Configuration management
- Testing utilities

---

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
- Link to issues/PRs when relevant: `([#123](https://github.com/username/doqtoq/issues/123))`
- Group related changes together
- Use past tense ("Added" not "Add")
- Start with a capital letter
- Don't end with a period

### Example Entry
```markdown
### Added
- New document format support for DOCX files ([#45](https://github.com/username/doqtoq/issues/45))
- Real-time collaboration features
- Advanced search functionality with filters

### Fixed
- Memory leak in document processing ([#67](https://github.com/username/doqtoq/issues/67))
- UI responsiveness on mobile devices
```
