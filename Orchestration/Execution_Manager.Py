"""
Execution_Manager.py
Supreme Computation OS (SC-OS)
Execution Manager: orchestrates deterministic-quantum hybrid workflows.
"""

class ExecutionManager:

    def __init__(self, classical_layer=None, quantum_layer=None, router=None):
        self.classical = classical_layer
        self.quantum = quantum_layer
        self.router = router
        self.log = []

    def load_layers(self, classical_layer, quantum_layer, router):
        """Attach execution layers to the manager."""
        self.classical = classical_layer
        self.quantum = quantum_layer
        self.router = router
        self.log.append("Layers loaded.")

    def run(self, input_state):
        """
        Orchestrate a full SC-OS execution cycle:
        1. Classical deterministic preprocessing
        2. Quantum-native routing + transformation
        3. Classical reconstruction for stable output
        """

        if not (self.classical and self.quantum and self.router):
            raise Exception("ExecutionManager is missing one or more layers.")

        # Step 1: Classical deterministic pass
        classical_out = self.classical.process(input_state)
        self.log.append(f"Classical out: {classical_out}")

        # Step 2: Route into quantum layer
        quantum_ready = self.router.route(classical_out)
        self.log.append(f"Router out: {quantum_ready}")

        # Step 3: Execute quantum-native logic
        quantum_out = self.quantum.execute(quantum_ready)
        self.log.append(f"Quantum out: {quantum_out}")

        # Step 4: Classical reconstruction
        final_out = self.classical.reconstruct(quantum_out)
        self.log.append(f"Final out: {final_out}")

        return final_out

    def summary(self):
        """Return execution history."""
        return {
            "steps": len(self.log),
            "history": self.log
        }
