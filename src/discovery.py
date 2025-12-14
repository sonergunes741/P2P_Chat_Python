"""
Discovery Module
=================
Handles peer discovery on the local network using UDP broadcast.
"""

import socket
import threading
import time
from typing import Callable, Set, Tuple, Optional
import logging

from .protocol import (
    Message,
    MessageType,
    create_discovery_message,
    create_discovery_response
)

# Configure logging
logger = logging.getLogger(__name__)


class PeerDiscovery:
    """
    Handles UDP broadcast-based peer discovery on LAN.
    
    Attributes:
        local_ip: The local IP address of this peer
        broadcast_port: Port used for discovery broadcasts
        tcp_port: TCP port to advertise for connections
    """
    
    BROADCAST_ADDRESS = "255.255.255.255"
    BUFFER_SIZE = 1024
    
    def __init__(
        self,
        local_ip: str,
        broadcast_port: int = 5001,
        tcp_port: int = 5000
    ):
        self.local_ip = local_ip
        self.broadcast_port = broadcast_port
        self.tcp_port = tcp_port
        
        self._discovered_peers: Set[Tuple[str, int]] = set()
        self._listening = False
        self._listen_thread: Optional[threading.Thread] = None
        self._on_peer_discovered: Optional[Callable[[str, int], None]] = None
    
    @property
    def discovered_peers(self) -> Set[Tuple[str, int]]:
        """Returns set of discovered peers as (ip, port) tuples."""
        return self._discovered_peers.copy()
    
    def set_peer_discovered_callback(self, callback: Callable[[str, int], None]) -> None:
        """Set callback function to be called when a new peer is discovered."""
        self._on_peer_discovered = callback
    
    def broadcast_discovery(self, timeout: float = 3.0) -> Set[Tuple[str, int]]:
        """
        Broadcast a discovery message and collect responses.
        
        Args:
            timeout: How long to wait for responses (seconds)
            
        Returns:
            Set of discovered peers as (ip, port) tuples
        """
        logger.info("Broadcasting discovery message...")
        
        # Create UDP socket for broadcasting
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.5)  # Short timeout for receiving
        
        try:
            # Send discovery broadcast
            # Include our TCP port in the message so local peers can distinguish us
            discovery_msg = create_discovery_message(self.local_ip, self.tcp_port)
            sock.sendto(
                discovery_msg.to_bytes(),
                (self.BROADCAST_ADDRESS, self.broadcast_port)
            )
            
            # Collect responses
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(self.BUFFER_SIZE)
                    self._handle_discovery_response(data, addr)
                except socket.timeout:
                    continue
                except Exception as e:
                    logger.error(f"Error receiving discovery response: {e}")
                    
        except Exception as e:
            logger.error(f"Error broadcasting discovery: {e}")
        finally:
            sock.close()
        
        logger.info(f"Discovery complete. Found {len(self._discovered_peers)} peers.")
        return self.discovered_peers
    
    def _handle_discovery_response(self, data: bytes, addr: Tuple[str, int]) -> None:
        """Process a discovery response."""
        try:
            msg = Message.from_bytes(data)
            peer_ip = addr[0]
            
            if msg.msg_type == MessageType.DISCOVERY_RESPONSE:
                peer_tcp_port = int(msg.payload)
                
                # Ignore our own responses (same IP AND same Port)
                if peer_ip == self.local_ip and peer_tcp_port == self.tcp_port:
                    return
                
                peer_info = (peer_ip, peer_tcp_port)
                
                if peer_info not in self._discovered_peers:
                    self._discovered_peers.add(peer_info)
                    logger.info(f"Discovered peer: {peer_ip}:{peer_tcp_port}")
                    
                    if self._on_peer_discovered:
                        self._on_peer_discovered(peer_ip, peer_tcp_port)
                        
        except Exception as e:
            logger.debug(f"Could not parse discovery response: {e}")
    
    def start_listening(self) -> None:
        """Start listening for discovery broadcasts from other peers."""
        if self._listening:
            logger.warning("Already listening for discovery broadcasts")
            return
        
        self._listening = True
        self._listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self._listen_thread.start()
        logger.info(f"Listening for discovery broadcasts on port {self.broadcast_port}")
    
    def stop_listening(self) -> None:
        """Stop listening for discovery broadcasts."""
        self._listening = False
        if self._listen_thread:
            self._listen_thread.join(timeout=1.0)
            self._listen_thread = None
        logger.info("Stopped listening for discovery broadcasts")
    
    def _listen_loop(self) -> None:
        """Main loop for listening to discovery broadcasts."""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Enable broadcast receiving
        try:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except Exception:
            pass
        
        sock.settimeout(1.0)
        
        try:
            sock.bind(('', self.broadcast_port))
        except Exception as e:
            logger.error(f"Could not bind to discovery port: {e}")
            return
        
        while self._listening:
            try:
                data, addr = sock.recvfrom(self.BUFFER_SIZE)
                self._handle_discovery_request(data, addr, sock)
            except socket.timeout:
                continue
            except Exception as e:
                if self._listening:
                    logger.error(f"Error in discovery listener: {e}")
        
        sock.close()
    
    def _handle_discovery_request(
        self,
        data: bytes,
        addr: Tuple[str, int],
        sock: socket.socket
    ) -> None:
        """Handle an incoming discovery request and send response."""
        try:
            msg = Message.from_bytes(data)
            peer_ip = addr[0]
            
            if msg.msg_type == MessageType.DISCOVERY:
                # Parse sender's TCP port from payload if available
                sender_tcp_port = 0
                if ":" in msg.payload:
                    try:
                        _, port_str = msg.payload.split(":", 1)
                        sender_tcp_port = int(port_str)
                    except ValueError:
                        pass
                
                # Ignore our own broadcasts (same IP AND same Port)
                if peer_ip == self.local_ip and sender_tcp_port == self.tcp_port:
                    return

                # Send response with our TCP port
                response = create_discovery_response(self.local_ip, self.tcp_port)
                sock.sendto(response.to_bytes(), addr)
                logger.debug(f"Responded to discovery from {peer_ip}")
                
        except Exception as e:
            logger.debug(f"Could not handle discovery request: {e}")
    
    def clear_discovered_peers(self) -> None:
        """Clear the list of discovered peers."""
        self._discovered_peers.clear()
