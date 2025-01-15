import pandas as pd
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import warnings
warnings.filterwarnings('ignore')

class ProductAnalyzer:
    def __init__(self, metadata_path, reviews_path):
        """Initialize the ProductAnalyzer with data paths."""
        self.metadata_path = metadata_path
        self.reviews_path = reviews_path
        self.metadata_df = None
        self.reviews_df = None
        self.llm_chain = None
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
        """Set up the LangChain chain with Ollama."""
        llm = Ollama(model="mistral")  # good for cross-lingual task , Owl-v2 for english text
        
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
            Review #{idx + 1}:
            Title: {review['title']}
            Helpful Vots: {review['helpful_vote']}
            Content: {review['text']}
            """
            reviews_analysis.append(review_text)
        return "\n".join(reviews_analysis)

    def analyze_product(self, asin):
        """Analyze a specific product and generate improvement suggestions."""
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
            print('Next is running LLM')
            result = self.llm_chain.run(context)
            print('After running LLM')
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
                'category':   '/'.join([str(item) if item is not None else '' for item in product.get('categories', 'No category available')]) ,
                'reviews_count': reviews_count,
                'average_rating': avg_rating,
                'price': product.get('price', 'No price available')
            }
        except Exception as e:
            raise Exception(f"Error getting product details: {str(e)}")
