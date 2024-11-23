import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib
import numpy as np

# --- User Authentication ---
class Authentication:
    def __init__(self):
        self.users = {
            "admin": "240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9",
            "user": "04f8996da763b7a969b1028ee3007569eaf3a635486ddab211d512c85b9df8fb"
        }

    def login_page(self):
        st.markdown("""
        <style>
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
            background-color: white;
        }
        .stButton > button {
            width: 100%;
            margin-top: 10px;
        }
        </style>
        """, unsafe_allow_html=True)

        with st.container():
            st.title("🔐 Crypto Dashboard Login")
            
            col1, col2 = st.columns([3, 2])
            
            with col1:
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                if st.button("Login", key="login_button"):
                    if username in self.users:
                        if hashlib.sha256(str.encode(password)).hexdigest() == self.users[username]:
                            st.session_state["authenticated"] = True
                            st.session_state["username"] = username
                            st.rerun()
                        else:
                            st.error("Incorrect password")
                    else:
                        st.error("Username not found")
            
            with col2:
                st.markdown("""
                ### Demo Credentials
                - Username: `admin`
                - Password: `admin`
                
                or
                
                - Username: `user`
                - Password: `user`
                """)

# --- Visualization Functions ---
def create_enhanced_scatter_plot(df, x_col, y_col):
    fig = px.scatter(df,
                     x=x_col,
                     y=y_col,
                     size='24h_volume_usd',
                     color='name',
                     hover_name='name',
                     log_x=True,
                     log_y=True,
                     title=f'{y_col} vs {x_col} Scatter Plot')
    
    fig.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def create_boxplot(df, column):
    fig = px.box(df, y=column, color='name', 
                 title=f'Distribution of {column}')
    
    fig.update_layout(
        height=500,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def create_correlation_heatmap(df):
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    corr = df[numeric_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr,
        x=numeric_cols,
        y=numeric_cols,
        colorscale='RdBu',
        zmid=0
    ))
    fig.update_layout(
        title='Correlation Heatmap',
        height=600,
        margin=dict(l=40, r=40, t=40, b=40),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig

def main():
    st.set_page_config(
        page_title="Advanced Crypto Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            padding: 0rem 1rem;
        }
        .stPlotlyChart {
            background-color: #1c1c1c;
            border-radius: 5px;
            padding: 10px;
        }
        .row-widget.stButton > button {
            width: 100%;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Authentication
    auth = Authentication()
    if "authenticated" not in st.session_state:
        auth.login_page()
        return
    
    # Main Dashboard
    st.title("📊 Advanced Cryptocurrency Analytics")
    
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state['username']}!")
        st.markdown("---")
        
        # Data Source Selection
        data_source = st.radio("Select Data Source", 
                               ["Static Dataset", "Upload Custom CSV"])
        
        if data_source == "Static Dataset":
            # Load static dataset
            df = pd.read_csv('cleaned_sorted_output_cleaned.csv')
        else:
            # CSV File Upload
            uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success("File uploaded successfully!")
                except Exception as e:
                    st.error(f"Error reading file: {e}")
                    return
            else:
                st.info("Please upload a CSV file")
                return
        
        # Data Preprocessing
        df['volume_to_market_cap'] = df['24h_volume_usd'] / df['market_cap_usd']
        
        # Visualization Controls
        st.header("Visualization Controls")
        
        # Scatter Plot Controls
        st.subheader("Scatter Plot")
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        x_axis = st.selectbox("X-axis", options=numeric_columns, index=0)
        y_axis = st.selectbox("Y-axis", options=numeric_columns, index=1)
        
        # Box Plot Controls
        st.subheader("Box Plot")
        box_column = st.selectbox("Select Column", 
                                  options=numeric_columns, 
                                  index=0)
        
        # Additional Features
        st.markdown("---")
        st.header("Advanced Analytics")
        show_correlation = st.checkbox("Show Correlation Heatmap")
        show_top_n = st.slider("Show Top N Cryptocurrencies", 
                               min_value=5, max_value=50, value=20)
        
        # Logout
        st.markdown("---")
        if st.button("Logout", key="logout_button"):
            st.session_state.clear()
            st.rerun()
    
    # Main Content Area
    col1, col2 = st.columns(2)
    
    with col1:
        # Scatter Plot
        st.subheader(f"Scatter Plot: {x_axis} vs {y_axis}")
        scatter_plot_data = df.head(show_top_n)
        scatter_plot = create_enhanced_scatter_plot(scatter_plot_data, x_axis, y_axis)
        st.plotly_chart(scatter_plot, use_container_width=True)
    
    with col2:
        # Box Plot
        st.subheader(f"Distribution of {box_column}")
        box_plot = create_boxplot(df, box_column)
        st.plotly_chart(box_plot, use_container_width=True)
    
    # Correlation Heatmap (Optional)
    if show_correlation:
        st.markdown("## Correlation Heatmap")
        correlation_heatmap = create_correlation_heatmap(df)
        st.plotly_chart(correlation_heatmap, use_container_width=True)
    
    # Raw Data View
    st.markdown("## Raw Data")
    st.dataframe(df.head(show_top_n), use_container_width=True)
    
    # Download Options
    st.markdown("## Download Options")
    col_download1, col_download2 = st.columns(2)
    
    with col_download1:
        st.download_button(
            label="Download Full Dataset (CSV)",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='crypto_dataset.csv',
            mime='text/csv'
        )
    
    with col_download2:
        st.download_button(
            label="Download Filtered Dataset (CSV)",
            data=df.head(show_top_n).to_csv(index=False).encode('utf-8'),
            file_name='top_cryptos.csv',
            mime='text/csv'
        )

if __name__ == "__main__":
    main()