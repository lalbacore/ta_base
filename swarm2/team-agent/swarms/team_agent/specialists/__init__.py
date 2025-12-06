"""
Specialist Agents - Domain-specific agents that use capabilities.

Specialist agents are registered in agent_cards with type="specialist".
They use one or more capabilities from the capability registry to perform
domain-specific tasks.

Available Specialists:
- LegalSpecialist: Legal document generation and contract analysis
- MedicalSpecialist: Medical documentation (future)
- FinancialSpecialist: Financial reports and analysis (future)
"""

from .base import BaseSpecialist
from .legal_specialist import LegalSpecialist

__all__ = [
    "BaseSpecialist",
    "LegalSpecialist",
]
