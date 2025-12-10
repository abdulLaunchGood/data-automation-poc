# Asset Reusability in Dagster

## YES! One Source Can Be Used by Multiple Assets! 🎯

This is one of the **most powerful features** of Dagster assets - **reusability and fan-out patterns**.

## Example from Our POC

```python
# sources.py - ONE source asset
@asset(group_name="sources")
def api_users_raw(context):
    """Fetch users once"""
    return fetch_users_from_api()

# transforms.py - MULTIPLE assets use it
@asset(group_name="transforms")
def users_cleaned(context, api_users_raw: Dict):
    """Transform 1: Clean the user data"""
    return clean_users(api_users_raw)

# analytics.py - ANOTHER asset uses it
@asset(group_name="analytics")
def user_activity_stats(context, users_cleaned, posts_cleaned):
    """Uses users_cleaned (which came from api_users_raw)"""
    return calculate_stats(users_cleaned, posts_cleaned)

# exports.py - YET ANOTHER asset uses it
@asset(group_name="exports")
def users_csv(context, users_cleaned):
    """Export users (which came from api_users_raw)"""
    return export_to_csv(users_cleaned)
```

## Fan-Out Pattern Visualization

```
                    ┌─────────────────┐
                    │ api_users_raw   │  ← Fetched ONCE
                    │  (source)       │
                    └────────┬────────┘
                             │
                    ┌────────┴────────┐
                    │                 │
          ┌─────────▼─────────┐   ┌──▼──────────┐
          │ users_cleaned     │   │ Another     │
          │  (transform)      │   │ Transform   │
          └─────────┬─────────┘   └─────────────┘
                    │
          ┌─────────┴─────────┐
          │                   │
    ┌─────▼───────┐    ┌──────▼──────────────┐
    │ users_csv   │    │ user_activity_stats │
    │  (export)   │    │   (analytics)       │
    └─────────────┘    └─────────────────────┘
```

## Real Example in Your POC

### api_users_raw is used by:

1. **users_cleaned** (transforms.py)
   ```python
   def users_cleaned(context, api_users_raw: Dict):
       # Uses api_users_raw to clean data
   ```

2. **user_activity_stats** (analytics.py)
   ```python
   def user_activity_stats(context, users_cleaned, posts_cleaned):
       # Indirectly uses api_users_raw through users_cleaned
   ```

3. **users_csv** (exports.py)
   ```python
   def users_csv(context, users_cleaned):
       # Indirectly uses api_users_raw through users_cleaned
   ```

## Benefits of This Pattern

### 1. **Efficiency**
- API called only **ONCE** ✅
- Result is **cached** by Dagster
- Multiple downstream assets reuse the same data

### 2. **Cost Savings**
- Single API call instead of multiple
- Reduced bandwidth usage
- Lower API rate limit consumption

### 3. **Consistency**
- All downstream assets use the **same snapshot** of data
- No data skew between different transformations
- Reproducible results

### 4. **Modularity**
- Easy to add new transformations
- Each transformation is independent
- Can test each asset separately

## Complex Fan-Out Example

```python
# ONE source
@asset
def raw_data(context):
    return fetch_data()

# MANY consumers
@asset
def cleaned_data(context, raw_data): 
    return clean(raw_data)

@asset
def summary_stats(context, raw_data):
    return summarize(raw_data)

@asset
def ml_features(context, raw_data):
    return extract_features(raw_data)

@asset
def validation_report(context, raw_data):
    return validate(raw_data)

@asset
def backup_copy(context, raw_data):
    return backup(raw_data)
```

**Result:**
```
                raw_data (fetched ONCE)
                    │
     ┌──────┬───────┼───────┬──────┐
     │      │       │       │      │
cleaned  summary  ml_    validation backup
_data    _stats   features _report  _copy
```

## Fan-Out + Fan-In Pattern

Even more powerful - combine multiple sources!

```python
# Two sources
@asset
def users_data(context):
    return fetch_users()

@asset  
def orders_data(context):
    return fetch_orders()

# Fan-in: Uses BOTH sources
@asset
def user_order_analysis(context, users_data, orders_data):
    return analyze(users_data, orders_data)
```

**Pattern:**
```
users_data ──┐
             ├──► user_order_analysis
orders_data ─┘
```

## In Your Modular POC

### Current Dependencies:

```
api_users_raw ────► users_cleaned ───┬──► users_csv
                                     │
                                     ├──► user_activity_stats ──► user_stats_csv
                                     │
                                     └──► posts_with_user_info ──► posts_enriched_csv


api_posts_raw ────► posts_cleaned ───┬──► posts_with_user_info
                                     │
                                     └──► user_activity_stats
```

**Key Points:**
- `api_users_raw` used by **multiple** downstream assets
- `users_cleaned` used by **4 different assets**
- `user_activity_stats` combines data from **2 sources**

## Dagster Handles This Automatically!

When you run "Materialize all":

1. **Fetch sources** (once each):
   - `api_users_raw`
   - `api_posts_raw`

2. **Transform** (using cached sources):
   - `users_cleaned` (uses `api_users_raw`)
   - `posts_cleaned` (uses `api_posts_raw`)

3. **Analyze** (using cached transforms):
   - `user_activity_stats` (uses both `users_cleaned` + `posts_cleaned`)
   - `top_authors` (uses `user_activity_stats`)

4. **Export** (using all cached data):
   - `users_csv`
   - `posts_enriched_csv`
   - `user_stats_csv`
   - `top_authors_csv`
   - `export_summary` (uses ALL 4 CSV paths!)

## Try It!

Run your POC and check the logs - you'll see:
- API calls happen **once**
- Subsequent assets load from cache
- Multiple assets can run in **parallel** if they don't depend on each other!

---

**This is why Dagster is so powerful for data pipelines!** 🚀

One source → Many uses → No redundant work → Maximum efficiency!
