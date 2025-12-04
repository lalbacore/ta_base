"""
Router module providing MissionRouter and RoutedOrchestrator.
"""
from typing import Any, Dict, List, Set, Optional
import re
from swarms.team_agent.state.turing_tape import TuringTape  # optional persistence
from swarms.team_agent.state.hitl import HumanApprovalGate  # new


class MissionRouter:
    """Routes missions to appropriate capabilities and execution strategies."""

    def __init__(self, registry):
        """
        Args:
            registry: CapabilityRegistry instance (or compatible)
        """
        self.registry = registry

    def _all_capability_names(self) -> List[str]:
        try:
            if hasattr(self.registry, "list_capabilities"):
                names = self.registry.list_capabilities()
                return list(names) if names else []
        except Exception:
            pass
        names: Set[str] = set()
        # Common internal maps keyed by name
        for attr in ("_capability_map", "_capabilities_by_name"):
            mapping = getattr(self.registry, attr, None)
            if isinstance(mapping, dict):
                names.update(mapping.keys())
        # Public/semipublic attributes
        caps = getattr(self.registry, "capabilities", None)
        if isinstance(caps, dict):
            names.update(caps.keys())
        if isinstance(caps, list):
            for c in caps:
                meta = getattr(c, "metadata", None) or {}
                name = meta.get("name") or c.__class__.__name__.lower()
                names.add(name)
        # Generic introspection
        try:
            for v in getattr(self.registry, "__dict__", {}).values():
                if isinstance(v, dict):
                    names.update([k for k in v.keys() if isinstance(k, str)])
                elif isinstance(v, list):
                    for c in v:
                        if hasattr(c, "metadata"):
                            meta = getattr(c, "metadata", None) or {}
                            name = meta.get("name") or c.__class__.__name__.lower()
                            names.add(name)
        except Exception:
            pass
        return list(names)

    def _match_capabilities(self, mission: str) -> List[Any]:
        ctx = {"mission": mission, "input": mission}
        # Helper: find_all_matches
        try:
            fam = getattr(self.registry, "find_all_matches", None)
            if callable(fam):
                matches = fam(mission)
                if matches:
                    return list(matches)
                matches = fam(ctx)
                if matches:
                    return list(matches)
        except Exception:
            pass
        # Helper: find (single)
        try:
            f = getattr(self.registry, "find", None)
            if callable(f):
                found = f(mission) or f(ctx)
                if found:
                    return [found]
        except Exception:
            pass
        # Manual scan
        candidates: List[Any] = []
        caps_list = getattr(self.registry, "capabilities", None)
        if isinstance(caps_list, list):
            candidates.extend(caps_list)
        for attr in ("_capability_map", "_capabilities_by_name", "_capabilities_by_type", "_capabilities_by_domain"):
            mapping = getattr(self.registry, attr, None)
            if isinstance(mapping, dict):
                for v in mapping.values():
                    if isinstance(v, list):
                        candidates.extend(v)
                    else:
                        candidates.append(v)
        try:
            for v in getattr(self.registry, "__dict__", {}).values():
                if isinstance(v, dict):
                    candidates.extend([obj for obj in v.values() if hasattr(obj, "matches")])
                elif isinstance(v, list):
                    candidates.extend([obj for obj in v if hasattr(obj, "matches")])
        except Exception:
            pass
        seen: Set[int] = set()
        deduped: List[Any] = []
        for c in candidates:
            oid = id(c)
            if oid not in seen:
                seen.add(oid)
                deduped.append(c)
        matches: List[Any] = []
        for cap_obj in deduped:
            try:
                if cap_obj.matches(ctx) or cap_obj.matches(mission):
                    matches.append(cap_obj)
            except Exception:
                continue
        return matches

    def _assess_complexity(self, mission: str, multi_task: bool, capability_count: int) -> str:
        ml = mission.lower()
        words = ml.split()
        comma_count = ml.count(",")
        sep_count = comma_count + ml.count(";") + ml.count(":") + ml.count("/") + ml.count(" - ")
        complex_signals = [
            "architecture", "architect", "design", "integrat", "database",
            "orchestrate", "pipeline", "deployment", "monitor", "optimiz",
            "scalable", "distributed", "security", "secure", "compliance",
            "governance", "performance", "evaluation", "testing", "end-to-end",
            "microservice", "kubernetes", "container", "ml", "ai",
            "comprehensive", "detailed", "including", "include", "overview",
            "requirements", "plan", "specification", "specifications",
            "outline", "roadmap", "breakdown", "section", "sections", "step", "steps"
        ]
        if multi_task:
            return "complex"
        if capability_count > 1:
            return "complex"
        if any(sig in ml for sig in complex_signals):
            return "complex"
        if sep_count >= 1:
            return "complex"
        # Lowered threshold so substantial single-clause missions count as complex
        if len(words) >= 8:
            return "complex"
        return "simple"

    def analyze_mission(self, mission: str) -> Dict[str, Any]:
        matching_objects = self._match_capabilities(mission)
        capability_names = [
            (getattr(cap, "metadata", {}) or {}).get("name", cap.__class__.__name__.lower())
            for cap in matching_objects
        ]

        ml = mission.lower()
        multi_task = any(tok in ml for tok in [
            " and ", ",", " both ", "multiple", "parallel", "concurrently", "simultaneously"
        ])

        if not capability_names:
            all_names = self._all_capability_names()
            if multi_task and len(all_names) >= 2:
                capability_names = all_names
            elif all_names:
                capability_names = all_names

        if multi_task:
            strategy = "parallel_capabilities"
        elif len(capability_names) == 1:
            strategy = "single_capability"
        elif len(capability_names) > 1:
            strategy = "parallel_capabilities"
        else:
            strategy = "decompose_and_route"

        complexity = self._assess_complexity(mission, multi_task, len(capability_names))
        requires_decomposition = (len(capability_names) == 0) and (not multi_task)
        can_parallelize = strategy == "parallel_capabilities" or len(capability_names) > 1

        return {
            "strategy": strategy,
            "capabilities": capability_names,
            "workflow": {
                "phases": ["architecture", "implementation", "review", "recording"],
                "parallelizable": can_parallelize,
            },
            "complexity": complexity,
            "requires_decomposition": requires_decomposition,
            "can_parallelize": can_parallelize,
        }

    def decompose_mission(self, mission: str, max_parts: int = 3, min_chunk_words: int = 3) -> List[Dict[str, Any]]:
        """
        Decompose a mission into smaller subtasks with proposed capabilities.

        Args:
            mission: Full mission description
            max_parts: Max number of subtasks to return
            min_chunk_words: Minimum words per chunk; smaller fragments will be merged

        Returns:
            List of { "description": str, "capabilities": [str] }
        """
        text = mission.strip()
        if not text:
            return []

        # Split by common separators indicating multiple steps
        # Added ' with ', ' using ' to catch phrasing like "... with API UI"
        separators = r"(,|;| and | then | afterwards | next | followed by | with | using )"
        parts = [p.strip(" ,;") for p in re.split(separators, text, flags=re.IGNORECASE)
                 if p and not re.fullmatch(separators, p, flags=re.IGNORECASE)]

        # If splitting didn’t help, fall back to sentences
        if len(parts) <= 1:
            parts = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]

        # If still a single part, try heuristic component extraction (API/UI/backend/db)
        if len(parts) <= 1:
            ml = text.lower()
            components: List[str] = []

            # Full-stack implies at least UI + backend
            if "full stack" in ml or "full-stack" in ml:
                components.extend(["Design backend services", "Build UI"])

            if "api" in ml:
                components.append("Design and implement API")
            if "ui" in ml or "frontend" in ml or "front end" in ml:
                components.append("Build UI")
            if "backend" in ml or "back end" in ml or "server" in ml:
                components.append("Implement backend")
            if "database" in ml or "db" in ml or "data model" in ml:
                components.append("Design database schema")

            # Deduplicate while preserving order
            seen = set()
            components = [c for c in components if not (c in seen or seen.add(c))]

            if len(components) > 1:
                parts = components[:max_parts]
            else:
                parts = [text]

        # Merge tiny fragments into previous chunk
        merged: List[str] = []
        for p in parts:
            if not merged:
                merged.append(p)
                continue
            if len(p.split()) < min_chunk_words:
                merged[-1] = f"{merged[-1]} {p}".strip()
            else:
                merged.append(p)

        # Limit to max_parts; merge overflow into the last
        if len(merged) > max_parts:
            head = merged[: max_parts - 1]
            tail = " ".join(merged[max_parts - 1 :]).strip()
            merged = head + ([tail] if tail else [])

        # Propose capabilities per chunk
        subtasks: List[Dict[str, Any]] = []
        all_names = self._all_capability_names()
        for chunk in merged:
            objs = self._match_capabilities(chunk)
            names = [
                (getattr(cap, "metadata", {}) or {}).get("name", cap.__class__.__name__.lower())
                for cap in objs
            ]
            # Fallback to available names if nothing matches
            if not names and all_names:
                names = all_names
            subtasks.append({"description": chunk, "capabilities": names})

        return subtasks


