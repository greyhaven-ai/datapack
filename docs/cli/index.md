# Command Line Interface

Datapack provides a powerful Command Line Interface (CLI) that allows you to work with documents directly from your terminal. This guide provides an overview of the available commands and how to use them.

## Installation

The CLI is automatically installed when you install Datapack:

```bash
pip install datapack
```

To verify that the CLI is installed correctly, run:

```bash
datapack --version
```

## Basic Usage

The basic syntax for the CLI is:

```bash
datapack [command] [options]
```

To see a list of available commands:

```bash
datapack --help
```

## Available Commands

Here's a summary of the main commands available in the Datapack CLI:

| Command | Description |
|---------|-------------|
| `create` | Create a new document |
| `info` | Display information about a document |
| `convert` | Convert a document to another format |
| `edit` | Edit a document's content or metadata |
| `list` | List documents in a directory |
| `diff` | Compare two documents |
| `validate` | Validate a document against a schema |
| `search` | Search for documents by content or metadata |

## Command Usage and Examples

### Creating Documents

Create a new document:

```bash
# Create a blank document
datapack create --output new_document.mdp

# Create a document with title and author
datapack create --title "My Document" --author "John Doe" --output new_document.mdp

# Create a document with content from a file
datapack create --content-file source.md --output new_document.mdp

# Create a document with tags
datapack create --title "Tagged Document" --tags "example,documentation,cli" --output tagged_document.mdp
```

### Getting Document Information

View information about a document:

```bash
# View basic info
datapack info document.mdp

# View detailed info
datapack info document.mdp --detailed

# Output in JSON format
datapack info document.mdp --format json

# Focus on specific metadata fields
datapack info document.mdp --fields "title,author,version,tags"
```

### Converting Documents

Convert documents between formats:

```bash
# Convert MDP to Markdown
datapack convert document.mdp --output document.md --format markdown

# Convert MDP to HTML
datapack convert document.mdp --output document.html --format html

# Convert external format to MDP
datapack convert document.md --output document.mdp --format mdp

# Convert with a specific template
datapack convert document.mdp --output document.html --format html --template custom_template.html
```

### Editing Documents

Edit document content or metadata:

```bash
# Open document in default editor
datapack edit document.mdp

# Update specific metadata fields
datapack edit document.mdp --set-metadata "title=Updated Title,version=1.1.0"

# Add tags
datapack edit document.mdp --add-tags "updated,edited"

# Remove tags
datapack edit document.mdp --remove-tags "draft"
```

### Working with Multiple Documents

Manage multiple documents:

```bash
# List all MDP documents in a directory
datapack list ./documents/

# List documents with specific tags
datapack list ./documents/ --filter-tags "important"

# Merge multiple documents
datapack merge doc1.mdp doc2.mdp --output merged.mdp

# Compare two documents
datapack diff original.mdp updated.mdp
```

### Validation

Validate documents against schemas:

```bash
# Basic validation
datapack validate document.mdp

# Validate against a specific schema
datapack validate document.mdp --schema schema.json

# Validate a directory of documents
datapack validate ./documents/ --recursive
```

## Advanced Usage

### Piping and Redirection

The CLI works well with Unix pipes and redirection:

```bash
# Create a document from piped content
echo "# Hello World" | datapack create --output hello.mdp

# Pipe document content to another command
datapack info document.mdp --content-only | grep "Important"

# Redirect output to a file
datapack info document.mdp --format json > document_info.json
```

### Scripts and Automation

The CLI is designed to be used in scripts and automation:

```bash
# Process multiple documents
for file in *.md; do
  datapack convert "$file" --output "${file%.md}.mdp" --format mdp
done

# Extract specific metadata from all documents
for file in *.mdp; do
  echo -n "$file: "
  datapack info "$file" --fields "title" --format csv
done
```

## Configuration

You can configure default behavior in a configuration file:

```bash
# Create a config file with defaults
datapack config init

# Set a default output format
datapack config set default_format html

# View current configuration
datapack config show
```

The configuration file is located at `~/.datapack/config.yml` by default.

## Next Steps

To learn more about specific CLI commands, see:

- [Document Commands](document-commands.md): Commands for working with individual documents
- [Utility Commands](utility-commands.md): Additional utility commands for various tasks

For a complete reference of all CLI options and arguments, run:

```bash
datapack [command] --help
``` 