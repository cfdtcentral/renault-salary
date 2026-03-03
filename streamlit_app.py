import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
ADMIN_PWD = "RENAULT_PRO_2026"
MASTER_FILE = "Renault_Contributions.xlsx"
ECO_FILE = "Renault_Grille_SMH_Inflation.xlsx"

# Colonnes cibles (on va les chercher intelligemment)
COL_MATRICULE = "Matricule de l'employé"
COL_NOM = "Employé"
COL_CLASSE = "Classe_Emploi"

def load_all_data():
    if not os.path.exists(MASTER_FILE):
        return pd.DataFrame(), []
    
    try:
        # On lit tous les onglets
        all_sheets = pd.read_excel(MASTER_FILE, sheet_name=None)
        cleaned_sheets = []
        
        for sheet_name, df in all_sheets.items():
            # SI LA LIGNE 1 EST "MEMBRES", ON REDÉFINIT LES TITRES
            if "Membres" in str(df.columns[0]):
                # On reprend le tableau à partir de la ligne suivante
                df.columns = df.iloc[0]
                df = df[1:].reset_index(drop=True)
            
            # NETTOYAGE DES COLONNES (enlève les espaces, les sauts de ligne, les tirets)
            df.columns = df.columns.astype(str).str.replace('\n', ' ').str.strip()
            
            # Correction spécifique pour "Classe _Emploi" ou "Classe emploi"
            df = df.rename(columns={
                "Classe _Emploi": "Classe_Emploi",
                "Classe emploi": "Classe_Emploi",
                "Classe_Emploi": "Classe_Emploi"
            })
            
            if not df.empty:
                cleaned_sheets.append(df)
            
        if not cleaned_sheets:
            return pd.DataFrame(), []
            
        df_global = pd.concat(cleaned_sheets, ignore_index=True, sort=False)
        return df_global, list(all_sheets.keys())
    except Exception as e:
        st.error(f"Erreur technique lors de la lecture : {e}")
        return pd.DataFrame(), []

# --- INTERFACE ---
st.set_page_config(page_title="Renault Salary Insight", layout="wide")
st.title("💎 RENAULT SALARY INTELLIGENCE")

df_global, liste_classes = load_all_data()

tab_user, tab_admin = st.tabs(["📊 Mon Profil", "🔐 Administration"])

with tab_user:
    st.subheader("Identification Salarié")
    u_mat = st.text_input("Saisissez votre Matricule de l'employé (8 chiffres)")
    
    if u_mat:
        # On vérifie si la colonne matricule existe après nettoyage
        if COL_MATRICULE in df_global.columns:
            # Recherche flexible (enlève les espaces autour du matricule)
            match = df_global[df_global[COL_MATRICULE].astype(str).str.contains(str(u_mat).strip(), na=False)]
            
            if not match.empty:
                info = match.iloc[0]
                st.success(f"✅ Bonjour {info[COL_NOM]}")
                st.info(f"Fiche identifiée : {info.get('Poste', 'N/A')} | Classe : {info.get('Classe_Emploi', 'N/A')}")
                
                u_sal = st.number_input("Entrez votre salaire brut annuel actuel (€)", value=30000, step=500)
                if st.button("Enregistrer ma contribution"):
                    st.balloons()
                    st.success("Donnée enregistrée temporairement (Simulation)")
            else:
                st.warning("Matricule non trouvé dans la base Renault_Contributions.")
        else:
            st.error(f"La colonne '{COL_MATRICULE}' n'a pas été trouvée. Vérifiez vos entêtes Excel.")
            st.write("Colonnes détectées :", list(df_global.columns))

with tab_admin:
    if st.text_input("Code Secret", type="password") == ADMIN_PWD:
        st.write("### Gestion de la base")
        if liste_classes:
            choix = st.selectbox("Choisir l'onglet à vérifier", liste_classes)
            # Re-lecture brute pour l'édition
            df_edite = pd.read_excel(MASTER_FILE, sheet_name=choix)
            st.data_editor(df_edite)
