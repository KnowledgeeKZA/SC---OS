# Unity Protocol Layer (UPL) for SC-OS
# Handles node-to-node communication, coherence sync, and network-wide messaging.

class UnityProtocol:
    def __init__(self):
        self.nodes = {}            # Registered nodes
        self.messages = []         # Message log (optional)
        self.topology = {}         # Network topology map

    def register_node(self, node_id, metadata=None):
        """Register a new SC-OS node into the network."""
        self.nodes[node_id] = metadata or {}
        return {"status": "registered", "node": node_id}

    def broadcast(self, source_node, payload):
        """Broadcast a message to all nodes."""
        packet = {
            "from": source_node,
            "payload": payload
        }
        for node in self.nodes:
            if node != source_node:
                self.messages.append((node, packet))
        return {"delivered_to": list(self.nodes.keys())}

    def sync_coherence(self, node_id, coherence_state):
        """Update the network with a node's coherence state."""
        if node_id not in self.nodes:
            return {"error": "node not registered"}

        self.nodes[node_id]["coherence"] = coherence_state
        return {"status": "synced", "node": node_id}

    def get_network_state(self):
        """Return full network topology + coherence map."""
        return {
            "nodes": self.nodes,
            "messages": len(self.messages),
        }
