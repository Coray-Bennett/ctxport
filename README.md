# Code Context Exporter

Export your codebase context to markdown format for use with AI prompts. This tool helps you quickly grab relevant code context and either copy it to your clipboard or save it to a file.

## Installation

install from source:

```bash
git clone https://github.com/Coray-Bennett/ctxport.git
cd code-context-export
pip install .
```

## Usage

### Basic usage (copies to clipboard):
```bash
ctxport
```

### Export a specific directory:
```bash
ctxport <directory>
```

### Save to a file:
```bash
ctxport -o context.md
```

### Verbose output:
```bash
ctxport -v
```

### Debug mode:
```bash
ctxport --debug
```

### Initialize configuration:
```bash
# Create a local config file in current directory
ctxport --init-config

# Create a global config file
ctxport --init-global-config
```

## Configuration

The tool uses a flexible configuration system that allows you to customize file extensions, language mappings, and ignore patterns.

### Configuration Files

1. **Default Configuration**: Built-in defaults
2. **Global Configuration**: User-level settings
   - `~/.config/ctxport/ctxport.json` (Linux/macOS with XDG)
   - `~/.ctxport.json` (fallback)
3. **Directory Configuration**: Project-specific settings
   - `.ctxport.json` in any parent directory

Configuration files are merged in order, with later configurations overriding earlier ones.

### Configuration Format

Configuration files use JSON format:

```json
{
  "language_map": {
    ".custom": "custom-language",
    ".myext": "mylang"
  },
  "filename_map": {
    "makefile": "makefile",
    "dockerfile": "dockerfile",
    "jenkinsfile": "groovy"
  },
  "text_extensions": [
    ".custom",
    ".myext",
    ".conf"
  ],
  "ignore_patterns": [
    "*.log",
    "temp/",
    "*.tmp"
  ],
  "default_language": "text"
}
```

### Configuration Options

1. **language_map**: Maps file extensions to language identifiers for syntax highlighting
   - Key: file extension (including the dot)
   - Value: language identifier for markdown code blocks

2. **filename_map**: Maps specific filenames to language identifiers
   - Key: filename (case-insensitive)
   - Value: language identifier for markdown code blocks
   - Useful for files without extensions (Makefile, Dockerfile, etc.)

3. **text_extensions**: Set of file extensions to treat as text files
   - List of extensions (including the dot)
   - Files with these extensions will be included in the export

4. **ignore_patterns**: Patterns for files and directories to exclude
   - Supports glob patterns
   - Directory patterns should end with `/`

5. **default_language**: Default language to use when no mapping is found
   - Empty string results in no syntax highlighting

### Example Configurations

Create a project-specific configuration:

### Separate Ignore Files

The tool also supports a `context.ignore` file format. If a `context.ignore` file exists, its patterns will be merged with configuration ignore patterns.

## Ignore Patterns

You can exclude files and directories using ignore patterns:

1. Create a `.ctxport.json` file with ignore patterns
2. Or use a `context.ignore` file (legacy method)

Example `.ctxport.json`:
```json
{
  "ignore_patterns": [
    "node_modules/",
    "*.pyc",
    "__pycache__/",
    ".git/",
    ".venv/",
    "dist/",
    "build/"
  ]
}
```

Example `context.ignore`:
```
# Dependencies
node_modules/
vendor/

# Build outputs
dist/
build/
*.pyc
__pycache__/

# Version control
.git/
.svn/

# IDEs
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db
```

## Output Format

The tool generates markdown with:
- A header with the project name
- Each file in a section with its relative path
- Code blocks with appropriate syntax highlighting

Example output:
```markdown
# Code Context Export: my-project

## src/main.py

```python
def main():
    print("Hello, world!")

if __name__ == "__main__":
    main()
```
```