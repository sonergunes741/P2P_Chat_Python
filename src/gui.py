"""
GUI Module
==========
Professional Tkinter-based GUI for P2P Chat Application.
Clean, functional, engineer-style interface.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from typing import Optional, Set, Tuple
import socket


class P2PChatGUI:
    """
    Main GUI class for P2P Chat Application.
    
    Features:
    - Network info display
    - Peer discovery with one click
    - Easy connect/accept/reject
    - Real-time chat
    """
    
    # Color scheme - Engineer/Terminal style
    COLORS = {
        'bg_dark': '#1a1a2e',
        'bg_medium': '#16213e',
        'bg_light': '#0f3460',
        'accent': '#e94560',
        'text': '#eaeaea',
        'text_dim': '#a0a0a0',
        'success': '#00d26a',
        'warning': '#f39c12',
        'error': '#e74c3c',
        'border': '#2a2a4a'
    }
    
    def __init__(self, peer):
        """Initialize GUI with a Peer instance."""
        self.peer = peer
        self.root = tk.Tk()
        self.root.title("P2P Chat - Network Terminal")
        self.root.geometry("900x650")
        self.root.minsize(800, 550)
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        # Pending connection requests
        self.pending_requests: Set[str] = set()
        
        # Setup styles
        self._setup_styles()
        
        # Build UI
        self._build_ui()
        
        # Wire up peer callbacks
        self._setup_callbacks()
        
        # Start peer services
        self._start_peer()
    
    def _setup_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Button styles
        style.configure(
            'Action.TButton',
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text'],
            borderwidth=0,
            focusthickness=0,
            font=('Consolas', 10, 'bold')
        )
        style.map('Action.TButton',
            background=[('active', self.COLORS['accent'])]
        )
        
        # Success button
        style.configure(
            'Success.TButton',
            background=self.COLORS['success'],
            foreground='white',
            font=('Consolas', 9, 'bold')
        )
        
        # Danger button
        style.configure(
            'Danger.TButton',
            background=self.COLORS['error'],
            foreground='white',
            font=('Consolas', 9, 'bold')
        )
        
        # Label styles
        style.configure(
            'Header.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['accent'],
            font=('Consolas', 12, 'bold')
        )
        
        style.configure(
            'Info.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text'],
            font=('Consolas', 10)
        )
        
        style.configure(
            'Dim.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_dim'],
            font=('Consolas', 9)
        )
    
    def _build_ui(self):
        """Build the main UI layout."""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top bar - Network Info
        self._build_top_bar(main_frame)
        
        # Middle section - 3 columns
        middle_frame = tk.Frame(main_frame, bg=self.COLORS['bg_dark'])
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Discovery & Peers
        self._build_left_panel(middle_frame)
        
        # Right panel - Chat area
        self._build_chat_panel(middle_frame)
    
    def _build_top_bar(self, parent):
        """Build the top information bar."""
        top_frame = tk.Frame(parent, bg=self.COLORS['bg_medium'], height=60)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        # Left side - App title
        title_label = tk.Label(
            top_frame,
            text="⚡ P2P CHAT TERMINAL",
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['accent'],
            font=('Consolas', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Right side - Network info
        info_frame = tk.Frame(top_frame, bg=self.COLORS['bg_medium'])
        info_frame.pack(side=tk.RIGHT, padx=15)
        
        # IP Address
        ip_label = tk.Label(
            info_frame,
            text=f"IP: {self.peer.local_ip}",
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['success'],
            font=('Consolas', 11, 'bold')
        )
        ip_label.pack(side=tk.LEFT, padx=10)
        
        # Port
        port_label = tk.Label(
            info_frame,
            text=f"PORT: {self.peer.tcp_port}",
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['warning'],
            font=('Consolas', 11, 'bold')
        )
        port_label.pack(side=tk.LEFT, padx=10)
        
        # Status indicator
        self.status_label = tk.Label(
            info_frame,
            text="● ONLINE",
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['success'],
            font=('Consolas', 10, 'bold')
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
    
    def _build_left_panel(self, parent):
        """Build left panel with discovery and peer list."""
        left_frame = tk.Frame(parent, bg=self.COLORS['bg_dark'], width=280)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # -- Discovery Section --
        discovery_frame = tk.LabelFrame(
            left_frame,
            text=" 🔍 NETWORK DISCOVERY ",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['accent'],
            font=('Consolas', 10, 'bold'),
            bd=1,
            relief=tk.GROOVE
        )
        discovery_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Discover button
        self.discover_btn = ttk.Button(
            discovery_frame,
            text="🔎 SCAN NETWORK",
            style='Action.TButton',
            command=self._on_discover
        )
        self.discover_btn.pack(fill=tk.X, padx=10, pady=10)
        
        # Discovered peers listbox
        tk.Label(
            discovery_frame,
            text="Found Peers:",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_dim'],
            font=('Consolas', 9)
        ).pack(anchor=tk.W, padx=10)
        
        self.discovered_listbox = tk.Listbox(
            discovery_frame,
            height=4,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            font=('Consolas', 10),
            selectbackground=self.COLORS['accent'],
            bd=0,
            highlightthickness=1,
            highlightcolor=self.COLORS['border']
        )
        self.discovered_listbox.pack(fill=tk.X, padx=10, pady=5)
        
        # Connect button
        self.connect_btn = ttk.Button(
            discovery_frame,
            text="🔗 CONNECT",
            style='Success.TButton',
            command=self._on_connect_selected
        )
        self.connect_btn.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # -- Manual Connect --
        manual_frame = tk.LabelFrame(
            left_frame,
            text=" ⌨️ MANUAL CONNECT ",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['accent'],
            font=('Consolas', 10, 'bold'),
            bd=1,
            relief=tk.GROOVE
        )
        manual_frame.pack(fill=tk.X, pady=(0, 10))
        
        # IP Entry
        tk.Label(
            manual_frame,
            text="IP Address:",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_dim'],
            font=('Consolas', 9)
        ).pack(anchor=tk.W, padx=10, pady=(5, 0))
        
        self.ip_entry = tk.Entry(
            manual_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            font=('Consolas', 10),
            insertbackground=self.COLORS['text'],
            bd=0,
            highlightthickness=1,
            highlightcolor=self.COLORS['accent']
        )
        self.ip_entry.pack(fill=tk.X, padx=10, pady=2)
        
        # Port Entry
        tk.Label(
            manual_frame,
            text="Port:",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_dim'],
            font=('Consolas', 9)
        ).pack(anchor=tk.W, padx=10)
        
        self.port_entry = tk.Entry(
            manual_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            font=('Consolas', 10),
            insertbackground=self.COLORS['text'],
            bd=0,
            highlightthickness=1,
            highlightcolor=self.COLORS['accent']
        )
        self.port_entry.insert(0, "5000")
        self.port_entry.pack(fill=tk.X, padx=10, pady=2)
        
        # Manual connect button
        ttk.Button(
            manual_frame,
            text="🔗 CONNECT",
            style='Action.TButton',
            command=self._on_manual_connect
        ).pack(fill=tk.X, padx=10, pady=10)
        
        # -- Connected Peers --
        connected_frame = tk.LabelFrame(
            left_frame,
            text=" 👥 CONNECTED PEERS ",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['accent'],
            font=('Consolas', 10, 'bold'),
            bd=1,
            relief=tk.GROOVE
        )
        connected_frame.pack(fill=tk.BOTH, expand=True)
        
        self.connected_listbox = tk.Listbox(
            connected_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            font=('Consolas', 10),
            selectbackground=self.COLORS['accent'],
            bd=0,
            highlightthickness=0
        )
        self.connected_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _build_chat_panel(self, parent):
        """Build the main chat area."""
        chat_frame = tk.Frame(parent, bg=self.COLORS['bg_dark'])
        chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Pending requests notification
        self.pending_frame = tk.Frame(chat_frame, bg=self.COLORS['warning'])
        # Hidden by default, shown when there are pending requests
        
        self.pending_label = tk.Label(
            self.pending_frame,
            text="",
            bg=self.COLORS['warning'],
            fg='black',
            font=('Consolas', 10, 'bold')
        )
        self.pending_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.accept_btn = tk.Button(
            self.pending_frame,
            text="✓ ACCEPT",
            bg=self.COLORS['success'],
            fg='white',
            font=('Consolas', 9, 'bold'),
            bd=0,
            command=self._on_accept
        )
        self.accept_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.reject_btn = tk.Button(
            self.pending_frame,
            text="✗ REJECT",
            bg=self.COLORS['error'],
            fg='white',
            font=('Consolas', 9, 'bold'),
            bd=0,
            command=self._on_reject
        )
        self.reject_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Chat display area
        chat_label_frame = tk.LabelFrame(
            chat_frame,
            text=" 💬 MESSAGES ",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['accent'],
            font=('Consolas', 10, 'bold'),
            bd=1,
            relief=tk.GROOVE
        )
        chat_label_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_label_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            font=('Consolas', 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bd=0,
            highlightthickness=0
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure('system', foreground=self.COLORS['warning'])
        self.chat_display.tag_configure('incoming', foreground=self.COLORS['success'])
        self.chat_display.tag_configure('outgoing', foreground=self.COLORS['accent'])
        self.chat_display.tag_configure('error', foreground=self.COLORS['error'])
        
        # Message input area
        input_frame = tk.Frame(chat_frame, bg=self.COLORS['bg_dark'])
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.message_entry = tk.Entry(
            input_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text'],
            font=('Consolas', 11),
            insertbackground=self.COLORS['text'],
            bd=0,
            highlightthickness=2,
            highlightcolor=self.COLORS['accent']
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        self.message_entry.bind('<Return>', self._on_send_message)
        
        send_btn = tk.Button(
            input_frame,
            text="SEND ➤",
            bg=self.COLORS['accent'],
            fg='white',
            font=('Consolas', 10, 'bold'),
            bd=0,
            padx=20,
            command=lambda: self._on_send_message(None)
        )
        send_btn.pack(side=tk.RIGHT, padx=(10, 0), ipady=8)
    
    def _setup_callbacks(self):
        """Wire up peer callbacks to GUI updates."""
        self.peer.connections.set_message_callback(self._on_message_received)
        self.peer.connections.set_connect_callback(self._on_peer_connected)
        self.peer.connections.set_disconnect_callback(self._on_peer_disconnected)
    
    def _start_peer(self):
        """Start peer services."""
        if not self.peer.connections.start_server():
            messagebox.showerror("Error", "Could not start server. Port may be in use.")
            return
        
        self.peer.discovery.start_listening()
        self._log_system("Server started. Ready to accept connections.")
    
    def run(self):
        """Start the GUI main loop."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.mainloop()
    
    def _on_close(self):
        """Handle window close."""
        self.peer.discovery.stop_listening()
        self.peer.connections.stop_server()
        self.root.destroy()
    
    # ==================== Event Handlers ====================
    
    def _on_discover(self):
        """Handle discover button click."""
        self.discover_btn.config(state=tk.DISABLED)
        self._log_system("Scanning network...")
        
        def do_discover():
            self.peer.discovery.clear_discovered_peers()
            peers = self.peer.discovery.broadcast_discovery(timeout=3.0)
            self.root.after(0, lambda: self._update_discovered_peers(peers))
        
        threading.Thread(target=do_discover, daemon=True).start()
    
    def _update_discovered_peers(self, peers: Set[Tuple[str, int]]):
        """Update the discovered peers list."""
        self.discover_btn.config(state=tk.NORMAL)
        self.discovered_listbox.delete(0, tk.END)
        
        if peers:
            for ip, port in peers:
                self.discovered_listbox.insert(tk.END, f"{ip}:{port}")
            self._log_system(f"Found {len(peers)} peer(s)")
        else:
            self._log_system("No peers found on network")
    
    def _on_connect_selected(self):
        """Connect to selected peer from discovery list."""
        selection = self.discovered_listbox.curselection()
        if not selection:
            messagebox.showwarning("Select Peer", "Please select a peer from the list")
            return
        
        peer_str = self.discovered_listbox.get(selection[0])
        ip, port = peer_str.split(':')
        self._connect_to_peer(ip, int(port))
    
    def _on_manual_connect(self):
        """Handle manual connect button."""
        ip = self.ip_entry.get().strip()
        port_str = self.port_entry.get().strip()
        
        if not ip:
            messagebox.showwarning("Input Required", "Please enter an IP address")
            return
        
        try:
            port = int(port_str) if port_str else 5000
        except ValueError:
            messagebox.showwarning("Invalid Port", "Port must be a number")
            return
        
        self._connect_to_peer(ip, port)
    
    def _connect_to_peer(self, ip: str, port: int):
        """Connect to a peer."""
        self._log_system(f"Connecting to {ip}:{port}...")
        
        def do_connect():
            success = self.peer.connections.connect_to_peer(ip, port)
            if success:
                # Send connection request
                from .protocol import create_connection_request
                conn = self.peer.connections._connections.get(ip)
                if conn:
                    req = create_connection_request("")
                    conn.socket.sendall(req.to_bytes() + b'\n')
                self.root.after(0, lambda: self._log_system(f"Connected to {ip}, waiting for approval..."))
            else:
                self.root.after(0, lambda: self._log_error(f"Could not connect to {ip}:{port}"))
        
        threading.Thread(target=do_connect, daemon=True).start()
    
    def _on_accept(self):
        """Accept pending connection."""
        if self.pending_requests:
            peer_ip = next(iter(self.pending_requests))
            if self.peer.connections.accept_connection(peer_ip):
                self._log_system(f"Accepted connection from {peer_ip}")
                self.pending_requests.discard(peer_ip)
                self._update_pending_ui()
                self._update_connected_list()
            else:
                self._log_error(f"Could not accept connection from {peer_ip}")
    
    def _on_reject(self):
        """Reject pending connection."""
        if self.pending_requests:
            peer_ip = next(iter(self.pending_requests))
            self.peer.connections.reject_connection(peer_ip)
            self._log_system(f"Rejected connection from {peer_ip}")
            self.pending_requests.discard(peer_ip)
            self._update_pending_ui()
    
    def _on_send_message(self, event):
        """Send a chat message."""
        content = self.message_entry.get().strip()
        if not content:
            return
        
        sent_count = self.peer.connections.broadcast_message(content)
        if sent_count > 0:
            self._log_outgoing(content)
        else:
            self._log_error("No approved connections. Message not sent.")
        
        self.message_entry.delete(0, tk.END)
    
    # ==================== Peer Callbacks ====================
    
    def _on_message_received(self, sender: str, message):
        """Handle incoming message from peer."""
        from .protocol import MessageType
        
        def handle():
            if message.msg_type == MessageType.MESSAGE:
                self._log_incoming(sender, message.payload)
            elif message.msg_type == MessageType.CONNECTION_REQUEST:
                self.pending_requests.add(sender)
                self._update_pending_ui()
                self._log_system(f"{sender} wants to connect")
            elif message.msg_type == MessageType.CONNECTION_ACCEPT:
                self._log_system(f"Connection accepted by {sender}!")
                self._update_connected_list()
            elif message.msg_type == MessageType.CONNECTION_REJECT:
                self._log_error(f"Connection rejected by {sender}")
        
        self.root.after(0, handle)
    
    def _on_peer_connected(self, peer_ip: str):
        """Handle new peer connection."""
        self.root.after(0, lambda: self._log_system(f"Peer connected: {peer_ip}"))
    
    def _on_peer_disconnected(self, peer_ip: str):
        """Handle peer disconnection."""
        def handle():
            self._log_system(f"Peer disconnected: {peer_ip}")
            self.pending_requests.discard(peer_ip)
            self._update_pending_ui()
            self._update_connected_list()
        
        self.root.after(0, handle)
    
    # ==================== UI Updates ====================
    
    def _update_pending_ui(self):
        """Update pending connection request UI."""
        if self.pending_requests:
            peer_ip = next(iter(self.pending_requests))
            self.pending_label.config(text=f"⚠ {peer_ip} wants to connect")
            self.pending_frame.pack(fill=tk.X, pady=(0, 5))
        else:
            self.pending_frame.pack_forget()
    
    def _update_connected_list(self):
        """Update connected peers list."""
        self.connected_listbox.delete(0, tk.END)
        for peer_ip in self.peer.connections.connected_peers:
            approved = self.peer.connections.is_peer_approved(peer_ip)
            status = "✓" if approved else "⏳"
            self.connected_listbox.insert(tk.END, f"{status} {peer_ip}")
    
    # ==================== Logging ====================
    
    def _log_message(self, text: str, tag: str = None):
        """Log a message to chat display."""
        self.chat_display.config(state=tk.NORMAL)
        if tag:
            self.chat_display.insert(tk.END, text + "\n", tag)
        else:
            self.chat_display.insert(tk.END, text + "\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def _log_system(self, text: str):
        self._log_message(f"[SYSTEM] {text}", 'system')
    
    def _log_incoming(self, sender: str, text: str):
        self._log_message(f"[{sender}] {text}", 'incoming')
    
    def _log_outgoing(self, text: str):
        self._log_message(f"[YOU] {text}", 'outgoing')
    
    def _log_error(self, text: str):
        self._log_message(f"[ERROR] {text}", 'error')
