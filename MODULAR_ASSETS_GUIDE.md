# Modular Assets Guide - Advanced Dagster Structure

This guide explains the **modular assets architecture** in the Dagster POC, demonstrating production-ready organizational patterns.

## 📁 Project Structure

```
dagster_poc/
├── assets/                    # Modular assets package
│   ├── __init__.py           # Asset registry
│   ├── sources.py            # Data extraction (APIs)
│   ├── transforms.py         # Data cleaning & enrichment
│   ├── analytics.py          # Aggregations & insights
│   └── exports.py            # File exports & summaries
├── assets.py                 # Simple assets (basic POC)
├── ops.py                    # Ops for jobs
├── jobs.py                   # Job definitions
└── __init__.py              # Definitions (combines everything)
```

## 🎯 Why Modular Assets?

### Benefits

1. **🗂️ Organization** - Clear separation of concerns
2. **♻️ Reusability** - Assets can be used across multiple pipelines
3. **🧪 Testability** - Easier to test individual modules
4. **👥 Team Collaboration** - Different teams can work on different modules
5. **📈 Scalability** - Easy to add new asset groups
6. **🔍 Discoverability** - Assets grouped by function in UI

## 📊 Asset Groups in This POC

### 1. **Sources** (`assets/sources.py`)
**Purpose:** Data extraction from external sources

```python
@asset(group_name="sources", compute_kind="api")
def api_users_raw(context):
    """Fetch users from API"""
    return fetch_from_api("users")

@asset(group_name="sources", compute_kind="api")
def api_posts_raw(context):
    """Fetch posts from API"""
    return fetch_from_api("posts")
```

**Assets:**
- `api_users_raw` - User data from JSONPlaceholder API
- `api_posts_raw` - Posts data from JSONPlaceholder API

**Dependencies:** None (source data)

---

### 2. **Transforms** (`assets/transforms.py`)
**Purpose:** Data cleaning, structuring, and enrichment

```python
@asset(group_name="transforms", compute_kind="pandas")
def users_cleaned(context, api_users_raw):
    """Clean and structure user data"""
    return transform_users(api_users_raw)

@asset(group_name="transforms", compute_kind="pandas")
def posts_with_user_info(context, posts_cleaned, users_cleaned):
    """Enrich posts with user information"""
    return posts_cleaned.merge(users_cleaned, on="user_id")
```

**Assets:**
- `users_cleaned` - Cleaned user data DataFrame
- `posts_cleaned` - Cleaned posts data DataFrame
- `posts_with_user_info` - Posts enriched with author details

**Dependencies:** Sources → Transforms

---

### 3. **Analytics** (`assets/analytics.py`)
**Purpose:** Aggregations, statistics, and insights

```python
@asset(group_name="analytics", compute_kind="pandas")
def user_activity_stats(context, users_cleaned, posts_cleaned):
    """Calculate activity statistics per user"""
    return calculate_stats(users_cleaned, posts_cleaned)

@asset(group_name="analytics", compute_kind="pandas")
def top_authors(context, user_activity_stats):
    """Identify top 5 authors"""
    return user_activity_stats.nlargest(5, "total_posts")
```

**Assets:**
- `user_activity_stats` - Per-user activity metrics
- `top_authors` - Top 5 most active authors
- `data_summary` - Overall dataset statistics

**Dependencies:** Transforms → Analytics

---

### 4. **Exports** (`assets/exports.py`)
**Purpose:** Save processed data to files

```python
@asset(group_name="exports", compute_kind="csv")
def users_csv(context, users_cleaned):
    """Export users to CSV"""
    users_cleaned.to_csv("output/modular_users.csv")
    return "output/modular_users.csv"

@asset(group_name="exports", compute_kind="python")
def export_summary(context, users_csv, posts_enriched_csv, ...):
    """Generate export summary"""
    return {"exported_files": [...], "summary": {...}}
```

**Assets:**
- `users_csv` - Users exported to CSV
- `posts_enriched_csv` - Enriched posts exported to CSV
- `user_stats_csv` - Activity stats exported to CSV
- `top_authors_csv` - Top authors exported to CSV
- `export_summary` - Final summary with metadata

**Dependencies:** All previous layers → Exports

---

## 🔄 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         SOURCES (APIs)                          │
├──────────────────────┬──────────────────────────────────────────┤
│  api_users_raw       │  api_posts_raw                           │
└──────────┬───────────┴──────────────┬──────────────────────────┘
           │                          │
           ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      TRANSFORMS (Cleaning)                       │
├──────────────────────┬──────────────────┬───────────────────────┤
│  users_cleaned       │  posts_cleaned   │  posts_with_user_info │
└──────────┬───────────┴────────┬─────────┴─────┬─────────────────┘
           │                    │               │
           ├────────────────────┼───────────────┘
           ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYTICS (Insights)                          │
├──────────────────────┬──────────────────┬───────────────────────┤
│user_activity_stats   │  top_authors     │  data_summary         │
└──────────┬───────────┴────────┬─────────┴─────┬─────────────────┘
           │                    │               │
           └────────────────────┼───────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXPORTS (Files & Summary)                    │
