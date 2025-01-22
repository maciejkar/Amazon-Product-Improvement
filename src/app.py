
import streamlit as st
import pandas as pd
from product_analyzer import ProductAnalyzer
import os

# Define data paths at the top level (global scope)
metadata_path = r"C:\Users\karczews\OneDrive - Politechnika Wroclawska\studia\Amazon-Product-Improvement\data\metadata_Cell_Phones_and_Accessories.parquet"
reviews_path = r"C:\Users\karczews\OneDrive - Politechnika Wroclawska\studia\Amazon-Product-Improvement\data\review_Cell_Phones_and_Accessories.parquet"

# Set page config
st.set_page_config(
    page_title="Product Improvement Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .big-font {
            font-size:2rem !important;
            font-weight: bold;
        }
        .small-font {
            font-size:0.9rem !important;
        }
        .stButton>button {
            color: white;
            background-color: #FF4B4B;
            border: none;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 12px;
        }
        /* Style the input text itself */
        .stTextInput>div>div>input {
            border: 2px solid #ccc;
            border-radius: 4px;
            padding: 10px;
            color: #262730; /* Ensure text color is set */
            background-color: white; /* Set a default background */
        }
        /* Style the selectbox container */
        .stSelectbox>div>div>div {
            border: 2px solid #ccc;
            border-radius: 4px;
            background-color: white; /* Set a default background */
        }
        /* Style the text within the selectbox */
        .stSelectbox>div>div>div>div {
            color: #262730 !important; /* Ensure text color is set */
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'google_api_key' not in st.session_state:
    st.session_state.google_api_key = ""

if 'analyzer' not in st.session_state or st.session_state.google_api_key != os.getenv('GOOGLE_API_KEY'):
    st.session_state.analyzer = ProductAnalyzer(metadata_path, reviews_path, api_key=os.getenv('GOOGLE_API_KEY')) # Initialize with API key

# Sidebar for API key
with st.sidebar.expander("⚙️ Gemini API Key", expanded=not st.session_state.google_api_key):
    api_key = st.text_input("Enter your Google Gemini API Key:", type="password")
    if api_key:
        st.session_state.google_api_key = api_key
        os.environ['GOOGLE_API_KEY'] = api_key  # Update environment variable
        st.session_state.analyzer = ProductAnalyzer(metadata_path, reviews_path, api_key=api_key)
        st.success("API Key saved!")

def main():
    st.markdown("<p class='big-font'>📱 Product Improvement Analyzer</p>", unsafe_allow_html=True)
    st.markdown("---")

 

    products_df = st.session_state.analyzer.get_available_products()
    categories = sorted(st.session_state.analyzer.metadata_df['category'].unique().tolist())

    with st.expander("🔎 Filters", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            search_term = st.text_input("Search for a product:", "")
        with col2:
            selected_category = st.selectbox(
                "Filter by category:",
                options=["All Categories"] + categories,
                index=0
            )

    filtered_products = products_df.copy()
    if search_term:
        filtered_products = filtered_products[filtered_products['title'].str.contains(search_term, case=False, na=False)]
    if selected_category != "All Categories":
        category_asins = st.session_state.analyzer.metadata_df[
            st.session_state.analyzer.metadata_df['category'] == selected_category
        ]['parent_asin'].unique()
        filtered_products = filtered_products[filtered_products['parent_asin'].isin(category_asins)]

    st.subheader("Select a Product")
    if len(filtered_products) > 0:
        selected_title = st.selectbox(
            "Choose a product to analyze:",
            options=filtered_products['title'].tolist(),
            index=0 if len(filtered_products) > 0 else None
        )

        if selected_title:
            selected_asin = filtered_products[filtered_products['title'] == selected_title]['parent_asin'].iloc[0]
            product_details = st.session_state.analyzer.get_product_details(selected_asin)

            st.subheader("Product Details")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Price", product_details['price'] if product_details['price'] != 'No price available' else 'N/A')
            col2.metric("Category", product_details['category'])
            col3.metric("Reviews", product_details['reviews_count'])
            col4.metric("Avg. Rating", f"{product_details['average_rating']:.2f}/5.0" if not pd.isna(product_details['average_rating']) else 'N/A')

            with st.expander("ℹ️ More Product Information"):
                st.write(f"**Description:** {product_details['description']}")
            if not st.session_state.google_api_key:
                    st.warning("Please enter your Google Gemini API Key in the sidebar to use the analysis features.")
                    return
            if st.button("Generate Improvement Analysis", use_container_width=True):
                with st.spinner("Analyzing product reviews..."):
                    try:
                        analysis = st.session_state.analyzer.analyze_product(selected_asin)
                        st.session_state.current_analysis = analysis
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")

            if 'current_analysis' in st.session_state:
                st.subheader("💡 Improvement Analysis")
                st.markdown(st.session_state.current_analysis)
    else:
        st.warning("No products found matching your search criteria.")

if __name__ == "__main__":
    main()
