#!/usr/bin/env python3
"""
P2P Chat Application
====================
Entry point for the peer-to-peer chat application.

Usage:
    python main.py [--port PORT] [--broadcast-port PORT]

Authors:
    - Soner Güneş (240104004201)
    - Ömer Faruk Olkay (210104004039)
"""

import argparse
import sys

from src.peer import Peer


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="P2P Chat Application - Chat without a central server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py                     # Start with default ports
    python main.py --port 5000         # Use custom TCP port
    python main.py --port 5001         # Second instance on same machine
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=5000,
        help='TCP port for peer connections (default: 5000)'
    )
    
    parser.add_argument(
        '--broadcast-port', '-b',
        type=int,
        default=5001,
        help='UDP port for peer discovery (default: 5001)'
    )
    
    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )
    
    return parser.parse_args()


def main() -> int:
    """Main entry point."""
    args = parse_arguments()
    
    # Enable debug logging if requested
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create and start the peer
        peer = Peer(
            tcp_port=args.port,
            broadcast_port=args.broadcast_port
        )
        peer.start()
        return 0
        
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
