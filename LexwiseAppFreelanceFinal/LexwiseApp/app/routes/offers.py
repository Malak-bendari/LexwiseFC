from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.offer import Offer
from app.models.project import Project
from app.models.notification import Notification
import random

offers_bp = Blueprint('offers', __name__, url_prefix='/api/offers')

def create_notification(user_id, title, message, type='info', link=None):
    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=type,
        link=link
    )
    db.session.add(notif)
    db.session.commit()

@offers_bp.route('/', methods=['GET'])
@login_required
def get_offers():
    if current_user.profile_type == 'freelancer':
        # Get offers for freelancer's projects
        offers = Offer.query.join(Project).filter(Project.user_id == current_user.id).all()
    else:
        # Get offers made by investor
        offers = Offer.query.filter_by(investor_id=current_user.id).all()
    
    return jsonify({'offers': [o.to_dict() for o in offers]})

@offers_bp.route('/', methods=['POST'])
@login_required
def create_offer():
    data = request.get_json()
    project_id = data.get('project_id')
    amount = data.get('amount')
    equity = data.get('equity')
    message = data.get('message', '')
    
    if not project_id or not amount or not equity:
        return jsonify({'error': 'Missing required fields'}), 400
    
    project = Project.query.get_or_404(project_id)
    
    # Only investors can make offers
    if current_user.profile_type != 'investor':
        return jsonify({'error': 'Only investors can make offers'}), 403
    
    # Calculate offer score based on fairness
    try:
        amount_num = int(''.join(filter(str.isdigit, amount)))
        equity_num = int(''.join(filter(str.isdigit, equity)))
        
        # Basic scoring logic
        score = 70  # base score
        if 5 <= equity_num <= 20:
            score += 15
        elif equity_num > 30:
            score -= 10
        
        if 20000 <= amount_num <= 200000:
            score += 10
        elif amount_num < 10000:
            score -= 10
            
        offer_score = min(98, max(50, score))
    except:
        offer_score = random.randint(65, 95)
    
    offer = Offer(
        project_id=project_id,
        investor_id=current_user.id,
        amount=amount,
        equity=equity,
        message=message,
        offer_score=offer_score
    )
    
    db.session.add(offer)
    db.session.commit()
    
    # Create notification for freelancer
    create_notification(
        user_id=project.user_id,
        title='💰 New Investment Offer!',
        message=f'{current_user.username} made an offer of {amount} for {equity} equity on your project "{project.title}". Offer score: {offer_score}/100',
        type='offer',
        link=f'/projects/{project_id}'
    )
    
    return jsonify({'success': True, 'offer': offer.to_dict(), 'offer_score': offer_score})

@offers_bp.route('/<int:offer_id>/respond', methods=['PUT'])
@login_required
def respond_to_offer(offer_id):
    data = request.get_json()
    status = data.get('status')  # 'accepted' or 'rejected'
    
    offer = Offer.query.get_or_404(offer_id)
    project = Project.query.get(offer.project_id)
    
    # Only the project owner (freelancer) can respond
    if project.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    offer.status = status
    db.session.commit()
    
    # Create notification for investor
    create_notification(
        user_id=offer.investor_id,
        title=f'Offer {status.capitalize()}!',
        message=f'Your offer on "{project.title}" has been {status}.',
        type='offer_response'
    )
    
    return jsonify({'success': True, 'status': status})

@offers_bp.route('/pending-count', methods=['GET'])
@login_required
def get_pending_count():
    if current_user.profile_type == 'freelancer':
        count = Offer.query.join(Project).filter(Project.user_id == current_user.id, Offer.status == 'pending').count()
    else:
        count = Offer.query.filter_by(investor_id=current_user.id, status='pending').count()
    
    return jsonify({'count': count})