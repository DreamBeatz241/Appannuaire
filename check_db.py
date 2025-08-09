import sqlite3
import os

base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, "annuaire.db")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Tables dans la base de données :")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        print(f"- {table[0]}")

    print("\nColonnes de la table 'user' :")
    cursor.execute("PRAGMA table_info(user);")
    columns = cursor.fetchall()
    for column in columns:
        print(f"- {column[1]} (type: {column[2]}, nullable: {'YES' if column[3] == 0 else 'NO'})")

    print("\nColonnes de la table 'contact' :")
    cursor.execute("PRAGMA table_info(contact);")
    columns = cursor.fetchall()
    for column in columns:
        print(f"- {column[1]} (type: {column[2]}, nullable: {'YES' if column[3] == 0 else 'NO'})")

    print("\nDépartements dans la table 'group' :")
    cursor.execute("SELECT name FROM \"group\";")
    groups = cursor.fetchall()
    for group in groups:
        print(f"- {group[0]}")

    print("\nExemple de contacts avec numéros :")
    cursor.execute("SELECT nom, prenom, num1, num2 FROM contact LIMIT 5;")
    contacts = cursor.fetchall()
    airtel_prefixes = ('077', '074', '076', '+24177', '+24174', '+24176')
    libertis_prefixes = ('060', '062', '065', '066', '+24160', '+24162', '+24165', '+24166')
    for contact in contacts:
        num1_type = 'Airtel' if contact[2] and contact[2].startswith(airtel_prefixes) else 'Libertis' if contact[2] and contact[2].startswith(libertis_prefixes) else 'Inconnu'
        num2_type = 'Airtel' if contact[3] and contact[3].startswith(airtel_prefixes) else 'Libertis' if contact[3] and contact[3].startswith(libertis_prefixes) else 'Inconnu'
        print(f"- {contact[0]} {contact[1]}: Num1={contact[2]} ({num1_type}), Num2={contact[3]} ({num2_type})")

    conn.close()
except Exception as e:
    print(f"Erreur : {e}")