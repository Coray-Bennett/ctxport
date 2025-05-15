#!/usr/bin/env python3
"""
Setup script for Code Context Exporter
"""

import os
from setuptools import setup, find_packages

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Read the README.md file
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="code-context-export",
    version="0.3.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Export codebase context to markdown for AI prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/code-context-export",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/code-context-export/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        # "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ctxport=ctxport:main",
        ],
    },
)