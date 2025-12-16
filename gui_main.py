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
        from src.startup_dialog import StartupDialog
        
        # 1. Launch Startup Dialog
        # (Pass args.port as default suggestion if needed, but for now strict dialog control)
        dialog = StartupDialog()
        
        # Override default port in dialog if provided via CLI
        if args.port != 5000:
            dialog.port_combo.set(str(args.port))
            
        settings = dialog.run()
        
        # If user closed dialog or cancelled
        if not settings:
            print("Session cancelled.")
            return 0
            
        username = settings['username']
        port = settings['port']
        
        # 2. Initialize Peer
        print(f"Starting {username} on port {port}...")
        peer = Peer(
            tcp_port=port,
            broadcast_port=args.broadcast_port,
            username=username
        )
        
        # 3. Create and run GUI with username
        gui = P2PChatGUI(peer, username=username)
        gui.run()
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
