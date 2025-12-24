import sys
import threading
from typing import Callable, Optional, Dict
from enum import Enum


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    @classmethod
    def colorize(cls, text: str, color: str) -> str:
        return f"{color}{text}{cls.RESET}"


class CommandType(Enum):
    DISCOVER = "discover"
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    LIST = "list"
    HELP = "help"
    QUIT = "quit"
    MESSAGE = "message"
    ACCEPT = "accept"
    REJECT = "reject"


class CLICommand:
    
    def __init__(self, cmd_type: CommandType, args: list = None):
        self.type = cmd_type
        self.args = args or []


class ChatCLI:
    
    PROMPT = "> "
    COMMANDS = {
        "/discover": CommandType.DISCOVER,
        "/connect": CommandType.CONNECT,
        "/disconnect": CommandType.DISCONNECT,
        "/list": CommandType.LIST,
        "/help": CommandType.HELP,
        "/quit": CommandType.QUIT,
        "/exit": CommandType.QUIT,
        "/accept": CommandType.ACCEPT,
        "/reject": CommandType.REJECT,
    }
    
    def __init__(self, local_ip: str, port: int):
        self.local_ip = local_ip
        self.port = port
        self._running = False
        self._input_lock = threading.Lock()
        
        self._handlers: Dict[CommandType, Callable] = {}
    
    def register_handler(self, cmd_type: CommandType, handler: Callable) -> None:
        self._handlers[cmd_type] = handler
    
    def print_banner(self) -> None:
        banner = f"""
{Color.CYAN}{'═' * 55}
       P2P Chat Application - Welcome!
{'═' * 55}{Color.RESET}
{Color.GREEN}Your IP:{Color.RESET} {self.local_ip}
{Color.GREEN}Listening on port:{Color.RESET} {self.port}

{Color.YELLOW}[System]{Color.RESET} Type /help for available commands
"""
        print(banner)
    
    def print_help(self) -> None:
        help_text = f"""
{Color.BOLD}Available Commands:{Color.RESET}
  {Color.CYAN}/discover{Color.RESET}           Search for peers on the network
  {Color.CYAN}/connect <ip>{Color.RESET}       Connect to a peer (default port: 5000)
  {Color.CYAN}/connect <ip> <port>{Color.RESET} Connect to a peer on specific port
  {Color.CYAN}/disconnect <ip>{Color.RESET}    Disconnect from a peer
  {Color.CYAN}/list{Color.RESET}               Show connected peers
  {Color.CYAN}/accept <ip>{Color.RESET}        Accept connection request from IP
  {Color.CYAN}/reject <ip>{Color.RESET}        Reject connection request from IP
  {Color.CYAN}/help{Color.RESET}               Show this help message
  {Color.CYAN}/quit{Color.RESET}               Exit the application

{Color.BOLD}Sending Messages:{Color.RESET}
  Just type your message and press Enter to send to all connected peers.
"""
        print(help_text)
    
    def print_system(self, message: str) -> None:
        with self._input_lock:
            print(f"\r{Color.YELLOW}[System]{Color.RESET} {message}")
            if self._running:
                print(self.PROMPT, end='', flush=True)
    
    def print_error(self, message: str) -> None:
        with self._input_lock:
            print(f"\r{Color.RED}[Error]{Color.RESET} {message}")
            if self._running:
                print(self.PROMPT, end='', flush=True)
    
    def print_success(self, message: str) -> None:
        with self._input_lock:
            print(f"\r{Color.GREEN}[OK]{Color.RESET} {message}")
            if self._running:
                print(self.PROMPT, end='', flush=True)
    
    def print_discovery(self, message: str) -> None:
        with self._input_lock:
            print(f"\r{Color.MAGENTA}[Discovery]{Color.RESET} {message}")
            if self._running:
                print(self.PROMPT, end='', flush=True)
    
    def print_connection(self, message: str) -> None:
        with self._input_lock:
            print(f"\r{Color.BLUE}[Connection]{Color.RESET} {message}")
            if self._running:
                print(self.PROMPT, end='', flush=True)
    
    def print_incoming_message(self, sender: str, content: str) -> None:
        with self._input_lock:
            print(f"\r{Color.GREEN}[{sender}]{Color.RESET} {content}")
            if self._running:
                print(self.PROMPT, end='', flush=True)
    
    def print_outgoing_message(self, content: str) -> None:
        with self._input_lock:
            print(f"\r{Color.CYAN}[You]{Color.RESET} {content}")
            if self._running:
                print(self.PROMPT, end='', flush=True)
    
    def parse_command(self, user_input: str) -> CLICommand:
        user_input = user_input.strip()
        
        if not user_input:
            return None
        
        if user_input.startswith('/'):
            parts = user_input.split()
            cmd_str = parts[0].lower()
            args = parts[1:] if len(parts) > 1 else []
            
            if cmd_str in self.COMMANDS:
                return CLICommand(self.COMMANDS[cmd_str], args)
            else:
                self.print_error(f"Unknown command: {cmd_str}")
                return None
        
        return CLICommand(CommandType.MESSAGE, [user_input])
    
    def run(self) -> None:
        self._running = True
        self.print_banner()
        
        try:
            while self._running:
                try:
                    user_input = input(self.PROMPT)
                    command = self.parse_command(user_input)
                    
                    if command:
                        self._execute_command(command)
                        
                except EOFError:
                    break
                except KeyboardInterrupt:
                    print()
                    self._running = False
                    break
                    
        finally:
            self._running = False
    
    def stop(self) -> None:
        self._running = False
    
    def _execute_command(self, command: CLICommand) -> None:
        if command.type == CommandType.HELP:
            self.print_help()
            return
        
        if command.type == CommandType.QUIT:
            self.print_system("Goodbye!")
            self._running = False
            return
        
        if command.type in self._handlers:
            self._handlers[command.type](command.args)
        else:
            self.print_error(f"No handler for command: {command.type.value}")
