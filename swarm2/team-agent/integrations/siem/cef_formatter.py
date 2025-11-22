"""Convert workflow records to Common Event Format (CEF) for SIEM ingestion."""
from typing import Dict, List
from datetime import datetime

class CEFFormatter:
    """Format workflow records as CEF events for SIEM systems."""
    
    # CEF Version
    CEF_VERSION = "0"
    
    # Device info
    DEVICE_VENDOR = "TeamAgent"
    DEVICE_PRODUCT = "WorkflowOrchestration"
    DEVICE_VERSION = "1.0"
    DEVICE_EVENT_CLASS_ID = "WORKFLOW"
    
    @staticmethod
    def format_workflow_record(record: Dict) -> str:
        """
        Convert a workflow record to CEF format.
        
        CEF Format: CEF:0|vendor|product|version|event_id|event_name|severity|extension
        """
        timestamp = datetime.utcnow().strftime("%b %d %Y %H:%M:%S")
        severity = CEFFormatter._calculate_severity(record)
        
        # Build the CEF header
        cef_header = (
            f"CEF:{CEFFormatter.CEF_VERSION}|"
            f"{CEFFormatter.DEVICE_VENDOR}|"
            f"{CEFFormatter.DEVICE_PRODUCT}|"
            f"{CEFFormatter.DEVICE_VERSION}|"
            f"{CEFFormatter.DEVICE_EVENT_CLASS_ID}|"
            f"WorkflowExecution|"
            f"{severity}"
        )
        
        # Build extensions (key=value pairs)
        extensions = CEFFormatter._build_extensions(record, timestamp)
        
        return f"{cef_header}|{extensions}"
    
    @staticmethod
    def _calculate_severity(record: Dict) -> int:
        """
        Calculate severity (0-10) based on workflow result.
        0 = Lowest, 10 = Highest
        """
        status = record.get("status", "failed")
        composite_score = record.get("composite_score", {}).get("overall", 0)
        
        if status == "success" and composite_score >= 80:
            return 3  # Low (success)
        elif status == "success" and composite_score < 80:
            return 5  # Medium (partial success)
        elif status == "rejected":
            return 7  # High (policy rejection)
        else:
            return 9  # Very High (failure)
    
    @staticmethod
    def _build_extensions(record: Dict, timestamp: str) -> str:
        """Build CEF extension key=value pairs."""
        workflow_id = record.get("workflow_id", "unknown")
        status = record.get("status", "unknown")
        request = record.get("request", "").replace("=", "\\=")[:1024]  # Escape and limit
        composite_score = record.get("composite_score", {}).get("overall", 0)
        signature_hash = record.get("signature", {}).get("hash", "unknown")
        
        # Get stage details
        stages = record.get("stages", {})
        architect_status = stages.get("architect", {}).get("status", "unknown")
        builder_status = stages.get("builder", {}).get("status", "unknown")
        critic_status = stages.get("critic", {}).get("status", "unknown")
        governance_status = stages.get("governance", {}).get("status", "unknown")
        recorder_status = stages.get("recorder", {}).get("status", "unknown")
        
        # Build extensions
        extensions = (
            f"rt={timestamp} "
            f"cn1={composite_score} "
            f"cn1Label=CompositeScore "
            f"cs1={status} "
            f"cs1Label=WorkflowStatus "
            f"cs2={workflow_id} "
            f"cs2Label=WorkflowID "
            f"cs3={signature_hash} "
            f"cs3Label=SignatureHash "
            f"cs4={architect_status} "
            f"cs4Label=ArchitectStage "
            f"cs5={builder_status} "
            f"cs5Label=BuilderStage "
            f"cs6={critic_status} "
            f"cs6Label=CriticStage "
            f"cs7={governance_status} "
            f"cs7Label=GovernanceStage "
            f"cs8={recorder_status} "
            f"cs8Label=RecorderStage "
            f"msg={request}"
        )
        
        return extensions
    
    @staticmethod
    def format_batch(records: List[Dict]) -> List[str]:
        """Convert multiple workflow records to CEF events."""
        return [CEFFormatter.format_workflow_record(record) for record in records]


class CEFValidator:
    """Validate CEF format compliance."""
    
    @staticmethod
    def validate(cef_event: str) -> bool:
        """Check if a CEF event is properly formatted."""
        if not cef_event.startswith("CEF:"):
            return False
        
        parts = cef_event.split("|")
        if len(parts) < 7:
            return False
        
        return True
    
    @staticmethod
    def validate_batch(cef_events: List[str]) -> Dict[str, int]:
        """Validate a batch of CEF events."""
        results = {
            "total": len(cef_events),
            "valid": 0,
            "invalid": 0
        }
        
        for event in cef_events:
            if CEFValidator.validate(event):
                results["valid"] += 1
            else:
                results["invalid"] += 1
        
        return results