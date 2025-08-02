# Security Policy

## Supported Versions

We provide security updates for the following versions of DoqToq:

| Version | Supported          |
| ------- | ------------------ |
| main    | ✅ (latest)        |
| 1.0.x   | ✅ (when released) |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in DoqToq, please report it responsibly.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them privately:

1. **Email**: Send details to [security@doqtoq.com]
2. **GitHub Security Advisories**: Use GitHub's private vulnerability reporting feature
3. **Encrypted Communication**: If needed, we can provide a PGP key for sensitive reports

### What to Include

When reporting a vulnerability, please include:

- **Description**: Clear description of the vulnerability
- **Impact**: What an attacker could achieve
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Proof of Concept**: Code or screenshots demonstrating the vulnerability
- **Suggested Fix**: If you have ideas for fixing the issue

### Response Timeline

- **Initial Response**: Within 48 hours
- **Assessment**: Within 1 week
- **Fix Timeline**: Varies by severity (critical issues prioritized)
- **Public Disclosure**: After fix is released and users have time to update

## Security Considerations

### Current Security Measures

DoqToq implements several security measures:

1. **Input Validation**: File type and size validation for uploads
2. **Prompt Injection Protection**: Built-in detection and prevention
3. **API Key Security**: Environment variable usage, no hardcoded keys
4. **File Isolation**: Secure file handling and temporary storage
5. **Output Sanitization**: Proper handling of AI-generated content

### Known Security Considerations

Users should be aware of:

1. **API Key Management**: Keep your API keys secure and rotate them regularly
2. **Document Privacy**: Uploaded documents are processed by AI models (respect your organization's data policies)
3. **Local Processing**: Consider using Ollama for sensitive documents
4. **Network Security**: Ensure secure connections when using cloud AI services

### Best Practices for Users

1. **Environment Variables**: Always use `.env` files for API keys
2. **Document Sensitivity**: Be mindful of what documents you upload
3. **Regular Updates**: Keep DoqToq updated to get security patches
4. **Access Control**: Secure your DoqToq deployment appropriately
5. **Local Deployment**: Consider local models for sensitive use cases

### Security Headers and Configuration

For production deployments, consider:

- Reverse proxy with security headers
- Rate limiting for API endpoints
- SSL/TLS encryption
- Authentication if needed
- Regular security audits

## Vulnerability Assessment

### Attack Vectors We Monitor

1. **File Upload Vulnerabilities**: Malicious file uploads
2. **Prompt Injection**: Attempts to manipulate AI behavior
3. **Data Exfiltration**: Unauthorized access to document content
4. **API Key Exposure**: Accidental exposure of credentials
5. **Dependency Vulnerabilities**: Third-party library security issues

### Regular Security Practices

- Dependency scanning with tools like `safety` or `snyk`
- Regular updates of all dependencies
- Code review for security implications
- Testing with security-focused test cases

## Responsible Disclosure

We appreciate security researchers who responsibly disclose vulnerabilities. We commit to:

1. **Acknowledgment**: Recognizing researchers who report vulnerabilities
2. **Transparency**: Providing updates on fix progress
3. **Credit**: Giving appropriate credit (if desired) when vulnerabilities are disclosed
4. **No Legal Action**: Not pursuing legal action against researchers who follow responsible disclosure

## Security Updates

Security updates will be:

- **Prioritized**: Critical security issues get immediate attention
- **Clearly Marked**: Security releases will be clearly identified
- **Well Documented**: Include details about what was fixed
- **Backward Compatible**: When possible, maintain compatibility

## Contact

For security-related questions or concerns:

- **General Security Questions**: Open a GitHub discussion
- **Vulnerability Reports**: Use private channels described above
- **Security Feature Requests**: Use GitHub issues with security label

Thank you for helping keep DoqToq secure!
