#!/bin/bash
# Setup script for SHL Assessment Recommendation System

echo "=========================================="
echo "SHL Assessment Recommendation System Setup"
echo "=========================================="
echo ""

# Create virtual environment
echo "1. Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "2. Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "3. Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "4. Installing dependencies..."
pip install -r requirements.txt

# Create assessment data
echo "5. Creating assessment data..."
python create_mock_data.py

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "To activate the virtual environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the server, run:"
echo "  python app.py"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
