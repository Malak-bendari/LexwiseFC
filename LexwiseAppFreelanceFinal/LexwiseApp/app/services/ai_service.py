import random
import json

def analyze_project_idea(title, description):
    """Analyze project idea and return insights"""
    # Mock AI analysis - in production, call OpenAI API
    description_lower = description.lower()
    
    # Check for keywords
    has_ai = 'ai' in description_lower or 'artificial intelligence' in description_lower
    has_blockchain = 'blockchain' in description_lower or 'web3' in description_lower
    has_mobile = 'mobile' in description_lower or 'app' in description_lower
    has_saas = 'saas' in description_lower or 'subscription' in description_lower
    
    strengths = []
    weaknesses = []
    suggestions = []
    
    if has_ai:
        strengths.append("Uses AI/ML technology - high growth potential")
    else:
        suggestions.append("Consider incorporating AI for competitive advantage")
    
    if has_blockchain:
        strengths.append("Blockchain integration - leading edge technology")
    else:
        weaknesses.append("Missing modern tech stack")
        suggestions.append("Evaluate blockchain for transparency/security")
    
    if has_mobile:
        strengths.append("Mobile-first approach - good user reach")
    
    if has_saas:
        strengths.append("SaaS model - recurring revenue potential")
    
    if len(strengths) == 0:
        strengths.append("Novel concept with market potential")
    
    if len(suggestions) == 0:
        suggestions.append("Conduct market validation survey")
        suggestions.append("Build MVP to test with early adopters")
    
    # Generate random market size estimate
    market_size = random.choice(["$50M", "$100M", "$250M", "$500M", "$1B"])
    competition = random.choice(["Low", "Medium", "High"])
    
    return {
        'strengths': strengths,
        'weaknesses': weaknesses,
        'suggestions': suggestions,
        'market_size': market_size,
        'competition_level': competition,
        'estimated_timeline': '6-12 months to MVP',
        'recommended_team_size': random.randint(2, 8)
    }

def analyze_contract(contract_text):
    """Analyze contract for dangerous clauses"""
    contract_lower = contract_text.lower()
    
    dangerous_clauses = []
    recommendations = []
    
    # Check for common dangerous clauses
    dangerous_patterns = [
        ('indemnification', 'Unlimited indemnification clause detected - high risk'),
        ('non-compete', 'Broad non-compete clause - may limit future opportunities'),
        ('exclusive', 'Exclusivity clause - restricts working with other clients'),
        ('termination without cause', 'One-sided termination clause'),
        ('intellectual property', 'IP ownership unclear - consider negotiating'),
        ('limitation of liability', 'Limited liability may cap damages'),
        ('confidentiality', 'Broad confidentiality - ensure reasonable scope'),
        ('governing law', 'Check governing law jurisdiction - may be unfavorable')
    ]
    
    for pattern, message in dangerous_patterns:
        if pattern in contract_lower:
            dangerous_clauses.append({
                'type': pattern,
                'message': message,
                'severity': random.choice(['High', 'Medium', 'Low'])
            })
            recommendations.append(f"Review and negotiate the {pattern} clause")
    
    if not dangerous_clauses:
        dangerous_clauses.append({
            'type': 'none',
            'message': 'No major red flags detected',
            'severity': 'Low'
        })
        recommendations.append("Contract looks good - proceed with caution")
    
    # Generate summary
    summary = f"This contract contains {len(dangerous_clauses)} clauses that require attention. "
    summary += f"Key areas to review: {', '.join([c['type'] for c in dangerous_clauses[:3]])}."
    
    # Generate negotiation script
    negotiation_script = generate_negotiation_script(contract_text, 'unfair')
    
    return {
        'dangerous_clauses': dangerous_clauses,
        'recommendations': recommendations,
        'summary': summary,
        'negotiation_script': negotiation_script.get('script', ''),
        'alternative_text': negotiation_script.get('alternative', '')
    }

def generate_negotiation_script(clause_text, clause_type):
    """Generate negotiation script for unfair clauses"""
    
    script = f"""
Dear [Counterparty Name],

I have reviewed the proposed agreement and would like to discuss the following clause:

Original Clause:
"{clause_text[:200]}..."

Concerns:
1. This clause appears unbalanced and may create unnecessary risk for both parties
2. Industry standard practices typically handle this differently
3. The current wording could lead to unintended consequences

Proposed Alternative:
{clause_text[:150]}... [revised to be more balanced]

Suggested Resolution:
- Let's schedule a brief call to discuss mutual concerns
- I'm open to finding a solution that works for both parties
- Happy to accept reasonable modifications

Looking forward to your thoughts.

Best regards,
[Your Name]
"""
    
    return {
        'script': script,
        'alternative': f"Revised: {clause_text[:100]}... [with fair terms]"
    }

