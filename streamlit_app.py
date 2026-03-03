import streamlit as st
import pandas as pd
import os

# --- CONFIGURATION ---
ADMIN_PWD = "RENAULT_PRO_2026"
MASTER_FILE = "Renault_Contributions.xlsx"

def load_all_data():
    if not os.path.exists(MASTER_FILE):
        return pd.DataFrame(), []
    
    try:
        all_sheets = pd.read_excel(MASTER_FILE, sheet_name=None)
        if not all_sheets:
            return pd.DataFrame(), []
        
        cleaned_sheets = []
        for name, df in all_sheets.items():
            # Nettoyage automatique : on enlève les espaces vides autour des noms de colonnes
            df.columns = df.columns.astype(str).str.strip()
            cleaned_sheets.append(df)
            
        df_global = pd.concat(cleaned_sheets, ignore_index=True, sort=False)
        return df_global, list(all_sheets.keys())
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier Excel : {e}")
        return pd.DataFrame(), []

# --- INTERFACE ---
st.set_page_config(page_title="Renault Salary Insight", layout="wide")
st.title("💎 RENAULT SALARY INTELLIGENCE")

df_global, liste_classes = load_all_data()

# Vérification de la présence de la colonne avant de lancer l'app
COL_NAME = "Matricule de l'employé"

u_mat = st.text_input("Saisissez votre Matricule (8 chiffres)")

if u_mat:
    if df_global.empty:
        st.error("Le fichier de données est vide ou introuvable.")
    elif COL_NAME not in df_global.columns:
        st.error(f"⚠️ Erreur de format : La colonne '{COL_NAME}' est absente du fichier Excel.")
        st.write("Colonnes détectées dans votre fichier :", list(df_global.columns))
    else:
        # Recherche si la colonne existe
        match = df_global[df_global[COL_NAME].astype(str).str.strip() == str(u_mat).strip()]
        
        if not match.empty:
            info = match.iloc[0]
            st.success(f"✅ Salarié reconnu : {info.get('Employé', 'Nom inconnu')}")
            # ... suite du code
        else:
            st.warning("Matricule non trouvé.")
