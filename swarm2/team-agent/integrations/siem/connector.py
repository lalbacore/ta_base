"""SIEM connector for exporting workflow records."""
from typing import List, Optional, Dict
from storage.database import get_storage
from storage.models import SIEMConnector, WorkflowRecord
from integrations.siem.cef_formatter import CEFFormatter, CEFValidator

class SIEMExporter:
    """Export workflow records to SIEM systems."""
    
    def __init__(self):
        self.storage = get_storage()
        self.batch_size = 100
    
    def get_connectors(self, enabled_only: bool = True) -> List[SIEMConnector]:
        """Get configured SIEM connectors."""
        return self.storage.list_siem_connectors(enabled_only=enabled_only)
    
    def export_workflow_record(self, record: WorkflowRecord) -> Dict:
        """
        Export a workflow record to all enabled SIEM connectors.
        
        Returns export status for each connector.
        """
        connectors = self.get_connectors(enabled_only=True)
        results = {
            "workflow_id": record.workflow_id,
            "connectors": {}
        }
        
        # Format record as CEF
        cef_event = CEFFormatter.format_workflow_record(record.to_dict())
        
        # Export to each connector
        for connector in connectors:
            result = self._send_to_connector(connector, cef_event)
            results["connectors"][connector.name] = result
        
        return results
    
    def export_batch(self, records: List[WorkflowRecord]) -> Dict:
        """
        Export multiple workflow records to SIEM systems.
        
        Returns aggregated export status.
        """
        connectors = self.get_connectors(enabled_only=True)
        results = {
            "total_records": len(records),
            "connectors": {}
        }
        
        # Format records as CEF
        cef_events = CEFFormatter.format_batch([r.to_dict() for r in records])
        
        # Validate before sending
        validation = CEFValidator.validate_batch(cef_events)
        results["validation"] = validation
        
        # Export to each connector
        for connector in connectors:
            result = self._send_batch_to_connector(connector, cef_events)
            results["connectors"][connector.name] = result
        
        return results
    
    def _send_to_connector(self, connector: SIEMConnector, cef_event: str) -> Dict:
        """
        Send a CEF event to a specific connector.
        
        In production, this would implement actual HTTP/API calls.
        For now, we simulate the connection.
        """
        return {
            "status": "queued",
            "connector_type": connector.connector_type,
            "endpoint": connector.endpoint,
            "format": connector.format,
            "message": f"Event queued for {connector.name}",
            "event_hash": hash(cef_event) % 10000
        }
    
    def _send_batch_to_connector(self, connector: SIEMConnector, cef_events: List[str]) -> Dict:
        """
        Send multiple CEF events to a specific connector.
        
        In production, this would batch and implement actual HTTP/API calls.
        """
        return {
            "status": "queued",
            "connector_type": connector.connector_type,
            "endpoint": connector.endpoint,
            "batch_size": len(cef_events),
            "format": connector.format,
            "message": f"Batch of {len(cef_events)} events queued for {connector.name}"
        }