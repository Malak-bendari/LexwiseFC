import re
import math
import random
from datetime import datetime

def calculate_originality_score(description, title=""):
    """
    Calculate originality score for project idea (0-100)
    Uses multiple factors: uniqueness, detail level, technical depth
    """
    score = 65  # Base score
    description_lower = description.lower()
    title_lower = title.lower()
    
    # === UNIQUENESS INDICATORS (+points) ===
    unique_indicators = [
        ('first', 8), ('never', 6), ('unique', 10), ('novel', 8),
        ('innovative', 7), ('patent', 15), ('patented', 15),
        ('cutting-edge', 6), ('revolutionary', 10), ('breakthrough', 12),
        ('disruptive', 10), ('groundbreaking', 12), ('world-first', 15)
    ]
    
    for indicator, points in unique_indicators:
        if indicator in description_lower:
            score += points
    
    # === COMMON/VAGUE TERMS (-points) ===
    common_terms = [
        ('app', -2), ('website', -2), ('platform', -1),
        ('easy', -3), ('simple', -3), ('basic', -4),
        ('standard', -2), ('ordinary', -5), ('typical', -3),
        ('another', -4), ('similar', -3)
    ]
    
    for term, penalty in common_terms:
        if term in description_lower:
            score += penalty
    
    # === DETAIL LEVEL FACTOR ===
    word_count = len(description.split())
    if word_count > 500:
        score += 15
    elif word_count > 300:
        score += 10
    elif word_count > 150:
        score += 5
    elif word_count < 50:
        score -= 15
    elif word_count < 30:
        score -= 25
    
    # === TECHNICAL DEPTH ===
    tech_terms = [
        'algorithm', 'data', 'api', 'cloud', 'blockchain', 'ai', 
        'machine learning', 'analytics', 'neural', 'deep learning',
        'encryption', 'distributed', 'microservices', 'kubernetes',
        'docker', 'react', 'python', 'javascript', 'database',
        'backend', 'frontend', 'mobile', 'ios', 'android'
    ]
    tech_count = sum(1 for term in tech_terms if term in description_lower)
    score += min(tech_count * 3, 20)  # Max 20 points from tech terms
    
    # === MARKET POTENTIAL INDICATORS ===
    market_terms = ['market', 'users', 'customers', 'revenue', 'growth', 'scalable']
    market_count = sum(1 for term in market_terms if term in description_lower)
    score += market_count * 3
    
    # === COMPETITION AWARENESS ===
    competition_terms = ['competitor', 'competition', 'unique selling', 'usp', 'different']
    competition_count = sum(1 for term in competition_terms if term in description_lower)
    score += competition_count * 4
    
    # Ensure score is within 0-100
    return max(0, min(100, score))

def calculate_fairness_score(contract_text, dangerous_clauses=None):
    """
    Calculate fairness score for contract (0-100)
    Lower score = more unfair/dangerous clauses
    """
    if dangerous_clauses is None:
        dangerous_clauses = detect_dangerous_clauses(contract_text)
    
    # Start with perfect score
    score = 100
    
    # Deduct points based on clause severity
    for clause in dangerous_clauses:
        severity = clause.get('severity', 'Medium')
        if severity == 'Critical':
            score -= 25
        elif severity == 'High':
            score -= 15
        elif severity == 'Medium':
            score -= 8
        else:
            score -= 3
    
    # Check for balanced language
    balanced_indicators = [
        ('mutually', 5), ('both parties', 5), ('agree', 3),
        ('reasonable', 4), ('standard', 2), ('industry', 3)
    ]
    
    text_lower = contract_text.lower()
    for indicator, points in balanced_indicators:
        if indicator in text_lower:
            score += points
    
    # Check for one-sided language
    one_sided_terms = [
        ('sole discretion', -8), ('indemnify', -5), ('non-compete', -10),
        ('exclusive', -6), ('irrevocable', -4), ('waive', -5)
    ]
    
    for term, penalty in one_sided_terms:
        if term in text_lower:
            score += penalty
    
    return max(0, min(100, score))

def detect_dangerous_clauses(contract_text):
    """Detect dangerous clauses in contract text"""
    text_lower = contract_text.lower()
    dangerous_clauses = []
    
    clause_patterns = [
        ('indemnification', 'Unlimited indemnification - high risk', 'High'),
        ('indemnify', 'Indemnification clause - review carefully', 'High'),
        ('non-compete', 'Non-compete clause - may limit future work', 'High'),
        ('exclusive', 'Exclusivity clause - restricts other work', 'Medium'),
        ('termination for convenience', 'One-sided termination clause', 'High'),
        ('without cause', 'Termination without cause - risky', 'High'),
        ('intellectual property', 'IP ownership - ensure you retain rights', 'High'),
        ('assignment', 'Assignment clause - check who can transfer', 'Medium'),
        ('limitation of liability', 'Limited liability - may cap damages', 'Medium'),
        ('confidentiality', 'Confidentiality - ensure reasonable scope', 'Low'),
        ('governing law', 'Governing law - check jurisdiction', 'Low'),
        ('arbitration', 'Arbitration clause - limits legal recourse', 'Medium'),
        ('class action', 'Class action waiver', 'Medium'),
        ('force majeure', 'Force majeure - check for balance', 'Low'),
        ('non-solicitation', 'Non-solicitation - may restrict hiring', 'Medium'),
        ('non-disparagement', 'Non-disparagement - limits feedback', 'Low'),
        ('liquidated damages', 'Liquidated damages - ensure reasonable', 'High'),
        ('warranty', 'Warranty clause - review scope', 'Medium'),
        ('representation', 'Representations - ensure accurate', 'Medium'),
        ('severability', 'Severability - generally safe', 'Low')
    ]
    
    for keyword, message, severity in clause_patterns:
        if keyword in text_lower:
            dangerous_clauses.append({
                'type': keyword,
                'message': message,
                'severity': severity
            })
    
    # Remove duplicates based on keyword
    seen = set()
    unique_clauses = []
    for clause in dangerous_clauses:
        if clause['type'] not in seen:
            seen.add(clause['type'])
            unique_clauses.append(clause)
    
    return unique_clauses

