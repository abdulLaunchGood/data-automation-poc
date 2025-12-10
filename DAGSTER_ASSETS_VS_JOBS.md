# Dagster: Assets vs Jobs - Key Differences

This document explains the difference between Dagster's **Assets** and **Jobs/Ops** approaches.

## Quick Summary

| Feature | **Assets** (Modern) | **Jobs/Ops** (Traditional) |
|---------|-------------------|------------------------|
| **Focus** | What you're producing | How you're processing |
| **UI Visualization** | ✅ Beautiful lineage graph | ❌ Limited visualization |
| **Declarative** | Yes - focuses on data | No - focuses on computation |
| **Incremental Updates** | ✅ Built-in support | Manual implementation |
| **Best For** | Data pipelines, ETL | Process orchestration |
| **Dagster Recommendation** | ✅ **Recommended** | Legacy approach |

---

## Conceptual Difference

### Assets (What You're Building)
**Think: "I want to create this dataset"**

```python
@asset
def transformed_user_data(raw_user_data):
    """I produce a transformed dataset"""
    return transform(raw_user_data)
```

- Focus on **the data/output**
- Dagster tracks what exists and what needs updating
- Dependencies are implicit (function parameters)
- Great for data products

### Jobs/Ops (How You're Processing)
**Think: "I want to run this process"**

```python
@op
def transform_data(context, raw_data):
    """I perform a transformation"""
    return transform(raw_data)

@job
def data_pipeline():
    """I orchestrate multiple operations"""
    raw = fetch()
    transformed = transform_data(raw)
    save(transformed)
```

- Focus on **the computation/steps**
- Manual dependency management
- Traditional workflow orchestration
- Great for one-off processes

---

## Visual Comparison in UI

### Assets UI (Our POC)
```
┌─────────────────┐
│ raw_user_data   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│ transformed_user_data   │
└────────┬────────────────┘
         │
         ├──────────────┐
         ▼              ▼
┌────────────────┐  ┌──────────────────────────┐
│ user_data_csv  │  │ data_extraction_summary  │
└────────────────┘  └──────────────────────────┘
```
✅ **Beautiful graph showing data lineage**
✅ Click any node to see details
✅ Materialize individual assets or all

### Jobs UI
```
Running job: data_extraction_job
├─ Step 1: fetch_data_from_api
├─ Step 2: transform_data
├─ Step 3: save_to_csv
└─ Step 4: generate_summary
```
❌ **Linear list, no visual graph**
❌ Less intuitive
❌ Can't easily see dependencies

---

## Real Example from Our POC

### 1. Assets Approach (assets.py)

```python
@asset(description="Raw user data fetched from JSONPlaceholder API")
def raw_user_data(context: AssetExecutionContext) -> Dict:
    """Fetch raw data - I AM the raw data asset"""
    return fetch_from_api()

@asset(description="Transformed user data as DataFrame")
def transformed_user_data(context: AssetExecutionContext, raw_user_data: Dict) -> pd.DataFrame:
    """Transform data - I depend on raw_user_data asset"""
    return transform(raw_user_data)
```

**Benefits:**
- Dependencies are clear from function parameters
- Dagster knows `transformed_user_data` depends on `raw_user_data`
- UI shows this relationship visually
- Can rematerialize just one asset

### 2. Jobs/Ops Approach (ops.py + jobs.py)

```python
# ops.py
@op(out=Out(Dict))
def fetch_data_from_api(context) -> Dict:
    """Fetch data - I'm a computation step"""
    return fetch_from_api()

@op
def transform_data(context, raw_data: Dict) -> pd.DataFrame:
    """Transform data - I'm another computation step"""
    return transform(raw_data)

# jobs.py
@job
def data_extraction_job():
    """Wire everything together manually"""
    raw_data = fetch_data_from_api()
    transformed_df = transform_data(raw_data)
    file_path = save_to_csv(transformed_df)
    generate_summary(transformed_df, file_path)
```

**Characteristics:**
- Must explicitly wire dependencies in job
- Less declarative
- No built-in lineage visualization
- Traditional workflow pattern

---

## When to Use Each

### Use **Assets** when:
✅ Building data pipelines (ETL/ELT)
✅ Creating datasets/tables/reports
✅ Need data lineage tracking
✅ Want incremental updates
✅ Building data products
✅ **90% of modern use cases**

**Example:** Daily sales report, user analytics table, ML feature store

### Use **Jobs/Ops** when:
- One-off data migrations
- Complex computational graphs
- Non-data workflows (sending emails, API calls)
- Legacy code migration

---

## Key Advantages of Assets

### 1. **Automatic Dependency Resolution**
```python
# Assets - dependencies from parameters
@asset
def c(a, b):  # Automatically depends on assets 'a' and 'b'
    return a + b
```

### 2. **Incremental Materialization**
- Only recompute what changed
- Smart caching
- Asset metadata tracking

### 3. **Beautiful UI**
- Visual lineage graph
- Click nodes for details
- Easy debugging
- Asset catalog

### 4. **Data-Centric Thinking**
- Focus on what you're creating
- Not how you're creating it
- Better for analytics/data engineering

---

## In Our POC

We provide **BOTH** approaches so you can compare:

### Assets (`assets.py`)
- 4 assets with clear dependencies
- Beautiful graph in UI
- Modern Dagster approach
- **Recommended for evaluation**

### Jobs (`ops.py` + `jobs.py`)
- 4 ops orchestrated by 1 job
- Traditional approach
- Shows workflow steps
- **Good for comparison**

---

## Dagster's Official Recommendation

> **Dagster strongly recommends using Assets for new projects.**
> 
> Assets are the modern way to build data pipelines in Dagster and provide better:
> - Developer experience
> - UI visualization
> - Dependency management
> - Incremental processing

Jobs/Ops are still supported for:
- Legacy migrations
- Special cases
- Non-data workflows

---

## Try Both in the POC!

1. **Assets**: Open UI → "Assets" tab → See the beautiful graph
2. **Jobs**: Open UI → "Jobs" tab → See the traditional list

Both do the same thing, but Assets provides a much better experience! 🎉

---

## Further Reading

- [Dagster Assets Documentation](https://docs.dagster.io/concepts/assets/software-defined-assets)
- [Dagster Ops & Jobs](https://docs.dagster.io/concepts/ops-jobs-graphs)
- [When to use Assets vs Jobs](https://docs.dagster.io/guides/dagster/when-to-use-assets-vs-ops)
