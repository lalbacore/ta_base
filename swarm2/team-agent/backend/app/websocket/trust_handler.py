"""
WebSocket handler for trust score updates.
"""
from flask_socketio import emit, join_room, leave_room
from app import socketio


@socketio.on('join_trust')
def handle_join_trust():
    """Join the trust updates room."""
    join_room('trust_updates')
    emit('joined_trust', {'status': 'subscribed'})


@socketio.on('leave_trust')
def handle_leave_trust():
    """Leave the trust updates room."""
    leave_room('trust_updates')
    emit('left_trust', {'status': 'unsubscribed'})


def broadcast_trust_update(agent_id, trust_score, event_type, details):
    """
    Broadcast trust score update to all clients.

    Args:
        agent_id: Agent identifier
        trust_score: New trust score
        event_type: Type of event that caused the update
        details: Additional event details
    """
    socketio.emit(
        'trust_update',
        {
            'type': 'trust_score_updated',
            'agent_id': agent_id,
            'trust_score': trust_score,
            'event_type': event_type,
            'details': details
        },
        room='trust_updates'
    )


def broadcast_agent_event(agent_id, event_data):
    """
    Broadcast agent event (success, failure, incident, etc.).

    Args:
        agent_id: Agent identifier
        event_data: Event data
    """
    socketio.emit(
        'agent_event',
        {
            'type': 'agent_event',
            'agent_id': agent_id,
            'event': event_data
        },
        room='trust_updates'
    )
