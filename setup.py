from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="code-context-export",
    version="0.2.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Export codebase context to markdown for AI prompts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/code-context-export",
    packages=find_packages(),
    py_modules=['code_context_export', 'config'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "ctxport=code_context_export:main",
        ],
    },
)