from setuptools import setup

setup(
    name='context-export',
    version='1.0.0',
    py_modules=['code_context_export'],
    entry_points={
        'console_scripts': [
            'context-export=code_context_export:main',
        ],
    },
    install_requires=[],
    python_requires='>=3.6',
    author='Your Name',
    author_email='your.email@example.com',
    description='Export codebase context to markdown for AI prompts',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/context-export',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
)