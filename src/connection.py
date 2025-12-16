"""
Connection Module
==================
Manages TCP connections between peers for reliable message exchange.
"""

import socket
import threading
from typing import Dict, Callable, Optional, Tuple
import logging

from .protocol import (
    Message,
    MessageType,
    create_chat_message,
    create_disconnect_message,
    create_connection_request,
    create_connection_accept,
    create_connection_reject
)

# Configure logging
logger = logging.getLogger(__name__)


class PeerConnection:
    """
    Represents a single TCP connection to a peer.
    
    Attributes:
        peer_ip: IP address of the connected peer
        peer_port: Port of the connected peer
        socket: The TCP socket for this connection
    """
    
    BUFFER_SIZE = 4096
    
    def __init__(
        self,
        peer_ip: str,
        peer_port: int,
        sock: socket.socket,
        on_message: Optional[Callable[[str, Message], None]] = None,
        on_disconnect: Optional[Callable[[str], None]] = None
    ):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.socket = sock
        self._on_message = on_message
        self._on_disconnect = on_disconnect
        
        self._connected = True
        self._is_approved = False  # Handshake status
        self._receive_thread: Optional[threading.Thread] = None
    
    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def is_approved(self) -> bool:
        return self._is_approved
    
    @is_approved.setter
    def is_approved(self, value: bool) -> None:
        self._is_approved = value
    
    @property
    def peer_address(self) -> str:
        return f"{self.peer_ip}:{self.peer_port}"
    
    def start_receiving(self) -> None:
        """Start the receive loop in a separate thread."""
        self._receive_thread = threading.Thread(
            target=self._receive_loop,
            daemon=True
        )
        self._receive_thread.start()
    
    def send_message(self, content: str) -> bool:
        """
        Send a chat message to this peer.
        
        Args:
            content: Message content to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self._connected:
            return False
        
        # Only allow sending chat messages if approved, or if it's a handshake message
        # Handshake messages are created internally and sent directly via socket
        if not self._is_approved:
            # We assume user is trying to send a chat message
            return False
        
        try:
            msg = create_chat_message("", content)  # Sender filled by receiver
            data = msg.to_bytes() + b'\n'  # Add delimiter
            self.socket.sendall(data)
            return True
        except Exception as e:
            logger.error(f"Error sending message to {self.peer_address}: {e}")
            self._handle_disconnect()
            return False
    
    def disconnect(self) -> None:
        """Gracefully disconnect from this peer."""
        if not self._connected:
            return
        
        try:
            # Send disconnect notification
            msg = create_disconnect_message("")
            self.socket.sendall(msg.to_bytes() + b'\n')
        except Exception:
            pass
        
        self._handle_disconnect()
    
    def _receive_loop(self) -> None:
        """Continuously receive messages from the peer."""
        buffer = ""
        
        while self._connected:
            try:
                data = self.socket.recv(self.BUFFER_SIZE)
                if not data:
                    break
                
                buffer += data.decode('utf-8')
                
                # Process complete messages (delimited by newline)
                while '\n' in buffer:
                    msg_str, buffer = buffer.split('\n', 1)
                    if msg_str:
                        self._process_message(msg_str)
                        
            except socket.timeout:
                continue
            except Exception as e:
                if self._connected:
                    logger.debug(f"Connection error with {self.peer_address}: {e}")
                break
        
        self._handle_disconnect()
    
    def _process_message(self, msg_str: str) -> None:
        """Process a received message string."""
        try:
            msg = Message.from_json(msg_str)
            msg.sender = self.peer_ip  # Override with actual sender IP
            
            if msg.msg_type == MessageType.DISCONNECT:
                logger.info(f"Peer {self.peer_address} disconnected")
                self._handle_disconnect()
                
            elif msg.msg_type == MessageType.CONNECTION_REQUEST:
                # Let the manager/peer handle the approval logic
                if self._on_message:
                    self._on_message(self.peer_ip, msg)
            
            elif msg.msg_type == MessageType.CONNECTION_ACCEPT:
                self._is_approved = True
                if self._on_message:
                    self._on_message(self.peer_ip, msg)
            
            elif msg.msg_type == MessageType.CONNECTION_REJECT:
                logger.info(f"Connection rejected by {self.peer_address}")
                self._handle_disconnect()
                if self._on_message:
                    self._on_message(self.peer_ip, msg)

            elif msg.msg_type == MessageType.MESSAGE:
                if self._is_approved:
                    if self._on_message:
                        self._on_message(self.peer_ip, msg)
                else:
                     logger.warning(f"Ignored message from unapproved peer {self.peer_address}")
                    
        except Exception as e:
            logger.debug(f"Could not parse message: {e}")
    
    def _handle_disconnect(self) -> None:
        """Handle disconnection cleanup."""
        if not self._connected:
            return
        
        self._connected = False
        
        try:
            self.socket.close()
        except Exception:
            pass
        
        if self._on_disconnect:
            self._on_disconnect(self.peer_ip)


class ConnectionManager:
    """
    Manages all peer connections and the TCP server.
    
    Attributes:
        local_ip: Local IP address
        port: TCP port for accepting connections
    """
    
    def __init__(
        self,
        local_ip: str,
        port: int = 5000
    ):
        self.local_ip = local_ip
        self.port = port
        
        self._connections: Dict[str, list] = {}  # Map IP to LIST of PeerConnections
        self._server_socket: Optional[socket.socket] = None
        self._accepting = False
        self._accept_thread: Optional[threading.Thread] = None
        
        self._on_message: Optional[Callable[[str, Message], None]] = None
        self._on_peer_connected: Optional[Callable[[str], None]] = None
        self._on_peer_disconnected: Optional[Callable[[str], None]] = None
    
    @property
    def connected_peers(self) -> list:
        """List of connected peer IPs."""
        return list(self._connections.keys())

    def get_connection(self, ip: str, port: int = None) -> Optional[PeerConnection]:
        """Get a specific connection by IP and optionally port."""
        if ip not in self._connections:
            return None
        
        if port is not None:
            for conn in self._connections[ip]:
                if conn.peer_port == port:
                    return conn
        
        # If no port specified or not found, return the most recent one
        return self._connections[ip][-1] if self._connections[ip] else None
    
    def set_message_callback(self, callback: Callable[[str, Message], None]) -> None:
        """Set callback for incoming messages."""
        self._on_message = callback
    
    def set_connect_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for new connections."""
        self._on_peer_connected = callback
    
    def set_disconnect_callback(self, callback: Callable[[str], None]) -> None:
        """Set callback for disconnections."""
        self._on_peer_disconnected = callback
    
    def start_server(self) -> bool:
        """
        Start the TCP server to accept incoming connections.
        
        Returns:
            True if server started successfully
        """
        try:
            self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server_socket.bind(('', self.port))
            self._server_socket.listen(5)
            self._server_socket.settimeout(1.0)
            
            self._accepting = True
            self._accept_thread = threading.Thread(
                target=self._accept_loop,
                daemon=True
            )
            self._accept_thread.start()
            
            logger.info(f"TCP server started on port {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Could not start TCP server: {e}")
            return False
    
    def stop_server(self) -> None:
        """Stop the TCP server and disconnect all peers."""
        self._accepting = False
        
        # Disconnect all peers
        for peer_ip in list(self._connections.keys()):
            self.disconnect_peer(peer_ip)
        
        # Close server socket
        if self._server_socket:
            try:
                self._server_socket.close()
            except Exception:
                pass
            self._server_socket = None
        
        if self._accept_thread:
            self._accept_thread.join(timeout=2.0)
            self._accept_thread = None
        
        logger.info("TCP server stopped")
    
    def _accept_loop(self) -> None:
        """Accept incoming connections."""
        while self._accepting:
            try:
                client_socket, addr = self._server_socket.accept()
                peer_ip = addr[0]
                peer_port = addr[1]
                
                logger.info(f"Incoming connection from {peer_ip}:{peer_port}")
                self._add_connection(peer_ip, peer_port, client_socket)
                
            except socket.timeout:
                continue
            except Exception as e:
                if self._accepting:
                    logger.error(f"Error accepting connection: {e}")
    

    def is_peer_approved(self, peer_ip: str) -> bool:
        """Check if connection to peer is approved."""
        if peer_ip in self._connections:
            # Return true if ANY connection from this IP is approved
            return any(c.is_approved for c in self._connections[peer_ip])
        return False

    def accept_connection(self, peer_ip: str) -> bool:
        """Accept a pending connection request."""
        if peer_ip not in self._connections:
            return False
        
        # Find unapproved connection
        target_conn = None
        for conn in self._connections[peer_ip]:
            if not conn.is_approved:
                target_conn = conn
                break
                
        if not target_conn:
            # Check if we have any approved one, if so return True (already connected)
            if self.is_peer_approved(peer_ip):
                return True
            return False
            
        try:
            # Send ACCEPT message
            msg = create_connection_accept("")
            # Need to send raw bytes because send_message is blocked for unapproved
            target_conn.socket.sendall(msg.to_bytes() + b'\n')
            
            # Update local state
            target_conn.is_approved = True
            logger.info(f"Accepted connection from {peer_ip}")
            return True
        except Exception as e:
            logger.error(f"Error accepting connection: {e}")
            return False

    def reject_connection(self, peer_ip: str) -> None:
        """Reject and close a connection."""
        if peer_ip not in self._connections:
            return
            
        try:
            # Reject all unapproved connections from this IP
            for conn in self._connections[peer_ip]:
                if not conn.is_approved:
                    msg = create_connection_reject("")
                    try:
                        conn.socket.sendall(msg.to_bytes() + b'\n')
                    except Exception:
                        pass
        except Exception:
            pass
            
        # We don't necessarily disconnect everyone, just the pending ones?
        # For simplicity, let's keep old behavior: disconnect IP
        self.disconnect_peer(peer_ip)

    def connect_to_peer(self, peer_ip: str, peer_port: int = 5000) -> bool:
        """
        Initiate a connection to a peer.
        """
        # Check if we are already connected to this IP:PORT
        if peer_ip in self._connections:
            for conn in self._connections[peer_ip]:
                if conn.peer_port == peer_port:
                    logger.warning(f"Already connected to {peer_ip}:{peer_port}")
                    return True
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)
            sock.connect((peer_ip, peer_port))
            sock.settimeout(1.0)
            
            # Create connection wrapper
            conn = self._add_connection(peer_ip, peer_port, sock)
            
            logger.info(f"Connected to peer {peer_ip}:{peer_port}")
            return True
        
        except Exception as e:
            logger.error(f"Could not connect to {peer_ip}:{peer_port}: {e}")
            return False
    
    def disconnect_peer(self, peer_ip: str) -> None:
        """Disconnect from a specific peer (all connections to that IP)."""
        if peer_ip in self._connections:
            # Disconnect all
            for conn in list(self._connections[peer_ip]):
                conn.disconnect()
            
            # Key should be removed by callback, but force it
            if peer_ip in self._connections:
                del self._connections[peer_ip]
    
    def send_to_peer(self, peer_ip: str, content: str) -> bool:
        """Send a message to a specific peer."""
        if peer_ip not in self._connections:
            return False
        
        # Send to all approved connections for this IP
        sent = False
        for conn in self._connections[peer_ip]:
            if conn.send_message(content):
                sent = True
        return sent
    
    def broadcast_message(self, content: str) -> int:
        """
        Send a message to all connected peers.
        """
        count = 0
        for peer_list in self._connections.values():
            for conn in peer_list:
                if conn.send_message(content):
                    count += 1
        return count
    
    def _add_connection(
        self,
        peer_ip: str,
        peer_port: int,
        sock: socket.socket
    ) -> PeerConnection:
        """Add a new peer connection."""
        conn = PeerConnection(
            peer_ip=peer_ip,
            peer_port=peer_port,
            sock=sock,
            on_message=self._on_message,
            on_disconnect=self._handle_peer_disconnect
        )
        
        if peer_ip not in self._connections:
            self._connections[peer_ip] = []
        self._connections[peer_ip].append(conn)
        
        conn.start_receiving()
        
        if self._on_peer_connected:
            self._on_peer_connected(peer_ip)
            
        return conn
    
    def _handle_peer_disconnect(self, peer_ip: str) -> None:
        """Handle peer disconnection."""
        # Find which connection triggered this?
        # Actually _handle_disconnect uses peer_ip.
        # It's hard to know WHICH connection died if we only get IP.
        # But wait, PeerConnection calls this.
        # We need to cleanup closed connections.
        
        if peer_ip in self._connections:
            # Filter out disconnected ones
            approved_disconnect = False
            
            # We iterate backwards to safely remove
            for i in range(len(self._connections[peer_ip]) - 1, -1, -1):
                conn = self._connections[peer_ip][i]
                if not conn.is_connected:
                    if conn.is_approved:
                        approved_disconnect = True
                    self._connections[peer_ip].pop(i)
            
            if not self._connections[peer_ip]:
                del self._connections[peer_ip]
                
                # Notify GUI if the last approved connection is gone?
                # Or if ANY approved connection is gone?
                # Let's say if we lost connection to the IP entirely (or partly)
                if approved_disconnect and self._on_peer_disconnected:
                    self._on_peer_disconnected(peer_ip)
            elif approved_disconnect:
                # Still have connections, but one approved died.
                # Maybe notify? 
                pass
