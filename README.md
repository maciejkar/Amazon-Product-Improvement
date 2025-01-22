# Amazon Product Improvement Analyzer

A tool that analyzes Amazon product reviews and metadata to suggest product improvements using LangChain and LLMs.

## Features

- Product analysis using LangChain and Ollama
- Web interface built with Streamlit
- Category and title-based product filtering
- Detailed product improvement suggestions
- Review analysis with ratings and titles

## Setup

1. Install requirements:
```bash
pip install -r requirements.txt
```

2. Install Ollama:
- Visit [Ollama's website](https://ollama.ai/) and follow installation instructions
- Pull the Mistral model:
```bash
ollama pull mistral
```

3. Place your data files in the `data/` directory:
- `metadata_Cell_Phones_and_Accessories.parquet`
- `review_Cell_Phones_and_Accessories.parquet`

## Usage

Run the web application:
```bash
cd src
streamlit run app.py
```

## Project Structure

- `src/`
  - `product_analyzer.py`: Main analysis class
  - `app.py`: Streamlit web interface
- `data/`: Data directory (not included in repository)
- `requirements.txt`: Python dependencies