├────────────┬─────────────┬─────────────┬────────────┬───────────┤
│ users_csv  │posts_enr_csv│user_stats   │top_authors │  export   │
│            │             │    _csv     │   _csv     │  _summary │
└────────────┴─────────────┴─────────────┴────────────┴───────────┘
```

## 🎨 Asset Metadata

Each asset includes rich metadata:

- **`group_name`** - Logical grouping in UI
- **`description`** - Human-readable description
- **`compute_kind`** - Technology used (api, pandas, csv, python)

```python
@asset(
    group_name="transforms",           # Groups in UI
    description="Cleaned user data",   # Shows in asset details
    compute_kind="pandas"              # Icon/badge in UI
)
def users_cleaned(context, api_users_raw):
    ...
```

## 🖥️ UI Visualization

When you run `dagster dev`, you'll see:

### Asset Groups View
- **sources** - 2 assets (API extractions)
- **transforms** - 3 assets (Data cleaning)
- **analytics** - 3 assets (Insights)
- **exports** - 5 assets (File outputs)

### Lineage Graph
Beautiful visualization showing:
- Dependencies between assets
- Data flow from sources → exports
- Asset status (materialized, stale, etc.)
- Compute kind badges

## 📝 Code Organization Best Practices

### 1. **Separate by Domain**
```python
# ✅ Good - Domain separation
assets/
  sources.py      # All data sources
  transforms.py   # All transformations
  analytics.py    # All analytics

# ❌ Bad - Mixed concerns
assets.py         # Everything in one file
```

### 2. **Use Consistent Naming**
```python
# ✅ Good - Clear, descriptive names
api_users_raw       # Raw from API
users_cleaned       # Cleaned data
users_csv           # Exported CSV

# ❌ Bad - Vague names
data1, data2
process_stuff
output
```

### 3. **Document Dependencies**
```python
# ✅ Good - Clear docstrings
@asset
def posts_with_user_info(context, posts_cleaned, users_cleaned):
    """
    Enrich posts with user information.
    
    Args:
        posts_cleaned: Cleaned posts DataFrame
        users_cleaned: Cleaned users DataFrame
    
    Returns:
        DataFrame with posts enriched with user info
    """
```

### 4. **Group Related Assets**
```python
# ✅ Good - Logical grouping
@asset(group_name="analytics")  # Related assets grouped
def user_stats(...):
    ...

@asset(group_name="analytics")  # Same group
def top_users(...):
    ...
```

## 🧪 Testing Modular Assets

Each module can be tested independently:

```python
# Test sources
def test_api_users_raw():
    result = api_users_raw(context)
    assert "data" in result
    assert len(result["data"]) > 0

# Test transforms
def test_users_cleaned():
    mock_raw_data = {...}
    result = users_cleaned(context, mock_raw_data)
    assert isinstance(result, pd.DataFrame)
    assert "user_id" in result.columns
```

## 🚀 Running Modular Assets

### Materialize All Assets
```bash
dagster dev
# In UI: Assets tab → "Materialize all"
```

### Materialize Specific Group
In the UI:
1. Go to Assets tab
2. Click on group name (e.g., "transforms")
3. Click "Materialize all" for that group

### Materialize Single Asset
In the UI:
1. Go to Assets tab
2. Click on asset name
3. Click "Materialize"

## 📊 Comparison: Simple vs Modular

### Simple Assets (`assets.py`)
```python
# Single file, simple structure
@asset
def raw_user_data(...):
    ...

@asset
def transformed_user_data(...):
    ...
```
✅ **Good for:** POCs, prototypes, learning  
❌ **Limited:** Scalability, organization

### Modular Assets (`assets/`)
```python
# Multiple files, organized structure
# assets/sources.py
@asset(group_name="sources")
def api_users_raw(...):
    ...

# assets/transforms.py
@asset(group_name="transforms")
def users_cleaned(...):
    ...
```
✅ **Good for:** Production, teams, large projects  
✅ **Better:** Organization, testing, collaboration

## 🎓 Learning Path

1. **Start with Simple Assets** (`assets.py`)
   - Learn basic @asset decorator
   - Understand dependencies

2. **Graduate to Modular** (`assets/`)
   - Organize by domain
   - Use group_name
   - Add rich metadata

3. **Advanced Patterns**
   - Dynamic assets
   - Asset partitions
   - Asset sensors

## 🔗 Both Approaches in This POC!

We provide **both** to help you learn:

1. **Simple Assets** (`assets.py`)
   - 4 assets: raw_user_data, transformed_user_data, user_data_csv, data_extraction_summary
   - Single file, easy to understand

2. **Modular Assets** (`assets/`)
   - 13 assets across 4 modules
   - Production-ready organization
   - Shows best practices

**In the UI, you'll see both!** This lets you compare and learn the differences.

## 📚 Further Reading

- [Dagster Asset Groups](https://docs.dagster.io/concepts/assets/software-defined-assets#grouping-assets)
- [Asset Organization](https://docs.dagster.io/guides/dagster/recommended-project-structure)
- [Production Best Practices](https://docs.dagster.io/guides/dagster/production-guide)

---

**Try it now!** Run `dagster dev` and explore both the simple and modular assets in the UI! 🎉
