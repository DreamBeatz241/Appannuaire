import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import re
import os

class AnnuaireApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Annuaire GRT3")
        self.root.geometry("600x400")

        # Bannière
        self.label = tk.Label(root, text="Annuaire GRT3 - @Copyright 2025-2026", font=("Arial", 14))
        self.label.pack(pady=10)

        # Boutons du menu principal
        self.btn_enregistrer = tk.Button(root, text="Enregistrer un contact", command=self.enregistrer)
        self.btn_enregistrer.pack(pady=5)

        self.btn_supprimer = tk.Button(root, text="Supprimer un contact", command=self.supprimer)
        self.btn_supprimer.pack(pady=5)

        self.btn_rechercher = tk.Button(root, text="Rechercher un contact", command=self.rechercher)
        self.btn_rechercher.pack(pady=5)

        self.btn_modifier = tk.Button(root, text="Modifier un contact", command=self.modifier)
        self.btn_modifier.pack(pady=5)

        self.btn_afficher = tk.Button(root, text="Afficher l'annuaire", command=self.afficher)
        self.btn_afficher.pack(pady=5)

        self.btn_graph = tk.Button(root, text="Voir les statistiques", command=self.graphiques)
        self.btn_graph.pack(pady=5)

    def enregistrer(self):
        window = tk.Toplevel(self.root)
        window.title("Enregistrer un contact")
        window.geometry("300x300")

        tk.Label(window, text="Nom :").pack()
        nom_entry = tk.Entry(window)
        nom_entry.pack()

        tk.Label(window, text="Prénom :").pack()
        prenom_entry = tk.Entry(window)
        prenom_entry.pack()

        tk.Label(window, text="Email :").pack()
        email_entry = tk.Entry(window)
        email_entry.pack()

        tk.Label(window, text="Num1 :").pack()
        num1_entry = tk.Entry(window)
        num1_entry.pack()

        tk.Label(window, text="Num2 :").pack()
        num2_entry = tk.Entry(window)
        num2_entry.pack()

        def sauvegarder():
            nom, prenom, email, num1, num2 = nom_entry.get(), prenom_entry.get(), email_entry.get(), num1_entry.get(), num2_entry.get()
            if not (nom or prenom):
                messagebox.showerror("Erreur", "Le nom ou le prénom doit être fourni !")
                return
            # Remplacer les champs vides par ""
            nom = nom if nom else ""
            prenom = prenom if prenom else ""
            email = email if email else ""
            num1 = num1 if num1 else ""
            num2 = num2 if num2 else ""
            with open("annuaire.txt", "a") as f:
                if num1 and len(num1) > 1 and num1[1] == '7':
                    f.write(f"Nom:{nom};Prenom:{prenom};Email:{email};NumAirtel:{num1};NumLib:{num2}\n")
                else:
                    f.write(f"Nom:{nom};Prenom:{prenom};Email:{email};NumAirtel:{num2};NumLib:{num1}\n")
            messagebox.showinfo("Succès", "Contact enregistré avec succès !")
            window.destroy()

        tk.Button(window, text="Sauvegarder", command=sauvegarder).pack(pady=10)

    def supprimer(self):
        window = tk.Toplevel(self.root)
        window.title("Supprimer un contact")
        window.geometry("500x300")
        text_area = scrolledtext.ScrolledText(window, height=10, width=60)
        text_area.pack(pady=10)
        contacts = []
        try:
            with open("annuaire.txt", "r") as f:
                contacts = f.readlines()
                for i, contact in enumerate(contacts, 1):
                    text_area.insert(tk.END, f"{i}. {contact}")
        except FileNotFoundError:
            text_area.insert(tk.END, "Aucun contact enregistré.")

        tk.Label(window, text="Numéro du contact à supprimer :").pack()
        sup_entry = tk.Entry(window)
        sup_entry.pack()

        def supprimer_contact():
            try:
                sup = int(sup_entry.get()) - 1
                if 0 <= sup < len(contacts):
                    contacts.pop(sup)
                    with open("annuaire.txt", "w") as f:
                        f.writelines(contacts)
                    messagebox.showinfo("Succès", "Contact supprimé avec succès !")
                    window.destroy()
                else:
                    messagebox.showerror("Erreur", "Numéro invalide !")
            except ValueError:
                messagebox.showerror("Erreur", "Entrez un numéro valide !")

        tk.Button(window, text="Supprimer", command=supprimer_contact).pack(pady=10)

    def rechercher(self):
        window = tk.Toplevel(self.root)
        window.title("Rechercher un contact")
        window.geometry("400x200")

        tk.Label(window, text="Rechercher par :").pack()
        critere = tk.StringVar(value="Nom")
        tk.Radiobutton(window, text="Nom", variable=critere, value="Nom").pack()
        tk.Radiobutton(window, text="Prénom", variable=critere, value="Prenom").pack()
        tk.Radiobutton(window, text="Email", variable=critere, value="Email").pack()
        tk.Radiobutton(window, text="Numéro", variable=critere, value="Num").pack()

        tk.Label(window, text="Valeur :").pack()
        valeur_entry = tk.Entry(window)
        valeur_entry.pack()

        def rechercher_contact():
            resultat = ""
            try:
                with open("annuaire.txt", "r") as f:
                    for line in f:
                        if critere.get() == "Num":
                            if valeur_entry.get() in line:
                                resultat += line
                        elif re.search(valeur_entry.get(), line, re.IGNORECASE):
                            resultat += line
                if resultat:
                    messagebox.showinfo("Résultat", resultat)
                else:
                    messagebox.showinfo("Résultat", "Aucun contact trouvé.")
            except FileNotFoundError:
                messagebox.showerror("Erreur", "Aucun contact enregistré.")

        tk.Button(window, text="Rechercher", command=rechercher_contact).pack(pady=10)

    def modifier(self):
        window = tk.Toplevel(self.root)
        window.title("Modifier un contact")
        window.geometry("500x400")
        text_area = scrolledtext.ScrolledText(window, height=10, width=60)
        text_area.pack(pady=10)
        contacts = []
        try:
            with open("annuaire.txt", "r") as f:
                contacts = f.readlines()
                for i, contact in enumerate(contacts, 1):
                    text_area.insert(tk.END, f"{i}. {contact}")
        except FileNotFoundError:
            text_area.insert(tk.END, "Aucun contact enregistré.")

        tk.Label(window, text="Numéro du contact à modifier :").pack()
        cho_entry = tk.Entry(window)
        cho_entry.pack()

        tk.Label(window, text="Champ à modifier :").pack()
        champ = tk.StringVar(value="Nom")
        tk.Radiobutton(window, text="Nom", variable=champ, value="Nom").pack()
        tk.Radiobutton(window, text="Prénom", variable=champ, value="Prenom").pack()
        tk.Radiobutton(window, text="Email", variable=champ, value="Email").pack()
        tk.Radiobutton(window, text="Num Airtel", variable=champ, value="NumAirtel").pack()
        tk.Radiobutton(window, text="Num Libertis", variable=champ, value="NumLib").pack()

        tk.Label(window, text="Nouvelle valeur :").pack()
        new_val_entry = tk.Entry(window)
        new_val_entry.pack()

        def modifier_contact():
            try:
                cho = int(cho_entry.get()) - 1
                if 0 <= cho < len(contacts):
                    contact = contacts[cho].strip().split(";")
                    fields = {f.split(":")[0]: f.split(":")[1] for f in contact}
                    fields[champ.get()] = new_val_entry.get()
                    contacts[cho] = f"Nom:{fields['Nom']};Prenom:{fields['Prenom']};Email:{fields['Email']};NumAirtel:{fields['NumAirtel']};NumLib:{fields['NumLib']}\n"
                    with open("annuaire.txt", "w") as f:
                        f.writelines(contacts)
                    messagebox.showinfo("Succès", "Contact modifié avec succès !")
                    window.destroy()
                else:
                    messagebox.showerror("Erreur", "Numéro invalide !")
            except ValueError:
                messagebox.showerror("Erreur", "Entrez un numéro valide !")

        tk.Button(window, text="Modifier", command=modifier_contact).pack(pady=10)

    def afficher(self):
        window = tk.Toplevel(self.root)
        window.title("Annuaire")
        window.geometry("500x300")
        text_area = scrolledtext.ScrolledText(window, height=15, width=60)
        text_area.pack(pady=10)
        try:
            with open("annuaire.txt", "r") as f:
                text_area.insert(tk.END, f.read())
        except FileNotFoundError:
            text_area.insert(tk.END, "Aucun contact enregistré.")

    def graphiques(self):
        airtel_count, libertis_count = 0, 0
        try:
            with open("annuaire.txt", "r") as f:
                for line in f:
                    if "NumAirtel" in line:
                        airtel_count += 1
                    if "NumLib" in line:
                        libertis_count += 1
        except FileNotFoundError:
            airtel_count, libertis_count = 0, 0

        fig, ax = plt.subplots()
        labels = ['Airtel', 'Libertis']
        counts = [airtel_count, libertis_count]
        colors = ['#1f77b4', '#ff7f0e']
        ax.bar(labels, counts, color=colors)
        ax.set_title("Répartition des numéros par opérateur")
        ax.set_ylabel("Nombre de contacts")

        window = tk.Toplevel(self.root)
        window.title("Statistiques")
        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = AnnuaireApp(root)
    root.mainloop()