import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from datetime import datetime

# --- CONFIGURATION DES FICHIERS ---
FILES = {
    "CONTRIB": "Renault_Contributions.xlsx",
    "RH_REF": "Renault_Referentiel_350k.xlsx",
    "ECO": "Renault_Grille_SMH_Inflation.xlsx",
    "LOGS": "Renault_Tracabilite_Admin.xlsx",
    "HISTO": "Renault_Historique_Annees.xlsx"
}
ADMIN_PWD = "RENAULT_PRO_2026"

# --- MOTEUR DE GESTION DES DONNÉES ---
def load_data(key, columns=[]):
    if os.path.exists(FILES[key]):
        try:
            return pd.read_excel(FILES[key])
        except:
            return pd.DataFrame(columns=columns)
    return pd.DataFrame(columns=columns)

def save_data(df, key, user_action="Modification"):
    df.to_excel(FILES[key], index=False)
    log_entry(user_action, FILES[key])

def log_entry(action, filename):
    logs = load_data("LOGS", ["Date", "Action", "Fichier"])
    new_log = pd.DataFrame([{"Date": datetime.now().strftime("%d/%m/%y %H:%M"), "Action": action, "Fichier": filename}])
    pd.concat([logs, new_log], ignore_index=True).to_excel(FILES["LOGS"], index=False)

# --- CHARGEMENT INITIAL ---
df_contrib = load_data("CONTRIB", ["MATRICULE", "CATEGORIE", "SALAIRE", "VALIDATION"])
df_rh = load_data("RH_REF", ["Matricule", "E-mail", "Site"])
df_eco = load_data("ECO", ["CATEGORIE", "SMH_VALEUR", "MEDIANE_RENAULT"])
df_histo = load_data("HISTO", ["ANNEE", "CATEGORIE", "MEDIANE_MOYENNE"])

# --- INTERFACE UTILISATEUR ---
st.set_page_config(page_title="Renault Salary Intelligence", layout="wide")
st.title("💎 RENAULT SALARY INTELLIGENCE")

tab_user, tab_dashboard, tab_admin = st.tabs(["📊 Mon Positionnement", "📈 Évolutions Historiques", "🔐 Espace Administrateur"])

with tab_user:
    st.subheader("Vérifiez votre salaire et contribuez")
    col1, col2 = st.columns(2)
    with col1:
        u_mat = st.text_input("Matricule (pour vérification RH)")
        u_cat = st.selectbox("Catégorie", df_eco["CATEGORIE"].unique() if not df_eco.empty else ["A1"])
        u_sal = st.number_input("Mon Salaire Brut Annuel (€)", value=35000)
    
    if st.button("Lancer l'analyse et vérifier mon identité"):
        # Vérification dans le référentiel des 350 000 salariés
        if str(u_mat) in df_rh["Matricule"].astype(str).values:
            st.success("✅ Identité Renault confirmée dans le référentiel RH.")
            if not df_eco.empty:
                seuil = df_eco[df_eco["CATEGORIE"] == u_cat].iloc[0]
                if u_sal < seuil["SMH_VALEUR"]:
                    st.error(f"⚠️ ALERTE : Votre salaire est inférieur au SMH ({seuil['SMH_VALEUR']:,} €)")
                else:
                    st.info(f"✅ Conforme au SMH ({seuil['SMH_VALEUR']:,} €)")
                st.metric("Écart / Médiane Renault", f"{u_sal - seuil['MEDIANE_RENAULT']:,} €")
        else:
            st.error("❌ Matricule inconnu. Seuls les salariés Renault peuvent contribuer.")

with tab_dashboard:
    st.header("Historique des salaires Renault")
    if not df_histo.empty:
        fig = px.line(df_histo, x="ANNEE", y="MEDIANE_MOYENNE", color="CATEGORIE", markers=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Aucune donnée historique archivée pour le moment.")

with tab_admin:
    if st.text_input("Code Secret Admin", type="password") == ADMIN_PWD:
        st.success("Accès Administrateur Déverrouillé")
        adm_t1, adm_t2, adm_t3 = st.tabs(["📂 Import/Export", "📝 Édition Directe", "🕵️ Traçabilité"])
        
        with adm_t1:
            st.write("### Initialisation des fichiers Excel")
            file_key = st.selectbox("Choisir le fichier", list(FILES.keys()))
            up = st.file_uploader("Importer le fichier Excel", type="xlsx")
            if st.button("Remplacer la base de données"):
                if up:
                    save_data(pd.read_excel(up), file_key, f"IMPORT MASSIF {file_key}")
                    st.success("Fichier mis à jour !")
            
            st.divider()
            if st.button("Exporter toute la base (Sauvegarde local)"):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    for k in FILES.keys(): load_data(k).to_excel(writer, sheet_name=k, index=False)
                st.download_button("Télécharger le pack complet .xlsx", output.getvalue(), "Renault_Full_Backup.xlsx")

        with adm_t2:
            target = st.radio("Tableau à corriger :", ["CONTRIB", "ECO", "RH_REF"])
            new_df = st.data_editor(load_data(target), num_rows="dynamic")
            if st.button("Sauvegarder les corrections"):
                save_data(new_df, target, f"ÉDITION MANUELLE {target}")

        with adm_t3:
            st.write("### Journal des modifications (Audit Log)")
            st.dataframe(load_data("LOGS"), use_container_width=True)
