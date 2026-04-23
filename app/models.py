from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TroubleInput:
    symptom: str
    alarm_code: str = ""
    machine_model: str = ""
    material: str = ""
    thickness: str = ""
    timing: str = ""


@dataclass
class RetrievedDocument:
    source_type: str
    title: str
    snippet: str
    metadata: dict[str, str] = field(default_factory=dict)
    score: float | None = None


@dataclass
class CauseCandidateResult:
    causes: list[str]
    checks: list[str]
    evidences: list[str]
    cautions: list[str]
    raw_response: str
    retrieved_documents: list[RetrievedDocument] = field(default_factory=list)