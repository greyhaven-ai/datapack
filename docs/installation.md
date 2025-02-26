# Installation

This guide covers how to install Datapack in your environment.

## Requirements

Before installing Datapack, make sure your system meets the following requirements:

- Python 3.8 or higher
- pip (Python package installer)
- Optional: virtualenv or conda for isolated environments (recommended)

## Basic Installation

The simplest way to install Datapack is using pip:

```bash
pip install datapack
```

This installs the core Datapack package with basic functionality.

## Installation with Extras

Datapack offers several "extras" packages for additional functionality:

### Available Extras

- **pdf**: Support for PDF document processing
- **docx**: Support for Microsoft Word document processing
- **html**: Enhanced HTML processing capabilities
- **nlp**: Natural language processing features
- **full**: All available extras

### Installing with Extras

To install Datapack with specific extras:

```bash
# Install with PDF support
pip install datapack[pdf]

# Install with Word document support
pip install datapack[docx]

# Install with multiple extras
pip install datapack[pdf,docx,html]

# Install with all extras
pip install datapack[full]
```

## Development Installation

If you're planning to contribute to Datapack or want the latest development version:

```bash
# Clone the repository
git clone https://github.com/greyhaven-ai/datapack.git
cd datapack

# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

## Using Virtual Environments

It's recommended to install Datapack in a virtual environment to avoid conflicts with other packages:

### Using venv (Python's built-in)

```bash
# Create a virtual environment
python -m venv datapack-env

# Activate the environment (Linux/macOS)
source datapack-env/bin/activate

# Activate the environment (Windows)
datapack-env\Scripts\activate

# Install Datapack
pip install datapack

# When finished, deactivate the environment
deactivate
```

### Using conda

```bash
# Create a conda environment
conda create -n datapack-env python=3.10

# Activate the environment
conda activate datapack-env

# Install Datapack
pip install datapack

# When finished, deactivate the environment
conda deactivate
```

## Verifying Installation

To verify that Datapack is installed correctly:

```bash
# Check the installed version
python -c "import datapack; print(datapack.__version__)"

# Verify CLI installation
datapack --version
```

## Docker Installation

Datapack can also be used with Docker:

```bash
# Pull the official Docker image
docker pull greyhaven/datapack:latest

# Run a container
docker run -it --rm greyhaven/datapack:latest

# Or with mounted volumes for document processing
docker run -it --rm -v $(pwd):/documents greyhaven/datapack:latest
```

## Platform-Specific Notes

### Windows

On Windows, you might need additional dependencies for certain features:

```bash
# For PDF support on Windows
pip install datapack[pdf]
pip install pdfminer.six
```

### macOS

On macOS, you might need to install additional system libraries:

```bash
# Using Homebrew
brew install poppler

# Then install Datapack
pip install datapack[pdf]
```

### Linux

On Linux, install required system dependencies:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3-dev poppler-utils libpoppler-cpp-dev

# Then install Datapack
pip install datapack[pdf]
```

## Troubleshooting

If you encounter issues during installation:

1. Make sure you have the latest pip version:
   ```bash
   pip install --upgrade pip
   ```

2. If you have permission issues:
   ```bash
   pip install --user datapack
   ```

3. If you encounter dependency conflicts, try using a virtual environment or:
   ```bash
   pip install --ignore-installed datapack
   ```

4. For platform-specific issues, check the [detailed troubleshooting guide](support/troubleshooting.md).

## Next Steps

Now that you have Datapack installed, you can:

- Follow the [Quick Start Guide](quick-start.md) to begin using Datapack
- Explore the [Core Concepts](concepts/index.md) to understand how Datapack works
- Try out the [Examples](examples/index.md) to see Datapack in action 