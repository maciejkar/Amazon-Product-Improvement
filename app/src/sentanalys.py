import pandas as pd
import plotly.express as px
from nltk.sentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:

    def __init__(self, merged_data):
        self.merged_data = merged_data
        self.sid = SentimentIntensityAnalyzer()

    def analyze_sentiment(self, text):
        """
        Analyze sentiment of the given text and return the compound score.

        :param text: Text to analyze.
        :return: Compound sentiment score.
        """
        scores = self.sid.polarity_scores(text)
        return scores['compound']

    def apply_sentiment_analysis(self):
        """
        Apply sentiment analysis to the review text in the merged data.
        """
        self.merged_data['sentiment_score'] = self.merged_data['text'].apply(self.analyze_sentiment)
        self.merged_data['sentiment_category'] = pd.cut(
            self.merged_data['sentiment_score'],
            bins=[-1, -0.1, 0.1, 1],
            labels=['Negative', 'Neutral', 'Positive']
        )

    def prepare_sentiment_data(self, products):
        """
        Prepare sentiment data for visualization.

        :param products: List of product ASINs to include in the analysis.
        :return: DataFrame containing sentiment distribution data.
        """
        sentiment_data = []

        for product_asin in products:
            product_data = self.merged_data[self.merged_data['parent_asin'] == product_asin]
            product_title = (
                self.metadata.loc[self.metadata['parent_asin'] == product_asin, 'title'].values[0]
                if not self.metadata.empty else product_asin
            )

            # Count sentiment categories
            sentiment_counts = product_data['sentiment_category'].value_counts()

            # Append to the list
            for sentiment, count in sentiment_counts.items():
                sentiment_data.append({
                    'Product': product_title,
                    'Sentiment Category': sentiment,
                    'Count': count
                })

        return pd.DataFrame(sentiment_data)

    def create_sentiment_plot(self, product):
        """
        Create a horizontal bar plot for sentiment distribution of top products.

        :param top_n: Number of top products to include in the plot.
        :return: Plotly figure object.
        """
        # Get the top N products by review count
        sentiment_df = self.prepare_sentiment_data(product)

        # Create the plot
        fig = px.bar(
            sentiment_df,
            x='Count',
            y='Product',
            color='Sentiment Category',
            orientation='h',
            title='Sentiment Distribution for Top Products',
            labels={'Count': 'Number of Reviews', 'Product': 'Products'},
            color_discrete_sequence=px.colors.qualitative.Set2
        )

        return fig
