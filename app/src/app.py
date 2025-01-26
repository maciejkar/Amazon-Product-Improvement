import streamlit as st

from src.analyzer import ProductAnalyzer
from src.config import settings
from src.fetcher import AmazonScraper
from src.logconf import setup_logging

# NOTE: This file would need some refactor.
# Current structure doesn't provide easy error handling


class AppToolConnectionError(Exception):
    pass


class AppManager:
    @classmethod
    def run(cls):
        if "logger_set" not in st.session_state:
            st.session_state.logger_set = True
            setup_logging()
        cls.set_basic_config()
        cls.set_menu()
        cls.set_working_section()

    @classmethod
    def set_basic_config(cls) -> None:
        title = "Amazon Product Improvement Analyzer"
        icon = "📊"
        st.set_page_config(page_title=title, page_icon=icon, layout="wide")
        with open(settings.CSS_PATH) as f:
            style = f"<style>{f.read()}</style>"
        st.markdown(style, unsafe_allow_html=True)

    @classmethod
    def set_menu(cls) -> None:
        menu_title = "⚙️ Credentials"
        with st.sidebar:
            st.title(menu_title)
            google_api_key = st.text_input(
                "Enter your Google Gemini API Key:",
                type="password",
                value=st.session_state.get("google_api_key", settings.GOOGLE_API_KEY),
            )
            amazon_login = st.text_input(
                "Enter your Amazon Login:",
                value=st.session_state.get("amazon_login", settings.EMAIL),
            )
            amazon_password = st.text_input(
                "Enter your Amazon Password:",
                type="password",
                value=st.session_state.get("amazon_password", settings.PASSWORD),
            )
            if st.button("Connect"):
                if hasattr(st.session_state, "product_analyzer"):
                    delattr(st.session_state, "product_analyzer")
                if hasattr(st.session_state, "amazon_scraper"):
                    delattr(st.session_state, "amazon_scraper")
                cls._handle_menu_submit(google_api_key, amazon_login, amazon_password)

    @staticmethod
    def _handle_menu_submit(
        google_api_key: str, amazon_login: str, amazon_password: str
    ) -> None:
        if google_api_key:
            st.session_state.google_api_key = google_api_key
            try:
                with st.spinner("Establishing connection..."):
                    st.session_state.product_analyzer = ProductAnalyzer(
                        api_key=google_api_key
                    )
                st.success("Analyzing tools ready to use!")
            except Exception:
                st.error("Unexpected error while connecting to Gemini.")

        if amazon_login and amazon_password:
            st.session_state.amazon_login = amazon_login
            st.session_state.amazon_password = amazon_password
            try:
                st.session_state.amazon_scraper = AmazonScraper(
                    email=amazon_login, password=amazon_password
                )
                with st.spinner("Connecting to Amazon..."):
                    st.session_state.amazon_scraper.open_connection()
                st.success("Amazon connected successfully!")
            except Exception:
                st.error(
                    "Error connecting Amazon. If the problem persists, try to solve captcha on your account."
                )

        if not google_api_key:
            st.warning("Google API Key is missing.")
        if not (amazon_login and amazon_password):
            st.warning("Amazon credentials are incomplete.")

    @classmethod
    def set_working_section(cls) -> None:
        cls._display_title()
        cls._display_product_input()
        cls._display_product_details()

    @staticmethod
    def _display_title() -> None:
        title = "📱 Product Improvement Analyzer"
        st.markdown(f"<p class='big-font'>{title}</p>", unsafe_allow_html=True)
        st.markdown("---")

    @classmethod
    def _display_product_input(cls) -> None:
        col1, col2 = st.columns([5, 1])
        with col1:
            product_url = st.text_input("Enter product URL:", "")
        with col2:
            max_pages = st.number_input(
                "Max pages to scrape:", min_value=1, step=1, value=5
            )
        if st.button("Run analysis"):
            if hasattr(st.session_state, "products_data"):
                delattr(st.session_state, "products_data")
            if hasattr(st.session_state, "current_summary"):
                delattr(st.session_state, "current_summary")
            cls._load_product_data(product_url, max_pages)
            cls._generate_analysis()

    @staticmethod
    def _load_product_data(product_url: str, max_pages: int) -> None:
        if not product_url:
            st.warning("Please enter a product URL.")
            return
        if "amazon_scraper" not in st.session_state:
            st.error("Connect to amazon first.")
        try:
            with st.spinner("Fetching product data..."):
                st.session_state.products_data = (
                    st.session_state.amazon_scraper.fetch_product_data(
                        product_url, max_pages
                    )
                )
                st.success("Product data loaded successfully!")
        except Exception:
            st.error("Error loading product data. Try to establish connection again.")

    @staticmethod
    def _generate_analysis() -> None:
        if "products_data" not in st.session_state:
            return
        data = st.session_state.products_data

        with st.spinner("Analyzing product reviews..."):
            try:
                summary = st.session_state.product_analyzer.analyze_product(data)
                st.session_state.current_summary = summary
                st.success("Analysis generated successfully!")
            except Exception:
                st.error("An error occured during analysis.")

    @staticmethod
    def _display_product_details() -> None:
        if "products_data" not in st.session_state:
            return
        data = st.session_state.products_data
        st.subheader("Product Details")
        col1, col2 = st.columns([3, 1])
        col1.markdown(f"### 🏷️ {data['product']}")
        col2.markdown(
            f"<span style='color:gray;'>**Category:** {data['category']}</span>",
            unsafe_allow_html=True,
        )
        truncated_url = (
            data["url"] if len(data["url"]) <= 100 else data["url"][:97] + "..."
        )
        st.markdown(
            f"<span style='color:gray;'>[{truncated_url}]({data['url']})</span>",
            unsafe_allow_html=True,
        )
        col1, col2, col3 = st.columns(3)
        col1.metric("Price", data["price"])
        rating = data["rating"] if data["rating"] > 0 else "?"
        col2.metric("Average rating", f"{rating}/5")
        col3.metric("Fetched comments", len(data["comments"]))
        if "current_summary" in st.session_state:
            st.subheader("💡 Improvement Analysis")
            st.markdown(st.session_state.current_summary)
