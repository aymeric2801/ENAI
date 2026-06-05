import streamlit as st
import pandas as pd
import os

# Configuration de la page (pas de bord arrondis via CSS personnalisé)
st.set_page_config(
    page_title="Ad Campaign Data Log",
    page_icon="📊",
    layout="centered"
)

# CSS pour supprimer les bords arrondis
st.markdown("""
    <style>
        /* Supprimer les arrondis sur tous les éléments principaux */
        .stApp, .stApp header, .stApp .stButton button, 
        .stFileUploader, .stFileUploader div, .stFileUploader label,
        .stAlert, .stMarkdown, .stDataFrame, .stSuccess, .stInfo {
            border-radius: 0px !important;
        }
        /* Bouton sans arrondi */
        .stButton button {
            border-radius: 0px !important;
        }
        /* Zone de dépôt de fichier sans arrondi */
        .stFileUploader > div:first-child {
            border-radius: 0px !important;
        }
        /* Supprimer les bordures arrondies des widgets */
        div[data-testid="stFileUploaderDropzone"] {
            border-radius: 0px !important;
        }
        /* Supprimer les arrondis des conteneurs */
        .stBlock, .stVerticalBlock, .stHorizontalBlock {
            border-radius: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("📁 Ad Campaign Data Upload")

# Message demandant de déposer le CSV (en anglais)
st.markdown("### Please drop your ad campaign data log CSV file below")

# Widget de dépôt de fichier (sans arrondi grâce au CSS)
uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    help="Upload your ad campaign data log in CSV format"
)

# Traitement du fichier si présent
if uploaded_file is not None:
    try:
        # Lire le CSV
        df = pd.read_csv(uploaded_file)
        
        # Afficher un aperçu
        st.success(f"✅ File loaded successfully! {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Afficher les premières lignes
        st.subheader("Preview of uploaded data:")
        st.dataframe(df.head(10))
        
        # Afficher les colonnes disponibles
        st.subheader("Columns detected:")
        st.write(list(df.columns))
        
        # Option supplémentaire : montrer des stats basiques
        if st.button("Show basic statistics", use_container_width=True):
            st.write(df.describe())
            
    except Exception as e:
        st.error(f"❌ Error reading CSV file: {str(e)}")
else:
    # Message d'attente lorsque aucun fichier n'est déposé
    st.info("📂 No file uploaded yet. Please drop your CSV file above.")

# Pied de page (optionnel)
st.markdown("---")
st.caption("Accepts CSV files with ad campaign data logs only.")