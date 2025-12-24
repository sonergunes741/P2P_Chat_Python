#!/usr/bin/env python3

import argparse
import sys


def parse_arguments() -> argparse.Namespace:
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
    parser.add_argument(
        '--username', '-u',
        type=str,
        help='Username for auto-start'
    )
    
    parser.add_argument(
        '--auto', '-a',
        action='store_true',
        help='Skip startup dialog and auto-start'
    )
    
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    
    try:
        from src.peer import Peer, get_local_ip
        from src.gui import P2PChatGUI
        from src.startup_dialog import StartupDialog
        
        username = None
        port = args.port
        
        if args.auto and args.username:
            username = args.username
        else:
            dialog = StartupDialog()
            
            if args.port != 5000:
                dialog.port_combo.set(str(args.port))
                
            settings = dialog.run()
            
            if not settings:
                print("Session cancelled.")
                return 0
                
            username = settings['username']
            port = settings['port']
        
        print(f"Starting {username} on port {port}...")
        peer = Peer(
            tcp_port=port,
            broadcast_port=args.broadcast_port,
            username=username
        )
        
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
