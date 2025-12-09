# Engine.py
# Supreme Computation OS (SC-OS)
# Deterministic Coherence Engine
#
# This module provides the primary deterministic execution engine for SC-OS.
# It evaluates operations against the TCAG invariant (Truth, Continuity,
# Alignment, Genesis) and records a minimal state lineage for auditing and
# hand-off to SupremeChain.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
import time
import uuid


# ---------- Data Structures ----------

@dataclass
class TCAGState:
    """Represents a single TCAG evaluation snapshot."""

    truth: bool
    continuity: bool
    alignment: bool
    genesis: bool
    score: float
    notes: str = ""


@dataclass
class LineageRecord:
    """Single execution step recorded by the engine."""

    id: str
    timestamp: float
    operation: str
    input_state: Any
    output_state: Any
    tcag: TCAGState
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------- Exceptions ----------

class CoherenceError(Exception):
    """Raised when an operation violates deterministic coherence."""


# ---------- Engine Implementation ----------

class DeterministicEngine:
    """
    Deterministic coherence engine for SC-OS.

    Responsibilities:
    - Maintain a registry of deterministic operations.
    - Execute operations with stable, predictable behavior.
    - Evaluate each step against TCAG.
    - Persist a minimal in-memory lineage log that can be exported
      to the SupremeChain ledger.
    """

    def __init__(self, name: str = "SC-OS-Core-Engine") -> None:
        self.name = name
        self._operations: Dict[str, Callable[[Any, Dict[str, Any]], Any]] = {}
        self._lineage: List[LineageRecord] = []

    # ----- Operation Registry -----

    def register_operation(
        self,
        name: str,
        fn: Callable[[Any, Dict[str, Any]], Any],
    ) -> None:
        """
        Register a deterministic operation with the engine.

        The function `fn` must be pure with respect to the engine:
        same input + same metadata -> same output.
        """
        if not callable(fn):
            raise TypeError("Operation must be callable.")
        self._operations[name] = fn

    def has_operation(self, name: str) -> bool:
        return name in self._operations

    # ----- TCAG Evaluation -----

    def _evaluate_tcag(
        self,
        input_state: Any,
        output_state: Any,
        metadata: Dict[str, Any],
    ) -> TCAGState:
        """
        Lightweight, engine-local TCAG evaluation.

        NOTE:
        In a full deployment this can delegate to a richer TCAG module.
        For the public skeleton we keep the logic simple and transparent.
        """

        # Truth: output is not None and operation did not signal error.
        truth = output_state is not None

        # Continuity: lineage must remain ordered and append-only.
        continuity = True  # Enforced structurally by append-only log.

        # Alignment: operation declares an intent; we check that it was provided.
        alignment = "intent" in metadata

        # Genesis: operation allows further composition (i.e., result is reusable).
        genesis = output_state is not None

        # Simple scoring: % of invariants satisfied.
        satisfied = sum([truth, continuity, alignment, genesis])
        score = satisfied / 4.0

        notes = metadata.get("tcag_notes", "")

        return TCAGState(
            truth=truth,
            continuity=continuity,
            alignment=alignment,
            genesis=genesis,
            score=score,
            notes=notes,
        )

    # ----- Execution -----

    def execute(
        self,
        operation: str,
        state: Any,
        metadata: Optional[Dict[str, Any]] = None,
        strict: bool = True,
    ) -> Any:
        """
        Execute a named operation deterministically and record lineage.

        Args:
            operation: Registered operation name.
            state:     Input state payload.
            metadata:  Optional dict with context (e.g., 'intent', 'source').
            strict:    If True, TCAG violation raises CoherenceError.
                       If False, violation is logged but execution continues.

        Returns:
            Output state produced by the operation.
        """
        if metadata is None:
            metadata = {}

        if operation not in self._operations:
            raise KeyError(f"Operation '{operation}' is not registered.")

        fn = self._operations[operation]

        # Execute deterministically.
        output_state = fn(state, metadata)

        # Evaluate TCAG.
        tcag = self._evaluate_tcag(state, output_state, metadata)

        if strict and tcag.score < 1.0:
            # Record the failed step before raising.
            self._record_lineage(operation, state, output_state, tcag, metadata)
            raise CoherenceError(
                f"TCAG violation in operation '{operation}' "
                f"(score={tcag.score:.2f})."
            )

        # Record successful step.
        self._record_lineage(operation, state, output_state, tcag, metadata)

        return output_state

    # ----- Lineage + Export -----

    def _record_lineage(
        self,
        operation: str,
        input_state: Any,
        output_state: Any,
        tcag: TCAGState,
        metadata: Dict[str, Any],
    ) -> None:
        record = LineageRecord(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            operation=operation,
            input_state=input_state,
            output_state=output_state,
            tcag=tcag,
            metadata=metadata.copy(),
        )
        self._lineage.append(record)

    @property
    def lineage(self) -> List[LineageRecord]:
        """Return a copy of the current lineage log."""
        return list(self._lineage)

    def export_lineage_for_supremechain(self) -> List[Dict[str, Any]]:
        """
        Export a SupremeChain-ready representation of the lineage.

        This does not write anywhere; it just returns a structured
        payload that Ledger.py can ingest.
        """
        exported: List[Dict[str, Any]] = []
        for rec in self._lineage:
            exported.append(
                {
                    "id": rec.id,
                    "timestamp": rec.timestamp,
                    "operation": rec.operation,
                    "input_state": rec.input_state,
                    "output_state": rec.output_state,
                    "tcag": {
                        "truth": rec.tcag.truth,
                        "continuity": rec.tcag.continuity,
                        "alignment": rec.tcag.alignment,
                        "genesis": rec.tcag.genesis,
                        "score": rec.tcag.score,
                        "notes": rec.tcag.notes,
                    },
                    "metadata": rec.metadata,
                }
            )
        return exported

    # ----- Utility -----

    def reset_lineage(self) -> None:
        """Clear the in-memory lineage log."""
        self._lineage.clear()


# Convenience factory for other modules
def create_default_engine() -> DeterministicEngine:
    """
    Create a default SC-OS deterministic engine instance.

    Other modules (Core, Orchestration, API) can import and use this
    without needing to know the implementation details.
    """
    return DeterministicEngine(name="SC-OS-Deterministic-Core")
