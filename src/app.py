import streamlit as st
import pandas as pd
from product_analyzer import ProductAnalyzer
import os

# Set page config
st.set_page_config(
    page_title="Product Improvement Analyzer",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if 'analyzer' not in st.session_state:
    metadata_path = r"C:\Users\karczews\OneDrive - Politechnika Wroclawska\studia\Amazon-Product-Improvement\data\metadata_Cell_Phones_and_Accessories.parquet"
    reviews_path = r"C:\Users\karczews\OneDrive - Politechnika Wroclawska\studia\Amazon-Product-Improvement\data\review_Cell_Phones_and_Accessories.parquet"
    st.session_state.analyzer = ProductAnalyzer(metadata_path, reviews_path)

def main():
    st.title("📱 Product Improvement Analyzer")
    st.markdown("---")

    # Get available products and categories
    products_df = st.session_state.analyzer.get_available_products()
    categories = sorted(st.session_state.analyzer.metadata_df['category'].unique().tolist())

    # Create filters section
    st.subheader("Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("Search for a product:", "")
    
    with col2:
        selected_category = st.selectbox(
            "Filter by category:",
            options=["All Categories"] + categories,
            index=0
        )
    
    # Apply filters
    filtered_products = products_df.copy()
    
    if search_term:
        filtered_products = filtered_products[filtered_products['title'].str.contains(search_term, case=False, na=False)]
    
    if selected_category != "All Categories":
        # Get ASINs for the selected category
        category_asins = st.session_state.analyzer.metadata_df[
            st.session_state.analyzer.metadata_df['category'] == selected_category
        ]['parent_asin'].unique()
        filtered_products = filtered_products[filtered_products['parent_asin'].isin(category_asins)]

    # Display product selector
    st.subheader("Select a Product")
    if len(filtered_products) > 0:
        selected_title = st.selectbox(
            "Choose a product to analyze:",
            options=filtered_products['title'].tolist(),
            index=0 if len(filtered_products) > 0 else None
        )
        
        if selected_title:
            selected_asin = filtered_products[filtered_products['title'] == selected_title]['parent_asin'].iloc[0]
            
            # Create columns for layout
            details_col1, details_col2 = st.columns([1, 2])
            
            with details_col1:
                st.subheader("Product Details")
                details = st.session_state.analyzer.get_product_details(selected_asin)
                
                st.write(f"**Price:** {details['price']}")
                st.write(f"**Category:** {details['category']}")
                st.write(f"**Number of Reviews:** {details['reviews_count']}")
                st.write(f"**Average Rating:** {details['average_rating']:.2f}/5.0")
                
                if st.button("Generate Improvement Analysis"):
                    with st.spinner("Analyzing product reviews..."):
                        try:
                            analysis = st.session_state.analyzer.analyze_product(selected_asin)
                            st.session_state.current_analysis = analysis
                        except Exception as e:
                            st.error(f"Error during analysis: {str(e)}")
            
            with details_col2:
                st.subheader("Improvement Analysis")
                if 'current_analysis' in st.session_state:
                    st.markdown(st.session_state.current_analysis)
    else:
        st.warning("No products found matching your search criteria.")

if __name__ == "__main__":
    main()
