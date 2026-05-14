from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.notification import Notification

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')

# Get all notifications for current user
@notifications_bp.route('/', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(50).all()
    return jsonify({'notifications': [n.to_dict() for n in notifications]})

# Create a new notification
@notifications_bp.route('/', methods=['POST'])
@login_required
def create_notification():
    data = request.get_json()
    
    notification = Notification(
        user_id=data.get('user_id'),
        title=data.get('title'),
        message=data.get('message'),
        type=data.get('type', 'info'),
        link=data.get('link')
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({'success': True, 'notification': notification.to_dict()})

# Get unread notifications count
@notifications_bp.route('/unread-count', methods=['GET'])
@login_required
def get_unread_count():
    count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return jsonify({'count': count})

# Get only unread notifications
@notifications_bp.route('/unread', methods=['GET'])
@login_required
def get_unread():
    notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).order_by(Notification.created_at.desc()).all()
    return jsonify({'unread': [n.to_dict() for n in notifications]})

# Mark a single notification as read
@notifications_bp.route('/<int:notif_id>/read', methods=['PUT'])
@login_required
def mark_read(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    notif.is_read = True
    db.session.commit()
    return jsonify({'success': True})

# Mark all notifications as read
@notifications_bp.route('/mark-all-read', methods=['PUT'])
@login_required
def mark_all_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify({'success': True})

# Delete a notification
@notifications_bp.route('/<int:notif_id>', methods=['DELETE'])
@login_required
def delete_notification(notif_id):
    notif = Notification.query.get_or_404(notif_id)
    if notif.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(notif)
    db.session.commit()
    return jsonify({'success': True})