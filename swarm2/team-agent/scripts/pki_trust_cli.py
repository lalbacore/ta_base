#!/usr/bin/env python3
"""
PKI Trust Management CLI

Command-line interface for managing agent reputation and trust scores.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import argparse

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from swarms.team_agent.crypto.trust import AgentReputationTracker, EventType


def format_timestamp(ts_str: str) -> str:
    """Format ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(ts_str.rstrip('Z'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return ts_str


def cmd_list(args):
    """List all agents and their trust scores."""
    tracker = AgentReputationTracker()
    agents = tracker.list_all_agents()

    if not agents:
        print("No agents registered.")
        return

    print(f"\n{'Agent ID':<30} {'Trust Score':<12} {'Operations':<12} {'Success Rate':<15} {'Incidents':<10}")
    print("=" * 95)

    for agent in agents:
        score_color = ""
        if agent.trust_score >= 80:
            score_color = "\033[92m"  # Green
        elif agent.trust_score >= 60:
            score_color = "\033[93m"  # Yellow
        else:
            score_color = "\033[91m"  # Red

        print(f"{agent.agent_id:<30} {score_color}{agent.trust_score:>6.2f}\033[0m      "
              f"{agent.total_operations:>6}       {agent.success_rate:>6.1f}%        "
              f"{agent.security_incidents:>5}")

    print()


def cmd_show(args):
    """Show detailed information for an agent."""
    tracker = AgentReputationTracker()
    metrics = tracker.get_agent_metrics(args.agent_id)

    if not metrics:
        print(f"Agent not found: {args.agent_id}")
        return

    print(f"\n{'='*60}")
    print(f"Agent: {metrics.agent_id}")
    print(f"{'='*60}")
    print()

    # Trust Score
    score_label = "EXCELLENT" if metrics.trust_score >= 90 else \
                  "GOOD" if metrics.trust_score >= 75 else \
                  "FAIR" if metrics.trust_score >= 60 else \
                  "POOR" if metrics.trust_score >= 40 else "CRITICAL"

    print(f"Trust Score:        {metrics.trust_score:.2f} / 100.0 ({score_label})")
    print(f"Last Seen:          {format_timestamp(metrics.last_seen.isoformat())}")
    print()

    # Operations
    print("Operations:")
    print(f"  Total:            {metrics.total_operations}")
    print(f"  Successful:       {metrics.successful_operations} ({metrics.success_rate:.1f}%)")
    print(f"  Failed:           {metrics.failed_operations} ({metrics.failure_rate:.1f}%)")
    print(f"  Errors:           {metrics.error_operations} ({metrics.error_rate:.1f}%)")
    print()

    # Security
    print("Security:")
    print(f"  Incidents:        {metrics.security_incidents}")
    print(f"  Cert Revocations: {metrics.certificate_revocations}")
    print(f"  Policy Violations: {metrics.policy_violations}")
    print()

    # Performance
    print("Performance:")
    print(f"  Avg Response Time: {metrics.average_response_time:.3f}s")
    print(f"  Total Uptime:     {metrics.total_uptime_seconds:.1f}s")
    print()


def cmd_history(args):
    """Show trust score history for an agent."""
    tracker = AgentReputationTracker()
    history = tracker.get_trust_history(args.agent_id, limit=args.limit)

    if not history:
        print(f"No history found for agent: {args.agent_id}")
        return

    print(f"\nTrust Score History for {args.agent_id}")
    print(f"\n{'Timestamp':<20} {'Trust Score':<15} {'Success Rate':<15} {'Error Rate':<12}")
    print("=" * 70)

    for record in history:
        print(f"{format_timestamp(record['timestamp']):<20} "
              f"{record['trust_score']:>8.2f}       "
              f"{record['success_rate']:>8.1f}%       "
              f"{record['error_rate']:>6.1f}%")

    print()


def cmd_events(args):
    """Show recent events for an agent."""
    tracker = AgentReputationTracker()
    events = tracker.get_recent_events(args.agent_id, limit=args.limit)

    if not events:
        print(f"No events found for agent: {args.agent_id}")
        return

    print(f"\nRecent Events for {args.agent_id}")
    print(f"\n{'Timestamp':<20} {'Event Type':<25} {'Metadata'}")
    print("=" * 80)

    for event in events:
        metadata_str = str(event['metadata']) if event['metadata'] else ""
        if len(metadata_str) > 30:
            metadata_str = metadata_str[:27] + "..."

        print(f"{format_timestamp(event['timestamp']):<20} "
              f"{event['event_type']:<25} {metadata_str}")

    print()


def cmd_register(args):
    """Register a new agent."""
    tracker = AgentReputationTracker()

    if tracker.register_agent(args.agent_id):
        print(f"✓ Registered agent: {args.agent_id}")
    else:
        print(f"Agent already registered: {args.agent_id}")


def cmd_record(args):
    """Record an event for an agent."""
    tracker = AgentReputationTracker()

    try:
        event_type = EventType[args.event_type.upper().replace('-', '_')]
    except KeyError:
        print(f"Invalid event type: {args.event_type}")
        print(f"Valid types: {', '.join(e.name.lower().replace('_', '-') for e in EventType)}")
        return

    metadata = {}
    if args.metadata:
        for item in args.metadata:
            key, value = item.split('=', 1)
            metadata[key] = value

    tracker.record_event(
        agent_id=args.agent_id,
        event_type=event_type,
        metadata=metadata if metadata else None,
        response_time=args.response_time
    )

    print(f"✓ Recorded {event_type.value} for {args.agent_id}")

    # Show updated score
    metrics = tracker.get_agent_metrics(args.agent_id)
    if metrics:
        print(f"  Updated trust score: {metrics.trust_score:.2f}")


def cmd_delete(args):
    """Delete an agent and all associated data."""
    if not args.force:
        response = input(f"Delete agent '{args.agent_id}' and all data? [y/N] ")
        if response.lower() != 'y':
            print("Cancelled.")
            return

    tracker = AgentReputationTracker()

    if tracker.delete_agent(args.agent_id):
        print(f"✓ Deleted agent: {args.agent_id}")
    else:
        print(f"Agent not found: {args.agent_id}")


def cmd_stats(args):
    """Show overall system statistics."""
    tracker = AgentReputationTracker()
    stats = tracker.get_statistics()

    print("\nSystem Statistics")
    print("=" * 50)
    print(f"Total Agents:          {stats['total_agents']}")
    print(f"Average Trust Score:   {stats['average_trust_score']:.2f}")
    print(f"Min Trust Score:       {stats['min_trust_score']:.2f}")
    print(f"Max Trust Score:       {stats['max_trust_score']:.2f}")
    print(f"Total Operations:      {stats['total_operations']}")
    print(f"Security Incidents:    {stats['total_security_incidents']}")
    print()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="PKI Trust Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all agents
  pki-trust list

  # Show detailed info for an agent
  pki-trust show architect-agent

  # View trust score history
  pki-trust history builder-agent --limit 10

  # Register new agent
  pki-trust register new-agent

  # Record successful operation
  pki-trust record architect-agent operation-success --response-time 0.5

  # Record security incident
  pki-trust record bad-agent security-incident --metadata reason=unauthorized

  # System statistics
  pki-trust stats
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # List command
    parser_list = subparsers.add_parser('list', help='List all agents')
    parser_list.set_defaults(func=cmd_list)

    # Show command
    parser_show = subparsers.add_parser('show', help='Show agent details')
    parser_show.add_argument('agent_id', help='Agent identifier')
    parser_show.set_defaults(func=cmd_show)

    # History command
    parser_history = subparsers.add_parser('history', help='Show trust score history')
    parser_history.add_argument('agent_id', help='Agent identifier')
    parser_history.add_argument('--limit', type=int, default=20, help='Number of records (default: 20)')
    parser_history.set_defaults(func=cmd_history)

    # Events command
    parser_events = subparsers.add_parser('events', help='Show recent events')
    parser_events.add_argument('agent_id', help='Agent identifier')
    parser_events.add_argument('--limit', type=int, default=50, help='Number of events (default: 50)')
    parser_events.set_defaults(func=cmd_events)

    # Register command
    parser_register = subparsers.add_parser('register', help='Register new agent')
    parser_register.add_argument('agent_id', help='Agent identifier')
    parser_register.set_defaults(func=cmd_register)

    # Record command
    parser_record = subparsers.add_parser('record', help='Record an event')
    parser_record.add_argument('agent_id', help='Agent identifier')
    parser_record.add_argument('event_type', help='Event type',
                               choices=[e.name.lower().replace('_', '-') for e in EventType])
    parser_record.add_argument('--response-time', type=float, help='Response time in seconds')
    parser_record.add_argument('--metadata', nargs='+', help='Metadata as key=value pairs')
    parser_record.set_defaults(func=cmd_record)

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete an agent')
    parser_delete.add_argument('agent_id', help='Agent identifier')
    parser_delete.add_argument('--force', action='store_true', help='Skip confirmation')
    parser_delete.set_defaults(func=cmd_delete)

    # Stats command
    parser_stats = subparsers.add_parser('stats', help='Show system statistics')
    parser_stats.set_defaults(func=cmd_stats)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
