import tkinter as tk
from tkinter import ttk, messagebox
import socket

class StartupDialog:
    
    def __init__(self):
        self.result = None
        self.root = tk.Tk()
        self.root.title("P2P Communication - Setup")
        self.root.geometry("400x450")
        self.root.resizable(False, False)
        
        self.bg_color = '#121212'
        self.fg_color = '#d4d4d4'
        self.accent_color = '#007acc'
        self.input_bg = '#1e1e1e'
        
        self.root.configure(bg=self.bg_color)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(
            'TCombobox', 
            fieldbackground=self.input_bg,
            background=self.bg_color,
            foreground='white',
            arrowcolor='white',
            bordercolor=self.input_bg,
            selectbackground=self.accent_color,
            selectforeground='white'
        )
        
        style.map('TCombobox', 
            fieldbackground=[('readonly', self.input_bg)],
            selectbackground=[('readonly', self.input_bg)],
            selectforeground=[('readonly', 'white')],
            foreground=[('readonly', 'white')]
        )
        self.root.option_add('*TCombobox*Listbox.background', self.input_bg)
        self.root.option_add('*TCombobox*Listbox.foreground', 'white')
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.accent_color)
        self.root.option_add('*TCombobox*Listbox.selectForeground', 'white')
        self.root.option_add('*TCombobox*Listbox.font', ('Segoe UI', 10))
        
        self._build_ui()
        
    def _is_port_free(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) != 0
        
    def _build_ui(self):
        self.root.eval('tk::PlaceWindow . center')
        
        title_lbl = tk.Label(
            self.root, 
            text="WELCOME", 
            font=('Segoe UI', 20, 'bold'),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title_lbl.pack(pady=(40, 10))
        
        subtitle_lbl = tk.Label(
            self.root, 
            text="Configure your session", 
            font=('Segoe UI', 10),
            bg=self.bg_color,
            fg='#858585'
        )
        subtitle_lbl.pack(pady=(0, 30))
        
        form_frame = tk.Frame(self.root, bg=self.bg_color)
        form_frame.pack(fill=tk.X, padx=40)
        
        tk.Label(
            form_frame, 
            text="USERNAME *", 
            font=('Segoe UI', 9, 'bold'),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.username_entry = tk.Entry(
            form_frame,
            font=('Segoe UI', 11),
            bg=self.input_bg,
            fg='white',
            insertbackground='white',
            relief=tk.FLAT,
            bd=5
        )
        self.username_entry.pack(fill=tk.X, pady=(0, 20), ipady=3)
        self.username_entry.focus()
        
        tk.Label(
            form_frame, 
            text="PORT", 
            font=('Segoe UI', 9, 'bold'),
            bg=self.bg_color,
            fg=self.fg_color
        ).pack(anchor=tk.W, pady=(0, 5))
        
        available_ports = [str(p) for p in range(5000, 5011)]
        
        self.port_combo = ttk.Combobox(
            form_frame,
            values=available_ports,
            font=('Segoe UI', 11),
            state="readonly"
        )
        if available_ports:
            self.port_combo.current(0)
            
        self.port_combo.pack(fill=tk.X, pady=(0, 30), ipady=3)
        
        start_btn = tk.Button(
            self.root,
            text="START SESSION",
            font=('Segoe UI', 11, 'bold'),
            bg=self.accent_color,
            fg='white',
            activebackground='#0098ff',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self._on_start
        )
        start_btn.pack(fill=tk.X, padx=40, ipady=10)
        
        self.root.bind('<Return>', lambda e: self._on_start())
        
    def _on_start(self):
        username = self.username_entry.get().strip()
        port_str = self.port_combo.get().strip()
        
        if not username:
             messagebox.showwarning("Required", "Username is required to continue.")
             self.username_entry.focus()
             return
        
        if len(username) > 12:
             messagebox.showwarning("Username Too Long", "Username must be 12 characters or less.\nCurrent length: " + str(len(username)))
             self.username_entry.focus()
             return
            
        try:
            port = int(port_str)
            if not self._is_port_free(port):
                messagebox.showerror("Port Busy", f"Port {port} is already in use.\nPlease select another port.")
                return
        except ValueError:
             messagebox.showerror("Invalid Port", "Please select a valid port.")
             return
             
        self.result = {'username': username, 'port': port}
        self.root.destroy()
        
    def run(self):
        self.root.mainloop()
        return self.result
