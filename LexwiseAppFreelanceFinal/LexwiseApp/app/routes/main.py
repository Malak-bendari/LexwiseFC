from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app import db
from app.models.project import Project
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

bp = Blueprint('main', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def analyze_idea(title, description):
    """Simple AI analysis - will be replaced with real AI later"""
    score = 0
    feedback = []
    
    # Basic analysis based on description length
    if len(description) > 500:
        score += 30
        feedback.append("✓ Detailed description - good clarity")
    elif len(description) > 200:
        score += 20
        feedback.append("✓ Description could be more detailed")
    else:
        feedback.append("⚠️ Add more details to your idea for better analysis")
    
    # Check for keywords
    keywords = ['market', 'user', 'problem', 'solution', 'revenue', 'growth', 'platform', 'app', 'web']
    found_keywords = [kw for kw in keywords if kw.lower() in description.lower()]
    score += len(found_keywords) * 5
    feedback.append(f"✓ Found {len(found_keywords)} key business elements")
    
    # Title quality
    if len(title) > 10:
        score += 15
        feedback.append("✓ Clear project title")
    else:
        feedback.append("⚠️ Consider a more descriptive title")
    
    # Random factor to make it interesting (will be replaced by real AI)
    import random
    score += random.randint(10, 30)
    
    # Cap at 100
    score = min(score, 100)
    
    # Determine risk level
    if score >= 80:
        risk = 'low'
        feedback.append("🎉 Strong idea! Ready for investor presentation.")
    elif score >= 60:
        risk = 'medium'
        feedback.append("📈 Good potential. Consider refining your value proposition.")
    else:
        risk = 'high'
        feedback.append("⚠️ Needs more work. Focus on problem-solution fit.")
    
    return score, risk, '\n'.join(feedback)

# Dashboard routes
@bp.route('/')
def index():
    return render_template('dashboard.html')

@bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Projects routes
@bp.route('/projects')
@login_required
def projects():
    user_projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template('projects.html', projects=user_projects)

@bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        
        if not title or not description:
            flash('Title and description are required', 'danger')
            return render_template('new_project.html')
        
        # Analyze the idea
        score, risk, feedback = analyze_idea(title, description)
        
        # Handle file upload
        file_path = None
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Create upload folder if it doesn't exist
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'projects')
                os.makedirs(upload_folder, exist_ok=True)
                
                file_path = os.path.join('uploads', 'projects', unique_filename)
                full_path = os.path.join(current_app.root_path, 'static', file_path)
                file.save(full_path)
        
        # Create project
        project = Project(
            user_id=current_user.id,
            title=title,
            description=description,
            category=category,
            originality_score=score,
            risk_level=risk,
            ai_feedback=feedback,
            file_path=file_path,
            status='analyzed'
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash(f'Project analyzed! Originality score: {score}/100', 'success')
        return redirect(url_for('main.projects'))
    
    return render_template('new_project.html')

@bp.route('/projects/<int:project_id>')
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('main.projects'))
    return render_template('view_project.html', project=project)

@bp.route('/projects/<int:project_id>/delete')
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied', 'danger')
        return redirect(url_for('main.projects'))
    
    # Delete file if exists
    if project.file_path:
        file_path = os.path.join(current_app.root_path, 'static', project.file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(project)
    db.session.commit()
    flash('Project deleted successfully', 'success')
    return redirect(url_for('main.projects'))

# Static page routes
@bp.route('/contracts')
def contracts():
    return render_template('contracts.html')

@bp.route('/matches')
def matches():
    return render_template('matches.html')

@bp.route('/messages')
def messages():
    return render_template('messages.html')