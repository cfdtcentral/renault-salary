import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Positionnement Salarial Renault", layout="wide")

# --- CHARGEMENT DES DONNÉES (Initialement depuis Excel) ---
@st.cache_data
def load_data():
    # Simulation du fichier Excel de 7625 salariés
    df = pd.read_excel("base_salaires_renault.xlsx")
    return df

data = load_data()

# --- BARRE LATÉRALE : CONNEXION ---
st.sidebar.title("🔑 Connexion")
ipn_user = st.sidebar.text_input("Entrez votre IPN")

# --- LOGIQUE DES ONGLETS ---
tab1, tab2, tab3, tab4 = st.tabs(["📊 Mon Positionnement", "✍️ Contribuer", "🔍 Tableau de Bord", "⚙️ Admin"])

with tab1:
    if ipn_user:
        st.header(f"Analyse pour l'IPN : {ipn_user}")
        # Extraction des données du salarié
        user_info = data[data['IPN'] == ipn_user]
        
        if not user_info.empty:
            col1, col2, col3 = st.columns(3)
            # Calcul du percentile
            cat = user_info['Categorie'].values[0]
            salaires_cat = data[data['Categorie'] == cat]['Salaire']
            percentile = (salaires_cat < user_info['Salaire'].values[0]).mean() * 100
            
            col1.metric("Votre Percentile", f"{percentile:.1f}%")
            col2.metric("Écart à la Médiane", f"{user_info['Salaire'].values[0] - salaires_cat.median():.0f} €")
            col3.metric("Écart H/F (Votre Cat)", "-2.4%") # Exemple statique
            
            # Graphique BoxPlot
            st.subheader(f"Positionnement dans la catégorie {cat}")
            st.boxplot(data=data[data['Categorie'] == cat], x='Categorie', y='Salaire')
        else:
            st.warning("IPN inconnu. Veuillez contribuer pour voir vos stats.")
    else:
        st.info("💡 Connectez-vous avec votre IPN pour débloquer votre analyse personnalisée.")

with tab2:
    st.header("Contribuer à la base")
    with st.form("form_contribution"):
        new_genre = st.selectbox("Genre", ["Homme", "Femme", "Autre"])
        new_cat = st.selectbox("Catégorie", [f"A{i}" for i in range(1,6)] + [f"I{i}" for i in range(1,19)])
        new_sal = st.number_input("Salaire Annuel Brut", min_value=20000)
        submit = st.form_submit_button("Envoyer pour validation")
        
        if submit:
            st.success("Données envoyées ! Elles apparaîtront après validation par l'administrateur.")

with tab3:
    st.header("Indicateurs Macro - Groupe Renault")
    # Ici : Graphiques barres des médianes par catégorie
    # Courbe Inflation vs SMH Métallurgie
    st.line_chart(np.random.randn(10, 2)) # Placeholder pour Inflation/SMH

with tab4:
    st.header("🕵️ Zone Administrateur")
    pwd = st.text_input("Mot de passe admin", type="password")
    if pwd == "Renault2024":
        st.write("Demandes en attente de validation :")
        st.dataframe(data.head(5)) # Liste des derniers IPN inscrits
        if st.button("Tout Valider"):
            st.balloons()
