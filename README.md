# Data Automation POC: Dagster vs Prefect

This POC compares two data orchestration platforms for simple data extraction tasks.

## Platforms Compared

1. **Dagster** - Open-source data orchestrator
2. **Prefect** - Modern workflow orchestration

## Project Structure

```
data-automation-poc/
├── dagster-poc/          # Dagster implementation
│   ├── dagster_poc/      # Main package
│   └── tests/            # Unit tests
├── prefect-poc/          # Prefect implementation
│   ├── prefect_poc/      # Main package
│   └── tests/            # Unit tests
└── README.md
```

## Setup Instructions

**⚠️ Important:** Use Python 3.10-3.13 (3.13 recommended). Python 3.14 has compatibility issues with Dagster dependencies.

See [SETUP.md](SETUP.md) for detailed setup and installation instructions.

### Quick Start

**Dagster:**
```bash
cd dagster-poc
python3 -m venv venv
source venv/bin/activate
pip install -e .
dagster dev  # Access UI at http://localhost:3000
```

**Prefect:**
```bash
cd prefect-poc
python3 -m venv venv
source venv/bin/activate
pip install -e .
python prefect_poc/flows.py
```

**Run Tests (unittest):**
```bash
python -m unittest discover tests
```

## Comparison Summary

### Dagster
**Pros:**
- Excellent UI/observability
- Strong typing and testing support
- Great for complex data pipelines
- Free open-source

**Cons:**
- Steeper learning curve
- More boilerplate code

### Prefect
**Pros:**
- Very easy to use
- Pythonic and intuitive
- Quick to get started
- Free tier available

**Cons:**
- Less opinionated structure
- UI requires cloud account (free tier)

## Cost Comparison

- **Dagster**: 100% free and open-source
- **Prefect**: Free tier available (10,000+ runs/month), paid plans for advanced features
