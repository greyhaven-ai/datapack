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

from datapack.mdp.document import Document
from datapack.mdp.collection import Collection
from datapack.mdp.converter import convert_to_html, convert_to_pdf
from datapack.mdp.utils import find_mdp_files
from datapack.workflows.dev import sync_codebase_docs, generate_api_docs
from datapack.workflows.releases import create_release_notes, generate_changelog
from datapack.workflows.content import batch_process_documents, merge_documents


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


if __name__ == "__main__":
    sys.exit(main()) 