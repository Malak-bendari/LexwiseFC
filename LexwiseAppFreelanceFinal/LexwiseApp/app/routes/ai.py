from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services.ai_service import analyze_project_idea, analyze_contract, generate_negotiation_script
from app.services.scoring_service import calculate_originality_score, calculate_fairness_score

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/analyze-project', methods=['POST'])
@login_required
def analyze_project():
    """AI analysis for project ideas"""
    data = request.get_json()
    title = data.get('title', '')
    description = data.get('description', '')
    
    if not title or not description:
        return jsonify({'error': 'Title and description required'}), 400
    
    # Analyze project idea
    analysis = analyze_project_idea(title, description)
    originality = calculate_originality_score(description)
    
    return jsonify({
        'title': title,
        'originality_score': originality,
        'analysis': analysis,
        'suggestions': analysis.get('suggestions', [])
    })

@ai_bp.route('/analyze-contract', methods=['POST'])
@login_required
def analyze_contract_route():
    """AI analysis for contracts"""
    data = request.get_json()
    contract_text = data.get('content', '')
    contract_title = data.get('title', '')
    
    if not contract_text:
        return jsonify({'error': 'Contract content required'}), 400
    
    # Analyze contract
    analysis = analyze_contract(contract_text)
    fairness_score = calculate_fairness_score(analysis)
    dangerous_clauses = analysis.get('dangerous_clauses', [])
    
    return jsonify({
        'title': contract_title,
        'fairness_score': fairness_score,
        'dangerous_clauses': dangerous_clauses,
        'summary': analysis.get('summary', ''),
        'recommendations': analysis.get('recommendations', [])
    })

@ai_bp.route('/generate-script', methods=['POST'])
@login_required
def generate_script():
    """Generate negotiation script for unfair clauses"""
    data = request.get_json()
    clause_text = data.get('clause', '')
    clause_type = data.get('type', 'unfair')
    
    if not clause_text:
        return jsonify({'error': 'Clause text required'}), 400
    
    script = generate_negotiation_script(clause_text, clause_type)
    
    return jsonify({
        'original_clause': clause_text,
        'negotiation_script': script,
        'suggested_alternative': script.get('alternative', '')
    })

@ai_bp.route('/match-investor', methods=['POST'])
@login_required
def match_investor():
    """Match project with potential investors"""
    data = request.get_json()
    project_id = data.get('project_id')
    budget = data.get('budget', 0)
    category = data.get('category', '')
    
    # Simple matching logic
    matches = []
    
    # Mock investor data - in real app, query from database
    mock_investors = [
        {'name': 'TechVentures Capital', 'min_budget': 25000, 'max_budget': 200000, 'categories': ['AI', 'SaaS', 'Tech'], 'score': 94},
        {'name': 'Angel Fund Group', 'min_budget': 10000, 'max_budget': 100000, 'categories': ['Startups', 'Mobile'], 'score': 89},
        {'name': 'Blockchain Angels', 'min_budget': 30000, 'max_budget': 150000, 'categories': ['Blockchain', 'Web3'], 'score': 82},
        {'name': 'HealthTech Ventures', 'min_budget': 50000, 'max_budget': 300000, 'categories': ['HealthTech', 'AI'], 'score': 78},
        {'name': 'Eco Fund', 'min_budget': 20000, 'max_budget': 120000, 'categories': ['Green', 'Sustainability'], 'score': 85}
    ]
    
    for investor in mock_investors:
        if budget >= investor['min_budget'] and budget <= investor['max_budget']:
            if category in investor['categories'] or any(cat in investor['categories'] for cat in [category]):
                matches.append(investor)
    
    return jsonify({
        'project_id': project_id,
        'matches': matches[:5]  # Return top 5 matches
    })
@ai_bp.route('/match-project/<int:project_id>', methods=['GET'])
@login_required
def match_project(project_id):
    """Get matching investors for a specific project"""
    from app.models.project import Project
    from app.services.ai_service import find_investor_matches
    
    project = Project.query.get_or_404(project_id)
    
    # Check ownership
    if project.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    matches = find_investor_matches(project.to_dict())
    
    return jsonify({
        'project_id': project_id,
        'project_title': project.title,
        'matches': matches
    })

@ai_bp.route('/match-investor-projects', methods=['GET'])
@login_required
def match_investor_projects():
    """Get matching projects for an investor"""
    from app.models.project import Project
    from app.services.ai_service import find_project_matches_for_investor
    
    # Only investors can use this
    if current_user.profile_type != 'investor':
        return jsonify({'error': 'Only investors can access this endpoint'}), 403
    
    # Get all active projects
    projects = Project.query.filter_by(status='active').all()
    
    investor_profile = {
        'name': current_user.username,
        'focus_areas': ['ai', 'tech', 'startup'],  # Default - could be stored in user profile
        'budget_range': '$50,000 - $200,000'
    }
    
    matches = find_project_matches_for_investor(investor_profile, projects)
    
    return jsonify({
        'matches': matches
    })

@ai_bp.route('/analyze-contract-full', methods=['POST'])
@login_required
def analyze_contract_full():
    """Full contract analysis with detailed scoring"""
    from app.services.ai_service import analyze_contract_with_scoring
    
    data = request.get_json()
    contract_text = data.get('content', '')
    contract_title = data.get('title', '')
    
    if not contract_text:
        return jsonify({'error': 'Contract content required'}), 400
    
    analysis = analyze_contract_with_scoring(contract_text, contract_title)
    
    return jsonify(analysis)

@ai_bp.route('/bulk-match-projects', methods=['POST'])
@login_required
def bulk_match_projects():
    """Match multiple projects at once for investors"""
    from app.models.project import Project
    from app.services.ai_service import find_project_matches_for_investor
    
    if current_user.profile_type != 'investor':
        return jsonify({'error': 'Only investors can use this endpoint'}), 403
    
    data = request.get_json()
    project_ids = data.get('project_ids', [])
    
    if project_ids:
        projects = Project.query.filter(Project.id.in_(project_ids)).all()
    else:
        projects = Project.query.filter_by(status='active').limit(20).all()
    
    investor_profile = {
        'name': current_user.username,
        'focus_areas': data.get('focus_areas', ['ai', 'tech', 'startup']),
        'budget_range': data.get('budget_range', '$50,000 - $200,000')
    }
    
    matches = find_project_matches_for_investor(investor_profile, projects)
    
    return jsonify({
        'total_matches': len(matches),
        'matches': matches
    })