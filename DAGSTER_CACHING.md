# Dagster Caching & I/O Managers

## The Question 🤔

**If 2 assets read from the same MySQL source, does it query MySQL twice?**

## The Answer: NO! ✅

**Dagster queries MySQL ONCE and caches the result!** This is handled by the **I/O Manager**.

## How It Works

```python
# sources.py
@asset(group_name="sources")
def mysql_orders(context):
    """This runs ONCE per materialization"""
    context.log.info("🔵 Querying MySQL...")
    df = pd.read_sql("SELECT * FROM orders", engine)
    context.log.info(f"✅ Loaded {len(df)} rows from MySQL")
    return df

# transforms.py  
@asset(group_name="transforms")
def orders_cleaned(context, mysql_orders):
    """Uses cached mysql_orders - NO MySQL query!"""
    context.log.info("🟢 Loading mysql_orders from cache...")
    return clean(mysql_orders)

@asset(group_name="transforms")
def orders_summary(context, mysql_orders):
    """ALSO uses cached mysql_orders - NO MySQL query!"""
    context.log.info("🟢 Loading mysql_orders from cache...")
    return summarize(mysql_orders)
```

## Execution Flow

```
┌─────────────────────────────────────────────────┐
│ 1. MATERIALIZE mysql_orders                    │
│    - Query MySQL ONCE                           │
│    - Store result via I/O Manager               │
│    - Cache location: .dagster/storage/...       │
└─────────────────────────────────────────────────┘
                    │
                    ├─────────────────┐
                    │                 │
                    ▼                 ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│ 2. MATERIALIZE           │  │ 3. MATERIALIZE           │
│    orders_cleaned        │  │    orders_summary        │
│                          │  │                          │
│ - Load from CACHE        │  │ - Load from CACHE        │
│ - NO MySQL query! ✅     │  │ - NO MySQL query! ✅     │
└──────────────────────────┘  └──────────────────────────┘
```

## Real Logs Example

When you run "Materialize all", you'll see:

```
🔵 mysql_orders: Querying MySQL...
✅ mysql_orders: Loaded 10000 rows from MySQL
📝 mysql_orders: Writing to storage/mysql_orders

🟢 orders_cleaned: Loading mysql_orders from cache...
📖 orders_cleaned: Loaded from storage/mysql_orders
✅ orders_cleaned: Processed 10000 rows

🟢 orders_summary: Loading mysql_orders from cache...
📖 orders_summary: Loaded from storage/mysql_orders
✅ orders_summary: Summarized 10000 rows

MySQL was queried only ONCE! ✅
```

## I/O Manager Default Behavior

Dagster uses `PickledObjectFilesystemIOManager` by default:

```python
# When mysql_orders completes:
# 1. Return value is pickled
# 2. Saved to: .dagster/storage/mysql_orders
# 3. Asset marked as "materialized"

# When orders_cleaned needs mysql_orders:
# 1. Check if mysql_orders is materialized ✅
# 2. Load from .dagster/storage/mysql_orders
# 3. Unpickle and pass to orders_cleaned
# 4. NO MySQL query needed!
```

## Cache Duration

**Cache lasts until you re-materialize the source asset!**

```
Day 1:
- Materialize mysql_orders → Queries MySQL, saves to cache
- Materialize orders_cleaned → Loads from cache
- Materialize orders_summary → Loads from cache

Day 2 (without re-materializing mysql_orders):
- Materialize orders_cleaned → Still loads from Day 1 cache!
- Materialize orders_summary → Still loads from Day 1 cache!

Day 3 (re-materialize mysql_orders):
- Materialize mysql_orders → Queries MySQL again, updates cache
- Materialize orders_cleaned → Loads from new cache
```

## Dagster UI Shows This

In the UI, you'll see:

```
Asset: mysql_orders
Status: ✅ Materialized
Last materialization: 2 hours ago

Asset: orders_cleaned
Status: ✅ Materialized  
Last materialization: 1 hour ago
Dependencies: mysql_orders (from cache)

Asset: orders_summary
Status: ✅ Materialized
Last materialization: 1 hour ago  
Dependencies: mysql_orders (from cache)
```

## Benefits 🎯

### 1. **Efficiency**
- MySQL queried ONCE
- Subsequent assets use cache
- **Huge savings for expensive queries!**

### 2. **Consistency**
- All downstream assets use the **same snapshot**
- No data skew
- Reproducible results

### 3. **Speed**
- Cache reads are FAST (local disk)
- No network latency
- Parallel execution possible

### 4. **MySQL Resource Saving**
```
Without caching:
mysql_orders → MySQL query (10 seconds)
orders_cleaned → MySQL query (10 seconds)  ❌
orders_summary → MySQL query (10 seconds)  ❌
Total: 30 seconds + 3x MySQL load

With Dagster caching:
mysql_orders → MySQL query (10 seconds)
orders_cleaned → Cache read (0.1 seconds)  ✅
orders_summary → Cache read (0.1 seconds)  ✅
Total: 10.2 seconds + 1x MySQL load
```

