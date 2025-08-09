from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
import os

app = Flask(__name__)
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(base_dir, "annuaire.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    try:
        db.create_all()

        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='company'")).fetchone()
        if not result:
            db.session.execute(text('CREATE TABLE company (id INTEGER PRIMARY KEY, name TEXT NOT NULL)'))
            db.session.commit()

        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='group'")).fetchone()
        if not result:
            db.session.execute(text('CREATE TABLE "group" (id INTEGER PRIMARY KEY, name TEXT NOT NULL, company_id INTEGER NOT NULL, FOREIGN KEY (company_id) REFERENCES company(id))'))
            db.session.commit()

        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")).fetchone()
        if not result:
            db.session.execute(text('CREATE TABLE user (id INTEGER PRIMARY KEY, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, is_admin BOOLEAN DEFAULT 0, company_id INTEGER, group_id INTEGER, FOREIGN KEY (company_id) REFERENCES company(id), FOREIGN KEY (group_id) REFERENCES "group"(id))'))
            db.session.commit()

        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='contact'")).fetchone()
        if not result:
            db.session.execute(text('CREATE TABLE contact (id INTEGER PRIMARY KEY, nom TEXT, prenom TEXT, email TEXT, num1 TEXT, num2 TEXT, user_id INTEGER NOT NULL, created_at DATETIME, FOREIGN KEY (user_id) REFERENCES user(id))'))
            db.session.commit()

        result = db.session.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='contact_groups'")).fetchone()
        if not result:
            db.session.execute(text('CREATE TABLE contact_groups (contact_id INTEGER, group_id INTEGER, PRIMARY KEY (contact_id, group_id), FOREIGN KEY (contact_id) REFERENCES contact(id), FOREIGN KEY (group_id) REFERENCES "group"(id))'))
            db.session.commit()

        result = db.session.execute(text('PRAGMA table_info(contact)')).fetchall()
        columns = [row[1] for row in result]
        if 'num_airtel' in columns:
            db.session.execute(text('ALTER TABLE contact RENAME COLUMN num_airtel TO num1'))
            db.session.commit()
        if 'num_lib' in columns:
            db.session.execute(text('ALTER TABLE contact RENAME COLUMN num_lib TO num2'))
            db.session.commit()
        if 'created_at' not in columns:
            db.session.execute(text('ALTER TABLE contact ADD COLUMN created_at DATETIME'))
            db.session.commit()

        result = db.session.execute(text('PRAGMA table_info(user)')).fetchall()
        columns = [row[1] for row in result]
        if 'company_id' not in columns:
            db.session.execute(text('ALTER TABLE user ADD COLUMN company_id INTEGER'))
            db.session.commit()
        if 'group_id' not in columns:
            db.session.execute(text('ALTER TABLE user ADD COLUMN group_id INTEGER'))
            db.session.commit()

        result = db.session.execute(text("SELECT id FROM company WHERE name='TechCorp'")).fetchone()
        if not result:
            db.session.execute(text("INSERT INTO company (name) VALUES ('TechCorp')"))
            db.session.commit()
        company_id = db.session.execute(text("SELECT id FROM company WHERE name='TechCorp'")).fetchone()[0]

        departments = ['Informatique', 'Juridique', 'Marketing', 'Ressources Humaines', 'Finance']
        for name in departments:
            result = db.session.execute(text(f"SELECT id FROM \"group\" WHERE name='{name}' AND company_id={company_id}")).fetchone()
            if not result:
                db.session.execute(text(f"INSERT INTO \"group\" (name, company_id) VALUES ('{name}', {company_id})"))
                db.session.commit()

        group_id = db.session.execute(text(f"SELECT id FROM \"group\" WHERE name='Informatique' AND company_id={company_id}")).fetchone()[0]
        db.session.execute(text(f'UPDATE user SET company_id = {company_id} WHERE company_id IS NULL'))
        db.session.commit()

        print("Base de données initialisée avec succès.")
    except Exception as e:
        print(f"Erreur lors de l’initialisation : {e}")
        db.session.rollback()