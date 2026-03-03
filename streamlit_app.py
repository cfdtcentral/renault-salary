import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- CONFIGURATION ---
ADMIN_PWD = "RENAULT_PRO_2026"
MASTER_FILE = "Renault_Contributions.xlsx"
ECO_FILE = "Renault_Grille_SMH_Inflation.xlsx"

# --- MOTEUR DE GESTION EXCEL ---
def load_all_data():
    if not os.path.exists(MASTER_FILE):
        return pd.DataFrame(), []
    
    # Lecture de tous les onglets (classes d'emploi)
    all_sheets = pd.read_excel(MASTER_FILE, sheet_name=None)
    if not all_sheets:
        return pd.DataFrame(), []
    
    # Fusion pour la recherche globale par matricule
    df_global = pd.concat(all_sheets.values(), ignore_index=True, sort=False)
    return df_global, list(all_sheets.keys())

def save_entry(row_data, sheet_name):
    # Création ou mise à jour du fichier avec onglets
    if os.path.exists(MASTER_FILE):
        with pd.ExcelWriter(MASTER_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            try:
                # On essaie de lire l'onglet existant pour ajouter la ligne
                existing_df = pd.read_excel(MASTER_FILE, sheet_name=sheet_name)
                updated_df = pd.concat([existing_df, pd.DataFrame([row_data])], ignore_index=True)
                updated_df.to_excel(writer, sheet_name=sheet_name, index=False)
            except Exception:
                # Si l'onglet n'existe pas encore, on le crée
                pd.DataFrame([row_data]).to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        # Premier lancement : création du fichier
        with pd.ExcelWriter(MASTER_FILE, engine='openpyxl') as writer:
            pd.DataFrame([row_data]).to_excel(writer, sheet_name=sheet_name, index=False)

# --- INTERFACE ---
st.set_page_config(page_title="Renault Salary Insight", layout="wide")
st.title("💎 RENAULT SALARY INTELLIGENCE")

tab_user, tab_admin = st.tabs(["📊 Mon Profil", "🔐 Administration"])

df_global, liste_classes = load_all_data()

with tab_user:
    st.subheader("Identification")
    # Utilisation du champ exact : Matricule de l'employé
    u_mat = st.text_input("Saisissez votre Matricule de l'employé (8 chiffres)")
    
    if u_mat:
        # Recherche robuste (convertit en texte pour éviter les erreurs de format)
        match = df_global[df_global["Matricule de l'employé"].astype(str) == str(u_mat)]
        
        if not match.empty:
            info = match.iloc[0]
            st.success(f"✅ Salarié reconnu : {info['Employé']}")
            st.write(f"**Poste :** {info['Poste']} | **Classe :** {info['Classe_Emploi']}")
            
            u_sal = st.number_input("Salaire Brut Annuel Actuel (€)", value=30000)
            if st.button("Enregistrer ma rémunération"):
                new_data = info.to_dict()
                new_data['SALAIRE_REEL'] = u_sal
                new_data['VALIDATION'] = 1
                save_entry(new_data, str(info['Classe_Emploi']))
                st.balloons()
        else:
            st.warning("⚠️ Matricule absent du référentiel actuel.")
            with st.form("ajout_manquant"):
                st.write("Complétez vos informations (Soumis à validation admin)")
                n_nom = st.text_input("Nom Prénom")
                n_poste = st.text_input("Intitulé du Poste")
                n_classe = st.selectbox("Classe d'emploi", [f"A{i}" for i in range(1,11)] + [f"C{i}" for i in range(1,16)] + [f"I{i}" for i in range(1,19)])
                n_sal = st.number_input("Salaire (€)")
                if st.form_submit_button("Soumettre mon profil"):
                    new_row = {
                        "Matricule de l'employé": u_mat, "Employé": n_nom, 
                        "Poste": n_poste, "Classe_Emploi": n_classe, 
                        "SALAIRE_REEL": n_sal, "VALIDATION": 0
                    }
                    save_entry(new_row, n_classe)
                    st.info("Profil envoyé ! L'administrateur vérifiera votre classe d'emploi.")

with tab_admin:
    if st.text_input("Code Secret Admin", type="password") == ADMIN_PWD:
        st.subheader("Gestion des Classes d'Emploi (A1 à I18)")
        if liste_classes:
            classe_choisie = st.selectbox("Sélectionner la classe à gérer", liste_classes)
            df_classe = pd.read_excel(MASTER_FILE, sheet_name=classe_choisie)
            
            # Éditeur de données pour corriger ou valider
            st.write(f"Données pour la classe : {classe_choisie}")
            edited = st.data_editor(df_classe, num_rows="dynamic")
            
            if st.button("Sauvegarder les modifications"):
                with pd.ExcelWriter(MASTER_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    edited.to_excel(writer, sheet_name=classe_choisie, index=False)
                st.success("Modifications enregistrées.")
        else:
            st.error("Le fichier de contributions est vide. Importez vos données via Excel d'abord.")
