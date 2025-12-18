#!/bin/bash

# Clear Python cache
echo "Clearing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Clear Streamlit cache
echo "Clearing Streamlit cache..."
rm -rf ~/.streamlit/cache 2>/dev/null

echo "Starting Streamlit app..."
streamlit run app.py