## Custom I/O Manager for MySQL

If you want more control:

```python
from dagster import IOManager, io_manager
import pandas as pd
from sqlalchemy import create_engine

class SmartMySQLIOManager(IOManager):
    """
    Custom I/O Manager that:
    1. Saves to MySQL on write
    2. Loads from MySQL on read
    3. Caches in memory during run
    """
    
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self._cache = {}  # In-memory cache for same run
    
    def handle_output(self, context, obj):
        """Save DataFrame to MySQL"""
        asset_key = context.asset_key.path[-1]
        
        # Save to MySQL
        obj.to_sql(f"cache_{asset_key}", self.engine, if_exists='replace')
        
        # Also cache in memory for this run
        self._cache[asset_key] = obj
        
        context.log.info(f"💾 Saved {asset_key} to MySQL and memory cache")
    
    def load_input(self, context):
        """Load from cache or MySQL"""
        asset_key = context.asset_key.path[-1]
        
        # Try memory cache first (fastest)
        if asset_key in self._cache:
            context.log.info(f"⚡ Loading {asset_key} from memory cache")
            return self._cache[asset_key]
        
        # Load from MySQL (slower, but persistent)
        context.log.info(f"📖 Loading {asset_key} from MySQL cache")
        df = pd.read_sql_table(f"cache_{asset_key}", self.engine)
        
        # Cache in memory for future uses in this run
        self._cache[asset_key] = df
        
        return df

@io_manager
def smart_mysql_io_manager(init_context):
    return SmartMySQLIOManager(
        init_context.resource_config["connection_string"]
    )

# Use it in your definitions
from dagster import Definitions

defs = Definitions(
    assets=[...],
    resources={
        "io_manager": smart_mysql_io_manager.configured({
            "connection_string": "mysql://user:pass@host/db"
        })
    }
)
```

## Forcing a Refresh

Sometimes you want to re-query MySQL:

### Method 1: Re-materialize the source
```
In UI: Click mysql_orders → "Materialize"
This queries MySQL again and updates cache
```

### Method 2: Partitioned Assets
```python
from dagster import asset, DailyPartitionsDefinition

daily = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(partitions_def=daily)
def mysql_orders(context):
    """Each partition is cached separately"""
    date = context.partition_key
    query = f"SELECT * FROM orders WHERE date = '{date}'"
    return pd.read_sql(query, engine)

# Partition 2024-01-01 and 2024-01-02 have separate caches!
```

### Method 3: Freshness Policies
```python
from dagster import asset, FreshnessPolicy
from datetime import timedelta

@asset(
    freshness_policy=FreshnessPolicy(
        maximum_lag_minutes=60  # Re-materialize if older than 1 hour
    )
)
def mysql_orders(context):
    """Dagster auto-refreshes if cache is stale"""
    return pd.read_sql("SELECT * FROM orders", engine)
```

## Complete Example

```python
# sources.py
@asset(
    group_name="sources",
    description="Orders from MySQL - cached after first load"
)
def mysql_orders(context):
    context.log.info("🔵 QUERYING MySQL...")
    
    # This query runs ONCE per materialization
    df = pd.read_sql("""
        SELECT * FROM orders 
        WHERE order_date >= CURRENT_DATE - INTERVAL 30 DAY
    """, engine)
    
    context.log.info(f"✅ Loaded {len(df)} orders from MySQL")
    return df  # Dagster saves this to cache


# transforms.py
@asset(group_name="transforms")
def completed_orders(context, mysql_orders):
    context.log.info("🟢 Loading from cache (no MySQL query)")
    return mysql_orders[mysql_orders['status'] == 'completed']

@asset(group_name="transforms")
def pending_orders(context, mysql_orders):
    context.log.info("🟢 Loading from cache (no MySQL query)")
    return mysql_orders[mysql_orders['status'] == 'pending']

@asset(group_name="analytics")
def order_stats(context, mysql_orders):
    context.log.info("🟢 Loading from cache (no MySQL query)")
    return {
        'total': len(mysql_orders),
        'revenue': mysql_orders['amount'].sum()
    }
```

**Result:**
- MySQL queried 1 time
- Cache loaded 3 times
- MySQL load reduced by 66%!

## Key Takeaway 🎯

**Dagster is smart about caching!**

1. Source asset queries MySQL **ONCE**
2. Result is **automatically cached**
3. Downstream assets load from **cache**
4. **No duplicate MySQL queries** ✅
5. **Huge resource savings** ✅

This is one of the main reasons Dagster is so efficient for data pipelines - intelligent caching and dependency management built-in!

Your MySQL database will NOT be hit multiple times for the same data during a single run. 🚀
