"""
Peer Module
===========
Main orchestrator for the P2P chat application.
Coordinates discovery, connections, and the user interface.
"""

import socket
import logging
from typing import Optional

from .discovery import PeerDiscovery
from .connection import ConnectionManager
from .discovery import PeerDiscovery
from .connection import ConnectionManager
from .protocol import Message, MessageType
from .cli import ChatCLI, CommandType
from .cli import ChatCLI, CommandType

# Configure logging
logging.basicConfig(
    level=logging.WARNING,  # Set to DEBUG for verbose output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_local_ip() -> str:
    """
    Get the local IP address of this machine.
    
    Returns:
        Local IP address as string
    """
    try:
        # Create a dummy connection to find local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


class Peer:
    """
    Main P2P chat peer class.
    
    Orchestrates all components:
    - Discovery: Finding other peers on the network
    - Connection: Managing TCP connections
    - CLI: User interface
    
    Attributes:
        local_ip: This peer's IP address
        tcp_port: Port for TCP connections
        broadcast_port: Port for UDP discovery
    """
    
    def __init__(
        self,
        tcp_port: int = 5000,
        broadcast_port: int = 5001,
        username: str = "User"
    ):
        self.local_ip = get_local_ip()
        self.tcp_port = tcp_port
        self.broadcast_port = broadcast_port
        self.username = username
        
        # Initialize components
        self.discovery = PeerDiscovery(
            local_ip=self.local_ip,
            broadcast_port=broadcast_port,
            tcp_port=tcp_port,
            username=username
        )
        
        self.connections = ConnectionManager(
            local_ip=self.local_ip,
            port=tcp_port
        )
        
        self.cli = ChatCLI(
            local_ip=self.local_ip,
            port=tcp_port
        )
        
        # Wire up callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """Set up all component callbacks."""
        # Connection callbacks
        self.connections.set_message_callback(self._on_message_received)
        self.connections.set_connect_callback(self._on_peer_connected)
        self.connections.set_disconnect_callback(self._on_peer_disconnected)
        
        # CLI command handlers
        self.cli.register_handler(CommandType.DISCOVER, self._handle_discover)
        self.cli.register_handler(CommandType.CONNECT, self._handle_connect)
        self.cli.register_handler(CommandType.DISCONNECT, self._handle_disconnect)
        self.cli.register_handler(CommandType.LIST, self._handle_list)
        self.cli.register_handler(CommandType.MESSAGE, self._handle_message)
        self.cli.register_handler(CommandType.ACCEPT, self._handle_accept)
        self.cli.register_handler(CommandType.REJECT, self._handle_reject)
    
    def start(self) -> None:
        """Start the P2P chat peer."""
        logger.info(f"Starting P2P Chat on {self.local_ip}:{self.tcp_port}")
        
        # Start TCP server
        if not self.connections.start_server():
            self.cli.print_error("Could not start TCP server. Port may be in use.")
            return
        
        # Start discovery listener
        self.discovery.start_listening()
        
        try:
            # Run CLI (blocking)
            self.cli.run()
        finally:
            self.stop()
    
    def stop(self) -> None:
        """Stop the peer and clean up."""
        logger.info("Shutting down P2P Chat...")
        self.discovery.stop_listening()
        self.connections.stop_server()
    
    # ==================== Command Handlers ====================
    
    def _handle_discover(self, args: list) -> None:
        """Handle /discover command."""
        self.cli.print_discovery("Broadcasting on LAN...")
        
        # Clear previous discoveries
        self.discovery.clear_discovered_peers()
        
        # Broadcast and wait for responses
        peers = self.discovery.broadcast_discovery(timeout=3.0)
        
        if peers:
            self.cli.print_discovery(f"Found {len(peers)} peer(s):")
            for ip, port in peers:
                self.cli.print_discovery(f"  - {ip}:{port}")
        else:
            self.cli.print_discovery("No peers found on the network.")
    
    def _handle_connect(self, args: list) -> None:
        """Handle /connect command."""
        if not args:
            self.cli.print_error("Usage: /connect <ip> [port]")
            return
        
        # Handle "IP:PORT" format or "IP PORT" format
        if ":" in args[0]:
            try:
                peer_ip, port_str = args[0].split(":", 1)
                peer_port = int(port_str)
            except ValueError:
                self.cli.print_error("Invalid format. Use IP:PORT")
                return
        else:
            peer_ip = args[0]
            peer_port = int(args[1]) if len(args) > 1 else 5000
        
        self.cli.print_connection(f"Connecting to {peer_ip}:{peer_port}...")
        
        if self.connections.connect_to_peer(peer_ip, peer_port):
            self.cli.print_success(f"Connected to {peer_ip}")
        else:
            self.cli.print_error(f"Could not connect to {peer_ip}:{peer_port}")
    
    def _handle_disconnect(self, args: list) -> None:
        """Handle /disconnect command."""
        if not args:
            self.cli.print_error("Usage: /disconnect <ip>")
            return
        
        peer_ip = args[0]
        
        if peer_ip in self.connections.connected_peers:
            self.connections.disconnect_peer(peer_ip)
            self.cli.print_success(f"Disconnected from {peer_ip}")
        else:
            self.cli.print_error(f"Not connected to {peer_ip}")
    
    def _handle_list(self, args: list) -> None:
        """Handle /list command."""
        peers = self.connections.connected_peers
        
        if peers:
            self.cli.print_system(f"Connected peers ({len(peers)}):")
            for peer_ip in peers:
                self.cli.print_system(f"  - {peer_ip}")
        else:
            self.cli.print_system("No connected peers.")
    
    def _handle_message(self, args: list) -> None:
        """Handle sending a chat message."""
        if not args:
            return
        
        content = args[0]
        peers = self.connections.connected_peers
        
        if not peers:
            self.cli.print_error("No connected peers. Use /connect first.")
            return
        
        sent_count = self.connections.broadcast_message(content)
        
        if sent_count > 0:
            self.cli.print_outgoing_message(content)
        else:
            self.cli.print_error("Failed to send message. No approved connections.")
    
    def _handle_accept(self, args: list) -> None:
        """Handle /accept command."""
        if not args:
            self.cli.print_error("Usage: /accept <ip>")
            return
            
        peer_ip = args[0]
        if self.connections.accept_connection(peer_ip):
            self.cli.print_success(f"Accepted connection from {peer_ip}")
        else:
            self.cli.print_error(f"Could not accept connection from {peer_ip}")

    def _handle_reject(self, args: list) -> None:
        """Handle /reject command."""
        if not args:
            self.cli.print_error("Usage: /reject <ip>")
            return
            
        peer_ip = args[0]
        self.connections.reject_connection(peer_ip)
        self.cli.print_success(f"Rejected connection from {peer_ip}")
    
    # ==================== Event Callbacks ====================
    
    def _on_message_received(self, sender: str, message: Message) -> None:
        """Handle incoming chat message or handshake."""
        if message.msg_type == MessageType.MESSAGE:
            self.cli.print_incoming_message(sender, message.payload)
            
        elif message.msg_type == MessageType.CONNECTION_REQUEST:
            self.cli.print_system(f"{sender} wants to connect. Type '/accept {sender}' or '/reject {sender}'")
            
        elif message.msg_type == MessageType.CONNECTION_ACCEPT:
            self.cli.print_success(f"Connection accepted by {sender}. You can now chat!")
            
        elif message.msg_type == MessageType.CONNECTION_REJECT:
            self.cli.print_error(f"Connection rejected by {sender}.")
    
    def _on_peer_connected(self, peer_ip: str) -> None:
        """Handle new peer connection."""
        self.cli.print_connection(f"Peer connected: {peer_ip}")
    
    def _on_peer_disconnected(self, peer_ip: str) -> None:
        """Handle peer disconnection."""
        self.cli.print_connection(f"Peer disconnected: {peer_ip}")