def find_investor_matches(project):
    """Find matching investors for a project"""
    # Mock matching logic
    project_keywords = f"{project.title} {project.description} {project.category}".lower()
    
    investors = [
        {'name': 'TechVentures Capital', 'focus': ['ai', 'saas', 'tech'], 'budget': '$50K-$200K', 'score': 94},
        {'name': 'Angel Fund Group', 'focus': ['startup', 'mobile', 'app'], 'budget': '$25K-$100K', 'score': 89},
        {'name': 'Blockchain Angels', 'focus': ['blockchain', 'web3', 'crypto'], 'budget': '$30K-$150K', 'score': 82},
        {'name': 'HealthTech Ventures', 'focus': ['health', 'medical', 'ai'], 'budget': '$50K-$300K', 'score': 78},
        {'name': 'Eco Fund', 'focus': ['green', 'sustainable', 'environment'], 'budget': '$20K-$120K', 'score': 85}
    ]
    
    matches = []
    for investor in investors:
        match_score = 0
        for keyword in investor['focus']:
            if keyword in project_keywords:
                match_score += 30
        
        if match_score > 0:
            matches.append({
                'name': investor['name'],
                'match_score': min(match_score + random.randint(50, 80), 98),
                'budget_range': investor['budget'],
                'focus_areas': investor['focus']
            })
    
    return sorted(matches, key=lambda x: x['match_score'], reverse=True)[:5]
def find_investor_matches(project, limit=5):
    """Find matching investors for a project"""
    from app.services.scoring_service import calculate_match_score
    
    # Mock investor database - in production, query from database
    investors = [
        {
            'name': 'TechVentures Capital',
            'focus_areas': ['ai', 'machine learning', 'saas', 'tech', 'software'],
            'budget_range': '$50,000 - $200,000',
            'min_budget': 50000,
            'max_budget': 200000,
            'location': 'Global',
            'investment_stage': 'Seed, Series A'
        },
        {
            'name': 'Angel Fund Group',
            'focus_areas': ['startup', 'mobile', 'app', 'e-commerce', 'marketplace'],
            'budget_range': '$25,000 - $100,000',
            'min_budget': 25000,
            'max_budget': 100000,
            'location': 'North America',
            'investment_stage': 'Pre-seed, Seed'
        },
        {
            'name': 'Blockchain Angels',
            'focus_areas': ['blockchain', 'web3', 'crypto', 'defi', 'nft'],
            'budget_range': '$30,000 - $150,000',
            'min_budget': 30000,
            'max_budget': 150000,
            'location': 'Global',
            'investment_stage': 'Seed'
        },
        {
            'name': 'HealthTech Ventures',
            'focus_areas': ['health', 'medical', 'wellness', 'fitness', 'biotech'],
            'budget_range': '$50,000 - $300,000',
            'min_budget': 50000,
            'max_budget': 300000,
            'location': 'Europe, North America',
            'investment_stage': 'Seed, Series A'
        },
        {
            'name': 'Eco Fund',
            'focus_areas': ['green', 'sustainable', 'environment', 'clean energy', 'renewable'],
            'budget_range': '$20,000 - $120,000',
            'min_budget': 20000,
            'max_budget': 120000,
            'location': 'Global',
            'investment_stage': 'Pre-seed, Seed'
        },
        {
            'name': 'FinTech Capital',
            'focus_areas': ['fintech', 'banking', 'payments', 'lending', 'insurance'],
            'budget_range': '$100,000 - $500,000',
            'min_budget': 100000,
            'max_budget': 500000,
            'location': 'Global',
            'investment_stage': 'Series A, Series B'
        },
        {
            'name': 'SaaS Growth Partners',
            'focus_areas': ['saas', 'b2b', 'subscription', 'enterprise', 'cloud'],
            'budget_range': '$75,000 - $250,000',
            'min_budget': 75000,
            'max_budget': 250000,
            'location': 'North America, Europe',
            'investment_stage': 'Seed, Series A'
        },
        {
            'name': 'EdTech Investors',
            'focus_areas': ['education', 'edtech', 'learning', 'training', 'e-learning'],
            'budget_range': '$30,000 - $150,000',
            'min_budget': 30000,
            'max_budget': 150000,
            'location': 'Global',
            'investment_stage': 'Seed'
        }
    ]
    
    # Calculate match scores for each investor
    matches = []
    for investor in investors:
        match_result = calculate_match_score(project, investor, 'freelancer')
        matches.append({
            'name': investor['name'],
            'match_score': match_result['score'],
            'match_level': match_result['level'],
            'match_reasons': match_result['reasons'],
            'budget_range': investor['budget_range'],
            'focus_areas': investor['focus_areas'],
            'location': investor['location'],
            'investment_stage': investor['investment_stage']
        })
    
    # Sort by match score (highest first)
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    
    return matches[:limit]

