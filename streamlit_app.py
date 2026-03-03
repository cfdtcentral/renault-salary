import streamlit as st
import pandas as pd
import os
from io import BytesIO

# --- CONFIGURATION ---
ADMIN_PWD = "RENAULT_PRO_2026"
MASTER_FILE = "Renault_Contributions.xlsx"
ECO_FILE = "Renault_Grille_SMH_Inflation.xlsx"

# --- FONCTIONS DE GESTION EXCEL MULTI-ONGLETS ---
def load_all_sheets():
    if not os.path.exists(MASTER_FILE):
        return pd.DataFrame(), []
    
    # Charger tous les onglets du fichier Excel
    all_sheets = pd.read_excel(MASTER_FILE, sheet_name=None)
    sheet_names = list(all_sheets.keys())
    
    # Fusionner tous les onglets pour la recherche par matricule
    df_global = pd.concat(all_sheets.values(), ignore_index=True, sort=False)
    return df_global, sheet_names

def save_new_entry(new_row, sheet_name):
    # Charger le fichier existant par onglets
    if os.path.exists(MASTER_FILE):
        with pd.ExcelWriter(MASTER_FILE, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
            try:
                # Si l'onglet existe, on ajoute à la suite
                existing_df = pd.read_excel(MASTER_FILE, sheet_name=sheet_name)
                updated_df = pd.concat([existing_df, pd.DataFrame([new_row])], ignore_index=True)
                updated_df.to_excel(writer, sheet_name=sheet_name, index=False)
            except:
                # Si l'onglet n'existe pas, on le crée
                pd.DataFrame([new_row]).to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        # Créer le fichier s'il n'existe pas du tout
        with pd.ExcelWriter(MASTER_FILE, engine='openpyxl') as writer:
            pd.DataFrame([new_row]).to_excel(writer, sheet_name=sheet_name, index=False)

# --- INTERFACE ---
st.set_page_config(page_title="Renault Salary Insight Master", layout="wide")
st.title("💎 RENAULT SALARY INTELLIGENCE - GESTION CENTRALISÉE")

tab_user, tab_admin = st.tabs(["📊 Mon Positionnement & Contribution", "🔐 Espace Administration"])

# Chargement des données
df_global, onglets_existants = load_all_sheets()
df_eco = pd.read_excel(ECO_FILE) if os.path.exists(ECO_FILE) else pd.DataFrame()

with tab_user:
    u_mat = st.text_input("Saisissez votre Matricule (ex: 81236239)")
    
    if u_mat:
        # Recherche du matricule dans TOUS les onglets
        match = df_global[df_global["Matricule de l'employé"].astype(str) == str(u_mat)]
        
        if not match.empty:
            info = match.iloc[0]
            st.success(f"✅ Salarié identifié : {info['Employé']} (Classe : {info['Classe_Emploi']})")
            u_sal = st.number_input("Votre Salaire Brut Annuel (€)", value=35000)
            
            if st.button("Valider ma rémunération actuelle"):
                # On ajoute la donnée dans son onglet correspondant
                new_data = info.to_dict()
                new_data['SALAIRE_REEL'] = u_sal
                new_data['DATE_MAJ'] = pd.Timestamp.now().strftime("%d/%m/%Y")
                new_data['VALIDATION'] = 1 # Déjà dans le référentiel donc valide
                save_new_entry(new_data, str(info['Classe_Emploi']))
                st.balloons()
        else:
            # Cas : Matricule absent du fichier global
            st.warning("⚠️ Matricule inconnu dans les classes d'emploi actuelles.")
            with st.form("ajout_manuel"):
                st.write("Complétez votre profil pour validation par l'administrateur :")
                n_nom = st.text_input("Nom Prénom")
                n_classe = st.selectbox("Classe d'emploi", [f"A{i}" for i in range(1,11)] + [f"C{i}" for i in range(1,16)] + [f"I{i}" for i in range(1,19)])
                n_sal = st.number_input("Salaire Brut Annuel (€)")
                if st.form_submit_button("Envoyer mon profil"):
                    new_row = {
                        "Matricule de l'employé": u_mat, "Employé": n_nom, 
                        "Classe_Emploi": n_classe, "SALAIRE_REEL": n_sal, 
                        "VALIDATION": 0, "DATE_MAJ": pd.Timestamp.now().strftime("%d/%m/%Y")
                    }
                    save_new_entry(new_row, n_classe)
                    st.info(f"Profil envoyé ! Il sera ajouté à l'onglet {n_classe} après validation.")

with tab_admin:
    if st.text_input("Code Secret", type="password") == ADMIN_PWD:
        st.subheader("Pilotage des onglets (A1 à I18)")
        
        # Sélection de l'onglet à consulter/modifier
        if onglets_existants:
            onglet_sel = st.selectbox("Sélectionner une classe d'emploi à gérer :", onglets_existants)
            df_onglet = pd.read_excel(MASTER_FILE, sheet_name=onglet_sel)
            
            # Mise en évidence de ceux à valider (ceux qui ont VALIDATION = 0)
            st.write(f"Données de la classe {onglet_sel} :")
            edited_df = st.data_editor(df_onglet, num_rows="dynamic")
            
            if st.button("Enregistrer les modifications de cet onglet"):
                with pd.ExcelWriter(MASTER_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    edited_df.to_excel(writer, sheet_name=onglet_sel, index=False)
                st.success(f"Onglet {onglet_sel} mis à jour avec succès.")
        else:
            st.error("Le fichier Renault_Contributions.xlsx est vide ou introuvable.")
