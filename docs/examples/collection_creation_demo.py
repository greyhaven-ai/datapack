#!/usr/bin/env python3
"""
Collection Creation Demo

This script demonstrates the use of the CollectionCreationAgent to organize
documents into collections and create parent documents that reference them.
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional
from datapack.ai.agents import CollectionCreationAgent
from datapack.ai.models import AIModelConfig, Collection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("collection_demo")


async def create_collection(
    input_paths: List[str],
    output_dir: str,
    collection_name: str = "Documents Collection",
    model: str = "gpt-4o",
    organization_strategy: str = "thematic"
) -> Collection:
    """
    Create a collection from a list of documents.
    
    Args:
        input_paths: List of paths to input documents
        output_dir: Directory to save the collection
        collection_name: Name for the collection
        model: AI model to use
        organization_strategy: Strategy for organizing documents
        
    Returns:
        The created collection
    """
    logger.info(f"Creating collection '{collection_name}' from {len(input_paths)} documents")
    
    # Resolve paths
    input_files = [Path(p) for p in input_paths]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Configure the AI model
    model_config = AIModelConfig(
        model=model,
        temperature=0.2
    )
    
    # Create the agent
    agent = CollectionCreationAgent(model_config=model_config)
    
    # Create the collection
    collection = await agent.create_collection_from_documents(
        documents=input_files,
        collection_name=collection_name,
        base_path=output_path,
        organization_strategy=organization_strategy,
        create_parent_document=True
    )
    
    logger.info(f"Collection created with {len(collection.documents)} documents")
    logger.info(f"Parent document: {collection.documents[0].path}")
    
    return collection


async def organize_by_theme(
    input_paths: List[str],
    output_dir: str,
    max_collections: int = 3,
    min_documents_per_collection: int = 2,
    model: str = "gpt-4o"
) -> List[Collection]:
    """
    Organize documents into thematic collections.
    
    Args:
        input_paths: List of paths to input documents
        output_dir: Directory to save the collections
        max_collections: Maximum number of collections to create
        min_documents_per_collection: Minimum documents per collection
        model: AI model to use
        
    Returns:
        List of created collections
    """
    logger.info(f"Organizing {len(input_paths)} documents into thematic collections")
    
    # Resolve paths
    input_files = [Path(p) for p in input_paths]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Configure the AI model
    model_config = AIModelConfig(
        model=model,
        temperature=0.3  # Slightly higher temperature for creative grouping
    )
    
    # Create the agent
    agent = CollectionCreationAgent(model_config=model_config)
    
    # Organize documents
    collections = await agent.organize_documents_by_theme(
        documents=input_files,
        base_path=output_path,
        max_collections=max_collections,
        min_documents_per_collection=min_documents_per_collection
    )
    
    logger.info(f"Created {len(collections)} thematic collections")
    for i, collection in enumerate(collections):
        logger.info(f"Collection {i+1}: '{collection.name}' with {len(collection.documents)} documents")
        logger.info(f"  Parent document: {collection.documents[0].path}")
    
    return collections


async def analyze_collection_relationships(
    collections_dir: str,
    output_file: Optional[str] = None,
    model: str = "gpt-4o"
) -> None:
    """
    Analyze relationships between collections and generate a report.
    
    Args:
        collections_dir: Directory containing collections
        output_file: File to save the relationship report
        model: AI model to use
    """
    logger.info(f"Analyzing relationships between collections in {collections_dir}")
    
    # Resolve paths
    collections_path = Path(collections_dir)
    
    # Configure the AI model
    model_config = AIModelConfig(
        model=model,
        temperature=0.1
    )
    
    # Create the agent
    agent = CollectionCreationAgent(model_config=model_config)
    
    # Find all parent documents (first document in each collection)
    parent_docs = list(collections_path.glob("*/*_parent.mdp"))
    
    logger.info(f"Found {len(parent_docs)} collection parent documents")
    
    # Analyze relationships between collections
    relationships = await agent.analyze_collection_relationships(parent_docs)
    
    # Generate report
    report = "# Collection Relationships Analysis\n\n"
    report += f"Analysis of {len(parent_docs)} collections\n\n"
    
    for relationship in relationships:
        report += f"## {relationship.type}\n\n"
        report += f"**{relationship.source}** → **{relationship.target}**\n\n"
        report += f"{relationship.description}\n\n"
        if relationship.confidence:
            report += f"Confidence: {relationship.confidence:.2f}\n\n"
    
    # Save or print report
    if output_file:
        output_path = Path(output_file)
        output_path.write_text(report)
        logger.info(f"Saved relationship report to {output_file}")
    else:
        print("\n" + report)


def main():
    """Parse arguments and execute the requested function."""
    parser = argparse.ArgumentParser(description="Document Collection Demo")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create collection command
    create_parser = subparsers.add_parser("create", help="Create a collection from documents")
    create_parser.add_argument("-i", "--input", nargs="+", required=True, help="Input documents")
    create_parser.add_argument("-o", "--output", required=True, help="Output directory")
    create_parser.add_argument("-n", "--name", default="Documents Collection", help="Collection name")
    create_parser.add_argument("-m", "--model", default="gpt-4o", help="AI model to use")
    create_parser.add_argument("-s", "--strategy", default="thematic", 
                             choices=["thematic", "chronological", "hierarchical"],
                             help="Organization strategy")
    
    # Organize by theme command
    organize_parser = subparsers.add_parser("organize", help="Organize documents by theme")
    organize_parser.add_argument("-i", "--input", nargs="+", required=True, help="Input documents")
    organize_parser.add_argument("-o", "--output", required=True, help="Output directory")
    organize_parser.add_argument("-m", "--model", default="gpt-4o", help="AI model to use")
    organize_parser.add_argument("--max-collections", type=int, default=3, help="Maximum number of collections")
    organize_parser.add_argument("--min-docs", type=int, default=2, help="Minimum documents per collection")
    
    # Analyze relationships command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze collection relationships")
    analyze_parser.add_argument("-d", "--dir", required=True, help="Collections directory")
    analyze_parser.add_argument("-o", "--output", help="Output file for relationship report")
    analyze_parser.add_argument("-m", "--model", default="gpt-4o", help="AI model to use")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute the requested command
    if args.command == "create":
        asyncio.run(create_collection(
            input_paths=args.input,
            output_dir=args.output,
            collection_name=args.name,
            model=args.model,
            organization_strategy=args.strategy
        ))
    elif args.command == "organize":
        asyncio.run(organize_by_theme(
            input_paths=args.input,
            output_dir=args.output,
            max_collections=args.max_collections,
            min_documents_per_collection=args.min_docs,
            model=args.model
        ))
    elif args.command == "analyze":
        asyncio.run(analyze_collection_relationships(
            collections_dir=args.dir,
            output_file=args.output,
            model=args.model
        ))
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 