def calculate_match_score(project, investor, profile_type='freelancer'):
    """
    Calculate match score between project and investor
    Returns score 0-100 and match details
    """
    score = 50  # Base score
    match_reasons = []
    
    # Get project details
    project_title = (project.get('title', '') or getattr(project, 'title', '')).lower()
    project_desc = (project.get('description', '') or getattr(project, 'description', '')).lower()
    project_category = (project.get('category', '') or getattr(project, 'category', '')).lower()
    project_budget = project.get('budget', '') or getattr(project, 'budget', '')
    
    # Get investor details
    investor_focus = [f.lower() for f in investor.get('focus_areas', [])]
    investor_name = investor.get('name', '')
    investor_budget = investor.get('budget_range', '')
    
    # === CATEGORY MATCH (30 points max) ===
    if project_category:
        for focus in investor_focus:
            if focus in project_category or project_category in focus:
                score += 25
                match_reasons.append(f"Category match: {project_category} → {investor_name}")
                break
        else:
            # Check if category appears in project description
            for focus in investor_focus:
                if focus in project_desc:
                    score += 15
                    match_reasons.append(f"Relevant focus area: {focus}")
                    break
    
    # === KEYWORD MATCH (20 points max) ===
    keywords = project_title.split() + project_desc.split()[:50]
    keyword_matches = []
    for focus in investor_focus:
        if focus in keywords or any(focus in kw for kw in keywords):
            keyword_matches.append(focus)
    
    score += min(len(keyword_matches) * 5, 20)
    if keyword_matches:
        match_reasons.append(f"Keyword match: {', '.join(keyword_matches[:3])}")
    
    # === BUDGET MATCH (20 points max) ===
    if project_budget and investor_budget:
        # Extract numbers from budget strings
        import re
        project_numbers = re.findall(r'\d+', str(project_budget))
        investor_numbers = re.findall(r'\d+', investor_budget)
        
        if project_numbers and investor_numbers:
            project_avg = sum(map(int, project_numbers)) / len(project_numbers)
            investor_min = int(investor_numbers[0]) if investor_numbers else 0
            investor_max = int(investor_numbers[1]) if len(investor_numbers) > 1 else investor_min * 3
            
            if investor_min <= project_avg <= investor_max:
                score += 20
                match_reasons.append(f"Budget alignment: ${project_avg:,.0f} within ${investor_min:,.0f}-${investor_max:,.0f}")
            elif project_avg < investor_min:
                score += 10
                match_reasons.append(f"Project budget (${project_avg:,.0f}) below investor minimum (${investor_min:,.0f})")
            elif project_avg > investor_max:
                score += 5
                match_reasons.append(f"Project budget exceeds typical investor range")
    
    # === PROJECT SCORE BONUS (15 points max) ===
    project_score = project.get('originality_score', 0) or getattr(project, 'originality_score', 0)
    if project_score:
        score += (project_score - 50) * 0.3
        if project_score > 85:
            match_reasons.append(f"Excellent project score: {project_score}/100")
        elif project_score > 75:
            match_reasons.append(f"Good project score: {project_score}/100")
    
    # === COMPLETENESS BONUS (10 points) ===
    completeness = 0
    if project.get('budget'):
        completeness += 3
    if project.get('category'):
        completeness += 3
    if len(project_desc) > 200:
        completeness += 4
    score += completeness
    
    # Ensure score is within 0-100
    final_score = max(0, min(100, int(score)))
    
    # Determine match level
    if final_score >= 85:
        match_level = "Excellent"
    elif final_score >= 70:
        match_level = "Good"
    elif final_score >= 55:
        match_level = "Potential"
    else:
        match_level = "Low"
    
    return {
        'score': final_score,
        'level': match_level,
        'reasons': match_reasons[:5],
        'investor_name': investor_name,
        'investor_budget': investor_budget,
        'investor_focus': investor_focus
    }

def calculate_ai_confidence(factors):
    """Calculate AI confidence score based on multiple factors"""
    weights = {
        'data_quality': 0.25,
        'pattern_matches': 0.25,
        'context_relevance': 0.20,
        'historical_accuracy': 0.30
    }
    
    confidence = 0
    for factor, weight in weights.items():
        value = factors.get(factor, 0.7)  # Default 70%
        confidence += value * weight
    
    return min(0.95, max(0.5, confidence))