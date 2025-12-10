# Setup Guide for Data Automation POC

This guide will help you set up and run the POC for both Dagster and Prefect platforms.

## Prerequisites

- Python 3.10 or higher (Python 3.13 is recommended)
- pip

**Important:** Python 3.14 has compatibility issues with current Dagster dependencies (Pydantic errors). Please use Python 3.13 or 3.12 for best compatibility.

**Check your Python version:**
```bash
python3 --version
```

**If you need Python 3.13, you can:**
- Download from [python.org](https://www.python.org/downloads/)
- Or use `pyenv` to manage multiple Python versions:
  ```bash
  brew install pyenv  # On macOS
  pyenv install 3.13.0
  pyenv local 3.13.0
  ```

## Quick Start

We'll create separate virtual environments for each platform to avoid dependency conflicts.

---

## Dagster Setup

### 1. Navigate to Dagster POC directory
```bash
cd data-automation-poc/dagster-poc
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install dependencies
```bash
pip install -e .
```

### 4. Run the Dagster pipeline

**Option A: Using Dagster UI with Assets (Recommended - Best UI Experience)**
```bash
dagster dev
```
Then open http://localhost:3000 in your browser:
- Go to "Assets" tab to see the data lineage graph
- Click "Materialize all" to run the entire pipeline
- View the beautiful lineage visualization showing data flow

**Option B: Using Dagster UI with Jobs**
```bash
dagster dev
```
Then open http://localhost:3000, go to "Jobs" tab, select "data_extraction_job" and click "Launch run"

**Option C: Using Python directly**
```bash
python -c "from dagster_poc.jobs import data_extraction_job; data_extraction_job.execute_in_process()"
```

### 5. Run unit tests
```bash
python -m unittest discover tests
```

### 6. Deactivate virtual environment when done
```bash
deactivate
```

---

## Prefect Setup

### 1. Navigate to Prefect POC directory
```bash
cd data-automation-poc/prefect-poc
```

### 2. Create and activate virtual environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows
```

### 3. Install dependencies
```bash
pip install -e .
```

### 4. Run the Prefect flow
```bash
python prefect_poc/flows.py
```

### 5. Run unit tests
```bash
python -m unittest discover tests
```

### 6. Deactivate virtual environment when done
```bash
deactivate
```

---

## Output

Both pipelines will create an `output` directory with CSV files:
- Dagster: `output/dagster_users.csv`
- Prefect: `output/prefect_users.csv`

---

## What the POC Does

Both implementations perform the same data extraction pipeline:

1. **Fetch Data**: Retrieves user data from JSONPlaceholder API (https://jsonplaceholder.typicode.com/users)
2. **Transform Data**: Extracts relevant fields (id, name, username, email, city, company)
3. **Save to CSV**: Writes the transformed data to a CSV file
4. **Generate Summary**: Creates a summary report with record count and columns

---

## Comparison Notes

### Dagster
- **UI**: Excellent built-in UI at localhost:3000
- **Structure**: More structured with ops and jobs
- **Testing**: Native support with `build_op_context()`
- **Learning Curve**: Moderate - requires understanding of ops, jobs, and resources
- **Cost**: 100% Free and open-source

### Prefect
- **UI**: Requires cloud account (free tier available) for full UI experience
- **Structure**: Very Pythonic with simple decorators
- **Testing**: Access underlying functions with `.fn()`
- **Learning Curve**: Easy - very intuitive for Python developers
- **Cost**: Free tier available (10,000+ runs/month)

---

## Troubleshooting

### Issue: Module not found
**Solution**: Make sure you've installed the package with `pip install -e .` and your virtual environment is activated.

### Issue: Permission denied
**Solution**: Make sure you have write permissions in the directory where output files are created.

### Issue: Port 3000 already in use (Dagster)
**Solution**: Stop any other service using port 3000 or specify a different port:
```bash
dagster dev -p 3001
```

### Issue: API request fails
**Solution**: Check your internet connection. The POC uses the public JSONPlaceholder API.

---

## Next Steps

After running both POCs:
1. Review the generated CSV files in the `output` directory
2. Compare the UI experiences (Dagster has local UI, Prefect requires cloud setup for UI)
3. Review the code structure and ease of development
4. Run the unit tests to see testing approaches
5. Consider your specific requirements for scheduling, monitoring, and scalability
