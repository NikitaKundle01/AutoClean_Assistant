import streamlit as st
import pandas as pd
import os
import tempfile
from datetime import datetime
from modules.cleaner import DataCleaner
from modules.db_connector import DBHandler
from modules.auth import AuthManager
from pandas_profiling import ProfileReport

# Page configuration
st.set_page_config(
    page_title="AutoClean", 
    page_icon="🧹", 
    layout="wide",
    menu_items={
        'Get Help': 'https://github.com/yourusername/autoclean',
        'Report a bug': "https://github.com/yourusername/autoclean/issues",
        'About': "# AutoClean: Intelligent Data Cleaning Assistant"
    }
)

# Initialize services
auth = AuthManager()
db = DBHandler()

# Session state initialization
if 'df' not in st.session_state:
    st.session_state.df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None
if 'cleaning_history' not in st.session_state:
    st.session_state.cleaning_history = []

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #000000;}
    .stButton>button {background-color: #4CAF50; color: white;}
    .stFileUploader>div>div>button {background-color: #4CAF50; color: white;}
    .reportview-container .main .block-container {padding-top: 2rem;}
    .sidebar .sidebar-content {background-color: #e8f4f8;}
</style>
""", unsafe_allow_html=True)

# Navigation pages
def upload_page():
    """File upload and preview functionality"""
    st.title("📤 Upload Your Dataset")
    
    with st.expander("How to use", expanded=True):
        st.write("""
        1. Upload your CSV or Excel file
        2. Preview your data
        3. Navigate to other sections to clean or analyze
        """)
    
    uploaded_file = st.file_uploader(
        "Choose a file (CSV or Excel)", 
        type=["csv", "xlsx"],
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        try:
            # Read file based on extension
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            # Store in session state
            st.session_state.df = df
            st.session_state.cleaned_df = None
            st.session_state.cleaning_history = []
            
            st.success("✅ File uploaded successfully!")
            
            # Show file info
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rows", df.shape[0])
            with col2:
                st.metric("Columns", df.shape[1])
            
            # Data preview
            with st.expander("Data Preview", expanded=True):
                st.dataframe(df.head())
            
            # Basic stats
            with st.expander("Column Information"):
                st.table(pd.DataFrame({
                    'Column': df.columns,
                    'Data Type': df.dtypes,
                    'Missing Values': df.isna().sum(),
                    'Unique Values': df.nunique()
                }))
                
        except Exception as e:
            st.error(f"❌ Error reading file: {str(e)}")

def clean_page():
    """Data cleaning interface"""
    st.title("🧹 Clean Your Data")
    
    if st.session_state.df is None:
        st.warning("⚠️ Please upload a file first from the Upload Data page!")
        return
    
    df = st.session_state.df.copy()
    cleaner = DataCleaner(df)
    
    # Layout columns
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Cleaning Options")
        
        # Drop columns
        with st.expander("Remove Columns"):
            cols_to_drop = st.multiselect(
                "Select columns to remove",
                df.columns,
                key="cols_to_drop"
            )
            if cols_to_drop:
                cleaner.drop_columns(cols_to_drop)
                st.session_state.cleaning_history.append(
                    f"Removed columns: {', '.join(cols_to_drop)}"
                )
        
        # Handle missing values
        with st.expander("Handle Missing Values"):
            missing_cols = df.columns[df.isna().any()].tolist()
            
            if missing_cols:
                for col in missing_cols:
                    st.markdown(f"**{col}** ({df[col].dtype})")
                    strategy = st.selectbox(
                        f"Strategy for {col}",
                        ["Do nothing", "Drop rows", "Fill with mean", 
                         "Fill with median", "Fill with mode", "Custom value"],
                        key=f"missing_{col}"
                    )
                    
                    if strategy == "Custom value":
                        custom_val = st.text_input(
                            f"Value for {col}",
                            key=f"custom_{col}"
                        )
                        if st.button(f"Apply to {col}", key=f"apply_missing_{col}"):
                            cleaner.fill_missing(col, "custom", custom_val)
                            st.session_state.cleaning_history.append(
                                f"Filled missing values in {col} with {custom_val}"
                            )
                    elif strategy != "Do nothing":
                        if st.button(f"Apply to {col}", key=f"apply_missing_{col}"):
                            cleaner.fill_missing(col, strategy.lower().replace("fill with ", ""))
                            st.session_state.cleaning_history.append(
                                f"Filled missing values in {col} with {strategy}"
                            )
            else:
                st.info("No missing values found")
        
        # Remove duplicates
        with st.expander("Remove Duplicates"):
            if st.checkbox("Remove duplicate rows"):
                initial_rows = len(cleaner.df)
                cleaner.remove_duplicates()
                removed = initial_rows - len(cleaner.df)
                if removed > 0:
                    st.session_state.cleaning_history.append(
                        f"Removed {removed} duplicate rows"
                    )
                    st.success(f"Removed {removed} duplicates")
                else:
                    st.info("No duplicates found")
        
        # Data type conversion
        with st.expander("Convert Data Types"):
            for col in cleaner.df.columns:
                current_type = str(cleaner.df[col].dtype)
                new_type = st.selectbox(
                    f"{col} (current: {current_type})",
                    ["Keep as is", "int", "float", "str", "datetime", "category"],
                    key=f"dtype_{col}"
                )
                if new_type != "Keep as is":
                    if st.button(f"Convert {col}", key=f"convert_{col}"):
                        cleaner.convert_dtype(col, new_type)
                        st.session_state.cleaning_history.append(
                            f"Converted {col} from {current_type} to {new_type}"
                        )
    
    with col2:
        st.subheader("Data Preview")
        
        # Show current state of data
        if st.checkbox("Show full cleaned data", False):
            st.dataframe(cleaner.df)
        else:
            st.dataframe(cleaner.df.head())
        
        st.write(f"Shape: {cleaner.df.shape}")
        
        # Apply all cleaning
        if st.button("💾 Apply All Cleaning", use_container_width=True):
            st.session_state.cleaned_df = cleaner.df
            
            # Save to database if logged in
            if auth.is_authenticated():
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    user_id = auth.get_user_id()
                    
                    # Save files temporarily
                    os.makedirs("data", exist_ok=True)
                    cleaned_path = f"data/cleaned_{timestamp}.csv"
                    st.session_state.cleaned_df.to_csv(cleaned_path, index=False)
                    
                    # Save to database
                    db.save_cleaning_history(
                        user_id=user_id,
                        original_shape=str(st.session_state.df.shape),
                        cleaned_shape=str(st.session_state.cleaned_df.shape),
                        cleaning_notes=", ".join(st.session_state.cleaning_history),
                        cleaned_file_path=cleaned_path
                    )
                    
                    st.success("Cleaning history saved!")
                except Exception as e:
                    st.error(f"Could not save history: {str(e)}")
            
            st.success("All cleaning operations applied!")
            st.balloons()
        
        # Download cleaned data
        if st.session_state.cleaned_df is not None:
            st.subheader("Download Cleaned Data")
            
            # Format selection
            export_format = st.radio(
                "Export format",
                ["CSV", "Excel"],
                horizontal=True
            )
            
            if export_format == "CSV":
                csv = st.session_state.cleaned_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="cleaned_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                excel_file = tempfile.NamedTemporaryFile(delete=False)
                st.session_state.cleaned_df.to_excel(
                    excel_file.name, 
                    index=False,
                    engine='openpyxl'
                )
                with open(excel_file.name, "rb") as f:
                    st.download_button(
                        label="📥 Download Excel",
                        data=f,
                        file_name="cleaned_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                excel_file.close()
                os.unlink(excel_file.name)

def profile_page():
    """Data profiling and analysis"""
    st.title("📊 Data Profile Report")
    
    df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else st.session_state.df
    
    if df is None:
        st.warning("⚠️ Please upload a file first from the Upload Data page!")
        return
    
    # Quick stats
    st.subheader("Quick Statistics")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", df.shape[0])
    with col2:
        st.metric("Total Columns", df.shape[1])
    with col3:
        st.metric("Missing Values", df.isna().sum().sum())
    
    # Column selector for detailed stats
    selected_col = st.selectbox(
        "Select a column for detailed statistics",
        df.columns
    )
    
    if pd.api.types.is_numeric_dtype(df[selected_col]):
        st.write(df[selected_col].describe())
        
        # Histogram
        st.subheader("Distribution")
        st.bar_chart(df[selected_col].value_counts())
    else:
        st.write("Value counts:")
        st.write(df[selected_col].value_counts())
    
    # Full profile report
    st.subheader("Comprehensive Profile Report")
    if st.button("Generate Full Report", use_container_width=True):
        with st.spinner("Generating report... This may take a moment for large datasets"):
            profile = ProfileReport(
                df, 
                title="Data Profiling Report",
                explorative=True
            )
            st.components.v1.html(
                profile.to_html(), 
                height=1000, 
                scrolling=True
            )

def history_page():
    """User's cleaning history"""
    st.title("🕒 Cleaning History")
    
    if not auth.is_authenticated():
        st.warning("🔒 Please login to view your history")
        return
    
    try:
        history = db.get_user_history(auth.get_user_id())
        
        if not history:
            st.info("You don't have any cleaning history yet")
            return
        
        st.subheader("Your Recent Cleaning Sessions")
        
        for i, record in enumerate(history):
            with st.expander(f"Session {i+1} - {record['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Original Size:** {record['original_shape']}")
                    st.write(f"**Cleaned Size:** {record['cleaned_shape']}")
                with col2:
                    st.write(f"**Date:** {record['timestamp'].strftime('%Y-%m-%d')}")
                
                st.write("**Operations Performed:**")
                st.write(record['cleaning_notes'])
                
                if st.button(f"Reload this dataset", key=f"reload_{i}"):
                    try:
                        st.session_state.df = pd.read_csv(record['file_path'])
                        st.session_state.cleaned_df = None
                        st.session_state.cleaning_history = []
                        st.success("Dataset reloaded! Go to Clean Data page to continue working")
                    except Exception as e:
                        st.error(f"Error reloading: {str(e)}")
                
    except Exception as e:
        st.error(f"Error loading history: {str(e)}")

def auth_page():
    """Authentication interface"""
    st.title("🔐 Authentication")
    
    # In your main() function where you show the welcome message:
    if auth.is_authenticated():
        current_user = auth.get_current_user()
        if current_user:  # Additional safety check
            st.sidebar.success(f"Welcome {current_user['email']}")
        else:
            st.sidebar.warning("Session error - please login again")
            auth.logout_user()
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                success, message = auth.login_user(email, password)
                if success:
                    st.success(message)
                    st.experimental_rerun()
                else:
                    st.error(message)
    
    with tab2:
        with st.form("register_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            if st.form_submit_button("Register"):
                if password != confirm_password:
                    st.error("Passwords don't match")
                else:
                    success, message = auth.register_user(email, password, confirm_password)
                    if success:
                        st.success(message)
                        st.experimental_rerun()
                    else:
                        st.error(message)

# Main app navigation
def main():
    """Main application controller"""
    # Sidebar navigation
    st.sidebar.title("AutoClean")
    st.sidebar.image("https://via.placeholder.com/150x50?text=AutoClean", width=150)
    
    if auth.is_authenticated():
        st.sidebar.success(f"Welcome {auth.get_current_user()['email']}")
    
    menu_options = ["Upload Data", "Clean Data", "Data Profile", "History", "Account"]
    page = st.sidebar.radio("Navigation", menu_options)
    
    # Page routing
    if page == "Upload Data":
        upload_page()
    elif page == "Clean Data":
        clean_page()
    elif page == "Data Profile":
        profile_page()
    elif page == "History":
        history_page()
    elif page == "Account":
        auth_page()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **AutoClean** v1.0  
    [GitHub Repository](https://github.com/yourusername/autoclean)  
    © 2025 Nikita Dilip Kundle
    """)

if __name__ == "__main__":
    main()