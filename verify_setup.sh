#!/bin/bash

echo "================================"
echo "POC Setup Verification Script"
echo "================================"
echo ""

# Test Dagster
echo "1. Testing Dagster Setup..."
cd dagster-poc
if [ -d "venv" ]; then
    echo "   ✓ Virtual environment exists"
    if ./venv/bin/python -c "import dagster" 2>/dev/null; then
        echo "   ✓ Dagster is installed"
    else
        echo "   ✗ Dagster not installed - Run: pip install dagster dagster-webserver pandas requests"
    fi
else
    echo "   ✗ Virtual environment not found - Run: python3 -m venv venv"
fi
cd ..
echo ""

# Test Prefect
echo "2. Testing Prefect Setup..."
cd prefect-poc
if [ -d "venv" ]; then
    echo "   ✓ Virtual environment exists"
    if ./venv/bin/python -c "import prefect" 2>/dev/null; then
        echo "   ✓ Prefect is installed"
    else
        echo "   ✗ Prefect not installed - Run: pip install prefect pandas requests"
    fi
else
    echo "   ✗ Virtual environment not found - Run: python3 -m venv venv"
fi
cd ..
echo ""

echo "================================"
echo "Next Steps:"
echo "================================"
echo "1. Follow instructions in SETUP.md"
echo "2. Install dependencies in each venv"
echo "3. Run the pipelines and tests"
echo ""
