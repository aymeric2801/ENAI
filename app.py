import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Ad Campaign Analytics",
    page_icon="📊",
    layout="wide"
)

# ============================================
# CSS FOR EXTREME MINIMALISM (BEFORE UPLOAD)
# ============================================
st.markdown("""
    <style>
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Remove all padding and margins before upload */
        .main > div {
            padding: 0rem !important;
        }
        
        /* Ultra minimal before upload */
        .before-upload {
            text-align: center;
            padding: 0;
            margin: 0;
        }
        
        /* Massive drop zone */
        .stFileUploader > div:first-child {
            border-radius: 0px !important;
            border: 2px dashed #ccc !important;
            background: transparent !important;
            padding: 60px 20px !important;
            margin: 0 !important;
        }
        
        /* Center upload text */
        .stFileUploader label {
            font-size: 18px !important;
            color: #666 !important;
        }
        
        /* Remove rounded corners everywhere */
        .stApp, .stApp header, .stButton button, 
        .stFileUploader, .stFileUploader div,
        .stAlert, .stMarkdown, .stDataFrame {
            border-radius: 0px !important;
        }
        
        /* After upload styles - richer interface */
        .after-upload .stMetric {
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #ff4b4b;
            margin: 10px 0;
        }
        
        /* Better card styling after upload */
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
        }
        
        /* Dashboard container */
        .dashboard-container {
            padding: 20px;
            background: #ffffff;
        }
        
        /* Hide elements before upload */
        .hidden-before-upload {
            display: none;
        }
        
        /* Show elements after upload */
        .visible-after-upload {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
""", unsafe_allow_html=True)

# ============================================
# FUNCTIONS
# ============================================

def calculate_kpis(df):
    """Calculate missing KPIs"""
    df = df.copy()
    
    # Convert numeric columns
    numeric_cols = ['impressions', 'clicks', 'spend', 'conversions']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # CTR (Click-Through Rate)
    if 'ctr' not in df.columns or df['ctr'].isna().all():
        df['ctr'] = np.where(
            df['impressions'] > 0,
            (df['clicks'] / df['impressions']) * 100,
            0
        )
    
    # CPC (Cost Per Click)
    if 'cpc' not in df.columns or df['cpc'].isna().all():
        df['cpc'] = np.where(
            df['clicks'] > 0,
            df['spend'] / df['clicks'],
            0
        )
    
    # CPA (Cost Per Acquisition)
    if 'cpa' not in df.columns or df['cpa'].isna().all():
        df['cpa'] = np.where(
            df['conversions'] > 0,
            df['spend'] / df['conversions'],
            np.nan
        )
    
    # ROAS (Return on Ad Spend)
    if 'revenue' in df.columns:
        df['roas'] = np.where(
            df['spend'] > 0,
            df['revenue'] / df['spend'],
            np.nan
        )
    else:
        df['roas'] = np.nan
    
    # Round values
    df['ctr'] = df['ctr'].round(2)
    df['cpc'] = df['cpc'].round(3)
    df['cpa'] = df['cpa'].round(2)
    if 'roas' in df.columns:
        df['roas'] = df['roas'].round(2)
    
    return df

