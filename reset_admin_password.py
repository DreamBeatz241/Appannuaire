from flask import Blueprint, request, jsonify, flash
from flask_login import login_required, current_user
from models import User, PasswordReset, db
from werkzeug.security import generate_password_hash
import logging

reset_admin_password = Blueprint('reset_admin_password', __name__)

@reset_admin_password.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    user = User.query.get(current_user.id)
    if not user or not check_password_hash(user.password, old_password):
        logging.warning(f"Tentative de changement de mot de passe échouée pour {current_user.email}")
        return jsonify({'error': 'Ancien mot de passe incorrect.'}), 400
    user.password = generate_password_hash(new_password)
    reset = PasswordReset(user_id=user.id, reset_by=user.id)
    db.session.add(reset)
    db.session.commit()
    logging.info(f"Mot de passe changé pour {current_user.email}")
    return jsonify({'message': 'Mot de passe changé avec succès !'})

@reset_admin_password.route('/api/admin/reset-password', methods=['POST'])
@login_required
def reset_password():
    if not current_user.is_admin:
        logging.warning(f"Tentative non autorisée de réinitialisation de mot de passe par {current_user.email}")
        return jsonify({'error': 'Accès réservé aux administrateurs.'}), 403
    data = request.get_json()
    email = data.get('email')
    new_password = data.get('new_password')
    user = User.query.filter_by(email=email).first()
    if not user:
        logging.warning(f"Utilisateur non trouvé pour réinitialisation : {email}")
        return jsonify({'error': 'Utilisateur non trouvé.'}), 404
    user.password = generate_password_hash(new_password)
    reset = PasswordReset(user_id=user.id, reset_by=current_user.id)
    db.session.add(reset)
    db.session.commit()
    logging.info(f"Mot de passe réinitialisé pour {email} par {current_user.email}")
    return jsonify({'message': 'Mot de passe réinitialisé avec succès !'})