"""
Team Agent Capabilities - Pluggable domain knowledge.
"""

from .base_capability import BaseCapability
from .registry import CapabilityRegistry
from .document_generator import DocumentGenerator

# Import domain-specific capabilities (optional, only if they exist)
try:
    from .medical.hrt_guide import HRTGuideCapability
except ImportError:
    HRTGuideCapability = None

try:
    from .code.calculator import CalculatorCapability
except ImportError:
    CalculatorCapability = None

__all__ = [
    "BaseCapability",
    "CapabilityRegistry",
    "DocumentGenerator",
]

# Add to __all__ only if successfully imported
if HRTGuideCapability:
    __all__.append("HRTGuideCapability")

if CalculatorCapability:
    __all__.append("CalculatorCapability")