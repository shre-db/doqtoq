# Contributing to DoqToq

Thank you for your interest in contributing to DoqToq! This document provides guidelines and information for contributors.

## Ways to Contribute

- **Bug Reports**: Report issues you encounter
- **Feature Requests**: Suggest new features or improvements
- **Code Contributions**: Submit pull requests for bug fixes or new features
- **Documentation**: Improve README, code comments, or create tutorials
- **Testing**: Add test cases or improve test coverage

## Development Setup

### Prerequisites
- Python 3.12+
- Git
- Conda (recommended) or pip

### Setting up Development Environment

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/shre-db/doqtoq.git
   cd doqtoq
   ```

2. **Create development environment**
   ```bash
   # Using conda (recommended)
   conda env create -f environment.yaml
   conda activate doqtoq

   # Or using pip
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the application**
   ```bash
   streamlit run app/main.py
   ```

## Pull Request Process

### Before Submitting
1. **Create an issue** first to discuss major changes
2. **Fork the repository** and create a feature branch
3. **Follow code style** guidelines (see below)
4. **Add tests** for new functionality
5. **Update documentation** as needed

### Code Style Guidelines

#### Python Code Style
- Follow **PEP 8** conventions
- Use **type hints** for function parameters and return values
- Add **docstrings** for all public functions and classes
- Keep functions focused and under 50 lines when possible
- Use meaningful variable and function names

#### Example:
```python
def process_document(file_path: str, chunk_size: int = 1000) -> List[Document]:
    """
    Process a document file into chunks for RAG processing.

    Args:
        file_path: Path to the document file
        chunk_size: Maximum size of each text chunk

    Returns:
        List of processed document chunks

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If chunk_size is invalid
    """
    # Implementation here
    pass
```

#### Frontend Guidelines
- Keep Streamlit components modular
- Use session state appropriately
- Follow the existing UI patterns
- Ensure responsive design principles

### Testing
- Add unit tests for new functions in `tests/`
- Run existing tests: `python -m pytest tests/`
- Ensure all tests pass before submitting PR

### Commit Messages
Use descriptive commit messages following this format:
```
type(scope): brief description

Longer description if needed

- Bullet points for multiple changes
- Reference issues with #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Example:
```
feat(rag): add support for DOCX file format

- Add DOCX parsing in chunker.py
- Update file upload validation
- Add tests for DOCX processing

Fixes #45
```

## Bug Reports

When reporting bugs, please include:
- **Environment**: OS, Python version, dependency versions
- **Steps to reproduce**: Clear, minimal steps
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happened
- **Error messages**: Full stack traces if applicable
- **Screenshots**: If UI-related

Use this template:
```markdown
## Bug Description
Brief description of the bug

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.12.1]
- DoqToq version: [e.g., commit hash]

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
Description of expected behavior

## Actual Behavior
Description of what actually happened

## Error Messages
```
Paste error messages or stack traces here
```
## Additional Context
Any other relevant information
```

## Feature Requests

For feature requests, please provide:
- **Use case**: Why is this feature needed?
- **Proposed solution**: How should it work?
- **Alternatives considered**: Other ways to solve the problem
- **Additional context**: Screenshots, mockups, examples

## Architecture Guidelines

### Project Structure
```
doqtoq/
├── app/           # Streamlit frontend components
├── backend/       # Core RAG engine and AI logic
├── tests/         # Test suite
├── utils/         # Shared utilities
├── data/          # Sample data and uploads
└── docs/          # Documentation (future)
```

### Key Principles
- **Modularity**: Keep components loosely coupled
- **Testability**: Write testable code with clear interfaces
- **Documentation**: Document complex logic and API changes
- **Performance**: Consider performance implications of changes
- **Security**: Follow security best practices, especially for file handling

## Release Process

### Versioning
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release notes
- [ ] Tag release in Git

## Code of Conduct

### Our Standards
- **Be respectful** and inclusive
- **Be constructive** in discussions and reviews
- **Focus on the code**, not the person
- **Help others learn** and grow

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing private information

## Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community chat
- **Documentation**: Check README and code comments
- **Code Review**: Feel free to ask for help in PR comments

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes for significant contributions
- Given credit in documentation they help create

Thank you for contributing to DoqToq!
