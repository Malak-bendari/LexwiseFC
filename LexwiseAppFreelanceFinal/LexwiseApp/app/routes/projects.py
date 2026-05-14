from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
from app.services.grok_service import grok_service
import re
projects_bp = Blueprint('projects', __name__, url_prefix='/api/projects')

@projects_bp.route('/', methods=['GET'])
@login_required
def get_projects():
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return jsonify({'projects': [p.to_dict() for p in projects]})

@projects_bp.route('/', methods=['POST'])
@login_required
def create_project():
    # ONLY freelancers can create projects
    if current_user.profile_type != 'freelancer':
        return jsonify({'error': 'Only freelancers can upload projects'}), 403
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        budget = data.get('budget', '')
        category = data.get('category', '')
        
        print(f"Creating project - Title: {title}, User: {current_user.id}")
        print(f"Description length: {len(description)} characters")
        
        if not title or not description:
            return jsonify({'error': 'Title and description are required'}), 400
        
        # Check for minimum description length
        if len(description) < 30:
            return jsonify({'error': 'Please provide a more detailed description (minimum 30 characters)'}), 400
        
        # Use AI to analyze the project
        print("🤖 Calling Groq AI to analyze project...")
        analysis = grok_service.analyze_project(title, description, category, budget)
        
        # Get scores from AI analysis
        originality_score = analysis.get('final_score', analysis.get('originality_score', 50))
        
        # Create project
        project = Project(
            title=title,
            description=description,
            budget=budget if budget else None,
            category=category if category else None,
            originality_score=originality_score,
            user_id=current_user.id,
            status='active'
        )
        
        # Save full AI analysis as JSON in the project
        project.set_ai_analysis({
            'originality_score': analysis.get('originality_score', 0),
            'market_score': analysis.get('market_score', 0),
            'viability_score': analysis.get('viability_score', 0),
            'completeness_score': analysis.get('completeness_score', 0),
            'analysis_text': analysis.get('analysis', ''),
            'strengths': analysis.get('strengths', []),
            'weaknesses': analysis.get('weaknesses', []),
            'suggestions': analysis.get('suggestions', []),
            'market_insight': analysis.get('market_insight', ''),
            'investment_readiness': analysis.get('investment_readiness', 'Early Stage')
        })
        
        db.session.add(project)
        db.session.commit()
        
        # Increment usage AFTER successful creation
        # increment_usage(current_user.id)
        
        print(f"Project created - ID: {project.id}, Score: {originality_score}")
        
        return jsonify({
            'success': True,
            'project': project.to_dict(),
            'score': originality_score,
            'analysis': {
                'originality_score': analysis.get('originality_score', 0),
                'market_score': analysis.get('market_score', 0),
                'viability_score': analysis.get('viability_score', 0),
                'completeness_score': analysis.get('completeness_score', 0),
                'analysis_text': analysis.get('analysis', ''),
                'strengths': analysis.get('strengths', []),
                'weaknesses': analysis.get('weaknesses', []),
                'suggestions': analysis.get('suggestions', []),
                'market_insight': analysis.get('market_insight', ''),
                'investment_readiness': analysis.get('investment_readiness', '')
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating project: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
@projects_bp.route('/<int:project_id>', methods=['GET'])
@login_required
def get_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get AI analysis
    ai_analysis = project.get_ai_analysis()
    
    return jsonify({
        'project': {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'full_description': project.description,
            'budget': project.budget,
            'category': project.category,
            'status': project.status,
            'originality_score': project.originality_score,
            'ai_analysis': ai_analysis,
            'created_at': project.created_at.isoformat() if project.created_at else None
        }
    })

@projects_bp.route('/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'title' in data:
        project.title = data['title']
    if 'description' in data:
        project.description = data['description']
    if 'budget' in data:
        project.budget = data['budget']
    if 'category' in data:
        project.category = data['category']
    if 'status' in data:
        project.status = data['status']
    
    # Re-analyze with AI if description changed
    if 'description' in data and len(data['description']) > 30:
        print("🔄 Description changed, re-analyzing with AI...")
        analysis = grok_service.analyze_project(
            project.title, 
            project.description, 
            project.category, 
            project.budget
        )
        
        # Update scores
        project.originality_score = analysis.get('final_score', analysis.get('originality_score', 50))
        
        # Update AI analysis
        project.set_ai_analysis({
            'originality_score': analysis.get('originality_score', 0),
            'market_score': analysis.get('market_score', 0),
            'viability_score': analysis.get('viability_score', 0),
            'completeness_score': analysis.get('completeness_score', 0),
            'analysis_text': analysis.get('analysis', ''),
            'strengths': analysis.get('strengths', []),
            'weaknesses': analysis.get('weaknesses', []),
            'suggestions': analysis.get('suggestions', []),
            'market_insight': analysis.get('market_insight', ''),
            'investment_readiness': analysis.get('investment_readiness', 'Early Stage')
        })
    
    db.session.commit()
    return jsonify({'success': True, 'project': project.to_dict()})

@projects_bp.route('/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    db.session.delete(project)
    db.session.commit()
    return jsonify({'success': True})

@projects_bp.route('/public', methods=['GET'])
def get_public_projects():
    projects = Project.query.filter_by(status='active').order_by(Project.originality_score.desc()).limit(20).all()
    return jsonify({'projects': [p.to_dict() for p in projects]})

@projects_bp.route('/search', methods=['GET'])
@login_required
def search_projects():
    """Search and filter projects with AI-powered relevance scoring"""
    query = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'newest')
    status = request.args.get('status', '')
    
    # Base query for user's projects
    projects_query = Project.query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    if query:
        projects_query = projects_query.filter(
            Project.title.contains(query) | Project.description.contains(query)
        )
    
    # Apply category filter
    if category:
        projects_query = projects_query.filter_by(category=category)
    
    # Apply status filter
    if status:
        projects_query = projects_query.filter_by(status=status)
    
    # Apply sorting
    if sort_by == 'newest':
        projects_query = projects_query.order_by(Project.created_at.desc())
    elif sort_by == 'oldest':
        projects_query = projects_query.order_by(Project.created_at.asc())
    elif sort_by == 'score':
        projects_query = projects_query.order_by(Project.originality_score.desc())
    
    projects = projects_query.all()
    
    return jsonify({
        'projects': [p.to_dict() for p in projects],
        'total': len(projects),
        'filters': {'query': query, 'category': category, 'sort': sort_by}
    })

@projects_bp.route('/categories', methods=['GET'])
@login_required
def get_categories():
    """Get all unique categories from user's projects"""
    categories = db.session.query(Project.category).filter_by(user_id=current_user.id).distinct().all()
    categories = [c[0] for c in categories if c[0]]
    return jsonify({'categories': categories})

@projects_bp.route('/analyze-text', methods=['POST'])
@login_required
def analyze_text():
    """Analyze project text without saving - for preview"""
    try:
        data = request.get_json()
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        category = data.get('category', '')
        budget = data.get('budget', '')
        
        if not title or not description:
            return jsonify({'error': 'Title and description required'}), 400
        
        # Use AI to analyze
        analysis = grok_service.analyze_project(title, description, category, budget)
        
        return jsonify({
            'success': True,
            'score': analysis.get('final_score', analysis.get('originality_score', 50)),
            'analysis': {
                'originality_score': analysis.get('originality_score', 0),
                'market_score': analysis.get('market_score', 0),
                'viability_score': analysis.get('viability_score', 0),
                'completeness_score': analysis.get('completeness_score', 0),
                'analysis_text': analysis.get('analysis', ''),
                'strengths': analysis.get('strengths', []),
                'weaknesses': analysis.get('weaknesses', []),
                'suggestions': analysis.get('suggestions', []),
                'market_insight': analysis.get('market_insight', ''),
                'investment_readiness': analysis.get('investment_readiness', '')
            }
        })
        
    except Exception as e:
        print(f"Error analyzing text: {e}")
        return jsonify({'error': str(e)}), 500
    
@projects_bp.route('/<int:project_id>/funding', methods=['PUT'])
@login_required
def update_funding(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if 'funding_raised' in data:
        project.funding_raised = data['funding_raised']
        # Calculate percentage
        # This is simplified - you'd need to parse numbers properly
        project.funding_percentage = data.get('funding_percentage', 0)
    
    if 'funding_status' in data:
        project.funding_status = data['funding_status']
    
    db.session.commit()
    
    return jsonify({'success': True, 'project': project.to_dict()})
def to_dict(self):
    return {
        'id': self.id,
        'title': self.title,
        'description': self.description[:200],
        'budget': self.budget,
        'category': self.category,
        'status': self.status,
        'originality_score': self.originality_score,
        'user_id': self.user_id,  # MAKE SURE THIS LINE EXISTS
        'ai_analysis': self.get_ai_analysis(),
        'created_at': self.created_at.isoformat() if self.created_at else None,
        'updated_at': self.updated_at.isoformat() if self.updated_at else None
    }
@projects_bp.route('/public-with-owner', methods=['GET'])
def get_public_projects_with_owner():
    """Get public projects with owner info for investors"""
    projects = Project.query.filter_by(status='active').order_by(Project.originality_score.desc()).limit(20).all()
    
    projects_data = []
    for p in projects:
        project_dict = p.to_dict()
        project_dict['user_id'] = p.user_id  # Ensure user_id is included
        project_dict['owner_username'] = p.owner.username if p.owner else 'Unknown'
        projects_data.append(project_dict)
    
    return jsonify({'projects': projects_data})