def display_minimal_upload():
    """Display ultra-minimal interface before upload"""
    st.markdown('<div class="before-upload">', unsafe_allow_html=True)
    
    # Simple title
    st.markdown("# 📊")
    st.markdown("# Drop your CSV")
    st.markdown("### Ad campaign data")
    
    # Empty space
    st.markdown("<br>", unsafe_allow_html=True)
    
    # The uploader (massive and centered)
    uploaded_file = st.file_uploader(
        "",
        type=["csv"],
        label_visibility="collapsed"
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.caption("CSV only · impressions · clicks · spend · conversions")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return uploaded_file

def display_rich_dashboard(df):
    """Display rich analytics dashboard after upload"""
    
    st.markdown('<div class="visible-after-upload">', unsafe_allow_html=True)
    
    # Header with campaign count
    st.markdown(f"## 📊 Dashboard · {df.shape[0]} campaigns loaded")
    
    # Row 1: Main KPIs with rich cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_spend = df['spend'].sum() if 'spend' in df.columns else 0
        st.metric(
            "💰 Total Ad Spend", 
            f"€{total_spend:,.0f}",
            help="Total amount invested in advertising"
        )
        st.caption("💰 Total budget consumed")
    
    with col2:
        total_revenue = df['revenue'].sum() if 'revenue' in df.columns else 0
        if total_revenue > 0:
            st.metric(
                "💵 Total Revenue", 
                f"€{total_revenue:,.0f}",
                delta=f"ROI: {((total_revenue - total_spend)/total_spend*100):.0f}%" if total_spend > 0 else None,
                help="Total revenue generated from campaigns"
            )
        else:
            st.metric("💵 Total Revenue", "N/A", help="Add 'revenue' column for ROI tracking")
    
    with col3:
        total_conversions = df['conversions'].sum() if 'conversions' in df.columns else 0
        st.metric("🎯 Conversions", f"{total_conversions:,.0f}", help="Total desired actions completed")
    
    with col4:
        avg_ctr = df['ctr'].mean() if 'ctr' in df.columns else 0
        st.metric("📈 Average CTR", f"{avg_ctr:.2f}%", help="Click-Through Rate")
    
    # Row 2: Performance metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_cpc = df['cpc'].mean() if 'cpc' in df.columns else 0
        st.metric("💸 Avg CPC", f"€{avg_cpc:.3f}", help="Cost Per Click")
    
    with col2:
        avg_cpa = df['cpa'].mean() if 'cpa' in df.columns and not df['cpa'].isna().all() else 0
        if avg_cpa > 0:
            st.metric("🎯 Avg CPA", f"€{avg_cpa:.2f}", help="Cost Per Acquisition")
        else:
            st.metric("🎯 Avg CPA", "N/A", help="Requires conversion data")
    
    with col3:
        avg_roas = df['roas'].mean() if 'roas' in df.columns and not df['roas'].isna().all() else None
        if avg_roas:
            st.metric("📈 Avg ROAS", f"{avg_roas:.2f}x", help="Return on Ad Spend")
        else:
            st.metric("📈 Avg ROAS", "N/A", help="Add 'revenue' column")
    
    with col4:
        total_clicks = df['clicks'].sum() if 'clicks' in df.columns else 0
        st.metric("🖱️ Total Clicks", f"{total_clicks:,.0f}", help="Total interactions")
    
    # Charts section
    st.markdown("---")
    st.subheader("📊 Performance Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 5 campaigns by spend
        if 'campaign_name' in df.columns and 'spend' in df.columns:
            top_campaigns = df.nlargest(5, 'spend')[['campaign_name', 'spend', 'conversions']]
            fig = px.bar(
                top_campaigns, 
                x='campaign_name', 
                y='spend',
                title='Top 5 Campaigns by Ad Spend',
                color='conversions',
                color_continuous_scale='Viridis',
                text='spend'
            )
            fig.update_traces(texttemplate='€%{text:.0f}', textposition='outside')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # CTR by campaign
        if 'campaign_name' in df.columns and 'ctr' in df.columns:
            top_ctr = df.nlargest(5, 'ctr')[['campaign_name', 'ctr']]
            fig = px.bar(
                top_ctr,
                x='campaign_name',
                y='ctr',
                title='Top 5 Campaigns by CTR',
                color='ctr',
                color_continuous_scale='Hot',
                text='ctr'
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Performance matrix
    st.markdown("---")
    st.subheader("🎯 Campaign Performance Matrix")
    
    if 'campaign_name' in df.columns and 'ctr' in df.columns and 'cpc' in df.columns:
        # Create performance categories
        df['performance'] = 'Average'
        df.loc[(df['ctr'] > df['ctr'].median()) & (df['cpc'] < df['cpc'].median()), 'performance'] = '🌟 Star (High CTR, Low CPC)'
        df.loc[(df['ctr'] < df['ctr'].median()) & (df['cpc'] > df['cpc'].median()), 'performance'] = '⚠️ Poor (Low CTR, High CPC)'
        df.loc[(df['ctr'] > df['ctr'].median()) & (df['cpc'] > df['cpc'].median()), 'performance'] = '📊 Efficient but Expensive'
        df.loc[(df['ctr'] < df['ctr'].median()) & (df['cpc'] < df['cpc'].median()), 'performance'] = '💸 Cheap but Low Engagement'
        
        performance_counts = df['performance'].value_counts()
        
        fig = px.pie(
            values=performance_counts.values,
            names=performance_counts.index,
            title='Campaign Performance Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top & Worst campaigns
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Performing Campaigns")
        if 'campaign_name' in df.columns and 'roas' in df.columns and not df['roas'].isna().all():
            top_roas = df.nlargest(3, 'roas')[['campaign_name', 'roas', 'spend', 'conversions']]
            st.dataframe(top_roas, use_container_width=True)
        elif 'campaign_name' in df.columns and 'ctr' in df.columns:
            top_ctr_list = df.nlargest(3, 'ctr')[['campaign_name', 'ctr', 'clicks', 'spend']]
            st.dataframe(top_ctr_list, use_container_width=True)
    
    with col2:
        st.subheader("⚠️ Underperforming Campaigns")
        if 'campaign_name' in df.columns and 'roas' in df.columns and not df['roas'].isna().all():
            worst_roas = df.nsmallest(3, 'roas')[['campaign_name', 'roas', 'spend', 'conversions']]
            st.dataframe(worst_roas, use_container_width=True)
        elif 'campaign_name' in df.columns and 'cpc' in df.columns:
            high_cpc = df.nlargest(3, 'cpc')[['campaign_name', 'cpc', 'clicks', 'spend']]
            st.dataframe(high_cpc, use_container_width=True)
    
    # Detailed data preview
    with st.expander("🔍 View Complete Data with Calculated KPIs", expanded=False):
        # Select columns to display
        priority_columns = ['campaign_name', 'impressions', 'clicks', 'conversions', 
                           'spend', 'ctr', 'cpc', 'cpa', 'roas']
        existing_priority = [col for col in priority_columns if col in df.columns]
        other_columns = [col for col in df.columns if col not in priority_columns]
        display_columns = existing_priority + other_columns
        st.dataframe(df[display_columns], use_container_width=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV with KPIs",
            data=csv,
            file_name="campaign_analytics.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# MAIN APP LOGIC
# ============================================

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False

# Display ultra-minimal interface before upload
uploaded_file = display_minimal_upload()

# Process file when uploaded
if uploaded_file is not None:
    try:
        # Read and process CSV
        df = pd.read_csv(uploaded_file)
        df = calculate_kpis(df)
        
        # Store in session state
        st.session_state.df = df
        st.session_state.data_loaded = True
        
        # Clear everything and show rich dashboard
        st.empty()
        
        # Display rich analytics dashboard
        display_rich_dashboard(df)
        
    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.session_state.data_loaded = False

# Show nothing else if no file
else:
    st.session_state.data_loaded = False