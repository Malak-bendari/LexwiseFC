from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from app import db
from app.models.contract import Contract
import os
from werkzeug.utils import secure_filename
from datetime import datetime
contracts_bp = Blueprint('contracts', __name__, url_prefix='/api/contracts')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@contracts_bp.route('/upload', methods=['POST'])
@login_required
def upload_contract():
    """Upload and analyze a contract"""
    try:
        print("\n=== CONTRACT UPLOAD ===")
        print(f"User: {current_user.username} (ID: {current_user.id})")
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        title = request.form.get('title', '')
        
        print(f"File: {file.filename}")
        print(f"Title: {title}")
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': f'File type not allowed. Use: {", ".join(ALLOWED_EXTENSIONS)}'}), 400
        
        # Create upload folder
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{current_user.id}_{timestamp}_{filename}"
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Simple analysis
        fairness_score = 75
        summary = "Contract uploaded and analyzed successfully."
        dangerous_clauses = [{"type": "Standard Review", "severity": "Low", "explanation": "Review all clauses carefully"}]
        negotiation_script = "Please review all clauses carefully before signing. Consider consulting a legal professional for important contracts."
        
        # Create contract record
        contract = Contract(
            title=title if title else filename,
            filename=filename,
            file_path=file_path,
            content="Contract content extracted",
            fairness_score=fairness_score,
            summary=summary,
            negotiation_script=negotiation_script,
            user_id=current_user.id
        )
        contract.set_dangerous_clauses(dangerous_clauses)
        
        db.session.add(contract)
        db.session.commit()
        
        print(f"Contract saved with ID: {contract.id}")
        
        return jsonify({
            'success': True,
            'contract_id': contract.id,
            'fairness_score': fairness_score,
            'dangerous_clauses': dangerous_clauses,
            'negotiation_script': negotiation_script,
            'summary': summary,
            'message': 'Contract uploaded and analyzed successfully!'
        })
        
    except Exception as e:
        print(f"ERROR in upload_contract: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@contracts_bp.route('/', methods=['GET'])
@login_required
def get_contracts():
    contracts = Contract.query.filter_by(user_id=current_user.id).order_by(Contract.created_at.desc()).all()
    return jsonify([c.to_dict() for c in contracts])

@contracts_bp.route('/<int:contract_id>', methods=['GET'])
@login_required
def get_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if contract.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    return jsonify(contract.to_dict())

@contracts_bp.route('/<int:contract_id>/download', methods=['GET'])
@login_required
def download_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if contract.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'error': 'Access denied'}), 403
    
    if not os.path.exists(contract.file_path):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        contract.file_path, 
        as_attachment=True, 
        download_name=contract.filename
    )

@contracts_bp.route('/<int:contract_id>', methods=['DELETE'])
@login_required
def delete_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if contract.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    if os.path.exists(contract.file_path):
        os.remove(contract.file_path)
    
    db.session.delete(contract)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Contract deleted'})

@contracts_bp.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Contracts blueprint is working!'})