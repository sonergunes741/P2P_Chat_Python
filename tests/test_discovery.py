"""
Test Discovery Module
=====================
Unit tests for peer discovery functionality.
"""

import pytest
from src.discovery import PeerDiscovery


class TestPeerDiscovery:
    """Tests for PeerDiscovery class."""
    
    def test_initialization(self):
        """Test PeerDiscovery initialization."""
        discovery = PeerDiscovery(
            local_ip="192.168.1.1",
            broadcast_port=5001,
            tcp_port=5000
        )
        
        assert discovery.local_ip == "192.168.1.1"
        assert discovery.broadcast_port == 5001
        assert discovery.tcp_port == 5000
    
    def test_discovered_peers_initially_empty(self):
        """Test that discovered peers starts empty."""
        discovery = PeerDiscovery(local_ip="192.168.1.1")
        
        assert len(discovery.discovered_peers) == 0
    
    def test_clear_discovered_peers(self):
        """Test clearing discovered peers."""
        discovery = PeerDiscovery(local_ip="192.168.1.1")
        discovery._discovered_peers.add(("192.168.1.2", 5000))
        
        discovery.clear_discovered_peers()
        
        assert len(discovery.discovered_peers) == 0
    
    def test_discovered_peers_returns_copy(self):
        """Test that discovered_peers returns a copy."""
        discovery = PeerDiscovery(local_ip="192.168.1.1")
        discovery._discovered_peers.add(("192.168.1.2", 5000))
        
        peers = discovery.discovered_peers
        peers.add(("192.168.1.3", 5000))  # Modify the copy
        
        # Original should be unchanged
        assert len(discovery.discovered_peers) == 1
    
    def test_callback_registration(self):
        """Test callback registration."""
        discovery = PeerDiscovery(local_ip="192.168.1.1")
        callback_called = {"value": False}
        
        def callback(ip, port):
            callback_called["value"] = True
        
        discovery.set_peer_discovered_callback(callback)
        
        assert discovery._on_peer_discovered is not None


class TestPeerDiscoveryIntegration:
    """Integration tests - require network access."""
    
    @pytest.mark.skip(reason="Requires network access")
    def test_start_stop_listening(self):
        """Test starting and stopping the listener."""
        discovery = PeerDiscovery(
            local_ip="127.0.0.1",
            broadcast_port=15001,
            tcp_port=15000
        )
        
        discovery.start_listening()
        assert discovery._listening is True
        
        discovery.stop_listening()
        assert discovery._listening is False
