#!/usr/bin/env python3
"""
DoqToq - Documents that talk
Setup script for PyPI distribution
"""

import os
import re
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Read requirements
def read_requirements(filename):
    with open(filename, "r") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]

# Extract version from __init__.py
def get_version():
    version_file = os.path.join("backend", "__init__.py")
    if os.path.exists(version_file):
        with open(version_file, "r") as f:
            content = f.read()
            version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', content, re.M)
            if version_match:
                return version_match.group(1)
    return "0.1.0"  # fallback version

requirements = read_requirements("requirements.txt")
dev_requirements = read_requirements("requirements-dev.txt")

setup(
    name="doqtoq",
    version=get_version(),
    author="Shreyas Bangera",
    author_email="shreyasdb99@gmail.com",
    description="Transform your documents into intelligent conversational partners",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shre-db/doqtoq",
    project_urls={
        "Bug Reports": "https://github.com/shre-db/doqtoq/issues",
        "Source": "https://github.com/shre-db/doqtoq",
        "Documentation": "https://github.com/shre-db/doqtoq/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Streamlit",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.11.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "doqtoq=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yaml", "*.yml"],
        "assets": ["*.svg", "*.png"],
        "backend.prompts": ["*.md"],
    },
    keywords=[
        "ai",
        "rag",
        "retrieval-augmented-generation",
        "document-qa",
        "chatbot",
        "nlp",
        "langchain",
        "streamlit",
        "conversational-ai",
        "document-analysis",
    ],
    zip_safe=False,
)
