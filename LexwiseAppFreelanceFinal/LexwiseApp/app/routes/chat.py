from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.services.grok_service import grok_service
from app.models.message import Message
from app.models.notification import Notification
from app.models.user import User

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Existing - AI chat endpoint
@chat_bp.route('/send', methods=['POST'])
@login_required
def send():
    data = request.get_json()
    message = data.get('message', '')
    language = data.get('language', 'en')
    
    print(f"📨 Received message: {message}")
    
    if not message:
        return jsonify({'error': 'No message'}), 400
    
    reply = grok_service.chat(message, current_user.profile_type, language)
    
    print(f"🤖 Sending response: {reply[:100]}...")
    
    return jsonify({'reply': reply})

# Get all conversations for current user
@chat_bp.route('/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get all conversations for current user - exclude admin"""
    # Get unique users that current user has messaged with
    sent_msgs = Message.query.filter_by(sender_id=current_user.id).all()
    received_msgs = Message.query.filter_by(receiver_id=current_user.id).all()
    
    user_ids = set()
    for msg in sent_msgs:
        user_ids.add(msg.receiver_id)
    for msg in received_msgs:
        user_ids.add(msg.sender_id)
    
    conversations = []
    for uid in user_ids:
        # EXCLUDE ADMIN (ID 1) and exclude current user
        if uid == 1 or uid == current_user.id:
            continue
            
        user = User.query.get(uid)
        if user:
            # Get last message
            last_msg = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.receiver_id == uid)) |
                ((Message.sender_id == uid) & (Message.receiver_id == current_user.id))
            ).order_by(Message.created_at.desc()).first()
            
            unread = Message.query.filter_by(receiver_id=current_user.id, sender_id=uid, is_read=False).count()
            
            conversations.append({
                'user_id': user.id,
                'name': user.username,
                'last_message': last_msg.content[:50] if last_msg else '',
                'last_time': last_msg.created_at.isoformat() if last_msg else None,
                'unread_count': unread
            })
    
    return jsonify({'conversations': conversations})
# Send a message to another user
@chat_bp.route('/send-message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content', '')
    
    # PREVENT ADMIN FROM SENDING MESSAGES
    if current_user.is_admin:
        return jsonify({'error': 'Admin accounts cannot send messages'}), 403
    
    if not receiver_id or not content:
        return jsonify({'error': 'Missing fields'}), 400
    
    # Make sure receiver exists and is not admin
    receiver = User.query.get(receiver_id)
    if not receiver:
        return jsonify({'error': 'Receiver not found'}), 404
    
    # Prevent sending to admin
    if receiver.is_admin:
        return jsonify({'error': 'Cannot send messages to admin'}), 403
    
    # Don't allow sending to self
    if receiver_id == current_user.id:
        return jsonify({'error': 'Cannot send message to yourself'}), 400
    
    message = Message(
        sender_id=current_user.id,
        receiver_id=receiver_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    
    # Create notification for receiver
    notification = Notification(
        user_id=receiver_id,
        title='New Message',
        message=f'{current_user.username}: {content[:50]}...',
        type='message',
        link='/messages'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'success': True, 'message': message.to_dict()})
# Get messages with a specific user
@chat_bp.route('/messages/<int:user_id>', methods=['GET'])
@login_required
def get_messages(user_id):
    """Get all messages between current user and another user"""
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == user_id)) |
        ((Message.sender_id == user_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.created_at.asc()).all()
    
    # Mark messages as read
    for msg in messages:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.is_read = True
    db.session.commit()
    
    return jsonify({'messages': [m.to_dict() for m in messages]})

# Mark a message as read
@chat_bp.route('/mark-read/<int:message_id>', methods=['PUT'])
@login_required
def mark_read(message_id):
    message = Message.query.get_or_404(message_id)
    if message.receiver_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({'success': True})

# Get unread message count
@chat_bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    count = Message.query.filter_by(receiver_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})