from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import db, User, Contact, Department, PasswordReset
from config import Config
import logging
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

logging.basicConfig(filename='annuaire.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    user_contacts = Contact.query.filter_by(user_id=current_user.id).all()
    total_contacts = len(user_contacts)
    num1_airtel = sum(1 for c in user_contacts if c.num1 and 'airtel' in c.num1.lower())
    num1_libertis = sum(1 for c in user_contacts if c.num1 and 'libertis' in c.num1.lower())
    num2_airtel = sum(1 for c in user_contacts if c.num2 and 'airtel' in c.num2.lower())
    num2_libertis = sum(1 for c in user_contacts if c.num2 and 'libertis' in c.num2.lower())
    
    stats = {
        'total_contacts': total_contacts,
        'num1_airtel': num1_airtel,
        'num1_libertis': num1_libertis,
        'num1_airtel_percent': round(num1_airtel / total_contacts * 100, 2) if total_contacts else 0,
        'num1_libertis_percent': round(num1_libertis / total_contacts * 100, 2) if total_contacts else 0,
        'num2_airtel': num2_airtel,
        'num2_libertis': num2_libertis,
        'num2_airtel_percent': round(num2_airtel / total_contacts * 100, 2) if total_contacts else 0,
        'num2_libertis_percent': round(num2_libertis / total_contacts * 100, 2) if total_contacts else 0
    }
    
    admin_stats = None
    if current_user.is_admin:
        company_contacts = Contact.query.count()
        contacts_by_department = db.session.query(Department.name, db.func.count(Contact.id))\
            .join(Contact.departments).group_by(Department.name).all()
        users_by_department = db.session.query(Department.name, db.func.count(User.id))\
            .join(User.department).group_by(Department.name).all()
        no_dept_users = User.query.filter_by(department_id=None).count()
        
        admin_stats = {
            'company_contacts': company_contacts,
            'contacts_by_department': contacts_by_department,
            'users_by_department': users_by_department,
            'no_dept_users': no_dept_users
        }
    
    return render_template('index.html', stats=stats, admin_stats=admin_stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            logging.info(f"Utilisateur {email} connecté.")
            flash('Connexion réussie !', 'success')
            return redirect(url_for('index'))
        flash('Email ou mot de passe incorrect.', 'danger')
        logging.warning(f"Tentative de connexion échouée pour {email}.")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        department_id = request.form.get('department') or None
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà utilisé.', 'danger')
            return redirect(url_for('register'))
        user = User(email=email, password=password, department_id=department_id)
        db.session.add(user)
        db.session.commit()
        logging.info(f"Nouvel utilisateur inscrit : {email}")
        flash('Inscription réussie ! Connectez-vous.', 'success')
        return redirect(url_for('login'))
    departments = Department.query.all()
    return render_template('register.html', departments=departments)

@app.route('/logout')
@login_required
def logout():
    logging.info(f"Utilisateur {current_user.email} déconnecté.")
    logout_user()
    flash('Déconnexion réussie.', 'success')
    return redirect(url_for('login'))

@app.route('/add_contact', methods=['GET', 'POST'])
@login_required
def add_contact():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        num1 = request.form['num1']
        num2 = request.form['num2']
        group_ids = request.form.getlist('groups')
        contact = Contact(nom=nom, prenom=prenom, email=email, num1=num1, num2=num2, user_id=current_user.id)
        for group_id in group_ids:
            department = Department.query.get(group_id)
            if department:
                contact.departments.append(department)
        db.session.add(contact)
        db.session.commit()
        logging.info(f"Contact ajouté par {current_user.email}: {nom} {prenom}")
        flash('Contact ajouté avec succès !', 'success')
        return redirect(url_for('my_contacts'))
    departments = Department.query.all()
    return render_template('add_contact.html', departments=departments)

@app.route('/edit_contact/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_contact(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id and not current_user.is_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('my_contacts'))
    if request.method == 'POST':
        contact.nom = request.form['nom']
        contact.prenom = request.form['prenom']
        contact.email = request.form['email']
        contact.num1 = request.form['num1']
        contact.num2 = request.form['num2']
        group_ids = request.form.getlist('groups')
        contact.departments.clear()
        for group_id in group_ids:
            department = Department.query.get(group_id)
            if department:
                contact.departments.append(department)
        db.session.commit()
        logging.info(f"Contact modifié par {current_user.email}: {contact.nom} {contact.prenom}")
        flash('Contact modifié avec succès !', 'success')
        return redirect(url_for('my_contacts'))
    departments = Department.query.all()
    return render_template('edit_contact.html', contact=contact, departments=departments)

@app.route('/delete-contact/<int:id>')
@login_required
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    if contact.user_id != current_user.id and not current_user.is_admin:
        flash('Accès non autorisé.', 'danger')
        return redirect(url_for('my_contacts'))
    db.session.delete(contact)
    db.session.commit()
    logging.info(f"Contact supprimé par {current_user.email}: ID {id}")
    flash('Contact supprimé avec succès.', 'success')
    return redirect(url_for('my_contacts'))

@app.route('/contacts')
@login_required
def contacts():
    if current_user.is_admin:
        contacts = [(c.id, [f"Nom: {c.nom}", f"Prénom: {c.prenom}", f"Email: {c.email}", f"Num1: {c.num1}", f"Num2: {c.num2}", f"Propriétaire: {c.user.email}", f"Départements: {', '.join(d.name for d in c.departments)}"]) for c in Contact.query.all()]
    else:
        contacts = [(c.id, [f"Nom: {c.nom}", f"Prénom: {c.prenom}", f"Email: {c.email}", f"Num1: {c.num1}", f"Num2: {c.num2}", f"Départements: {', '.join(d.name for d in c.departments)}"]) for c in Contact.query.filter_by(user_id=current_user.id).all()]
    return render_template('contacts.html', contacts=contacts)

@app.route('/my-contacts')
@login_required
def my_contacts():
    contacts = [(c.id, [f"Nom: {c.nom}", f"Prénom: {c.prenom}", f"Email: {c.email}", f"Num1: {c.num1}", f"Num2: {c.num2}", f"Départements: {', '.join(d.name for d in c.departments)}"]) for c in Contact.query.filter_by(user_id=current_user.id).all()]
    return render_template('my_contacts.html', contacts=contacts)

@app.route('/public_search', methods=['GET', 'POST'])
@login_required
def public_search():
    contacts = []
    if request.method == 'POST':
        criterion = request.form.get('criterion')
        value = request.form.get('value')
        department_id = request.form.get('department')
        query = Contact.query
        if criterion and value:
            if criterion == 'nom':
                query = query.filter(Contact.nom.ilike(f'%{value}%'))
            elif criterion == 'prenom':
                query = query.filter(Contact.prenom.ilike(f'%{value}%'))
            elif criterion == 'email':
                query = query.filter(Contact.email.ilike(f'%{value}%'))
        if department_id:
            query = query.join(Contact.departments).filter(Department.id == department_id)
        contacts = [(c.id, [f"Nom: {c.nom}", f"Prénom: {c.prenom}", f"Email: {c.email}", f"Num1: {c.num1}", f"Num2: {c.num2}", f"Départements: {', '.join(d.name for d in c.departments)}"]) for c in query.all()]
    departments = Department.query.all()
    return render_template('public_search.html', contacts=contacts, departments=departments)

@app.route('/manage_departments', methods=['GET', 'POST'])
@login_required
def manage_departments():
    if not current_user.is_admin:
        flash('Accès réservé aux administrateurs.', 'danger')
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form['name']
        department = Department(name=name)
        db.session.add(department)
        db.session.commit()
        logging.info(f"Département créé par {current_user.email}: {name}")
        flash('Département créé avec succès !', 'success')
        return redirect(url_for('manage_departments'))
    departments = [(d.name, [(u.email, 'Admin' if u.is_admin else 'Utilisateur') for u in d.users]) for d in Department.query.all()]
    contacts = [(c.id, [f"Nom: {c.nom}", f"Prénom: {c.prenom}", f"Email: {c.email}", f"Num1: {c.num1}", f"Num2: {c.num2}", f"Propriétaire: {c.user.email}", f"Départements: {', '.join(d.name for d in c.departments)}"]) for c in Contact.query.all()]
    total_contacts = Contact.query.count()
    return render_template('manage_departments.html', departments=departments, contacts=contacts, total_contacts=total_contacts)

@app.route('/change-password', methods=['GET'])
@login_required
def change_password():
    return render_template('change_password.html')

@app.route('/reset-password', methods=['GET'])
@login_required
def reset_password():
    if not current_user.is_admin:
        flash('Accès réservé aux administrateurs.', 'danger')
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('reset_password.html', users=users)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(email='admin@example.com', password='admin123', is_admin=True)
            db.session.add(admin)
            db.session.commit()
            logging.info("Utilisateur admin créé.")
    app.run(debug=True)