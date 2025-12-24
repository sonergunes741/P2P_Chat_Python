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

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        return "127.0.0.1"


class Peer:
    
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
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        self.connections.set_message_callback(self._on_message_received)
        self.connections.set_connect_callback(self._on_peer_connected)
        self.connections.set_disconnect_callback(self._on_peer_disconnected)
        
        self.cli.register_handler(CommandType.DISCOVER, self._handle_discover)
        self.cli.register_handler(CommandType.CONNECT, self._handle_connect)
        self.cli.register_handler(CommandType.DISCONNECT, self._handle_disconnect)
        self.cli.register_handler(CommandType.LIST, self._handle_list)
        self.cli.register_handler(CommandType.MESSAGE, self._handle_message)
        self.cli.register_handler(CommandType.ACCEPT, self._handle_accept)
        self.cli.register_handler(CommandType.REJECT, self._handle_reject)
    
    def start(self) -> None:
        logger.info(f"Starting P2P Chat on {self.local_ip}:{self.tcp_port}")
        
        if not self.connections.start_server():
            self.cli.print_error("Could not start TCP server. Port may be in use.")
            return
        
        self.discovery.start_listening()
        
        try:
            self.cli.run()
        finally:
            self.stop()
    
    def stop(self) -> None:
        logger.info("Shutting down P2P Chat...")
        self.discovery.stop_listening()
        self.connections.stop_server()
    
    def _handle_discover(self, args: list) -> None:
        self.cli.print_discovery("Broadcasting on LAN...")
        
        self.discovery.clear_discovered_peers()
        
        peers = self.discovery.broadcast_discovery(timeout=3.0)
        
        if peers:
            self.cli.print_discovery(f"Found {len(peers)} peer(s):")
            for ip, port in peers:
                self.cli.print_discovery(f"  - {ip}:{port}")
        else:
            self.cli.print_discovery("No peers found on the network.")
    
    def _handle_connect(self, args: list) -> None:
        if not args:
            self.cli.print_error("Usage: /connect <ip> [port]")
            return
        
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
        peers = self.connections.connected_peers
        
        if peers:
            self.cli.print_system(f"Connected peers ({len(peers)}):")
            for peer_ip in peers:
                self.cli.print_system(f"  - {peer_ip}")
        else:
            self.cli.print_system("No connected peers.")
    
    def _handle_message(self, args: list) -> None:
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
        if not args:
            self.cli.print_error("Usage: /accept <ip>")
            return
            
        peer_ip = args[0]
        if self.connections.accept_connection(peer_ip):
            self.cli.print_success(f"Accepted connection from {peer_ip}")
        else:
            self.cli.print_error(f"Could not accept connection from {peer_ip}")

    def _handle_reject(self, args: list) -> None:
        if not args:
            self.cli.print_error("Usage: /reject <ip>")
            return
            
        peer_ip = args[0]
        self.connections.reject_connection(peer_ip)
        self.cli.print_success(f"Rejected connection from {peer_ip}")
    
    def _on_message_received(self, sender_ip: str, sender_port: int, message: Message) -> None:
        if message.msg_type == MessageType.MESSAGE:
            self.cli.print_incoming_message(sender_ip, message.payload)
            
        elif message.msg_type == MessageType.CONNECTION_REQUEST:
            self.cli.print_system(f"{sender_ip} wants to connect. Type '/accept {sender_ip}' or '/reject {sender_ip}'")
            
        elif message.msg_type == MessageType.CONNECTION_ACCEPT:
            self.cli.print_success(f"Connection accepted by {sender_ip}. You can now chat!")
            
        elif message.msg_type == MessageType.CONNECTION_REJECT:
            self.cli.print_error(f"Connection rejected by {sender_ip}.")
    
    def _on_peer_connected(self, peer_ip: str) -> None:
        self.cli.print_connection(f"Peer connected: {peer_ip}")
    
    def _on_peer_disconnected(self, peer_ip: str, peer_port: int = None) -> None:
        self.cli.print_connection(f"Peer disconnected: {peer_ip}")
