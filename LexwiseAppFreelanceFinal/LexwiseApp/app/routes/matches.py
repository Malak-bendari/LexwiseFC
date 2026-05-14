from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.match import Match
from app.models.project import Project
from app.models.user import User
from app.models.notification import Notification
from app.services.email_service import email_service

matches_bp = Blueprint('matches', __name__, url_prefix='/api/matches')

@matches_bp.route('/', methods=['GET'])
@login_required
def get_matches():
    """Get matches for current user"""
    if current_user.profile_type == 'freelancer':
        # Freelancer sees matches on their projects
        matches = Match.query.filter_by(user_id=current_user.id).order_by(Match.created_at.desc()).all()
    else:
        # Investor sees matches they initiated
        matches = Match.query.filter_by(investor_id=current_user.id).order_by(Match.created_at.desc()).all()
    
    return jsonify({'matches': [m.to_dict() for m in matches]})

@matches_bp.route('/pending', methods=['GET'])
@login_required
def get_pending_matches():
    """Get pending match requests for current user"""
    if current_user.profile_type == 'freelancer':
        # Freelancer sees pending requests sent to them
        matches = Match.query.filter_by(user_id=current_user.id, status='pending').all()
    else:
        # Investor sees pending requests they sent
        matches = Match.query.filter_by(investor_id=current_user.id, status='pending').all()
    
    # Get project titles
    matches_list = []
    for m in matches:
        match_dict = m.to_dict()
        project = Project.query.get(m.project_id)
        match_dict['project_title'] = project.title if project else 'Unknown'
        matches_list.append(match_dict)
    
    return jsonify({'pending_matches': matches_list})

@matches_bp.route('/request', methods=['POST'])
@login_required
def request_match():
    """Request a match between freelancer project and investor"""
    try:
        data = request.get_json()
        print(f"Match request data: {data}")
        
        project_id = data.get('project_id')
        investor_id = data.get('investor_id')
        match_score = data.get('match_score', 85)
        
        if not project_id or not investor_id:
            return jsonify({'error': 'Project ID and Investor ID required'}), 400
        
        # Get the project
        project = Project.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Get investor
        investor = User.query.get(investor_id)
        if not investor:
            return jsonify({'error': 'Investor not found'}), 404
        
        # Check if current user is the investor (not the project owner!)
        if current_user.id != investor_id:
            return jsonify({'error': 'You can only request matches as yourself'}), 403
        
        # Check if match already exists
        existing = Match.query.filter_by(
            project_id=project_id,
            investor_id=investor_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Match request already sent'}), 400
        
        # Create match request
        match = Match(
            project_id=project_id,
            investor_id=investor_id,
            investor_name=investor.username,
            match_score=match_score,
            user_id=project.user_id,  # freelancer who owns the project
            status='pending'
        )
        
        db.session.add(match)
        db.session.commit()
        
        print(f"Match created: {match.id}")
        
        # Create notification for freelancer
        notification = Notification(
            user_id=project.user_id,
            title='🤝 New Match Request!',
            message=f'{investor.username} is interested in investing in your project "{project.title}"',
            type='match',
            link='/matches'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'match': match.to_dict(),
            'message': 'Match request sent! The freelancer will be notified.'
        })
        
    except Exception as e:
        print(f"Error in request_match: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@matches_bp.route('/<int:match_id>/respond', methods=['PUT'])
@login_required
def respond_to_match(match_id):
    """Accept or reject a match request"""
    try:
        data = request.get_json()
        status = data.get('status')
        
        match = Match.query.get_or_404(match_id)
        
        if match.user_id != current_user.id:
            return jsonify({'error': 'Only the freelancer can respond to match requests'}), 403
        
        match.status = status
        db.session.commit()
        
        project = Project.query.get(match.project_id)
        
        if status == 'accepted':
            # Create a welcome message from freelancer to investor
            from app.models.message import Message
            
            welcome_message = Message(
                sender_id=current_user.id,  # freelancer
                receiver_id=match.investor_id,  # investor
                content=f"Hi! I've accepted your match request for my project '{project.title}'. Let's discuss further!",
                is_read=False
            )
            db.session.add(welcome_message)
            
            # Create notification for investor
            notification = Notification(
                user_id=match.investor_id,
                title='✅ Match Accepted!',
                message=f'{current_user.username} accepted your match request for project "{project.title}". Check your messages!',
                type='match',
                link='/messages'
            )
            db.session.add(notification)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Match accepted! A welcome message has been sent.',
                'investor_id': match.investor_id,
                'investor_name': match.investor_name
            })
        else:
            notification = Notification(
                user_id=match.investor_id,
                title='❌ Match Declined',
                message=f'{current_user.username} declined your match request for project "{project.title}".',
                type='match',
                link='/matches'
            )
            db.session.add(notification)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Match declined.'
            })
            
    except Exception as e:
        print(f"Error in respond_to_match: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    

@matches_bp.route('/request-investor', methods=['POST'])
@login_required
def request_match_from_investor():
    """Investor requests to match with a freelancer's project"""
    data = request.get_json()
    project_id = data.get('project_id')
    freelancer_id = data.get('freelancer_id')
    project_title = data.get('project_title', '')
    
    if not project_id or not freelancer_id:
        return jsonify({'error': 'Project ID and Freelancer ID required'}), 400
    
    # Check if current user is an investor
    if current_user.profile_type != 'investor':
        return jsonify({'error': 'Only investors can send match requests'}), 403
    
    # Get the project
    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Check if match already exists
    existing = Match.query.filter_by(
        project_id=project_id,
        investor_id=current_user.id
    ).first()
    
    if existing:
        return jsonify({'error': 'Match request already sent'}), 400
    
    # Create match request
    match = Match(
        project_id=project_id,
        investor_id=current_user.id,
        investor_name=current_user.username,
        match_score=data.get('match_score', 85),
        user_id=freelancer_id,  # freelancer who owns the project
        status='pending'
    )
    
    db.session.add(match)
    db.session.commit()
    
    # Create notification for freelancer
    notification = Notification(
        user_id=freelancer_id,
        title='🤝 New Match Request!',
        message=f'{current_user.username} is interested in investing in your project "{project.title}"',
        type='match',
        link='/matches'
    )
    db.session.add(notification)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'match': match.to_dict(),
        'message': 'Match request sent! The freelancer will be notified.'
    })