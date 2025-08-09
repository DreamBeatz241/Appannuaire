from flask import Blueprint, jsonify
from models import Contact, PasswordReset, Department
from datetime import datetime
from dateutil.relativedelta import relativedelta

api = Blueprint('api', __name__)

@api.route('/api/reset-stats')
def reset_stats():
    six_months_ago = datetime.utcnow() - relativedelta(months=6)
    resets = PasswordReset.query.filter(PasswordReset.reset_at >= six_months_ago).all()
    data = {}
    for reset in resets:
        month = reset.reset_at.strftime('%Y-%m')
        data[month] = data.get(month, 0) + 1
    labels = sorted(data.keys())
    values = [data[label] for label in labels]
    return jsonify({'labels': labels, 'values': values})

@api.route('/api/operator-stats')
def operator_stats():
    contacts = Contact.query.all()
    airtel = sum(1 for c in contacts if (c.num1 and 'airtel' in c.num1.lower()) or (c.num2 and 'airtel' in c.num2.lower()))
    libertis = sum(1 for c in contacts if (c.num1 and 'libertis' in c.num1.lower()) or (c.num2 and 'libertis' in c.num2.lower()))
    unknown = len(contacts) - airtel - libertis
    return jsonify({'airtel': airtel, 'libertis': libertis, 'unknown': unknown})

@api.route('/api/department-stats')
def department_stats():
    data = db.session.query(Department.name, db.func.count(Contact.id))\
        .join(Contact.departments).group_by(Department.name).all()
    labels, values = zip(*data) if data else ([], [])
    return jsonify({'labels': list(labels), 'values': list(values)})