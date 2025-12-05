"""
WebSocket handler for workflow updates.
"""
from flask_socketio import emit, join_room, leave_room
from app import socketio


@socketio.on('join_workflow')
def handle_join_workflow(data):
    """Join a workflow room for real-time updates."""
    workflow_id = data.get('workflow_id')
    if workflow_id:
        join_room(f'workflow_{workflow_id}')
        emit('joined', {'workflow_id': workflow_id})


@socketio.on('leave_workflow')
def handle_leave_workflow(data):
    """Leave a workflow room."""
    workflow_id = data.get('workflow_id')
    if workflow_id:
        leave_room(f'workflow_{workflow_id}')
        emit('left', {'workflow_id': workflow_id})


def broadcast_workflow_update(workflow_id, update_type, data):
    """
    Broadcast workflow update to all clients in the room.

    Args:
        workflow_id: Workflow identifier
        update_type: Type of update (stage_started, stage_completed, etc.)
        data: Update data
    """
    socketio.emit(
        'workflow_update',
        {
            'type': update_type,
            'workflow_id': workflow_id,
            'data': data,
            'timestamp': data.get('timestamp')
        },
        room=f'workflow_{workflow_id}'
    )
