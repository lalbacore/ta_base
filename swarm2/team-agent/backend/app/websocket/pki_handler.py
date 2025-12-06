"""
WebSocket handler for PKI events.
"""
from flask_socketio import emit, join_room, leave_room
from app import socketio


@socketio.on('join_pki')
def handle_join_pki():
    """Join the PKI events room."""
    join_room('pki_events')
    emit('joined_pki', {'status': 'subscribed'})


@socketio.on('leave_pki')
def handle_leave_pki():
    """Leave the PKI events room."""
    leave_room('pki_events')
    emit('left_pki', {'status': 'unsubscribed'})


def broadcast_certificate_expiring(domain, days_until_expiry):
    """
    Broadcast certificate expiring warning.

    Args:
        domain: Trust domain
        days_until_expiry: Days until certificate expires
    """
    socketio.emit(
        'pki_event',
        {
            'type': 'certificate_expiring',
            'domain': domain,
            'days_until_expiry': days_until_expiry
        },
        room='pki_events'
    )


def broadcast_certificate_revoked(serial_number, domain, reason):
    """
    Broadcast certificate revocation.

    Args:
        serial_number: Certificate serial number
        domain: Trust domain
        reason: Revocation reason
    """
    socketio.emit(
        'pki_event',
        {
            'type': 'certificate_revoked',
            'serial_number': serial_number,
            'domain': domain,
            'reason': reason
        },
        room='pki_events'
    )


def broadcast_certificate_renewed(domain, new_expiry):
    """
    Broadcast certificate renewal.

    Args:
        domain: Trust domain
        new_expiry: New expiration date
    """
    socketio.emit(
        'pki_event',
        {
            'type': 'certificate_renewed',
            'domain': domain,
            'new_expiry': new_expiry
        },
        room='pki_events'
    )
