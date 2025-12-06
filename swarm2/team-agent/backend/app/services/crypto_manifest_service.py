"""
Crypto Manifest Service - PKI Mesh Journey Tracker

Traces the complete cryptographic journey of a mission/workflow through all stages
and trust domains using the Turing Tape as the immutable source of truth.

Shows:
- Which trust domain signed each stage
- Complete chain of custody from mission creation to artifact publishing
- Signature verification status for each stage
- PKI mesh topology and trust relationships
- Breaks or weak links in the cryptographic chain
"""
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from swarms.team_agent.state.turing_tape import TuringTape
from swarms.team_agent.crypto import PKIManager, TrustDomain, Verifier


class CryptoManifestService:
    """
    Service for building cryptographic manifests from Turing Tape entries.

    A crypto manifest shows the complete PKI mesh journey of a workflow,
    tracking which trust domains signed each stage and verification status.
    """

    def __init__(self):
        """Initialize crypto manifest service with PKI manager."""
        self.pki = PKIManager()

        # Map of agent roles to trust domains
        self.role_trust_domains = {
            'orchestrator': TrustDomain.GOVERNMENT,
            'architect': TrustDomain.EXECUTION,
            'builder': TrustDomain.EXECUTION,
            'critic': TrustDomain.EXECUTION,
            'recorder': TrustDomain.LOGGING,
            'governance': TrustDomain.GOVERNMENT,
        }

        # Stage ordering for workflow
        self.stage_order = [
            'mission_start',
            'orchestrator',
            'architect',
            'builder',
            'critic',
            'recorder',
            'artifacts_published'
        ]

    def get_workflow_manifest(self, workflow_id: str, verify_signatures: bool = True) -> Dict[str, Any]:
        """
        Build complete crypto manifest for a workflow.

        Args:
            workflow_id: Workflow identifier
            verify_signatures: Whether to verify all signatures (slower but more complete)

        Returns:
            Crypto manifest with timeline, trust domains, verifications, and integrity status
        """
        # Load Turing Tape
        tape = TuringTape(workflow_id=workflow_id)

        # Read all entries
        entries = list(tape.read_all())

        if not entries:
            return {
                'workflow_id': workflow_id,
                'error': 'No Turing Tape entries found',
                'entries': [],
                'timeline': [],
                'trust_domains': [],
                'integrity': {
                    'status': 'unknown',
                    'chain_complete': False,
                    'all_signatures_valid': False,
                    'weak_links': ['No tape entries found']
                }
            }

        # Build timeline from entries
        timeline = self._build_timeline(entries, verify_signatures)

        # Extract trust domain flow
        trust_flow = self._extract_trust_flow(timeline)

        # Analyze chain integrity
        integrity = self._analyze_integrity(timeline, trust_flow)

        # Build PKI mesh topology
        pki_mesh = self._build_pki_mesh(timeline)

        # Identify weak links
        weak_links = self._identify_weak_links(timeline, integrity)

        return {
            'workflow_id': workflow_id,
            'generated_at': datetime.now().isoformat(),
            'total_entries': len(entries),
            'timeline': timeline,
            'trust_flow': trust_flow,
            'pki_mesh': pki_mesh,
            'integrity': integrity,
            'weak_links': weak_links,
            'displayable_chain': self._format_displayable_chain(timeline, trust_flow)
        }

    def _build_timeline(self, entries: List[Dict[str, Any]], verify: bool) -> List[Dict[str, Any]]:
        """
        Build chronological timeline with crypto metadata for each entry.

        Each timeline entry includes:
        - Timestamp
        - Agent/stage
        - Event
        - Trust domain
        - Signature status (signed/unsigned/verified/invalid)
        - Signature details
        """
        timeline = []

        for idx, entry in enumerate(entries):
            agent = entry.get('agent', 'unknown')
            event = entry.get('event', 'unknown')
            timestamp = entry.get('ts', 'unknown')

            # Determine trust domain for this agent
            trust_domain = self._get_trust_domain(agent)

            # Check if entry is signed
            has_signature = '_signature' in entry
            signature_valid = None

            if has_signature and verify:
                # Verify signature using appropriate trust domain
                signature_valid = self._verify_entry_signature(entry, trust_domain)

            # Extract signature metadata
            signature_meta = self._extract_signature_metadata(entry)

            timeline_entry = {
                'index': idx,
                'timestamp': timestamp,
                'agent': agent,
                'event': event,
                'trust_domain': trust_domain.value if trust_domain else 'unknown',
                'signed': has_signature,
                'signature_valid': signature_valid,
                'signature_metadata': signature_meta,
                'state_summary': self._summarize_state(entry.get('state', {})),
                'raw_entry': entry  # Include full entry for detailed inspection
            }

            timeline.append(timeline_entry)

        return timeline

    def _get_trust_domain(self, agent: str) -> Optional[TrustDomain]:
        """Map agent role to trust domain."""
        agent_lower = agent.lower()

        for role, domain in self.role_trust_domains.items():
            if role in agent_lower:
                return domain

        return None

    def _verify_entry_signature(self, entry: Dict[str, Any], trust_domain: Optional[TrustDomain]) -> bool:
        """
        Verify entry signature using appropriate trust domain certificate chain.

        Args:
            entry: Turing Tape entry with _signature
            trust_domain: Trust domain to verify against

        Returns:
            True if signature is valid, False otherwise
        """
        if not trust_domain:
            return False

        try:
            # Get certificate chain for trust domain
            chain_data = self.pki.get_chain(trust_domain)
            chain_pem = chain_data['chain']

            # Create verifier
            verifier = Verifier(chain_pem=chain_pem)

            # Verify entry
            tape = TuringTape()  # Temporary instance for verification
            return tape.verify_entry(entry, verifier)

        except Exception as e:
            print(f"Error verifying signature: {e}")
            return False

    def _extract_signature_metadata(self, entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract signature metadata from entry."""
        if '_signature' not in entry:
            return None

        sig_data = entry['_signature']

        return {
            'algorithm': sig_data.get('algorithm', 'unknown'),
            'timestamp': sig_data.get('timestamp', 'unknown'),
            'signer_id': sig_data.get('signer_id', 'unknown'),
            'signature_b64': sig_data.get('signature', 'unknown')[:32] + '...' if sig_data.get('signature') else None
        }

    def _summarize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create concise summary of state for timeline display."""
        summary = {}

        # Extract key fields
        if 'mission' in state:
            summary['mission'] = state['mission'][:100] if isinstance(state['mission'], str) else str(state['mission'])[:100]

        if 'artifacts' in state:
            artifacts = state['artifacts']
            if isinstance(artifacts, list):
                summary['artifacts_count'] = len(artifacts)
                summary['artifact_names'] = [a.get('name', 'unknown') for a in artifacts[:5]]
            elif isinstance(artifacts, dict):
                summary['artifacts_count'] = len(artifacts)
                summary['artifact_names'] = list(artifacts.keys())[:5]

        if 'status' in state:
            summary['status'] = state['status']

        if 'output' in state:
            summary['has_output'] = True

        return summary

    def _extract_trust_flow(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract the flow of trust domains through workflow stages.

        Returns list of trust domain transitions with verification status.
        """
        trust_flow = []
        prev_domain = None

        for entry in timeline:
            domain = entry['trust_domain']

            if domain != prev_domain:
                trust_flow.append({
                    'trust_domain': domain,
                    'timestamp': entry['timestamp'],
                    'agent': entry['agent'],
                    'event': entry['event'],
                    'signed': entry['signed'],
                    'signature_valid': entry['signature_valid']
                })
                prev_domain = domain

        return trust_flow

    def _build_pki_mesh(self, timeline: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build PKI mesh topology showing trust domain relationships.

        Returns:
            Dictionary with nodes (trust domains) and edges (transitions)
        """
        nodes = []
        edges = []
        domain_stats = {}

        # Collect trust domain statistics
        for entry in timeline:
            domain = entry['trust_domain']

            if domain not in domain_stats:
                domain_stats[domain] = {
                    'total_entries': 0,
                    'signed_entries': 0,
                    'verified_entries': 0,
                    'invalid_signatures': 0,
                    'unsigned_entries': 0
                }

            domain_stats[domain]['total_entries'] += 1

            if entry['signed']:
                domain_stats[domain]['signed_entries'] += 1

                if entry['signature_valid'] is True:
                    domain_stats[domain]['verified_entries'] += 1
                elif entry['signature_valid'] is False:
                    domain_stats[domain]['invalid_signatures'] += 1
            else:
                domain_stats[domain]['unsigned_entries'] += 1

        # Create nodes
        for domain, stats in domain_stats.items():
            nodes.append({
                'id': domain,
                'label': domain.upper(),
                'type': 'trust_domain',
                'statistics': stats,
                'integrity_score': self._calculate_domain_integrity(stats)
            })

        # Create edges (trust domain transitions)
        for i in range(len(timeline) - 1):
            curr_domain = timeline[i]['trust_domain']
            next_domain = timeline[i + 1]['trust_domain']

            if curr_domain != next_domain:
                edges.append({
                    'from': curr_domain,
                    'to': next_domain,
                    'timestamp': timeline[i + 1]['timestamp'],
                    'verified': timeline[i + 1]['signature_valid']
                })

        return {
            'nodes': nodes,
            'edges': edges,
            'domain_count': len(nodes)
        }

    def _calculate_domain_integrity(self, stats: Dict[str, int]) -> float:
        """Calculate integrity score for a trust domain (0-100)."""
        total = stats['total_entries']
        if total == 0:
            return 0.0

        # Perfect score: all entries signed and verified
        verified = stats['verified_entries']
        invalid = stats['invalid_signatures']
        unsigned = stats['unsigned_entries']

        # Score calculation
        verified_percent = (verified / total) * 100
        penalty_unsigned = (unsigned / total) * 20
        penalty_invalid = (invalid / total) * 50

        score = verified_percent - penalty_unsigned - penalty_invalid

        return max(0.0, min(100.0, score))

    def _analyze_integrity(self, timeline: List[Dict[str, Any]], trust_flow: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze overall cryptographic chain integrity.

        Returns:
            Integrity status with chain completeness, signature validity, and issues
        """
        total_entries = len(timeline)
        signed_entries = sum(1 for e in timeline if e['signed'])
        verified_entries = sum(1 for e in timeline if e['signature_valid'] is True)
        invalid_entries = sum(1 for e in timeline if e['signature_valid'] is False)
        unsigned_entries = sum(1 for e in timeline if not e['signed'])

        # Check chain completeness (all expected stages present)
        stages_present = set(e['event'] for e in timeline)
        expected_stages = {'mission_start', 'architect', 'builder', 'critic', 'recorder'}
        missing_stages = expected_stages - stages_present
        chain_complete = len(missing_stages) == 0

        # Check all signatures valid
        all_signatures_valid = invalid_entries == 0 and unsigned_entries == 0

        # Determine overall status
        if chain_complete and all_signatures_valid:
            status = 'verified'
            status_message = 'All stages present and cryptographically verified'
        elif chain_complete and verified_entries > 0:
            status = 'partial'
            status_message = f'{verified_entries}/{total_entries} entries verified'
        elif chain_complete:
            status = 'incomplete_signatures'
            status_message = 'All stages present but signatures missing/invalid'
        else:
            status = 'incomplete_chain'
            status_message = f'Missing stages: {", ".join(missing_stages)}'

        # Calculate overall integrity score
        integrity_score = self._calculate_overall_integrity(timeline)

        return {
            'status': status,
            'status_message': status_message,
            'integrity_score': integrity_score,
            'chain_complete': chain_complete,
            'all_signatures_valid': all_signatures_valid,
            'statistics': {
                'total_entries': total_entries,
                'signed_entries': signed_entries,
                'verified_entries': verified_entries,
                'invalid_entries': invalid_entries,
                'unsigned_entries': unsigned_entries
            },
            'missing_stages': list(missing_stages)
        }

    def _calculate_overall_integrity(self, timeline: List[Dict[str, Any]]) -> float:
        """Calculate overall integrity score (0-100)."""
        if not timeline:
            return 0.0

        total = len(timeline)
        verified = sum(1 for e in timeline if e['signature_valid'] is True)
        invalid = sum(1 for e in timeline if e['signature_valid'] is False)
        unsigned = sum(1 for e in timeline if not e['signed'])

        # Perfect score: all verified
        verified_percent = (verified / total) * 100
        penalty_unsigned = (unsigned / total) * 15
        penalty_invalid = (invalid / total) * 40

        score = verified_percent - penalty_unsigned - penalty_invalid

        return max(0.0, min(100.0, score))

    def _identify_weak_links(self, timeline: List[Dict[str, Any]], integrity: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identify weak links or breaks in the cryptographic chain.

        Returns list of issues with severity and remediation suggestions.
        """
        weak_links = []

        # Check for unsigned entries
        for entry in timeline:
            if not entry['signed']:
                weak_links.append({
                    'type': 'unsigned_entry',
                    'severity': 'high',
                    'timestamp': entry['timestamp'],
                    'agent': entry['agent'],
                    'event': entry['event'],
                    'message': f'Entry not cryptographically signed',
                    'remediation': 'Ensure Signer is configured for this agent\'s trust domain'
                })

        # Check for invalid signatures
        for entry in timeline:
            if entry['signature_valid'] is False:
                weak_links.append({
                    'type': 'invalid_signature',
                    'severity': 'critical',
                    'timestamp': entry['timestamp'],
                    'agent': entry['agent'],
                    'event': entry['event'],
                    'message': 'Signature verification failed - entry may be tampered',
                    'remediation': 'Investigate entry integrity and certificate chain'
                })

        # Check for missing stages
        if integrity.get('missing_stages'):
            for stage in integrity['missing_stages']:
                weak_links.append({
                    'type': 'missing_stage',
                    'severity': 'medium',
                    'stage': stage,
                    'message': f'Expected workflow stage "{stage}" not found in tape',
                    'remediation': 'Verify workflow completed all stages successfully'
                })

        # Check for trust domain gaps
        trust_domains_used = set(e['trust_domain'] for e in timeline if e['trust_domain'] != 'unknown')
        expected_domains = {'government', 'execution', 'logging'}
        missing_domains = expected_domains - trust_domains_used

        for domain in missing_domains:
            weak_links.append({
                'type': 'missing_trust_domain',
                'severity': 'low',
                'trust_domain': domain,
                'message': f'No entries from {domain} trust domain',
                'remediation': f'Verify workflow uses agents from {domain} trust domain'
            })

        return weak_links

    def _format_displayable_chain(self, timeline: List[Dict[str, Any]], trust_flow: List[Dict[str, Any]]) -> List[str]:
        """
        Format crypto chain as displayable/loggable text lines.

        Returns list of formatted lines for console or log output.
        """
        lines = []

        lines.append("=" * 80)
        lines.append("CRYPTOGRAPHIC CHAIN MANIFEST")
        lines.append("=" * 80)
        lines.append("")

        lines.append("Trust Domain Flow:")
        lines.append("-" * 80)

        for i, flow_entry in enumerate(trust_flow):
            domain = flow_entry['trust_domain'].upper()
            agent = flow_entry['agent']
            event = flow_entry['event']
            signed = "✓ SIGNED" if flow_entry['signed'] else "✗ UNSIGNED"
            verified = ""

            if flow_entry['signature_valid'] is True:
                verified = "✓ VERIFIED"
            elif flow_entry['signature_valid'] is False:
                verified = "✗ INVALID"

            lines.append(f"{i + 1}. [{domain}] {agent} - {event}")
            lines.append(f"   {signed} {verified}")
            lines.append(f"   Timestamp: {flow_entry['timestamp']}")
            lines.append("")

        lines.append("=" * 80)
        lines.append("Detailed Timeline:")
        lines.append("-" * 80)

        for entry in timeline:
            lines.append(f"[{entry['timestamp']}] {entry['agent']} ({entry['trust_domain'].upper()})")
            lines.append(f"  Event: {entry['event']}")
            lines.append(f"  Signed: {entry['signed']}")
            if entry['signature_valid'] is not None:
                lines.append(f"  Verified: {entry['signature_valid']}")
            if entry['signature_metadata']:
                lines.append(f"  Signature: {entry['signature_metadata'].get('algorithm', 'unknown')}")
            lines.append("")

        lines.append("=" * 80)

        return lines


# Singleton instance
crypto_manifest_service = CryptoManifestService()
