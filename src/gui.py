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
    
    # Color scheme - Professional Engineering / Dark Modern
    COLORS = {
        'bg_dark': '#121212',      # Very dark charcoal
        'bg_medium': '#1e1e1e',    # Standard dark gray (VS Code style)
        'bg_light': '#2d2d30',     # Lighter gray for interactive elements
        'accent': '#007acc',       # Professional Blue (Focus/Action)
        'accent_hover': '#0098ff', # Brighter blue for hover
        'text': '#d4d4d4',         # Soft white/light gray
        'text_bright': '#ffffff',  # Bright white for importance
        'text_dim': '#858585',     # Dimmed text
        'success': '#4caf50',      # Modern Green
        'warning': '#ffc107',      # Amber
        'error': '#f44336',        # Modern Red
        'border': '#333333'        # Subtle border
    }
    
    def __init__(self, peer, username="User"):
        """Initialize GUI with a Peer instance."""
        self.peer = peer
        self.username = username
        self.root = tk.Tk()
        self.root.title(f"P2P Communication - {username}")
        self.root.geometry("800x650")
        self.root.minsize(640, 360)
        self.root.configure(bg=self.COLORS['bg_dark'])
        
        # Data storage
        self.pending_requests: Set[str] = set()
        self.all_discovered_peers: Set[Tuple[str, int, str]] = set()
        self.approved_peer_info: Set[Tuple[str, int, str]] = set()  # Track approved connections (ip, port, username)
        
        # Setup styles
        self._setup_styles()
        
        # Build UI
        self._build_ui()
        
        # Wire up peer callbacks
        self._setup_callbacks()
        
        # Start peer services
        self._start_peer()

    # ... (styles and build_ui methods remain unchanged)


    


    def _filter_peers(self):
        """Filter peers - show only disconnected peers."""
        self.discovered_listbox.delete(0, tk.END)
        
        for ip, port, username in self.all_discovered_peers:
            # Check if this SPECIFIC peer (IP+Port+Username) is approved/connected
            if (ip, port, username) not in self.approved_peer_info:
                display_text = f"{username} [{ip}:{port}]"
                self.discovered_listbox.insert(tk.END, display_text)

    def _on_search_peers(self, event):
        """Handle search input change."""
        self._filter_peers()
    

    
    def _on_disconnect_selected(self):
        """Disconnect selected peer."""
        selection = self.connected_listbox.curselection()
        if not selection:
            return
            
        # Parse connection string: "✓ USERNAME [IP:PORT]" or "✓ IP"
        item_text = self.connected_listbox.get(selection[0])
        
        # Try to extract IP from brackets first
        if '[' in item_text and ']' in item_text:
            # Format: "✓ USERNAME [IP:PORT]"
            bracket_content = item_text[item_text.index('[')+1:item_text.index(']')]
            peer_ip = bracket_content.split(':')[0]  # Get IP part
        else:
            # Fallback: "✓ IP"
            parts = item_text.split()
            if len(parts) >= 2:
                peer_ip = parts[1]
            else:
                return
        
        self.peer.connections.disconnect_peer(peer_ip)
    # Log removed to avoid duplication with _on_peer_disconnected callback
    # self._log_system(f"Disconnected from {peer_ip}")

    
    def _setup_styles(self):
        """Configure ttk styles for modern look."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # General configurations
        main_font = ('Segoe UI', 10)
        header_font = ('Segoe UI', 12, 'bold')
        mono_font = ('Consolas', 10)
        
        # Button styles
        style.configure(
            'Action.TButton',
            background=self.COLORS['bg_light'],
            foreground=self.COLORS['text_bright'],
            borderwidth=0,
            focusthickness=0,
            font=('Segoe UI', 10, 'bold'),
            padding=(10, 8)
        )
        style.map('Action.TButton',
            background=[('active', self.COLORS['accent'])],
            foreground=[('active', 'white')]
        )
        
        # Success button
        style.configure(
            'Success.TButton',
            background=self.COLORS['success'],
            foreground='white',
            borderwidth=0,
            font=('Segoe UI', 10, 'bold'),
            padding=(10, 8)
        )
        style.map('Success.TButton',
            background=[('active', '#43a047')] # Slightly darker green on hover
        )
        
        # Danger button
        style.configure(
            'Danger.TButton',
            background=self.COLORS['error'],
            foreground='white',
            borderwidth=0,
            font=('Segoe UI', 10, 'bold'),
            padding=(10, 8)
        )
        style.map('Danger.TButton',
            background=[('active', '#d32f2f')] # Slightly darker red on hover
        )
        
        # Label styles
        style.configure(
            'Header.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_bright'],
            font=header_font
        )
        
        style.configure(
            'Info.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text'],
            font=main_font
        )
        
        style.configure(
            'Dim.TLabel',
            background=self.COLORS['bg_dark'],
            foreground=self.COLORS['text_dim'],
            font=('Segoe UI', 9)
        )
    
    def _build_ui(self):
        """Build the main UI layout."""
        # Main container with padding
        main_frame = tk.Frame(self.root, bg=self.COLORS['bg_dark'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top bar - Network Info
        self._build_top_bar(main_frame)
        
        # --- Scrollable Content Area ---
        # Create container for canvas and scrollbar
        content_container = tk.Frame(main_frame, bg=self.COLORS['bg_dark'], bd=0, highlightthickness=0)
        content_container.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Canvas and Scrollbar setup
        self.canvas = tk.Canvas(content_container, bg=self.COLORS['bg_dark'], highlightthickness=0, bd=0)
        self.scrollbar = ttk.Scrollbar(content_container, orient="vertical", command=self.canvas.yview)
        
        # Scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.COLORS['bg_dark'])
        
        # Create window in canvas
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas (scrollbar packed dynamically)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Event bindings for dynamic layout
        self.scrollable_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # --- Content Construction ---
        # Left panel - Discovery & Peers
        self._build_left_panel(self.scrollable_frame)
        
        # Right panel - Chat area
        self._build_chat_panel(self.scrollable_frame)

    def _on_frame_configure(self, event=None):
        """Handle scrollable frame resizing."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self._check_scroll_necessity()

    def _on_canvas_configure(self, event=None):
        """Handle canvas resizing."""
        # Match width exactly
        self.canvas.itemconfig(self.canvas_window, width=event.width)
        self._check_scroll_necessity()

    def _check_scroll_necessity(self):
        """Show/hide scrollbar based on content vs canvas height."""
        # Get dimensions
        canvas_height = self.canvas.winfo_height()
        _, _, _, req_height = self.canvas.bbox("all") or (0,0,0,0)
        
        if req_height > canvas_height and canvas_height > 10:
            # Content is taller than view - Show scrollbar
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
                # Re-bind mousewheel
                self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        else:
            # Content fits - Hide scrollbar
            if self.scrollbar.winfo_ismapped():
                self.scrollbar.pack_forget()
                self.canvas.unbind_all("<MouseWheel>")
                self.canvas.yview_moveto(0)
            
            # Specific fix: If content is smaller, force frame height to canvas height
            # so relative packing (expand=True) works for full height visuals
            if canvas_height > 1:
                self.canvas.itemconfig(self.canvas_window, height=canvas_height)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        if self.scrollbar.winfo_ismapped():
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _build_top_bar(self, parent):
        """Build the top information bar."""
        top_frame = tk.Frame(parent, bg=self.COLORS['bg_medium'], height=60)
        top_frame.pack(fill=tk.X)
        top_frame.pack_propagate(False)
        
        # Left side - App title
        title_label = tk.Label(
            top_frame,
            text="P2P COMMUNICATION",
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_bright'],
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        # Right side - Network info
        info_frame = tk.Frame(top_frame, bg=self.COLORS['bg_medium'])
        info_frame.pack(side=tk.RIGHT, padx=15)
        
        # IP Address (Selectable)
        tk.Label(
            info_frame,
            text="IP:",
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['accent'],
            font=('Segoe UI', 10, 'bold')
        ).pack(side=tk.LEFT)
        
        self.ip_display = tk.Entry(
            info_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['accent'],
            font=('Segoe UI', 10, 'bold'),
            bd=0,
            readonlybackground=self.COLORS['bg_medium'],
            width=15
        )
        self.ip_display.insert(0, self.peer.local_ip)
        self.ip_display.config(state='readonly')
        self.ip_display.pack(side=tk.LEFT, padx=(5, 15))
        
        # Port (Selectable)
        tk.Label(
            info_frame,
            text="PORT:",
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['warning'],
            font=('Segoe UI', 10, 'bold')
        ).pack(side=tk.LEFT)
        
        self.port_display = tk.Entry(
            info_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['warning'],
            font=('Segoe UI', 10, 'bold'),
            bd=0,
            readonlybackground=self.COLORS['bg_medium'],
            width=6
        )
        self.port_display.insert(0, str(self.peer.tcp_port))
        self.port_display.config(state='readonly')
        self.port_display.pack(side=tk.LEFT, padx=(5, 15))
        
        # User Info
        user_label = tk.Label(
            info_frame,
            text=f"👤 {self.username.upper()}",
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['success'],
            font=('Segoe UI', 10, 'bold')
        )
        user_label.pack(side=tk.LEFT, padx=10)
    
    def _build_left_panel(self, parent):
        """Build left panel with discovery and peer list."""
        left_frame = tk.Frame(parent, bg=self.COLORS['bg_dark'], width=340)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)  # Force width to remain 340, allowing contents to expand
        
        # -- Discovery Section --
    # -- Discovery Section --
        discovery_frame = tk.LabelFrame(
            left_frame,
            text=" NETWORK DISCOVERY ",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_dim'],
            font=('Segoe UI', 9, 'bold'),
            bd=1,
            relief=tk.FLAT
        )
        discovery_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Connect button (Pack first to ensure visibility at bottom)
        self.connect_btn = ttk.Button(
            discovery_frame,
            text="CONNECT",
            style='Success.TButton',
            command=self._on_connect_selected
        )
        self.connect_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(5, 10))
        
        # Discover button (Pack at top)
        self.discover_btn = ttk.Button(
            discovery_frame,
            text="SCAN NETWORK",
            style='Action.TButton',
            command=self._on_discover
        )
        self.discover_btn.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))
        
        # Found Peers Label
        tk.Label(
            discovery_frame,
            text="FOUND PEERS",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_dim'],
            font=('Segoe UI', 9, 'bold'),
            anchor='w'  # Left align
        ).pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))
        
        # Listbox with horizontal scroll
        discovered_list_frame = tk.Frame(discovery_frame, bg=self.COLORS['bg_dark'])
        discovered_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        discovered_xscroll = tk.Scrollbar(discovered_list_frame, orient=tk.HORIZONTAL, bg=self.COLORS['bg_dark'])
        discovered_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.discovered_listbox = tk.Listbox(
            discovered_list_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_bright'],
            font=('Segoe UI', 10),
            selectbackground=self.COLORS['accent'],
            bd=0,
            highlightthickness=1,
            highlightcolor=self.COLORS['border'],
            height=6,
            xscrollcommand=discovered_xscroll.set
        )
        self.discovered_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        discovered_xscroll.config(command=self.discovered_listbox.xview)
        
        # -- Connected Peers --
        connected_frame = tk.LabelFrame(
            left_frame,
            text=" CONNECTED PEERS ",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_dim'],
            font=('Segoe UI', 9, 'bold'),
            bd=1,
            relief=tk.FLAT
        )
        connected_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 0))
        
        # Disconnect button (Pack first to ensure visibility at bottom)
        self.disconnect_btn = ttk.Button(
            connected_frame,
            text="DISCONNECT",
            style='Danger.TButton',
            command=self._on_disconnect_selected
        )
        self.disconnect_btn.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
        
        # Connected listbox with horizontal scroll
        connected_list_frame = tk.Frame(connected_frame, bg=self.COLORS['bg_dark'])
        connected_list_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        connected_xscroll = tk.Scrollbar(connected_list_frame, orient=tk.HORIZONTAL, bg=self.COLORS['bg_dark'])
        connected_xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.connected_listbox = tk.Listbox(
            connected_list_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_bright'],
            font=('Segoe UI', 10),
            selectbackground=self.COLORS['accent'],
            bd=0,
            highlightthickness=0,
            height=6,
            xscrollcommand=connected_xscroll.set
        )
        self.connected_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        connected_xscroll.config(command=self.connected_listbox.xview)
    
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
            font=('Segoe UI', 10, 'bold')
        )
        self.pending_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        self.accept_btn = tk.Button(
            self.pending_frame,
            text="ACCEPT",
            bg=self.COLORS['success'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            bd=0,
            command=self._on_accept
        )
        self.accept_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.reject_btn = tk.Button(
            self.pending_frame,
            text="REJECT",
            bg=self.COLORS['error'],
            fg='white',
            font=('Segoe UI', 9, 'bold'),
            bd=0,
            command=self._on_reject
        )
        self.reject_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Chat display area
        chat_label_frame = tk.LabelFrame(
            chat_frame,
            text=" MESSAGES ",
            bg=self.COLORS['bg_dark'],
            fg=self.COLORS['text_dim'],
            font=('Segoe UI', 9, 'bold'),
            bd=1,
            relief=tk.FLAT
        )
        chat_label_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_label_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_bright'],
            font=('Consolas', 10),
            wrap=tk.WORD,
            state=tk.DISABLED,
            bd=0,
            highlightthickness=0,
            height=12  # Reduce chat height to ensure fit on 540p screens
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure('system', foreground=self.COLORS['warning'])
        self.chat_display.tag_configure('incoming', foreground=self.COLORS['success'])
        self.chat_display.tag_configure('outgoing', foreground=self.COLORS['accent_hover'])
        self.chat_display.tag_configure('error', foreground=self.COLORS['error'])
        
        # Message input area
        input_frame = tk.Frame(chat_frame, bg=self.COLORS['bg_dark'])
        input_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.message_entry = tk.Entry(
            input_frame,
            bg=self.COLORS['bg_medium'],
            fg=self.COLORS['text_bright'],
            font=('Segoe UI', 11),
            insertbackground=self.COLORS['text_bright'],
            bd=0,
            highlightthickness=2,
            highlightcolor=self.COLORS['accent']
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=10)
        self.message_entry.bind('<Return>', self._on_send_message)
        
        send_btn = tk.Button(
            input_frame,
            text="SEND",
            bg=self.COLORS['accent'],
            fg='white',
            font=('Segoe UI', 10, 'bold'),
            bd=0,
            padx=25,
            command=lambda: self._on_send_message(None)
        )
        send_btn.pack(side=tk.RIGHT, padx=(10, 0), ipady=10)
    
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
    
    def _update_discovered_peers(self, peers: Set[Tuple[str, int, str]]):
        """Update the discovered peers list."""
        self.discover_btn.config(state=tk.NORMAL)
        self.all_discovered_peers.update(peers)  # Merge new results with existing
        self._filter_peers()
        
        # Calculate filtered count (peers not currently connected)
        connected_ips = set(self.peer.connections.connected_peers)
        filtered_peers = [p for p in peers if p[0] not in connected_ips]
        count = len(filtered_peers)
        
        if count > 0:
            self._log_system(f"Scan complete. Found {count} peer(s).")
        else:
            # If we found peers but they are all connected to us
            if peers:
                self._log_system("Scan complete. Found 0 new peer(s).")
            else:
                self._log_system("No peers found on network")
    
    def _on_connect_selected(self):
        """Connect to selected peer from discovery list."""
        selection = self.discovered_listbox.curselection()
        if not selection:
            messagebox.showwarning("Select Peer", "Please select a peer from the list")
            return
        
        peer_str = self.discovered_listbox.get(selection[0])
        # Format: "Username [IP:Port]"
        try:
            # Extract content inside last brackets
            last_open = peer_str.rfind('[')
            last_close = peer_str.rfind(']')
            
            if last_open == -1 or last_close == -1:
                # Fallback for parentheses
                last_open = peer_str.rfind('(')
                last_close = peer_str.rfind(')')
                if last_open == -1 or last_close == -1:
                    raise ValueError("Invalid format")
            
            ip_port = peer_str[last_open+1:last_close]
            ip, port_str = ip_port.split(':')
            self._connect_to_peer(ip, int(port_str))
            
        except Exception:
             self._log_error(f"Could not parse peer info: {peer_str}")
    

    
    def _connect_to_peer(self, ip: str, port: int):
        """Connect to a peer."""
        display_name = self._get_peer_display_name(ip, port)
        self._log_system(f"Connecting to {display_name}...")
        
        def do_connect():
            success = self.peer.connections.connect_to_peer(ip, port)
            if success:
                # Send connection request with our username:port in payload
                from .protocol import Message, MessageType
                # Use get_connection with port to identify specific connection
                conn = self.peer.connections.get_connection(ip, port)
                if conn:
                    # Payload is username:port
                    payload = f"{self.peer.username}:{self.peer.tcp_port}"
                    req = Message(MessageType.CONNECTION_REQUEST, self.peer.local_ip, payload)
                    conn.socket.sendall(req.to_bytes() + b'\n')
                self.root.after(0, lambda: self._log_system(f"Connected to {display_name}, waiting for approval..."))
            else:
                self.root.after(0, lambda: self._log_error(f"Could not connect to {display_name}"))
        
        threading.Thread(target=do_connect, daemon=True).start()
    
    def _on_accept(self):
        """Accept pending connection."""
        if self.pending_requests:
            peer_ip = next(iter(self.pending_requests))
            
            # Get connection list
            conns = self.peer.connections._connections.get(peer_ip)
            if not conns:
                self._log_error(f"Connection not found for {peer_ip}")
                self.pending_requests.discard(peer_ip)
                self._update_pending_ui()
                return
            
            # Find the first unapproved connection
            conn = None
            # Handle list structure (new)
            for c in conns:
                if not c.is_approved:
                    conn = c
                    break
            
            if not conn:
                self._log_system("No pending connection to accept.")
                self.pending_requests.discard(peer_ip)
                self._update_pending_ui()
                return
            
            try:
                # Send ACCEPT message with our username:port
                from .protocol import Message, MessageType
                payload = f"{self.peer.username}:{self.peer.tcp_port}"
                accept_msg = Message(MessageType.CONNECTION_ACCEPT, self.peer.local_ip, payload)
                conn.socket.sendall(accept_msg.to_bytes() + b'\n')
                
                # Update connection state
                conn.is_approved = True
                
                # Find and track approved peer info from all_discovered_peers
                for d_ip, d_port, d_user in self.all_discovered_peers:
                    if d_ip == peer_ip:
                        self.approved_peer_info.add((d_ip, d_port, d_user))
                        break
                
                self._log_system(f"Accepted connection from {self._get_peer_display_name(peer_ip)}")
                
                # Check if any more unapproved connections exist from this IP
                any_pending = any(not c.is_approved for c in conns)
                if not any_pending:
                    self.pending_requests.discard(peer_ip)
                    
                self._update_pending_ui()
                self._update_connected_list()
            except Exception as e:
                self._log_error(f"Could not accept connection: {e}")
    
    def _on_reject(self):
        """Reject pending connection."""
        if self.pending_requests:
            peer_ip = next(iter(self.pending_requests))
            self.peer.connections.reject_connection(peer_ip)
            self._log_system(f"Rejected connection from {self._get_peer_display_name(peer_ip)}")
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
    
    def _on_message_received(self, sender_ip: str, sender_port: int, message):
        """Handle incoming message from peer."""
        from .protocol import MessageType
        
        def handle():
            if message.msg_type == MessageType.MESSAGE:
                self._log_incoming(sender_ip, sender_port, message.payload)
            elif message.msg_type == MessageType.CONNECTION_REQUEST:
                # Parse payload: USERNAME:PORT
                requester_name = "Unknown User"
                requester_port = 5000
                if message.payload and ':' in message.payload:
                    parts = message.payload.split(':')
                    requester_name = parts[0]
                    try:
                        requester_port = int(parts[1])
                    except (ValueError, IndexError):
                        pass
                elif message.payload:
                    requester_name = message.payload
                
                # Register this peer so we can show their name in messages
                peer_info = (sender_ip, requester_port, requester_name)
                # Remove old entry if exists (by IP AND port to handle multiple connections)
                self.all_discovered_peers = {p for p in self.all_discovered_peers if not (p[0] == sender_ip and p[1] == sender_port)}
                self.all_discovered_peers.add(peer_info)
                
                # NOW add to pending and update UI (after peer info is registered)
                self.pending_requests.add(sender_ip)
                self._update_pending_ui()
                
                self._log_system(f"Connection request from {requester_name} ({sender_ip}:{requester_port})")
            elif message.msg_type == MessageType.CONNECTION_ACCEPT:
                # Parse payload: USERNAME:PORT (if available)
                accepter_name = "Unknown User"
                accepter_port = 5000
                if message.payload and ':' in message.payload:
                    parts = message.payload.split(':')
                    accepter_name = parts[0]
                    try:
                        accepter_port = int(parts[1])
                    except (ValueError, IndexError):
                        pass
                elif message.payload and message.payload not in ["CONNECTION_ACCEPTED", "REQUEST_CONNECTION"]:
                    # Legacy or just username
                    accepter_name = message.payload
                
                # Register this peer
                peer_info = (sender_ip, accepter_port, accepter_name)
                self.all_discovered_peers = {p for p in self.all_discovered_peers if not (p[0] == sender_ip and p[1] == sender_port)}
                self.all_discovered_peers.add(peer_info)
                
                # Track as approved connection
                self.approved_peer_info.add(peer_info)
                
                self._log_system(f"Connection accepted by {accepter_name} [{sender_ip}:{accepter_port}]!")
                self._update_connected_list()
            elif message.msg_type == MessageType.CONNECTION_REJECT:
                self._log_error(f"Connection rejected by {self._get_peer_display_name(sender_ip, sender_port)}")
        
        self.root.after(0, handle)
    
    def _on_peer_connected(self, peer_ip: str):
        """Handle new peer connection."""
        pass
    
    def _on_peer_disconnected(self, peer_ip: str, peer_port: int = None):
        """Handle peer disconnection."""
        def handle():
            self._log_system(f"Peer disconnected: {self._get_peer_display_name(peer_ip, peer_port)}")
            
            # Remove specific approved peer info by IP and port
            if peer_port is not None:
                self.approved_peer_info = {p for p in self.approved_peer_info if not (p[0] == peer_ip and p[1] == peer_port)}
            else:
                # Fallback: remove all from this IP
                self.approved_peer_info = {p for p in self.approved_peer_info if p[0] != peer_ip}
            
            self.pending_requests.discard(peer_ip)
            self._update_pending_ui()
            self._update_connected_list()
            self._filter_peers()
        
        self.root.after(0, handle)
    
    # ==================== UI Updates ====================
    
    def _update_pending_ui(self):
        """Update pending connection request UI."""
        if self.pending_requests:
            peer_ip = next(iter(self.pending_requests))
            # Use display name format like other places (username [IP:port])
            peer_display = self._get_peer_display_name(peer_ip)
            self.pending_label.config(text=f"⚠ {peer_display} wants to connect")
            self.pending_frame.pack(fill=tk.X, pady=(0, 5))
        else:
            self.pending_frame.pack_forget()
    
    def _update_connected_list(self):
        """Update connected peers list."""
        self.connected_listbox.delete(0, tk.END)
        
        # Show all approved connections (handles multiple connections per IP correctly)
        for ip, port, username in self.approved_peer_info:
            display_text = f"{username} [{ip}:{port}]"
            self.connected_listbox.insert(tk.END, display_text)
        
        # Update Found Peers list to hide connected peers
        self._filter_peers()
    
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
    
    def _get_peer_display_name(self, ip: str, port: int = None) -> str:
        """Resolve IP to Username [IP:Port] format if available."""
        # Prioritize exact match if port is provided
        if port is not None:
             for peer_ip, peer_port, username in self.all_discovered_peers:
                 if peer_ip == ip and peer_port == port:
                     return f"{username} [{ip}:{port}]"
                     
        # Fallback to IP match
        for peer_ip, peer_port, username in self.all_discovered_peers:
            if peer_ip == ip:
                return f"{username} [{ip}:{peer_port}]"
        return f"[{ip}]"

    def _log_incoming(self, sender_ip: str, sender_port: int, text: str):
        display_name = self._get_peer_display_name(sender_ip, sender_port)
        self._log_message(f"{display_name}: {text}", 'incoming')
    
    def _log_outgoing(self, text: str):
        self._log_message(f"[YOU] {text}", 'outgoing')
    
    def _log_error(self, text: str):
        self._log_message(f"[ERROR] {text}", 'error')
