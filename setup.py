"""
Setup script for the datapack package.
"""

from setuptools import setup, find_packages
import os

# Read the long description from README.md
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

# Get version from a VERSION file, or hardcode it if not available
if os.path.exists('VERSION'):
    with open('VERSION') as f:
        version = f.read().strip()
else:
    version = '0.1.0'  # Default version

# Define extra dependencies
extras_require = {
    # AI capabilities with PydanticAI
    'ai': [
        'pydantic>=2.4.0',
        'pydanticai>=0.1.0',
        'rich>=13.0.0',
        'python-dotenv>=1.0.0',
    ],
    # Optional LLM providers (one is required for AI functionality)
    'openai': ['openai>=1.1.0'],
    'anthropic': ['anthropic>=0.5.0'],
    'cohere': ['cohere-ai>=4.0.0'],
    'nvidia': ['nvidia-modulus-client>=0.1.0'],
    'local': ['local-llm>=0.1.0'],  # Placeholder for local model support
    # All AI capabilities with OpenAI as the provider
    'ai-openai': [
        'pydantic>=2.4.0',
        'pydanticai>=0.1.0',
        'openai>=1.1.0',
        'rich>=13.0.0',
        'python-dotenv>=1.0.0',
    ],
    # Development tools
    'dev': [
        'pytest>=7.0.0',
        'black>=22.0.0',
        'flake8>=5.0.0',
        'mypy>=1.0.0',
        'sphinx>=5.0.0',
    ],
}

setup(
    name="datapack",
    version=version,
    author="Datapack Team",
    author_email="info@datapack.org",
    description="A platform for document ingestion, parsing, annotation, and secure sharing across software ecosystems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/datapack",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyyaml>=6.0",
        "markdown>=3.4.0",
        "python-frontmatter>=1.0.0",
        "jinja2>=3.1.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "weasyprint>=59.0",
        "beautifulsoup4>=4.12.0",
        "requests>=2.28.0",
        "uuid>=1.30",
        "mcp>=1.3.0",  # Model Context Protocol SDK
    ],
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'mdp=datapack.cli:main',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU Affero General Public License v3.0 (AGPL-3.0)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Documentation",
        "Topic :: Software Development :: Documentation",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.8",
) 