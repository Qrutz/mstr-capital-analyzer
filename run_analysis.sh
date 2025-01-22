#!/bin/bash

# MicroStrategy Debt Risk Analysis Runner
# Runs all analysis scripts and generates reports

echo "================================================"
echo "MSTR Debt Risk Analysis"
echo "================================================"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "Running analysis..."
echo ""

# Run main analysis
python analyze.py

echo ""
echo "================================================"
echo "Analysis complete!"
echo ""
echo "To view interactive dashboard, run:"
echo "  streamlit run dashboard/app.py"
echo ""
echo "To view detailed notebook analysis:"
echo "  jupyter notebook notebooks/debt_risk_analysis.ipynb"
echo "================================================"
