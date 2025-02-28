"""
Command-line interface for datapack.

This module provides the main CLI entry point for datapack.
"""

import sys
import argparse
from typing import Optional, List

from .converters import setup_parser as setup_converter_parser

# Check if AI support is available
try:
    from .ai import setup_parser as setup_ai_parser
    AI_SUPPORT = True
except ImportError:
    AI_SUPPORT = False


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for the datapack CLI.
    
    Args:
        args: Command-line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description='Datapack command-line tools',
        prog='datapack'
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Add convert command
    convert_parser = subparsers.add_parser(
        'convert',
        help='Convert files to MDP format'
    )
    setup_converter_parser(convert_parser)
    
    # Add AI commands if available
    if AI_SUPPORT:
        ai_parser = subparsers.add_parser(
            'ai',
            help='AI-powered document processing tools'
        )
        setup_ai_parser(ai_parser)
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Execute the appropriate command
    if parsed_args.command == 'convert':
        from .converters import main as convert_main
        return convert_main(args[1:] if args else None)
    elif parsed_args.command == 'ai' and AI_SUPPORT:
        from .ai import main as ai_main
        return ai_main(args[1:] if args else None)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main()) 