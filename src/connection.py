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

logger = logging.getLogger(__name__)


class PeerConnection:
    
    BUFFER_SIZE = 4096
    
    def __init__(
        self,
        peer_ip: str,
        peer_port: int,
        sock: socket.socket,
        on_message: Optional[Callable[[str, int, Message], None]] = None,
        on_disconnect: Optional[Callable[[str, int], None]] = None
    ):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.socket = sock
        self._on_message = on_message
        self._on_disconnect = on_disconnect
        
        self._connected = True
        self._is_approved = False
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
        self._receive_thread = threading.Thread(
            target=self._receive_loop,
            daemon=True
        )
        self._receive_thread.start()
    
    def send_message(self, content: str) -> bool:
        if not self._connected:
            return False
        
        if not self._is_approved:
            return False
        
        try:
            msg = create_chat_message("", content)
            data = msg.to_bytes() + b'\n'
            self.socket.sendall(data)
            return True
        except Exception as e:
            logger.error(f"Error sending message to {self.peer_address}: {e}")
            self._handle_disconnect()
            return False
    
    def disconnect(self) -> None:
        if not self._connected:
            return
        
        try:
            msg = create_disconnect_message("")
            self.socket.sendall(msg.to_bytes() + b'\n')
        except Exception:
            pass
        
        self._handle_disconnect()
    
    def _receive_loop(self) -> None:
        buffer = ""
        
        while self._connected:
            try:
                data = self.socket.recv(self.BUFFER_SIZE)
                if not data:
                    break
                
                buffer += data.decode('utf-8')
                
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
        try:
            msg = Message.from_json(msg_str)
            msg.sender = self.peer_ip
            
            if msg.msg_type == MessageType.DISCONNECT:
                logger.info(f"Peer {self.peer_address} disconnected")
                self._handle_disconnect()
                
            elif msg.msg_type == MessageType.CONNECTION_REQUEST:
                if self._on_message:
                    self._on_message(self.peer_ip, self.peer_port, msg)
            
            elif msg.msg_type == MessageType.CONNECTION_ACCEPT:
                self._is_approved = True
                if self._on_message:
                    self._on_message(self.peer_ip, self.peer_port, msg)
            
            elif msg.msg_type == MessageType.CONNECTION_REJECT:
                logger.info(f"Connection rejected by {self.peer_address}")
                self._handle_disconnect()
                if self._on_message:
                    self._on_message(self.peer_ip, self.peer_port, msg)

            elif msg.msg_type == MessageType.MESSAGE:
                if self._is_approved:
                    if self._on_message:
                        self._on_message(self.peer_ip, self.peer_port, msg)
                else:
                     logger.warning(f"Ignored message from unapproved peer {self.peer_address}")
                    
        except Exception as e:
            logger.debug(f"Could not parse message: {e}")
    
    def _handle_disconnect(self) -> None:
        if not self._connected:
            return
        
        self._connected = False
        
        try:
            self.socket.close()
        except Exception:
            pass
        
        if self._on_disconnect:
            self._on_disconnect(self.peer_ip, self.peer_port)


class ConnectionManager:
    
    def __init__(
        self,
        local_ip: str,
        port: int = 5000
    ):
        self.local_ip = local_ip
        self.port = port
        
        self._connections: Dict[str, list] = {}
        self._server_socket: Optional[socket.socket] = None
        self._accepting = False
        self._accept_thread: Optional[threading.Thread] = None
        
        self._on_message: Optional[Callable[[str, Message], None]] = None
        self._on_peer_connected: Optional[Callable[[str], None]] = None
        self._on_peer_disconnected: Optional[Callable[[str], None]] = None
    
    @property
    def connected_peers(self) -> list:
        return list(self._connections.keys())

    def get_connection(self, ip: str, port: int = None) -> Optional[PeerConnection]:
        if ip not in self._connections:
            return None
        
        if port is not None:
            for conn in self._connections[ip]:
                if conn.peer_port == port:
                    return conn
        
        return self._connections[ip][-1] if self._connections[ip] else None
    
    def set_message_callback(self, callback: Callable[[str, int, Message], None]) -> None:
        self._on_message = callback
    
    def set_connect_callback(self, callback: Callable[[str], None]) -> None:
        self._on_peer_connected = callback
    
    def set_disconnect_callback(self, callback: Callable[[str], None]) -> None:
        self._on_peer_disconnected = callback
    
    def start_server(self) -> bool:
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
        self._accepting = False
        
        for peer_ip in list(self._connections.keys()):
            self.disconnect_peer(peer_ip)
        
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
        if peer_ip in self._connections:
            return any(c.is_approved for c in self._connections[peer_ip])
        return False

    def accept_connection(self, peer_ip: str) -> bool:
        if peer_ip not in self._connections:
            return False
        
        target_conn = None
        for conn in self._connections[peer_ip]:
            if not conn.is_approved:
                target_conn = conn
                break
                
        if not target_conn:
            if self.is_peer_approved(peer_ip):
                return True
            return False
            
        try:
            msg = create_connection_accept("")
            target_conn.socket.sendall(msg.to_bytes() + b'\n')
            
            target_conn.is_approved = True
            logger.info(f"Accepted connection from {peer_ip}")
            return True
        except Exception as e:
            logger.error(f"Error accepting connection: {e}")
            return False

    def reject_connection(self, peer_ip: str) -> None:
        if peer_ip not in self._connections:
            return
            
        try:
            for conn in self._connections[peer_ip]:
                if not conn.is_approved:
                    msg = create_connection_reject("")
                    try:
                        conn.socket.sendall(msg.to_bytes() + b'\n')
                    except Exception:
                        pass
        except Exception:
            pass
            
        self.disconnect_peer(peer_ip)

    def connect_to_peer(self, peer_ip: str, peer_port: int = 5000) -> bool:
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
            
            conn = self._add_connection(peer_ip, peer_port, sock)
            
            logger.info(f"Connected to peer {peer_ip}:{peer_port}")
            return True
        
        except Exception as e:
            logger.error(f"Could not connect to {peer_ip}:{peer_port}: {e}")
            return False
    
    def disconnect_peer(self, peer_ip: str) -> None:
        if peer_ip in self._connections:
            for conn in list(self._connections[peer_ip]):
                conn.disconnect()
            
            if peer_ip in self._connections:
                del self._connections[peer_ip]
    
    def send_to_peer(self, peer_ip: str, content: str) -> bool:
        if peer_ip not in self._connections:
            return False
        
        sent = False
        for conn in self._connections[peer_ip]:
            if conn.send_message(content):
                sent = True
        return sent
    
    def broadcast_message(self, content: str) -> int:
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
    
    def _handle_peer_disconnect(self, peer_ip: str, peer_port: int) -> None:
        if peer_ip in self._connections:
            approved_disconnect = False
            disconnected_port = peer_port
            
            for i in range(len(self._connections[peer_ip]) - 1, -1, -1):
                conn = self._connections[peer_ip][i]
                if not conn.is_connected:
                    if conn.is_approved:
                        approved_disconnect = True
                        disconnected_port = conn.peer_port
                    self._connections[peer_ip].pop(i)
            
            if not self._connections[peer_ip]:
                del self._connections[peer_ip]
                
                if approved_disconnect and self._on_peer_disconnected:
                    self._on_peer_disconnected(peer_ip, disconnected_port)
            elif approved_disconnect:
                pass
