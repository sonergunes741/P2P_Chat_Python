#!/usr/bin/env python3
"""
P2P Chat Application - GUI Version
===================================
Launch the graphical user interface for P2P Chat.

Usage:
    python gui_main.py [--port PORT]

Authors:
    - Soner Güneş (240104004201)
    - Ömer Faruk Olkay (210104004039)
    - Ahmet Baha Çepni (2101040040xx)
"""

import argparse
import sys


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="P2P Chat Application - GUI Version",
        formatter_class=argparse.RawDescriptionHelpFormatter
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
    
    return parser.parse_args()


def main() -> int:
    """Main entry point for GUI."""
    args = parse_arguments()
    
    try:
        # Import here to avoid circular imports
        from src.peer import Peer, get_local_ip
        from src.gui import P2PChatGUI
        
        # Create peer instance (without starting CLI)
        peer = Peer(
            tcp_port=args.port,
            broadcast_port=args.broadcast_port
        )
        
        # Create and run GUI
        gui = P2PChatGUI(peer)
        gui.run()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
