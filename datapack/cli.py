"""
Command-line interface for Datapack utilities.

This module provides a CLI for working with MDP files, collections,
and workflows.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, List
import re

from mdp.document import Document
from mdp.collection import Collection
from mdp.converter import convert_to_html, convert_to_pdf
from mdp.utils import find_mdp_files
from datapack.workflows.dev import sync_codebase_docs, generate_api_docs
from datapack.workflows.releases import create_release_notes, generate_changelog
from datapack.workflows.content import batch_process_documents, merge_documents

# Check if AI support is available
try:
    from datapack.ai.models import AIModelConfig
    from datapack.ai.agents import CollectionCreationAgent
    AI_SUPPORT = True
except ImportError:
    AI_SUPPORT = False

def create_parser() -> argparse.ArgumentParser:
    """
    Create the command-line argument parser.
    
    Returns:
        An ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        description="MDP (Markdown Document Protocol) command-line tools",
        prog="mdp"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert MDP files to other formats")
    convert_parser.add_argument("input", help="Input file or directory")
    convert_parser.add_argument("--output", "-o", help="Output file or directory")
    convert_parser.add_argument("--format", "-f", choices=["html", "pdf"], default="html", 
                               help="Output format (default: html)")
    convert_parser.add_argument("--recursive", "-r", action="store_true", 
                               help="Process directories recursively")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show information about MDP files")
    info_parser.add_argument("file", help="MDP file to inspect")
    info_parser.add_argument("--metadata-only", "-m", action="store_true", 
                            help="Show only metadata")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new MDP document")
    create_parser.add_argument("output", help="Output file path")
    create_parser.add_argument("--title", "-t", help="Document title")
    create_parser.add_argument("--content", "-c", help="Document content (if not provided, open in editor)")
    create_parser.add_argument("--auto-metadata", "-a", action="store_true", 
                              help="Automatically generate metadata")
    
    # Collection commands
    collection_parser = subparsers.add_parser("collection", help="Work with MDP collections")
    collection_subparsers = collection_parser.add_subparsers(dest="subcmd")
    
    # Collection create
    coll_create = collection_subparsers.add_parser("create", help="Create a collection from MDP files")
    coll_create.add_argument("directory", help="Directory containing MDP files")
    coll_create.add_argument("output", help="Output collection file")
    coll_create.add_argument("--title", "-t", help="Collection title")
    coll_create.add_argument("--recursive", "-r", action="store_true", 
                           help="Process directories recursively")
    
    # Collection list
    coll_list = collection_subparsers.add_parser("list", help="List documents in a collection")
    coll_list.add_argument("collection", help="Collection file path")
    coll_list.add_argument("--format", "-f", choices=["text", "json"], default="text",
                         help="Output format (default: text)")
    
    # AI-powered collection commands (if AI support is available)
    if AI_SUPPORT:
        # AI-powered thematic organization
        coll_organize = collection_subparsers.add_parser(
            "organize-by-theme", 
            help="Organize documents into thematic collections using AI"
        )
        coll_organize.add_argument(
            "input_dir", 
            help="Directory containing documents to organize"
        )
        coll_organize.add_argument(
            "output_dir", 
            help="Directory to save the organized collections"
        )
        coll_organize.add_argument(
            "--max-collections", 
            type=int, 
            default=5,
            help="Maximum number of collections to create (default: 5)"
        )
        coll_organize.add_argument(
            "--min-documents", 
            type=int, 
            default=2,
            help="Minimum documents per collection (default: 2)"
        )
        coll_organize.add_argument(
            "--model", 
            default="gemini-1.5-flash",
            help="AI model to use for organization (default: gemini-1.5-flash)"
        )
        coll_organize.add_argument(
            "--no-parent-documents", 
            action="store_true",
            help="Skip creation of parent documents"
        )
        coll_organize.add_argument(
            "--recursive", 
            "-r", 
            action="store_true",
            help="Process input directory recursively"
        )
        
        # AI-powered collection analysis
        coll_analyze = collection_subparsers.add_parser(
            "analyze", 
            help="Analyze relationships between collections using AI"
        )
        coll_analyze.add_argument(
            "collections_dir", 
            help="Directory containing collections to analyze"
        )
        coll_analyze.add_argument(
            "--output", 
            "-o",
            help="Path to save the relationship analysis report"
        )
        coll_analyze.add_argument(
            "--model", 
            default="gemini-1.5-flash",
            help="AI model to use for analysis (default: gemini-1.5-flash)"
        )
    
    # Developer workflow commands
    dev_parser = subparsers.add_parser("dev", help="Developer workflows")
    dev_subparsers = dev_parser.add_subparsers(dest="subcmd")
    
    # Sync code docs
    sync_parser = dev_subparsers.add_parser("sync", help="Sync code documentation with MDP files")
    sync_parser.add_argument("code_dir", help="Code directory")
    sync_parser.add_argument("docs_dir", help="Documentation directory")
    sync_parser.add_argument("--patterns", "-p", nargs="+", default=["*.py", "*.js"],
                           help="File patterns to include (default: *.py *.js)")
    sync_parser.add_argument("--recursive", "-r", action="store_true", 
                           help="Process directories recursively")
    sync_parser.add_argument("--dry-run", "-d", action="store_true",
                           help="Don't write files, just show what would be done")
    
    # Generate API docs
    api_docs_parser = dev_subparsers.add_parser("api-docs", help="Generate API documentation")
    api_docs_parser.add_argument("code_dir", help="Code directory")
    api_docs_parser.add_argument("output", help="Output file path")
    api_docs_parser.add_argument("--module-name", "-m", required=True,
                               help="Module name for documentation")
    api_docs_parser.add_argument("--include", "-i", nargs="+", default=["*.py"],
                               help="File patterns to include (default: *.py)")
    api_docs_parser.add_argument("--exclude", "-e", nargs="+", 
                               default=["__pycache__", "*.pyc", "test_*", "*_test.py"],
                               help="File patterns to exclude")
    
    # Release workflow commands
    release_parser = subparsers.add_parser("release", help="Release workflows")
    release_subparsers = release_parser.add_subparsers(dest="subcmd")
    
    # Release notes
    notes_parser = release_subparsers.add_parser("notes", help="Generate release notes")
    notes_parser.add_argument("version", help="Version string (e.g., 1.0.0)")
    notes_parser.add_argument("output", help="Output file path")
    notes_parser.add_argument("--source-dir", "-s", help="Source directory for git operations")
    notes_parser.add_argument("--git-range", "-g", help="Git log range (e.g., v0.9.0..HEAD)")
    notes_parser.add_argument("--issue-tracker", "-i", help="Issue tracker URL")
    
    # Changelog
    changelog_parser = release_subparsers.add_parser("changelog", help="Generate changelog")
    changelog_parser.add_argument("output", help="Output file path")
    changelog_parser.add_argument("notes_dir", help="Directory containing release notes")
    changelog_parser.add_argument("--title", "-t", default="Changelog",
                                help="Changelog title (default: Changelog)")
    changelog_parser.add_argument("--max-versions", "-m", type=int,
                                help="Maximum number of versions to include")
    
    # Content workflow commands
    content_parser = subparsers.add_parser("content", help="Content workflows")
    content_subparsers = content_parser.add_subparsers(dest="subcmd")
    
    # Merge documents
    merge_parser = content_subparsers.add_parser("merge", help="Merge multiple documents")
    merge_parser.add_argument("files", nargs="+", help="MDP files to merge")
    merge_parser.add_argument("--output", "-o", required=True, help="Output file path")
    merge_parser.add_argument("--title", "-t", required=True, help="Title for merged document")
    merge_parser.add_argument("--include-metadata", "-m", action="store_true",
                            help="Include document metadata in output")
    
    # Document editing commands
    edit_parser = subparsers.add_parser("edit", help="Edit MDP document content")
    edit_parser.add_argument("file", help="MDP file to edit")
    edit_parser.add_argument("--content", "-c", required=True, help="New content to add or replace")
    edit_parser.add_argument("--output", "-o", help="Output file path (default: overwrite input file)")
    edit_parser.add_argument("--section", "-s", help="Section identifier to replace (e.g., '## Introduction')")
    edit_parser.add_argument("--replace-entire", "-r", action="store_true", help="Replace entire document content")
    edit_parser.add_argument("--append", "-a", action="store_true", help="Append content instead of replacing")
    edit_parser.add_argument("--track-changes", "-t", action="store_true", 
                           help="Track changes in metadata context field")
    edit_parser.add_argument("--change-summary", help="Custom summary of changes (used with --track-changes)")
    
    # Document context commands
    context_parser = subparsers.add_parser("add-context", help="Add context to MDP document")
    context_parser.add_argument("file", help="MDP file to add context to")
    context_parser.add_argument("--context", "-c", required=True, help="Context to add")
    context_parser.add_argument("--output", "-o", help="Output file path (default: overwrite input file)")
    context_parser.add_argument("--position", "-p", choices=["start", "end"], default="end", help="Where to add context")
    context_parser.add_argument("--section", "-s", help="Section to add context to (overrides position)")
    context_parser.add_argument("--as-comment", action="store_true", help="Format context as a Markdown comment")
    context_parser.add_argument("--track-changes", "-t", action="store_true", 
                              help="Track changes in metadata context field")
    context_parser.add_argument("--change-summary", help="Custom summary of changes (used with --track-changes)")
    
    # Document query commands
    query_parser = subparsers.add_parser("query", help="Query MDP document content")
    query_parser.add_argument("file", help="MDP file to query")
    query_parser.add_argument("--query", "-q", required=True, help="Query or question about the document")
    query_parser.add_argument("--section", "-s", help="Section to limit search to")
    query_parser.add_argument("--max-context", "-m", type=int, default=1000, help="Maximum context length to return")
    query_parser.add_argument("--use-ai", "-a", action="store_true", help="Use AI to enhance query results")
    
    # Collection modification commands
    collection_modify_parser = subparsers.add_parser("collection-modify", help="Modify a collection")
    collection_modify_parser.add_argument("collection", help="Collection file path")
    collection_modify_parser.add_argument("--action", "-a", choices=["add", "remove"], required=True, help="Action to perform")
    collection_modify_parser.add_argument("--documents", "-d", nargs="+", required=True, help="Documents to add or remove")
    collection_modify_parser.add_argument("--no-update-relationships", action="store_true", help="Skip updating relationships")
    collection_modify_parser.add_argument("--no-update-parent", action="store_true", help="Skip updating parent document")
    
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        args: Command-line arguments (if None, use sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = create_parser()
    
    if args is None:
        args = sys.argv[1:]
        
    parsed_args = parser.parse_args(args)
    
    # If no command specified, show help
    if not parsed_args.command:
        parser.print_help()
        return 0
    
    try:
        # Execute the requested command
        if parsed_args.command == "convert":
            _handle_convert(parsed_args)
        elif parsed_args.command == "info":
            _handle_info(parsed_args)
        elif parsed_args.command == "create":
            _handle_create(parsed_args)
        elif parsed_args.command == "collection":
            _handle_collection(parsed_args)
        elif parsed_args.command == "dev":
            _handle_dev(parsed_args)
        elif parsed_args.command == "release":
            _handle_release(parsed_args)
        elif parsed_args.command == "content":
            _handle_content(parsed_args)
        elif parsed_args.command == "edit":
            _handle_edit(parsed_args)
        elif parsed_args.command == "add-context":
            _handle_add_context(parsed_args)
        elif parsed_args.command == "query":
            _handle_query(parsed_args)
        elif parsed_args.command == "collection-modify":
            _handle_collection_modify(parsed_args)
        else:
            print(f"Unknown command: {parsed_args.command}")
            return 1
            
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1


def _handle_convert(args):
    """Handle the convert command."""
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Convert a single file
        if not args.output:
            # If no output specified, use input filename with new extension
            output = input_path.with_suffix(f".{args.format}")
        else:
            output = Path(args.output)
            
        if args.format == "html":
            convert_to_html(input_path, output)
        elif args.format == "pdf":
            convert_to_pdf(input_path, output)
            
        print(f"Converted {input_path} to {output}")
        
    elif input_path.is_dir():
        # Convert a directory
        if not args.output:
            # If no output specified, use input directory
            output_dir = input_path
        else:
            output_dir = Path(args.output)
            os.makedirs(output_dir, exist_ok=True)
            
        # Find MDP files
        mdp_files = find_mdp_files(input_path, recursive=args.recursive)
        
        for mdp_file in mdp_files:
            # Determine output path
            rel_path = mdp_file.relative_to(input_path)
            output_path = output_dir / rel_path.with_suffix(f".{args.format}")
            
            # Create output directory if needed
            os.makedirs(output_path.parent, exist_ok=True)
            
            # Convert the file
            if args.format == "html":
                convert_to_html(mdp_file, output_path)
            elif args.format == "pdf":
                convert_to_pdf(mdp_file, output_path)
                
            print(f"Converted {mdp_file} to {output_path}")
            
        print(f"Converted {len(mdp_files)} files")
    else:
        print(f"Error: {input_path} does not exist")


def _handle_info(args):
    """Handle the info command."""
    file_path = Path(args.file)
    
    try:
        doc = Document.from_file(file_path)
        
        if args.metadata_only:
            # Show only metadata
            print("Metadata:")
            for key, value in doc.metadata.items():
                print(f"  {key}: {value}")
        else:
            # Show document info
            print(f"File: {file_path}")
            print(f"Title: {doc.metadata.get('title', 'Untitled')}")
            print(f"UUID: {doc.metadata.get('uuid', 'None')}")
            print(f"Created: {doc.metadata.get('created_at', 'Unknown')}")
            print(f"Updated: {doc.metadata.get('updated_at', 'Unknown')}")
            print("\nMetadata:")
            for key, value in doc.metadata.items():
                if key not in ['title', 'uuid', 'created_at', 'updated_at']:
                    print(f"  {key}: {value}")
                    
            print(f"\nContent (first 5 lines):")
            lines = doc.content.splitlines()
            for i, line in enumerate(lines[:5]):
                print(f"  {line}")
                
            if len(lines) > 5:
                print("  ...")
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")


def _handle_create(args):
    """Handle the create command."""
    output_path = Path(args.output)
    
    # Ensure parent directory exists
    os.makedirs(output_path.parent, exist_ok=True)
    
    # Determine content
    content = args.content or ""
    
    if not content and not args.title:
        print("Error: Either --title or --content must be specified")
        return
        
    # Create title if not in content
    if args.title and not content.startswith("# "):
        content = f"# {args.title}\n\n{content}"
        
    # Create document
    if args.auto_metadata:
        doc = Document.create_with_auto_metadata(content=content)
    else:
        doc = Document(content=content)
        
    # Save document
    doc._mdp_file.path = output_path
    doc.save()
    
    print(f"Created document: {output_path}")


def _handle_collection(args):
    """Handle collection commands."""
    if not args.subcmd:
        print("Error: No collection subcommand specified")
        return
        
    if args.subcmd == "create":
        # Create a collection
        dir_path = Path(args.directory)
        output_path = Path(args.output)
        
        # Find MDP files
        mdp_files = find_mdp_files(dir_path, recursive=args.recursive)
        
        if not mdp_files:
            print(f"No MDP files found in {dir_path}")
            return
            
        # Create collection
        docs = [Document.from_file(path) for path in mdp_files]
        collection = Collection(
            documents=docs,
            title=args.title or f"Collection from {dir_path.name}"
        )
        
        # Save collection
        collection.save(output_path)
        
        print(f"Created collection with {len(docs)} documents: {output_path}")
        
    elif args.subcmd == "list":
        # List collection contents
        collection_path = Path(args.collection)
        
        try:
            collection = Collection.from_file(collection_path)
            
            if args.format == "json":
                import json
                result = {
                    "title": collection.title,
                    "documents": []
                }
                
                for doc in collection.documents:
                    result["documents"].append({
                        "title": doc.metadata.get("title", "Untitled"),
                        "uuid": doc.metadata.get("uuid", "Unknown"),
                        "created_at": doc.metadata.get("created_at", "Unknown"),
                        "updated_at": doc.metadata.get("updated_at", "Unknown")
                    })
                    
                print(json.dumps(result, indent=2))
                
            else:  # text format
                print(f"Collection: {collection.title}")
                print(f"Documents: {len(collection.documents)}")
                print("\nDocument List:")
                
                for i, doc in enumerate(collection.documents, 1):
                    title = doc.metadata.get("title", "Untitled")
                    uuid = doc.metadata.get("uuid", "Unknown")
                    print(f"{i}. {title} (UUID: {uuid})")
                    
        except Exception as e:
            print(f"Error reading collection {collection_path}: {e}")
    
    elif args.subcmd == "organize-by-theme" and AI_SUPPORT:
        # Import required modules locally
        import asyncio
        from pathlib import Path
        
        # Find all documents in the input directory
        input_dir = Path(args.input_dir)
        if not input_dir.is_dir():
            print(f"Error: {input_dir} is not a directory")
            return
            
        # Find document files
        input_files = []
        if args.recursive:
            for ext in [".mdp", ".md", ".txt"]:
                input_files.extend(list(input_dir.glob(f"**/*{ext}")))
        else:
            for ext in [".mdp", ".md", ".txt"]:
                input_files.extend(list(input_dir.glob(f"*{ext}")))
                
        if not input_files:
            print(f"Error: No document files found in {input_dir}")
            return
            
        # Configure the AI model
        model_config = AIModelConfig(
            model=args.model,
            temperature=0.3
        )
        
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create the collection agent
        agent = CollectionCreationAgent(model_config=model_config)
        
        # Run asynchronously
        async def organize_docs():
            # Organize documents
            collections = await agent.organize_documents_by_theme(
                documents=input_files,
                base_path=output_dir,
                max_collections=args.max_collections,
                min_documents_per_collection=args.min_documents,
                create_parent_documents=not args.no_parent_documents,
                save_documents=True
            )
            return collections
            
        # Run the async function
        try:
            collections = asyncio.run(organize_docs())
            
            print(f"Created {len(collections)} thematic collections")
            print(f"Collections saved to: {output_dir}")
            
            for i, collection in enumerate(collections):
                print(f"Collection {i+1}: '{collection.name}' with {len(collection.documents)} documents")
                if not args.no_parent_documents:
                    print(f"  Parent document: {collection.documents[0].path}")
                    
        except Exception as e:
            print(f"Error organizing documents: {e}")
            return
            
    elif args.subcmd == "analyze" and AI_SUPPORT:
        # Import required modules locally
        import asyncio
        from pathlib import Path
        
        # Resolve the collections directory
        collections_dir = Path(args.collections_dir)
        if not collections_dir.is_dir():
            print(f"Error: {collections_dir} is not a directory")
            return
            
        # Find all parent documents (first document in each collection)
        parent_docs = list(collections_dir.glob("*/*_parent.mdp"))
        if not parent_docs:
            print(f"Error: No collection parent documents found in {collections_dir}")
            return
            
        # Configure the AI model
        model_config = AIModelConfig(
            model=args.model,
            temperature=0.1
        )
        
        # Create the collection agent
        agent = CollectionCreationAgent(model_config=model_config)
        
        # Run asynchronously
        async def analyze_collections():
            # Analyze relationships between collections
            relationships = await agent.analyze_collection_relationships(parent_docs)
            return relationships
            
        # Run the async function
        try:
            relationships = asyncio.run(analyze_collections())
            
            # Generate relationship report
            report = "# Collection Relationships Analysis\n\n"
            report += f"Analysis of {len(parent_docs)} collections\n\n"
            
            for relationship in relationships:
                report += f"## {relationship.type}\n\n"
                report += f"**{relationship.source}** → **{relationship.target}**\n\n"
                report += f"{relationship.description}\n\n"
                if relationship.confidence:
                    report += f"Confidence: {relationship.confidence:.2f}\n\n"
            
            # Save or print report
            if args.output:
                output_path = Path(args.output)
                output_path.write_text(report)
                print(f"Analyzed {len(parent_docs)} collections")
                print(f"Found {len(relationships)} relationships")
                print(f"Saved relationship analysis to {args.output}")
            else:
                print("\nCollection Relationships Analysis")
                print("================================\n")
                print(f"Analyzed {len(parent_docs)} collections")
                print(f"Found {len(relationships)} relationships\n")
                print(report)
                
        except Exception as e:
            print(f"Error analyzing collections: {e}")
            return
    else:
        print(f"Error: Unknown collection subcommand: {args.subcmd}")


def _handle_dev(args):
    """Handle developer workflow commands."""
    if not args.subcmd:
        print("Error: No dev subcommand specified")
        return
        
    if args.subcmd == "sync":
        # Sync code documentation
        code_dir = Path(args.code_dir)
        docs_dir = Path(args.docs_dir)
        
        updated_docs = sync_codebase_docs(
            code_directory=code_dir,
            docs_directory=docs_dir,
            file_patterns=args.patterns,
            recursive=args.recursive,
            dry_run=args.dry_run
        )
        
        action = "Would update" if args.dry_run else "Updated"
        print(f"{action} {len(updated_docs)} documentation files")
        
    elif args.subcmd == "api-docs":
        # Generate API docs
        code_dir = Path(args.code_dir)
        output_file = Path(args.output)
        
        doc = generate_api_docs(
            code_directory=code_dir,
            output_file=output_file,
            module_name=args.module_name,
            include_patterns=args.include,
            exclude_patterns=args.exclude
        )
        
        print(f"Generated API documentation: {output_file}")


def _handle_release(args):
    """Handle release workflow commands."""
    if not args.subcmd:
        print("Error: No release subcommand specified")
        return
        
    if args.subcmd == "notes":
        # Generate release notes
        output_file = Path(args.output)
        
        doc = create_release_notes(
            version=args.version,
            output_file=output_file,
            issue_tracker_url=args.issue_tracker,
            source_directory=args.source_dir,
            git_log_range=args.git_range
        )
        
        print(f"Generated release notes: {output_file}")
        
    elif args.subcmd == "changelog":
        # Generate changelog
        output_file = Path(args.output)
        notes_dir = Path(args.notes_dir)
        
        doc = generate_changelog(
            output_file=output_file,
            release_notes_dir=notes_dir,
            title=args.title,
            max_versions=args.max_versions
        )
        
        print(f"Generated changelog: {output_file}")


def _handle_content(args):
    """Handle content workflow commands."""
    if not args.subcmd:
        print("Error: No content subcommand specified")
        return
        
    if args.subcmd == "merge":
        # Merge documents
        output_file = Path(args.output)
        
        # Load documents
        docs = []
        for file_path in args.files:
            try:
                doc = Document.from_file(file_path)
                docs.append(doc)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        if not docs:
            print("No valid documents to merge")
            return
            
        merged_doc = merge_documents(
            docs=docs,
            output_path=output_file,
            title=args.title,
            include_metadata=args.include_metadata
        )
        
        print(f"Merged {len(docs)} documents into: {output_file}")


def _handle_edit(args):
    """Handle the edit command."""
    file_path = Path(args.file)
    
    try:
        # Load the document
        doc = Document.from_file(file_path)
        
        # Determine output path
        output_path = Path(args.output) if args.output else file_path
        
        # Get current content
        current_content = doc.content
        
        # Store the action description for potential metadata update
        action_description = ""
        
        # Update content based on arguments
        if args.section:
            # Find the specified section
            section_start = current_content.find(args.section)
            if section_start == -1:
                print(f"Error: Section '{args.section}' not found in document")
                return
                
            # Look for the next header at the same level or higher
            header_level = args.section.count('#')
            pattern = r'\n#{1,' + str(header_level) + r'}\s+[^\n]+'
            
            next_matches = list(re.finditer(pattern, current_content[section_start:]))
            if next_matches:
                section_end = section_start + next_matches[0].start()
                # Replace just this section (including its header)
                new_content = (
                    current_content[:section_start] + 
                    args.section + '\n\n' + args.content + '\n\n' +
                    current_content[section_end:]
                )
                action_description = f"Updated section '{args.section}'"
                print(f"Replaced section '{args.section}'")
            else:
                # This is the last section, replace to the end
                new_content = (
                    current_content[:section_start] + 
                    args.section + '\n\n' + args.content
                )
                action_description = f"Updated section '{args.section}' to end of document"
                print(f"Replaced section '{args.section}' to end of document")
        elif args.replace_entire:
            # Replace the entire content
            new_content = args.content
            action_description = "Replaced entire document content"
            print("Replaced entire document content")
        elif args.append:
            # Append to the existing content
            new_content = current_content + "\n\n" + args.content
            action_description = "Appended content to document"
            print("Appended content to document")
        else:
            # Default to replacing entire content
            new_content = args.content
            action_description = "Replaced document content"
            print("Replaced document content")
        
        # Update the document with the new content
        doc.content = new_content
        
        # Update metadata context field if requested
        if args.track_changes:
            # Get the current context field or initialize it
            context_field = doc.metadata.get("context", "")
            
            # Get current date in ISO format
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Format the change entry
            change_summary = args.change_summary if args.change_summary else action_description
            change_entry = f"\n\n[{current_date}] {change_summary}"
            
            # Append to the context field
            if context_field:
                doc.metadata["context"] = context_field + change_entry
            else:
                doc.metadata["context"] = f"Document history:\n{change_entry.lstrip()}"
            
            print(f"Updated metadata context field with change information")
        
        # Save the document
        doc.save(output_path)
        
        print(f"Saved document to {output_path}")
        print(f"Original length: {len(current_content)} characters")
        print(f"New length: {len(new_content)} characters")
        print(f"Difference: {len(new_content) - len(current_content)} characters")
        
    except Exception as e:
        print(f"Error editing document {file_path}: {e}")


def _handle_add_context(args):
    """Handle the add-context command."""
    file_path = Path(args.file)
    
    try:
        # Load the document
        doc = Document.from_file(file_path)
        
        # Determine output path
        output_path = Path(args.output) if args.output else file_path
        
        # Get current content
        current_content = doc.content
        
        # Format the context if needed
        if args.as_comment:
            formatted_context = f"<!-- {args.context} -->\n\n"
        else:
            formatted_context = f"{args.context}\n\n"
        
        # Store the action description for potential metadata update
        action_description = ""
        
        # Determine where to add the context
        if args.section:
            # Find the specified section
            section_pos = current_content.find(args.section)
            if section_pos == -1:
                print(f"Error: Section '{args.section}' not found in document")
                return
                
            # Find the end of the section header line
            line_end = current_content.find('\n', section_pos)
            if line_end >= 0:
                # Insert after the section header
                new_content = (
                    current_content[:line_end + 1] + 
                    "\n" + formatted_context +
                    current_content[line_end + 1:]
                )
                action_description = f"Added context to section '{args.section}'"
                print(f"Added context to section '{args.section}'")
            else:
                # If no line end found, append to the end
                new_content = current_content + "\n\n" + formatted_context
                action_description = "Added context to the end of the document"
                print("Added context to the end of the document")
        elif args.position == "start":
            # Add at the start
            new_content = formatted_context + current_content
            action_description = "Added context to the start of the document"
            print("Added context to the start of the document")
        else:
            # Add at the end
            new_content = current_content + "\n\n" + formatted_context
            action_description = "Added context to the end of the document"
            print("Added context to the end of the document")
        
        # Update the document with the new content
        doc.content = new_content
        
        # Update metadata context field if requested
        if args.track_changes:
            # Get the current context field or initialize it
            context_field = doc.metadata.get("context", "")
            
            # Get current date in ISO format
            from datetime import datetime
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # Format the change entry
            change_summary = args.change_summary if args.change_summary else action_description
            change_entry = f"\n\n[{current_date}] {change_summary}"
            
            # Prepare a snippet of the added content (truncated if too long)
            content_snippet = args.context
            if len(content_snippet) > 50:
                content_snippet = content_snippet[:47] + "..."
            
            # Append to the context field with content snippet
            if context_field:
                doc.metadata["context"] = context_field + change_entry + f" - {content_snippet}"
            else:
                doc.metadata["context"] = f"Document history:\n{change_entry.lstrip()} - {content_snippet}"
            
            print(f"Updated metadata context field with change information")
        
        # Save the document
        doc.save(output_path)
        
        print(f"Saved document to {output_path}")
        print(f"Added {len(formatted_context)} characters of context")
        print(f"New document length: {len(new_content)} characters")
        
    except Exception as e:
        print(f"Error adding context to document {file_path}: {e}")


def _handle_query(args):
    """Handle the query command."""
    file_path = Path(args.file)
    
    try:
        # Load the document
        doc = Document.from_file(file_path)
        
        # Get document content
        content = doc.content
        
        # If section specified, extract only that section
        if args.section:
            section_start = content.find(args.section)
            if section_start == -1:
                print(f"Error: Section '{args.section}' not found in document")
                return
                
            # Find the next section header
            header_level = args.section.count('#')
            pattern = r'\n#{1,' + str(header_level) + r'}\s+[^\n]+'
            
            next_matches = list(re.finditer(pattern, content[section_start:]))
            if next_matches:
                section_end = section_start + next_matches[0].start()
                search_content = content[section_start:section_end]
            else:
                # This is the last section
                search_content = content[section_start:]
        else:
            search_content = content
        
        # If AI is requested, use the AI query function
        if args.use_ai and AI_SUPPORT:
            # Import AI functionality
            from datapack.cli.ai import query_document_content
            import asyncio
            
            # Run the AI query
            result = asyncio.run(query_document_content(
                input_path=str(file_path),
                query=args.query,
                section=args.section,
                max_context_length=args.max_context
            ))
            
            # Display results
            print(f"\nQuery: {result['query']}")
            print(f"Document: {result['document_title']}")
            if args.section:
                print(f"Section: {args.section}")
            print(f"Relevance score: {result['relevance_score']:.2f}")
            print("\nRelevant context:")
            print("-" * 40)
            print(result['context'])
            print("-" * 40)
            
        else:
            # Simple search implementation
            query_terms = args.query.lower().split()
            content_lower = search_content.lower()
            
            # Check for direct matches of the query
            direct_match = args.query.lower() in content_lower
            if direct_match:
                # Find the match position and extract surrounding context
                match_pos = content_lower.find(args.query.lower())
                
                # Get surrounding context
                start_pos = max(0, match_pos - args.max_context // 2)
                end_pos = min(len(search_content), match_pos + len(args.query) + args.max_context // 2)
                
                # Try to extend to paragraph boundaries
                while start_pos > 0 and search_content[start_pos] != '\n':
                    start_pos -= 1
                    
                while end_pos < len(search_content) and search_content[end_pos] != '\n':
                    end_pos += 1
                    
                # Extract the context
                context = search_content[start_pos:end_pos].strip()
                
                print(f"\nQuery: {args.query}")
                print(f"Document: {doc.title}")
                if args.section:
                    print(f"Section: {args.section}")
                print("\nRelevant context:")
                print("-" * 40)
                print(context)
                print("-" * 40)
            else:
                # Count term matches as a fallback
                term_matches = sum(1 for term in query_terms if term in content_lower)
                if term_matches > 0:
                    # Extract a relevant section based on term density
                    paragraphs = search_content.split('\n\n')
                    scored_paragraphs = []
                    
                    for para in paragraphs:
                        para_lower = para.lower()
                        score = sum(1 for term in query_terms if term in para_lower) / len(para)
                        scored_paragraphs.append((score, para))
                        
                    # Get best paragraph
                    scored_paragraphs.sort(reverse=True)
                    if scored_paragraphs:
                        context = scored_paragraphs[0][1]
                        if len(context) > args.max_context:
                            context = context[:args.max_context] + "..."
                            
                        print(f"\nQuery: {args.query}")
                        print(f"Document: {doc.title}")
                        if args.section:
                            print(f"Section: {args.section}")
                        print("\nRelevant context:")
                        print("-" * 40)
                        print(context)
                        print("-" * 40)
                    else:
                        print(f"No relevant content found for query: {args.query}")
                else:
                    print(f"No relevant content found for query: {args.query}")
        
    except Exception as e:
        print(f"Error querying document {file_path}: {e}")


def _handle_collection_modify(args):
    """Handle the collection-modify command."""
    collection_path = Path(args.collection)
    
    try:
        # Check if AI support is available
        if AI_SUPPORT:
            # Import AI functionality
            from datapack.cli.ai import modify_collection_documents
            import asyncio
            
            # Run the collection modification
            result = asyncio.run(modify_collection_documents(
                collection_path=str(collection_path),
                action=args.action,
                document_paths=args.documents,
                update_relationships=not args.no_update_relationships,
                update_parent_document=not args.no_update_parent
            ))
            
            # Display results
            print(f"Modified collection {collection_path}")
            print(f"Action: {result['action']}")
            print(f"Initial document count: {result['initial_document_count']}")
            print(f"Final document count: {result['final_document_count']}")
            print(f"Documents processed: {result['processed_count']}")
            
            if result.get('failed_paths'):
                print("\nFailed paths:")
                for fail in result['failed_paths']:
                    print(f"  - {fail['path']}: {fail['reason']}")
            
            if result.get('parent_document_updated'):
                print(f"\nUpdated parent document: {result['parent_document_updated']}")
                
        else:
            # Load the collection
            collection = Collection.from_file(collection_path)
            
            # Process based on action
            if args.action == "add":
                # Add documents to collection
                added_count = 0
                failed_paths = []
                
                for doc_path in args.documents:
                    try:
                        doc = Document.from_file(doc_path)
                        collection.add_document(doc)
                        added_count += 1
                    except Exception as e:
                        failed_paths.append((doc_path, str(e)))
                
                # Save the collection
                collection.save()
                
                print(f"Added {added_count} documents to collection {collection_path}")
                print(f"Collection now contains {len(collection.documents)} documents")
                
                if failed_paths:
                    print("\nFailed paths:")
                    for path, reason in failed_paths:
                        print(f"  - {path}: {reason}")
                    
            elif args.action == "remove":
                # Remove documents from collection
                removed_count = 0
                failed_paths = []
                
                for doc_path in args.documents:
                    # Find document by path
                    doc_to_remove = None
                    for doc in collection.documents:
                        if doc.path and str(doc.path) == doc_path:
                            doc_to_remove = doc
                            break
                    
                    if doc_to_remove:
                        collection.remove_document(doc_to_remove.id)
                        removed_count += 1
                    else:
                        failed_paths.append((doc_path, "Document not found in collection"))
                
                # Save the collection
                collection.save()
                
                print(f"Removed {removed_count} documents from collection {collection_path}")
                print(f"Collection now contains {len(collection.documents)} documents")
                
                if failed_paths:
                    print("\nFailed paths:")
                    for path, reason in failed_paths:
                        print(f"  - {path}: {reason}")
            
    except Exception as e:
        print(f"Error modifying collection {collection_path}: {e}")


if __name__ == "__main__":
    sys.exit(main()) 