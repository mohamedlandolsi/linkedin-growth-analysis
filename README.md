# LinkedIn Post Analysis Tool

A Python-based tool for analyzing LinkedIn posts using web scraping, NLP sentiment analysis, and machine learning.

## Project Structure

```
linkedin-growth-analysis/
├── notebooks/          # Jupyter notebooks for analysis
├── scripts/           # Python modules and utilities
├── data/             # Output data directory
│   ├── csv/         # CSV exports
│   └── json/        # JSON exports
├── requirements.txt  # Project dependencies
└── README.md        # Project documentation
```

## Setup

1. Create a virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Download required NLTK data (if needed):
   ```python
   import nltk
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

## Features

- **Web Scraping**: Selenium and BeautifulSoup for data collection
- **NLP Analysis**: TextBlob and VADER for sentiment analysis
- **Data Processing**: Pandas and NumPy for data manipulation
- **Machine Learning**: Scikit-learn for predictive modeling
- **Visualization**: Matplotlib, Seaborn, and Plotly for insights

## Usage

Start by creating analysis notebooks in the `notebooks/` folder and reusable scripts in the `scripts/` folder.
