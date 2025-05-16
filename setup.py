#!/usr/bin/env python3
"""
Setup script for Code Context Exporter
"""

import os
from setuptools import setup, find_packages

current_dir = os.path.dirname(os.path.abspath(__file__))

# Long description directly from README
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ctxport",
    version="0.3.0",
    author="Coray Bennett",
    author_email="cob3218@rit.edu",
    description="Export codebase context to markdown for AI prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Coray-Bennett/ctxport",
    project_urls={
        "Bug Tracker": "https://github.com/Coray-Bennett/ctxport/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
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