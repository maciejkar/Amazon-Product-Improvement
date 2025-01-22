import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
import warnings
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

class ProductAnalyzer:
    def __init__(self, metadata_path, reviews_path, api_key=None):
        """Initialize the ProductAnalyzer with data paths and API key."""
        self.metadata_path = metadata_path
        self.reviews_path = reviews_path
        self.metadata_df = None
        self.reviews_df = None
        self.llm_chain = None
        self.api_key = api_key
        self._load_data()
        self._setup_chain()

    def _load_data(self):
        """Load metadata and reviews from parquet files."""
        try:
            self.metadata_df = pd.read_parquet(self.metadata_path)
            self.reviews_df = pd.read_parquet(self.reviews_path)
            print("Data loaded successfully")
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")

    def get_available_products(self):
        """Return a DataFrame with product titles and ASINs."""
        return self.metadata_df[['title', 'parent_asin']].drop_duplicates()

    def _setup_chain(self):
        """Set up the LangChain chain with Google's Gemini."""
        if not self.api_key:
            return  # Do not set up chain if API key is missing

        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash-8b", # gemini-1.5-flash-8b or gemini-pro
            temperature=0.7,
            google_api_key=self.api_key
        )

        template = """
        Analyze the following product and its reviews to suggest improvements:

        Product Information:
        Title: {title}
        Category: {category}
        Description: {description}
        Average Rating: {average_rating:.2f}/5.0

        Customer Reviews:
        {reviews_analysis}

        Based on this information, please provide:
        1. Key issues identified from reviews (categorized by frequency and severity)
        2. Specific improvement suggestions for each identified issue
        3. Priority of improvements (High/Medium/Low) with justification
        4. Potential impact on customer satisfaction
        5. Estimated complexity of implementing each suggestion (Easy/Medium/Hard)

        Please format your response in a clear, structured manner with separate sections for each category.
        Focus on actionable improvements that could directly address the customer concerns.
        """

        prompt = PromptTemplate(
            input_variables=["title", "category", "description", "reviews_analysis", "average_rating"],
            template=template
        )

        self.llm_chain = LLMChain(llm=llm, prompt=prompt)

    def _prepare_review_analysis(self, reviews_df):
        """Prepare a detailed analysis string from reviews DataFrame."""
        reviews_analysis = []
        for idx, review in reviews_df.iterrows():
            review_text = f"""
            Next review:
            Title: {review['title']}
            Helpful Votes: {review['helpful_vote']}
            Content: {review['text']}
            """
            reviews_analysis.append(review_text)
        return "\n".join(reviews_analysis)

    def analyze_product(self, asin):
        """Analyze a specific product and generate improvement suggestions."""
        if not self.llm_chain:
            st.error("Gemini API Key is missing. Please enter it in the sidebar.")
            return None

        try:
            # Get product metadata
            product = self.metadata_df[self.metadata_df['parent_asin'] == asin].iloc[0]

            # Get product reviews
            product_reviews = self.reviews_df[self.reviews_df['parent_asin'] == asin]

            # Sort reviews by rating (prioritizing lower ratings for improvement analysis)
            product_reviews = product_reviews.sort_values('rating').head(5)

            # Prepare context
            context = {
                'title': product['title'],
                'description': product.get('description', 'No description available'),
                'category': product.get('category', 'No category available'),
                'reviews_analysis': self._prepare_review_analysis(product_reviews),
                'average_rating': product_reviews['rating'].mean()
            }

            # Run analysis
            print('Running Gemini analysis...')
            result = self.llm_chain.run(context)
            print('Analysis complete')
            return result

        except Exception as e:
            raise Exception(f"Error analyzing product: {str(e)}")

    def get_product_details(self, asin):
        """Get basic product details for display."""
        try:
            product = self.metadata_df[self.metadata_df['parent_asin'] == asin].iloc[0]
            reviews_count = len(self.reviews_df[self.reviews_df['parent_asin'] == asin])
            avg_rating = self.reviews_df[self.reviews_df['parent_asin'] == asin]['rating'].mean()

            return {
                'title': product['title'],
                'description': product.get('description', 'No description available'),
                'category': '/'.join([str(item) if item is not None else '' for item in product.get('categories', 'No category available')]),
                'reviews_count': reviews_count,
                'average_rating': avg_rating,
                'price': product.get('price', 'No price available')
            }
        except Exception as e:
            raise Exception(f"Error getting product details: {str(e)}")