def find_project_matches_for_investor(investor_profile, projects, limit=5):
    """Find matching projects for an investor"""
    from app.services.scoring_service import calculate_match_score
    
    matches = []
    for project in projects:
        # Convert project to dict if it's an object
        if hasattr(project, 'to_dict'):
            project_dict = project.to_dict()
        else:
            project_dict = project
        
        match_result = calculate_match_score(project_dict, investor_profile, 'investor')
        matches.append({
            'project_id': project_dict.get('id'),
            'project_title': project_dict.get('title'),
            'match_score': match_result['score'],
            'match_level': match_result['level'],
            'match_reasons': match_result['reasons'],
            'budget': project_dict.get('budget'),
            'category': project_dict.get('category'),
            'originality_score': project_dict.get('originality_score', 0)
        })
    
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches[:limit]

def analyze_contract_with_scoring(contract_text, title=""):
    """Full contract analysis with scoring"""
    from app.services.scoring_service import detect_dangerous_clauses, calculate_fairness_score
    
    # Detect dangerous clauses
    dangerous_clauses = detect_dangerous_clauses(contract_text)
    
    # Calculate fairness score
    fairness_score = calculate_fairness_score(contract_text, dangerous_clauses)
    
    # Generate recommendations based on clauses
    recommendations = []
    for clause in dangerous_clauses:
        if clause['severity'] in ['Critical', 'High']:
            recommendations.append({
                'clause': clause['type'],
                'recommendation': f"Negotiate or remove the {clause['type']} clause",
                'priority': 'High'
            })
        elif clause['severity'] == 'Medium':
            recommendations.append({
                'clause': clause['type'],
                'recommendation': f"Review and potentially revise the {clause['type']} clause",
                'priority': 'Medium'
            })
    
    # Generate negotiation script for the most critical clause
    negotiation_script = ""
    critical_clauses = [c for c in dangerous_clauses if c['severity'] in ['Critical', 'High']]
    if critical_clauses:
        negotiation_script = generate_contract_negotiation_script(critical_clauses[0]['type'])
    
    # Determine overall risk level
    if fairness_score >= 80:
        risk_level = "Low"
        summary = "This contract appears fair and balanced. Minor review recommended."
    elif fairness_score >= 60:
        risk_level = "Medium"
        summary = "This contract has several clauses that need attention. Negotiation recommended."
    else:
        risk_level = "High"
        summary = "This contract contains significant risks. Strongly recommend legal review and negotiation."
    
    return {
        'fairness_score': fairness_score,
        'risk_level': risk_level,
        'summary': summary,
        'dangerous_clauses': dangerous_clauses,
        'recommendations': recommendations,
        'negotiation_script': negotiation_script,
        'total_clauses_found': len(dangerous_clauses)
    }

def generate_contract_negotiation_script(clause_type):
    """Generate a negotiation script for a specific clause type"""
    scripts = {
        'indemnification': """
Dear [Counterparty],

I've reviewed the indemnification clause in our agreement. While I understand the need for protection, the current unlimited indemnification creates disproportionate risk.

I propose we amend this clause to a mutual indemnification limited to direct damages, capped at the total contract value. This aligns with industry standards and creates a more balanced agreement.

Looking forward to your thoughts.

Best regards,
[Your Name]
""",
        'non-compete': """
Dear [Counterparty],

Regarding the non-compete clause, the current restriction is broader than what's typical for this type of agreement.

I suggest we narrow the scope to:
- Specific competing products/services
- A reasonable 6-12 month timeframe
- Geographic limitations relevant to the work

This protects your legitimate business interests while allowing me to continue my career.

Best regards,
[Your Name]
""",
        'intellectual property': """
Dear [Counterparty],

The IP ownership clause needs clarification. I propose that:
- Background IP remains with each party
- Foreground IP created specifically for this project is assigned to you
- I retain the right to use knowledge and skills gained

This creates a fair arrangement that protects both parties' investments.

Best regards,
[Your Name]
""",
        'default': """
Dear [Counterparty],

I've reviewed the [CLAUSE_TYPE] clause and believe it needs revision for better balance.

I'm proposing a modified version that addresses both parties' concerns. Please let me know when we can discuss this.

Thank you for your consideration.

Best regards,
[Your Name]
"""
    }
    
    return scripts.get(clause_type, scripts['default'])