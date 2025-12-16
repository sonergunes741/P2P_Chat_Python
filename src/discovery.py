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
        tcp_port: int = 5000,
        username: str = "User"
    ):
        self.local_ip = local_ip
        self.broadcast_port = broadcast_port
        self.tcp_port = tcp_port
        self.username = username
        
        # Store (ip, port, username)
        self._discovered_peers: Set[Tuple[str, int, str]] = set()
        self._listening = False
        self._listen_thread: Optional[threading.Thread] = None
        self._on_peer_discovered: Optional[Callable[[str, int, str], None]] = None
    
    @property
    def discovered_peers(self) -> Set[Tuple[str, int, str]]:
        """Returns set of discovered peers as (ip, port, username) tuples."""
        return self._discovered_peers.copy()
    
    def set_peer_discovered_callback(self, callback: Callable[[str, int, str], None]) -> None:
        """Set callback function to be called when a new peer is discovered."""
        self._on_peer_discovered = callback
    
    def broadcast_discovery(self, timeout: float = 3.0) -> Set[Tuple[str, int, str]]:
        """
        Broadcast a discovery message and collect responses.
        
        Args:
            timeout: How long to wait for responses (seconds)
            
        Returns:
            Set of discovered peers as (ip, port, username) tuples
        """
        logger.info("Broadcasting discovery message...")
        
        # Create UDP socket for broadcasting
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(0.5)  # Short timeout for receiving
        
        try:
            # Send discovery broadcast
            # Format: IP:USERNAME:PORT
            payload = f"{self.local_ip}:{self.username}:{self.tcp_port}"
            discovery_msg = create_discovery_message(payload, 0) # Payload contains everything method signature might need adjustment or we just misuse payload
            # Wait, create_discovery_message takes (sender_ip, sender_port). Let's adjust helper usage.
            # Actually, standard protocol was taking sender_ip and port. We need to jam username in there.
            # Let's override the payload manually to be safe.
            
            msg = Message(MessageType.DISCOVERY, self.local_ip, payload)
            
            sock.sendto(
                msg.to_bytes(),
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
                payload_parts = msg.payload.split(':')
                
                peer_username = "Unknown"
                peer_tcp_port = 5000
                
                # Format: IP:USERNAME:PORT (New)
                if len(payload_parts) == 3:
                    peer_username = payload_parts[1]
                    try:
                        peer_tcp_port = int(payload_parts[2])
                    except ValueError:
                        return
                        
                # Format: USERNAME:PORT (Response format)
                elif len(payload_parts) == 2:
                    peer_username = payload_parts[0]
                    try:
                         peer_tcp_port = int(payload_parts[1])
                    except ValueError:
                         return
                         
                # Format: PORT (Legacy)
                elif len(payload_parts) == 1:
                    try:
                        peer_tcp_port = int(payload_parts[0])
                    except ValueError:
                        return
                
                # Ignore our own responses (same IP AND same Port)
                if peer_ip == self.local_ip and peer_tcp_port == self.tcp_port:
                    return
                
                peer_info = (peer_ip, peer_tcp_port, peer_username)
                
                existing = [p for p in self._discovered_peers if p[0] == peer_ip and p[1] == peer_tcp_port]
                if not existing:
                    self._discovered_peers.add(peer_info)
                    logger.info(f"Discovered peer: {peer_username} ({peer_ip}:{peer_tcp_port})")
                    
                    if self._on_peer_discovered:
                        self._on_peer_discovered(peer_ip, peer_tcp_port, peer_username)
                        
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
                # Parse sender's TCP port from payload
                # Format: IP:USERNAME:PORT (New)
                sender_tcp_port = 0
                parts = msg.payload.split(':')
                
                if len(parts) == 3:
                     try:
                         sender_tcp_port = int(parts[2])
                     except ValueError:
                         pass
                elif len(parts) == 2:
                     try:
                         sender_tcp_port = int(parts[1])
                     except ValueError:
                         pass
                elif len(parts) == 1:
                     try:
                         sender_tcp_port = int(parts[0])
                     except ValueError:
                         pass
                
                # Ignore our own broadcasts (same IP AND same Port)
                if peer_ip == self.local_ip and sender_tcp_port == self.tcp_port:
                    return

                # Send response with our Username and TCP port
                # Format: USERNAME:PORT
                response_payload = f"{self.username}:{self.tcp_port}"
                response = Message(MessageType.DISCOVERY_RESPONSE, self.local_ip, response_payload)
                sock.sendto(response.to_bytes(), addr)
                logger.debug(f"Responded to discovery from {peer_ip}")
                
        except Exception as e:
            logger.debug(f"Could not handle discovery request: {e}")
    
    def clear_discovered_peers(self) -> None:
        """Clear the list of discovered peers."""
        self._discovered_peers.clear()
