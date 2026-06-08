import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import warnings
from pathlib import Path
import hashlib
import pickle

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Ad Campaign Analytics with AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
    }
    .warning-text {
        color: #ff6b6b;
        font-weight: bold;
    }
    .upload-box {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# FONCTIONS DE CHARGEMENT DES DONNÉES (mémoire uniquement)
# ============================================

@st.cache_data
def load_data(uploaded_file):
    """Charge les données depuis un fichier CSV uploadé (reste en mémoire, jamais écrit sur disque)"""
    # uploaded_file est un objet BytesIO fourni par Streamlit
    df = pd.read_csv(uploaded_file)
    df['date'] = pd.to_datetime(df['date'])
    # Calcul des métriques dérivées
    df['ctr'] = (df['clicks'] / df['impressions'] * 100).round(2)
    df['conversion_rate'] = (df['conversions'] / df['clicks'] * 100).round(2)
    df['cpc'] = (df['spend'] / df['clicks']).round(2)
    df['cpm'] = (df['spend'] / df['impressions'] * 1000).round(2)
    df['roas'] = (df['business_goal'] / df['spend']).round(2)
    df['cpa'] = (df['spend'] / df['conversions']).round(2)
    return df

def calculate_kpis(df):
    """Calcule les KPIs pour l'analyse RAG"""
    df_calc = df.copy()
    if 'ctr' not in df_calc.columns:
        df_calc['ctr'] = (df_calc['clicks'] / df_calc['impressions'] * 100).round(2)
    if 'cpc' not in df_calc.columns:
        df_calc['cpc'] = (df_calc['spend'] / df_calc['clicks']).round(2)
    if 'cpm' not in df_calc.columns:
        df_calc['cpm'] = (df_calc['spend'] / df_calc['impressions'] * 1000).round(2)
    if 'roas' not in df_calc.columns and 'business_goal' in df_calc.columns:
        df_calc['roas'] = (df_calc['business_goal'] / df_calc['spend']).round(2)
    if 'cpa' not in df_calc.columns:
        df_calc['cpa'] = (df_calc['spend'] / df_calc['conversions']).round(2)
    return df_calc

# ============================================
# KNOWLEDGE BASE (AdTech Best Practices)
# ============================================

def load_knowledge_base():
    """Charge la base de connaissances pour le RAG"""
    knowledge_base = {
        "ctr_optimization": """
# CTR Optimization Framework

## Low CTR (< 1%):
- **Creative Issues**: Test new ad creatives (images/videos)
- **Audience Mismatch**: Refine targeting parameters
- **Ad Placement**: Review placement performance
- **Expected lift**: +50-100% CTR with proper optimization

## Medium CTR (1-3%):
- **A/B Testing**: Run multivariate tests on headlines
- **Ad Copy Refresh**: Update copy every 2-3 weeks
- **Call-to-Action**: Test different CTA buttons
- **Expected lift**: +20-30% CTR

## Best Practices:
- Use emotional triggers in headlines
- Include numbers/statistics
- Add social proof elements
- Mobile-first design
""",
        "cpa_reduction": """
# CPA Reduction Strategies

## Quick Wins (High Impact):
1. **Audience Segmentation**: Create lookalike audiences from converters
2. **Ad Scheduling**: Focus spend on peak conversion hours
3. **Landing Page Optimization**: Reduce load time + improve relevance
   - Expected CPA reduction: 15-25%

## Medium-term Strategies:
1. **Retargeting Funnels**: 3-step sequence for warm audiences
2. **Creative Refresh**: New angles for fatigued audiences
3. **Bid Adjustments**: Reduce bids on low-converting placements
   - Expected CPA reduction: 10-15%

## Long-term Optimization:
1. **Machine Learning Bidding**: Switch to automated strategies
2. **Cross-channel Attribution**: Optimize full funnel
3. **Creative Testing Framework**: Systematic testing pipeline
""",
        "roas_improvement": """
# ROAS Improvement Framework

## ROAS < 2x (Underperforming):
- **Immediate Actions**:
  - Pause bottom 20% performing ad sets
  - Increase budget on top 5% creative
  - Implement frequency capping (max 3 impressions/day)
  - Expected improvement: +50-100% ROAS

## ROAS 2-4x (Healthy):
- **Optimization Opportunities**:
  - Test value-based lookalike audiences
  - Implement dynamic creative optimization
  - Seasonal adjustment strategies
  - Expected improvement: +20-30% ROAS

## ROAS > 4x (Scale):
- **Scaling Strategies**:
  - Gradual budget increases (20% every 3 days)
  - Expand to similar geos/audiences
  - Test higher-funnel objectives
""",
        "audience_targeting": """
# Audience Targeting Best Practices

## Segment Performance Patterns:
- **18-24**: Best with video + social proof
  - Optimal creative: User-generated content
  - Peak hours: 6-10pm
  
- **25-34**: Decision-makers, value-driven
  - Best performing: Educational content
  - Peak hours: 12-2pm, 7-9pm
  
- **35-44**: Brand loyal, trust-focused
  - Best performing: Testimonials + case studies
  - Peak hours: 8-9am, 5-7pm
  
- **45+**: Practical + solution-focused
  - Best performing: Clear benefit statements
  - Peak hours: 7-9am, 6-8pm

## Geo-specific Strategies:
- **North America**: Direct, benefit-focused copy
- **Europe**: Quality + sustainability messaging
- **APAC**: Social proof + urgency elements
"""
    }
    return knowledge_base

# ============================================
# RAG SYSTEM WITH FAISS + LANGCHAIN + OPENAI
# ============================================

class AdTechRAG:
    """Complete RAG system using FAISS + LangChain + OpenAI"""
    
    def __init__(self, api_key=None):
        # Initialize OpenAI - utilisez votre clé API ici
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=api_key or st.secrets.get("OPENAI_API_KEY", "votre-clé-api-ici")
        )
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=api_key or st.secrets.get("OPENAI_API_KEY", "votre-clé-api-ici")
        )
        self.vectorstore = None
        self.retriever = None
        
    def load_and_index_documents(self, knowledge_base, kb_dir="./kb"):
        """Load documents from knowledge base and create FAISS index"""
        documents = []
        
        # Convert knowledge_base dict to LangChain Documents
        for doc_key, content in knowledge_base.items():
            if content:
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": doc_key,
                        "type": "adtech_playbook",
                        "filename": f"{doc_key}.md"
                    }
                )
                documents.append(doc)
        
        # Load raw markdown files if they exist
        if Path(kb_dir).exists():
            for file_path in Path(kb_dir).glob("*.md"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    doc = Document(
                        page_content=content,
                        metadata={
                            "source": file_path.stem,
                            "type": "playbook",
                            "filename": file_path.name
                        }
                    )
                    documents.append(doc)
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n## ", "\n### ", "\n\n", "\n", " "]
        )
        
        split_docs = text_splitter.split_documents(documents)
        st.info(f"📚 Created {len(split_docs)} document chunks from {len(documents)} playbooks")
        
        # Create FAISS vector store
        self.vectorstore = FAISS.from_documents(
            split_docs,
            self.embeddings
        )
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}
        )
        
        return len(split_docs)
    
    def save_index(self, path="./faiss_index"):
        """Save FAISS index to disk (optionnel, pour accélérer les prochains lancements)"""
        if self.vectorstore:
            self.vectorstore.save_local(path)
            st.success(f"💾 FAISS index saved to {path}")
    
    def load_index(self, path="./faiss_index"):
        """Load pre-built FAISS index"""
        if Path(path).exists():
            self.vectorstore = FAISS.load_local(
                path, 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            self.retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": 3}
            )
            return True
        return False
    
    def retrieve_context(self, query):
        """Retrieve relevant documents from FAISS"""
        if not self.retriever:
            return []
        
        docs = self.retriever.invoke(query)
        
        for i, doc in enumerate(docs):
            st.caption(f"📄 Retrieved chunk {i+1}: {doc.metadata.get('source', 'unknown')}")
        
        return docs
    
    def _extract_campaign_stats(self, df):
        """Extract meaningful statistics from CSV"""
        stats = []
        
        # Overall metrics
        if 'spend' in df.columns:
            stats.append(f"Total Spend: ${df['spend'].sum():,.2f}")
        if 'ctr' in df.columns:
            stats.append(f"Average CTR: {df['ctr'].mean():.2f}%")
            stats.append(f"CTR Range: {df['ctr'].min():.2f}% - {df['ctr'].max():.2f}%")
        if 'cpc' in df.columns:
            stats.append(f"Average CPC: ${df['cpc'].mean():.3f}")
        if 'conversions' in df.columns:
            stats.append(f"Total Conversions: {df['conversions'].sum():,.0f}")
        if 'cpa' in df.columns and not df['cpa'].isna().all():
            stats.append(f"Average CPA: ${df['cpa'].mean():.2f}")
            stats.append(f"Best CPA: ${df['cpa'].min():.2f}")
        
        # Performance by segment
        if 'audience_segment' in df.columns and 'cpa' in df.columns:
            best_segment = df.groupby('audience_segment')['cpa'].mean().idxmin()
            worst_segment = df.groupby('audience_segment')['cpa'].mean().idxmax()
            stats.append(f"Best performing audience: {best_segment}")
            stats.append(f"Worst performing audience: {worst_segment}")
        
        # Top/bottom campaigns
        if 'campaign_name' in df.columns and 'ctr' in df.columns:
            top_ctr = df.nlargest(3, 'ctr')['campaign_name'].tolist()
            stats.append(f"Top CTR campaigns: {', '.join(top_ctr)}")
        
        return "\n".join(stats)
    
    def generate_recommendations_rag(self, df, query):
        """Complete RAG pipeline"""
        
        # Extract data insights from CSV
        campaign_stats = self._extract_campaign_stats(df)
        
        # Retrieve relevant documents from FAISS
        retrieved_docs = self.retrieve_context(query)
        context = "\n\n---\n\n".join([doc.page_content for doc in retrieved_docs])
        
        # Build prompt
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert AdTech optimization consultant with 10+ years experience.
            
            CONTEXT FROM KNOWLEDGE BASE (AdTech best practices, optimization frameworks):
            {context}
            
            CAMPAIGN PERFORMANCE DATA:
            {campaign_data}
            
            Your task: Provide actionable, specific recommendations based on the data and best practices.
            Focus on:
            - Diagnosing root causes of underperformance
            - Providing specific, implementable actions
            - Prioritizing recommendations (High/Medium/Low impact)
            - Including expected lift/improvement metrics
            """),
            ("human", "{question}")
        ])
        
        # Generate response
        chain = (
            {
                "context": lambda x: context,
                "campaign_data": lambda x: campaign_stats,
                "question": lambda x: x["question"]
            }
            | prompt_template
            | self.llm
            | StrOutputParser()
        )
        
        response = chain.invoke({"question": query})
        
        return response, retrieved_docs
    
    def chat_with_campaign(self, df, user_question):
        """Interactive chat using RAG"""
        return self.generate_recommendations_rag(df, user_question)

# ============================================
# FONCTIONS D'AFFICHAGE DU DASHBOARD
# ============================================

def display_rich_dashboard(df, recommendations=None):
    """Affiche le dashboard complet"""
    
    # Sidebar - Filtres
    st.sidebar.markdown("## 🔍 Filtres")
    
    # Sélecteur de dates
    min_date = df['date'].min()
    max_date = df['date'].max()
    date_range = st.sidebar.date_input(
        "Période",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df['date'] >= pd.Timestamp(start_date)) & (df['date'] <= pd.Timestamp(end_date))
        filtered_df = df[mask].copy()
    else:
        filtered_df = df.copy()
    
    # Filtres supplémentaires
    if 'country' in filtered_df.columns:
        countries = st.sidebar.multiselect(
            "Pays",
            options=filtered_df['country'].unique(),
            default=filtered_df['country'].unique()
        )
        filtered_df = filtered_df[filtered_df['country'].isin(countries)]
    
    if 'ad_format' in filtered_df.columns:
        ad_formats = st.sidebar.multiselect(
            "Format publicitaire",
            options=filtered_df['ad_format'].unique(),
            default=filtered_df['ad_format'].unique()
        )
        filtered_df = filtered_df[filtered_df['ad_format'].isin(ad_formats)]
    
    if 'audience_segment' in filtered_df.columns:
        audience_segments = st.sidebar.multiselect(
            "Segment d'audience",
            options=filtered_df['audience_segment'].unique(),
            default=filtered_df['audience_segment'].unique()
        )
        filtered_df = filtered_df[filtered_df['audience_segment'].isin(audience_segments)]
    
    # Métriques clés
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_impressions = filtered_df['impressions'].sum()
        st.metric("Impressions totales", f"{total_impressions:,.0f}")
    
    with col2:
        total_clicks = filtered_df['clicks'].sum()
        st.metric("Clicks totaux", f"{total_clicks:,.0f}")
    
    with col3:
        avg_ctr = filtered_df['ctr'].mean()
        st.metric("CTR moyen", f"{avg_ctr:.2f}%")
    
    with col4:
        total_spend = filtered_df['spend'].sum()
        st.metric("Dépenses totales", f"${total_spend:,.0f}")
    
    with col5:
        avg_roas = filtered_df['roas'].mean()
        st.metric("ROAS moyen", f"{avg_roas:.2f}x")
    
    st.markdown("---")
    
    # Graphiques
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Évolution du CTR par campagne")
        fig_ctr = px.line(
            filtered_df,
            x='date',
            y='ctr',
            color='campaign_name',
            title="CTR dans le temps",
            labels={'ctr': 'CTR (%)', 'date': 'Date'}
        )
        st.plotly_chart(fig_ctr, use_container_width=True)
    
    with col2:
        st.subheader("💰 Dépenses vs Conversions")
        fig_spend = px.bar(
            filtered_df.groupby('campaign_name')[['spend', 'conversions']].sum().reset_index(),
            x='campaign_name',
            y=['spend', 'conversions'],
            title="Dépenses et conversions par campagne",
            barmode='group',
            labels={'value': 'Montant', 'variable': 'Métrique'}
        )
        st.plotly_chart(fig_spend, use_container_width=True)
    
    # Alertes
    st.markdown("---")
    st.subheader("⚠️ Alertes et Recommandations")
    
    low_ctr_campaigns = filtered_df[filtered_df['ctr'] < 1.0]['campaign_name'].unique()
    if len(low_ctr_campaigns) > 0:
        st.warning(f"📢 {len(low_ctr_campaigns)} campagne(s) ont un CTR inférieur à 1% : {', '.join(low_ctr_campaigns)}")
    
    low_roas_campaigns = filtered_df[filtered_df['roas'] < 2.0]['campaign_name'].unique()
    if len(low_roas_campaigns) > 0:
        st.error(f"💰 {len(low_roas_campaigns)} campagne(s) ont un ROAS inférieur à 2x : {', '.join(low_roas_campaigns)}")
    
    # Top performers
    st.subheader("🏆 Top 5 des meilleures campagnes (par ROAS)")
    top_campaigns = filtered_df.groupby('campaign_name')['roas'].mean().sort_values(ascending=False).head(5)
    for i, (campaign, roas) in enumerate(top_campaigns.items(), 1):
        st.success(f"{i}. **{campaign}** - ROAS: {roas:.2f}x")

# ============================================
# FONCTION PRINCIPALE SANS FICHIER PAR DÉFAUT
# ============================================

def main():
    """Fonction principale – exige un fichier uploadé, ne stocke rien sur disque"""
    
    # Titre principal
    st.markdown('<div class="main-header">📊 Ad Campaign Analytics with AI Consultant</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'df' not in st.session_state:
        st.session_state.df = None
    
    # Zone de dépôt de fichier – obligatoire
    st.markdown("### 📁 Déposez votre fichier CSV pour commencer l'analyse")
    st.markdown("""
    <div class="upload-box">
        <p style="font-size: 1.2rem;">⬇️ Déposez votre fichier CSV ci-dessous</p>
        <p style="color: #667eea;">Le fichier reste en mémoire et n'est jamais sauvegardé sur le disque.</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choisir un fichier CSV", type=['csv'], label_visibility="collapsed")
    
    if uploaded_file is not None:
        try:
            # Chargement des données – directement depuis le buffer mémoire
            with st.spinner("📊 Chargement et analyse du fichier..."):
                df = load_data(uploaded_file)
                df = calculate_kpis(df)
            
            # Chargement de la knowledge base (en mémoire)
            knowledge_base = load_knowledge_base()
            
            # Initialisation du système RAG (l'index FAISS peut être mis en cache sur disque,
            # mais c'est une optimisation technique, pas le fichier utilisateur)
            if st.session_state.rag_system is None:
                with st.spinner("🔧 Initialisation du système RAG avec FAISS + LangChain..."):
                    rag = AdTechRAG()
                    st.info("📚 Construction de l'index FAISS à partir de la base de connaissances...")
                    rag.load_and_index_documents(knowledge_base)
                    # Sauvegarde de l'index FAISS (optionnel, pour accélérer les prochains lancements)
                    # Ceci n'est pas le fichier CSV utilisateur, c'est un cache technique.
                    rag.save_index()
                    st.session_state.rag_system = rag
            
            # Stockage dans session state
            st.session_state.df = df
            st.session_state.data_loaded = True
            
            # Affichage du dashboard
            display_rich_dashboard(df)
            
            # Section RAG Chat
            st.markdown("---")
            st.subheader("🤖 AI Consultant Chat (Powered by RAG + FAISS)")
            st.caption("Posez vos questions sur les campagnes - L'IA va chercher les meilleures pratiques dans sa base de connaissances")
            
            # Quick questions buttons
            st.markdown("**Questions suggérées :**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("🔍 Pourquoi mon CTR est faible ?"):
                    st.session_state.quick_question = "Why is my CTR low? What specific actions should I take to improve it?"
            with col2:
                if st.button("💰 Comment réduire mon CPA ?"):
                    st.session_state.quick_question = "How can I reduce my CPA? Give me specific optimization strategies."
            with col3:
                if st.button("📈 Comment améliorer mon ROAS ?"):
                    st.session_state.quick_question = "How can I improve my ROAS? What are the best practices?"
            
            # Chat input
            user_question = st.text_input(
                "💬 Votre question :",
                placeholder="Ex: 'Pourquoi mes campagnes en France performent moins bien ?' ou 'Comment optimiser pour le segment 18-24 ans ?'",
                key="rag_input"
            )
            
            # Utiliser la quick question si elle existe
            if 'quick_question' in st.session_state and st.session_state.quick_question:
                user_question = st.session_state.quick_question
                st.session_state.quick_question = None
            
            if user_question:
                with st.spinner("🔍 Recherche dans FAISS + Génération de la réponse avec OpenAI..."):
                    response, retrieved_docs = st.session_state.rag_system.chat_with_campaign(df, user_question)
                    
                    # Store in history
                    st.session_state.chat_history.append(("user", user_question))
                    st.session_state.chat_history.append(("assistant", response))
                    
                    # Display response
                    st.markdown("### 💡 Réponse de l'IA Consultant")
                    st.markdown(response)
                    
                    # Show retrieved documents
                    with st.expander("🔍 Voir les documents récupérés par FAISS"):
                        for i, doc in enumerate(retrieved_docs):
                            st.markdown(f"**Document {i+1}:** {doc.metadata.get('source', 'unknown')}")
                            st.text(doc.page_content[:500] + "...")
                            st.markdown("---")
            
            # Display chat history
            if st.session_state.chat_history:
                with st.expander("📝 Historique de la conversation", expanded=False):
                    for role, msg in st.session_state.chat_history:
                        if role == "user":
                            st.markdown(f"**👤 Vous:** {msg}")
                        else:
                            st.markdown(f"**🤖 AI:** {msg}")
                        st.markdown("---")
                    
                    # Clear history button
                    if st.button("🗑️ Effacer l'historique"):
                        st.session_state.chat_history = []
                        st.rerun()
            
        except Exception as e:
            st.error(f"Erreur lors du traitement du fichier : {str(e)}")
            st.info("Assurez-vous que votre fichier CSV contient les colonnes nécessaires: date, campaign_name, impressions, clicks, spend, conversions, business_goal, country, ad_format, audience_segment")
    else:
        # Aucun fichier uploadé – on affiche seulement les instructions
        st.info("👋 **Bienvenue !** Pour commencer, veuillez déposer un fichier CSV ci-dessus.")
        st.markdown("""
        ### Format attendu du CSV:
        - `date`, `campaign_name`, `impressions`, `clicks`, `spend`, `conversions`, `business_goal`, `country`, `ad_format`, `audience_segment`
        
        ### Exemple de lignes:
        ```csv
        date,campaign_name,impressions,clicks,spend,conversions,business_goal,country,ad_format,audience_segment
        2024-01-01,Campaign A,10000,500,1000,50,2500,FR,video,18-24
        2024-01-02,Campaign B,15000,750,1500,75,3750,US,display,25-34

🔒 Confidentialité
Votre fichier reste uniquement en mémoire pendant la session. Il n'est jamais écrit sur le disque du serveur.
""")

if __name__ == "__main__":
    main()