class RoutedOrchestrator:
    """
    Minimal orchestrator that uses MissionRouter to select capabilities and run them.
    """

    def __init__(self, registry, router: Optional[MissionRouter] = None, workflow_id: str = "unknown", checkpoints: Optional[list] = None):
        self.registry = registry
        self.router = router or MissionRouter(registry)
        self.tape = TuringTape(workflow_id=workflow_id)
        self.hitl = HumanApprovalGate(self.tape)
        # checkpoints: list of dicts e.g. {"id": "cp1", "before_capability": "hrt_guide_generator"}
        self.checkpoints = checkpoints or []

    def _pending_checkpoint_for_capability(self, capability_name: str) -> Optional[str]:
        for cp in self.checkpoints:
            if cp.get("before_capability") == capability_name:
                return cp.get("id")
        return None

    def _get_capability_by_name(self, name: str) -> Optional[Any]:
        """Look up a capability by name from the registry."""
        # If registry is a CapabilityRegistry with a get method
        if hasattr(self.registry, 'get') and callable(getattr(self.registry, 'get')):
            return self.registry.get(name)
        # If registry is an Orchestrator with capability_registry attribute
        if hasattr(self.registry, 'capability_registry'):
            cap_reg = self.registry.capability_registry
            if hasattr(cap_reg, 'get') and callable(getattr(cap_reg, 'get')):
                return cap_reg.get(name)
        return None

    def execute(self, mission: str | Dict[str, Any]) -> Dict[str, Any]:
        # Support mission as dict with optional checkpoints
        mission_text = mission.get("text") if isinstance(mission, dict) else str(mission)
        if isinstance(mission, dict) and mission.get("checkpoints"):
            # Merge runtime checkpoints (mission-level) with constructor-level ones
            ids = {c.get("id") for c in self.checkpoints}
            for cp in mission["checkpoints"]:
                if cp.get("id") not in ids:
                    self.checkpoints.append(cp)

        analysis = self.router.analyze_mission(mission_text)
        self.tape.append(agent="orchestrator", event="analysis", state=analysis)
        used, artifacts, outputs = [], [], []

        for name in analysis.get("capabilities", []):
            # HITL checkpoint before capability
            cp_id = self._pending_checkpoint_for_capability(name)
            if cp_id:
                if not self.hitl.request_if_needed(cp_id, context={"capability": name, "mission": mission_text}):
                    # Stop and return pending
                    return {
                        "status": "pending_approval",
                        "pending_checkpoint_id": cp_id,
                        "mission": mission_text,
                        "analysis": analysis,
                        "used_capabilities": used,
                        "artifacts": artifacts,
                        "outputs": outputs,
                    }

            cap = self._get_capability_by_name(name)
            if not cap or not hasattr(cap, "execute"):
                continue
            self.tape.append(agent=name, event="start", state={"mission": mission_text})
            out = cap.execute({"mission": mission_text})
            self.tape.append(agent=name, event="complete", state={"output_keys": list(out.keys())})
            used.append(name)
            outputs.append(out)
            artifacts.extend(out.get("artifacts", []))

        final = {
            "status": "complete",
            "mission": mission_text,
            "analysis": analysis,
            "used_capabilities": used,
            "artifacts": artifacts,
            "outputs": outputs,
        }
        self.tape.append(agent="orchestrator", event="complete", state={"used_capabilities": used})
        return final

    def resume(self, mission: str | Dict[str, Any]) -> Dict[str, Any]:
        """
        Resume after approval(s). Same as execute, but if checkpoint is approved we pass through.
        """
        return self.execute(mission)