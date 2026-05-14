from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.investor_profile import InvestorProfile
from app.models.project import Project

investors_bp = Blueprint('investors', __name__, url_prefix='/api/investors')

@investors_bp.route('/', methods=['GET'])
@login_required
def get_investors():
    """Get all REAL investors from database"""
    investors = User.query.filter_by(profile_type='investor', is_active=True).all()
    
    investor_list = []
    for inv in investors:
        # Don't show the current user if they are an investor
        if inv.id == current_user.id:
            continue
            
        profile = InvestorProfile.query.filter_by(user_id=inv.id).first()
        
        investor_list.append({
            'id': inv.id,
            'name': inv.username,
            'email': inv.email,
            'focus_areas': profile.get_focus_areas() if profile else ['General'],
            'budget_range': f"{profile.min_investment} - {profile.max_investment}" if profile else 'Not specified',
            'location': profile.location if profile else 'Global',
            'investment_stage': profile.investment_stage if profile else 'All stages',
            'bio': profile.bio if profile else 'No bio yet',
            'has_profile': profile is not None
        })
    
    return jsonify({'investors': investor_list})

@investors_bp.route('/profile', methods=['GET', 'PUT'])
@login_required
def manage_profile():
    """Get or update investor profile"""
    # Only investors can access this
    if current_user.profile_type != 'investor':
        return jsonify({'error': 'Only investors can access profile'}), 403
    
    profile = InvestorProfile.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'GET':
        if not profile:
            return jsonify({'profile': None, 'message': 'No profile created yet'})
        return jsonify({'profile': profile.to_dict()})
    
    # PUT - Update or create profile
    data = request.get_json()
    
    if not profile:
        profile = InvestorProfile(user_id=current_user.id)
        db.session.add(profile)
    
    if 'company_name' in data:
        profile.company_name = data['company_name']
    if 'position' in data:
        profile.position = data['position']
    if 'bio' in data:
        profile.bio = data['bio']
    if 'website' in data:
        profile.website = data['website']
    if 'location' in data:
        profile.location = data['location']
    if 'investment_stage' in data:
        profile.investment_stage = data['investment_stage']
    if 'min_investment' in data:
        profile.min_investment = data['min_investment']
    if 'max_investment' in data:
        profile.max_investment = data['max_investment']
    
    if data.get('focus_areas'):
        profile.set_focus_areas(data['focus_areas'])
    
    db.session.commit()
    
    return jsonify({'success': True, 'profile': profile.to_dict()})

@investors_bp.route('/<int:investor_id>', methods=['GET'])
@login_required
def get_investor(investor_id):
    """Get a single investor by ID"""
    investor = User.query.get_or_404(investor_id)
    if investor.profile_type != 'investor':
        return jsonify({'error': 'User is not an investor'}), 400
    
    profile = InvestorProfile.query.filter_by(user_id=investor_id).first()
    
    return jsonify({
        'id': investor.id,
        'name': investor.username,
        'email': investor.email,
        'profile': profile.to_dict() if profile else None
    })