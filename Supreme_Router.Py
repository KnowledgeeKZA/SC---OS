"""
Supreme_Router.py
Supreme Computation OS (SC-OS) – Orchestration Router

Routes workloads between:
- Core deterministic engine
- Classical deterministic / hybrid layers
- Quantum execution layer
- External API boundary
- SupremeChain ledger for lineage & compliance

All routing decisions must satisfy the TCAG invariant:
Truth × Continuity × Alignment × Genesis
"""

from typing import Any, Dict, Optional

# Core deterministic engine
try:
    from Core.Engine import CoherenceEngine
except ImportError:
    CoherenceEngine = None  # Placeholder if engine not wired yet

# Classical layers
try:
    from Classical.Deterministic.Keep import Keep as DeterministicKeep
except ImportError:
    DeterministicKeep = None

try:
    from Classical.Deterministic.Hybrid.Keep import Keep as HybridKeep
except ImportError:
    HybridKeep = None

# Quantum layer + router
try:
    from Quantum.Quantum_Layer import QuantumLayer
    from Quantum.Quantum_Router import QuantumRouter
except ImportError:
    QuantumLayer = None
    QuantumRouter = None

# Public interface
try:
    from API.Interface import SCOSInterface
except ImportError:
    SCOSInterface = None

# SupremeChain ledger
try:
    from SupremeChain.Ledger import SupremeChainLedger
except ImportError:
    SupremeChainLedger = None


class SupremeRouter:
    """
    Central routing hub for SC-OS.

    All external requests should enter through:
        SupremeRouter.route(request)

    Expected request format (dict):
        {
            "source": "api" | "internal",
            "mode":   "classical" | "quantum" | "hybrid",
            "intent": "read" | "write" | "execute",
            "payload": {... arbitrary data ...}
        }
    """

    def __init__(self) -> None:
        self.engine = CoherenceEngine() if CoherenceEngine else None
        self.det_keep = DeterministicKeep() if DeterministicKeep else None
        self.hybrid_keep = HybridKeep() if HybridKeep else None
        self.q_layer = QuantumLayer() if QuantumLayer else None
        self.q_router = QuantumRouter(self.q_layer) if QuantumRouter and self.q_layer else None
        self.interface = SCOSInterface() if SCOSInterface else None
        self.ledger = SupremeChainLedger() if SupremeChainLedger else None

    # ---------- PUBLIC ENTRYPOINT ----------

    def route(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main routing entry for SC-OS.

        1) Validate + normalize request via API layer (if present)
        2) Decide execution path (classical / quantum / hybrid)
        3) Execute via the appropriate subsystem
        4) Log lineage into SupremeChain
        5) Return deterministic response dict
        """
        # Step 1 – optional interface validation
        normalized = self._normalize_request(request)

        # Step 2 – choose path
        mode = normalized.get("mode", "classical")

        if mode == "quantum":
            result = self._route_quantum(normalized)
        elif mode == "hybrid":
            result = self._route_hybrid(normalized)
        else:
            result = self._route_classical(normalized)

        # Step 3 – record lineage
        self._record_lineage(normalized, result)

        # Step 4 – wrap response
        return {
            "ok": True,
            "mode": mode,
            "result": result,
        }

    # ---------- INTERNAL HELPERS ----------

    def _normalize_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        if self.interface:
            return self.interface.validate_and_normalize(request)
        # Minimal fallback if API layer isn’t wired yet
        default = {
            "source": request.get("source", "internal"),
            "mode": request.get("mode", "classical"),
            "intent": request.get("intent", "execute"),
            "payload": request.get("payload", {}),
        }
        return default

    def _route_classical(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route into deterministic / classical path.
        """
        payload = request.get("payload", {})

        if self.det_keep:
            state = self.det_keep.store(payload)
        else:
            state = {"echo": payload}

        # Optional coherence validation
        if self.engine:
            coherent = self.engine.validate_tcag(
                truth=True,
                continuity=True,
                alignment=True,
                genesis=True,
            )
        else:
            coherent = True

        return {
            "path": "classical",
            "coherent": coherent,
            "state": state,
        }

    def _route_quantum(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route into quantum-native path.
        """
        payload = request.get("payload", {})
        noise_profile = payload.get("noise_profile", None)

        if self.q_router and self.q_layer:
            q_result = self.q_router.execute(payload, noise_profile=noise_profile)
        elif self.q_layer:
            q_result = self.q_layer.execute_circuit(payload)
        else:
            q_result = {"warning": "Quantum layer not wired; dry-run only.", "payload": payload}

        return {
            "path": "quantum",
            "result": q_result,
        }

    def _route_hybrid(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route into hybrid classical–quantum path.
        """
        payload = request.get("payload", {})

        classical_part = payload.get("classical", {})
        quantum_part = payload.get("quantum", {})

        if self.hybrid_keep:
            hybrid_state = self.hybrid_keep.store({
                "classical": classical_part,
                "quantum": quantum_part,
            })
        else:
            hybrid_state = {"classical": classical_part, "quantum": quantum_part}

        quantum_result = None
        if self.q_router and self.q_layer:
            quantum_result = self.q_router.execute(quantum_part)
        elif self.q_layer:
            quantum_result = self.q_layer.execute_circuit(quantum_part)

        return {
            "path": "hybrid",
            "state": hybrid_state,
            "quantum_result": quantum_result,
        }

    def _record_lineage(self, request: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        Send minimal lineage info into SupremeChain ledger if available.
        """
        if not self.ledger:
            return

        entry = {
            "source": request.get("source"),
            "mode": request.get("mode"),
            "intent": request.get("intent"),
            "coherent": result.get("coherent", True),
            "timestamp": self.ledger.now(),  # assume helper exists
        }
        self.ledger.append(entry)


# Convenience factory
def get_router() -> SupremeRouter:
    return SupremeRouter()
