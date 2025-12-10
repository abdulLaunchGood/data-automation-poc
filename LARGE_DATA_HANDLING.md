# Handling Large MySQL Tables in Dagster

## The Challenge 🤔

**YES, you can process MySQL tables in Dagster!** But for large tables, loading everything into a DataFrame can exhaust memory.

```python
# ❌ BAD for large tables
@asset
def all_orders(context):
    df = pd.read_sql("SELECT * FROM orders", conn)  # 100M rows = 💥 OOM
    return df
```

## Solutions for Large Data 🚀

### 1. **Chunking/Batching** (Best for Most Cases)

Process data in manageable chunks:

```python
from dagster import asset, AssetExecutionContext
import pandas as pd
from sqlalchemy import create_engine

@asset(
    group_name="sources",
    description="Orders data processed in chunks"
)
def orders_chunked(context: AssetExecutionContext):
    """
    Process large table in chunks to avoid memory issues.
    """
    engine = create_engine("mysql://user:pass@host/db")
    
    chunk_size = 10000  # Process 10k rows at a time
    offset = 0
    results = []
    
    while True:
        query = f"""
        SELECT * FROM orders 
        LIMIT {chunk_size} OFFSET {offset}
        """
        
        chunk = pd.read_sql(query, engine)
        
        if len(chunk) == 0:
            break
            
        # Process chunk
        processed = transform_chunk(chunk)
        results.append(processed)
        
        context.log.info(f"Processed {offset + len(chunk)} rows")
        offset += chunk_size
    
    # Combine results
    return pd.concat(results, ignore_index=True)


def transform_chunk(df):
    """Transform individual chunk"""
    # Your transformation logic
    return df[df['status'] == 'completed']
```

### 2. **SQL Pushdown** (Most Efficient!)

Do transformations in the database, load only results:

```python
@asset(
    group_name="sources",
    description="Aggregated orders - computed in database"
)
def orders_summary(context: AssetExecutionContext):
    """
    Let MySQL do the heavy lifting!
    Only load aggregated results.
    """
    engine = create_engine("mysql://user:pass@host/db")
    
    # Complex aggregation done in MySQL
    query = """
    SELECT 
        DATE(order_date) as date,
        status,
        COUNT(*) as order_count,
        SUM(total_amount) as total_revenue,
        AVG(total_amount) as avg_order_value
    FROM orders
    WHERE order_date >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    GROUP BY DATE(order_date), status
    ORDER BY date DESC
    """
    
    # Only load summary - much smaller!
    df = pd.read_sql(query, engine)
    context.log.info(f"Loaded {len(df)} summary rows instead of millions")
    
    return df
```

### 3. **Iterator/Generator Pattern**

Stream data without loading all into memory:

```python
from typing import Iterator
import sqlalchemy as sa

@asset(
    group_name="sources",
    description="Stream large table data"
)
def orders_stream(context: AssetExecutionContext):
    """
    Use iterator to process data without loading all into memory.
    """
    engine = create_engine("mysql://user:pass@host/db")
    
    def row_generator() -> Iterator[dict]:
        """Generator that yields rows one at a time"""
        with engine.connect() as conn:
            result = conn.execute(sa.text("SELECT * FROM orders"))
            
            for row in result:
                yield dict(row._mapping)
    
    # Process row by row
    processed_count = 0
    valid_orders = []
    
    for row in row_generator():
        # Process individual row
        if row['status'] == 'completed' and row['total_amount'] > 100:
            valid_orders.append({
                'order_id': row['id'],
                'amount': row['total_amount'],
                'date': row['order_date']
            })
        
        processed_count += 1
        if processed_count % 10000 == 0:
            context.log.info(f"Processed {processed_count} rows")
    
    return pd.DataFrame(valid_orders)
```

### 4. **Dagster Partitioning** (For Time-Series Data)

Partition large tables by date, process independently:

```python
from dagster import asset, DailyPartitionsDefinition
from datetime import datetime

# Define daily partitions
daily_partitions = DailyPartitionsDefinition(start_date="2023-01-01")

@asset(
    partitions_def=daily_partitions,
    group_name="sources",
    description="Orders partitioned by date"
)
def orders_by_date(context: AssetExecutionContext):
    """
    Process one day at a time.
    Dagster handles scheduling and tracking.
    """
    partition_date = context.partition_key
    
    engine = create_engine("mysql://user:pass@host/db")
    
    query = f"""
    SELECT * FROM orders
    WHERE DATE(order_date) = '{partition_date}'
    """
    
    df = pd.read_sql(query, engine)
    context.log.info(f"Loaded {len(df)} orders for {partition_date}")
    
    return df

# Materialize one partition at a time
# or backfill historical data gradually
```

### 5. **Write to File System (For Very Large Data)**

Instead of returning DataFrame, save to disk:

```python
@asset(
    group_name="sources",
    description="Orders saved to parquet files"
)
def orders_parquet(context: AssetExecutionContext) -> str:
    """
    Save large data to efficient file format.
    Return path, not data.
    """
    engine = create_engine("mysql://user:pass@host/db")
    output_path = f"data/orders_{datetime.now():%Y%m%d}.parquet"
    
    # Read in chunks and write to parquet
    chunk_iter = pd.read_sql(
        "SELECT * FROM orders",
        engine,
        chunksize=50000
    )
    
    for i, chunk in enumerate(chunk_iter):
        mode = 'w' if i == 0 else 'a'
        chunk.to_parquet(output_path, engine='fastparquet', append=mode=='a')
        context.log.info(f"Wrote chunk {i+1}")
    
    # Return path, not data!
    return output_path


@asset(
    group_name="transforms",
    description="Process parquet file in chunks"
)
def orders_analysis(context: AssetExecutionContext, orders_parquet: str):
    """
    Read from parquet file in chunks.
    """
    # Process file in chunks
    result = []
    for chunk in pd.read_parquet(orders_parquet, chunksize=10000):
        processed = analyze_chunk(chunk)
        result.append(processed)
    
    return pd.concat(result)
```

### 6. **Using Dask or Polars** (For Parallel Processing)

Use libraries designed for large datasets:

```python
import dask.dataframe as dd
import polars as pl

@asset(
    group_name="sources",
    description="Orders using Dask for parallel processing"
)
def orders_dask(context: AssetExecutionContext):
    """
    Use Dask for out-of-core computation.
    """
    # Read in parallel chunks
    ddf = dd.read_sql_table(
        'orders',
        'mysql://user:pass@host/db',
        index_col='id',
        npartitions=10  # Split into 10 partitions
    )
    
    # Lazy computation - doesn't load until compute()
    filtered = ddf[ddf['status'] == 'completed']
    aggregated = filtered.groupby('customer_id').agg({
        'total_amount': 'sum',
        'id': 'count'
    })
    
    # Compute result (still chunked processing)
    result = aggregated.compute()
    
    return result


@asset(
    group_name="sources",
    description="Orders using Polars for speed"
)
def orders_polars(context: AssetExecutionContext):
    """
    Use Polars - much faster than Pandas!
    """
    import connectorx as cx
    
    # ConnectorX + Polars = Very fast MySQL reads
    query = "SELECT * FROM orders WHERE order_date >= '2024-01-01'"
    df = pl.read_database(
        query,
        connection_uri="mysql://user:pass@host/db"
    )
    
    # Polars operations are much faster
    result = (df
        .filter(pl.col('status') == 'completed')
        .group_by('customer_id')
        .agg([
            pl.col('total_amount').sum().alias('total_spent'),
            pl.col('id').count().alias('order_count')
        ])
    )
    
    # Convert to pandas if needed
    return result.to_pandas()
```

### 7. **Custom I/O Manager**

Create custom I/O manager for MySQL:

```python
from dagster import IOManager, io_manager
from sqlalchemy import create_engine

class MySQLIOManager(IOManager):
    """
    Custom I/O manager for MySQL tables.
    Avoids loading into memory.
    """
    
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
    
    def handle_output(self, context, obj):
        """Save DataFrame to MySQL"""
        table_name = context.asset_key.path[-1]
        obj.to_sql(table_name, self.engine, if_exists='replace')
    
    def load_input(self, context):
        """Load from MySQL in chunks"""
        table_name = context.asset_key.path[-1]
        # Return iterator instead of full DataFrame
        return pd.read_sql_table(
            table_name, 
            self.engine,
            chunksize=10000
        )

@io_manager
def mysql_io_manager(init_context):
    return MySQLIOManager(
        init_context.resource_config["connection_string"]
    )
```

## Best Practices 📋

### Choose Based on Use Case:

| Scenario | Best Solution | Why |
|----------|---------------|-----|
| **Aggregations** | SQL Pushdown | Let database do the work |
| **Time-series data** | Partitioning | Process incrementally |
| **Simple filtering** | Chunking | Easy to implement |
| **Complex transforms** | Dask/Polars | Parallel processing |
| **Very large (TB+)** | File-based | Don't load into memory |

### Memory Management Tips:

```python
# ✅ Good practices
@asset
def efficient_processing(context):
    # 1. Select only needed columns
    query = "SELECT id, amount, date FROM orders"  # Not SELECT *
    
    # 2. Filter in database
    query += " WHERE date >= '2024-01-01'"
    
    # 3. Use appropriate dtypes
    df = pd.read_sql(query, engine, dtype={
        'id': 'int32',      # Not int64 if possible
        'amount': 'float32'  # Not float64 if possible
    })
    
    # 4. Delete intermediate results
    processed = transform(df)
    del df  # Free memory
    
    return processed
```

## Example: Complete Pipeline

```python
# sources.py
@asset(group_name="sources")
def mysql_orders_summary(context):
    """Aggregate in database - returns small result"""
    query = """
    SELECT 
        customer_id,
        COUNT(*) as order_count,
        SUM(total_amount) as lifetime_value
    FROM orders
    GROUP BY customer_id
    """
    return pd.read_sql(query, engine)  # Small result!

# transforms.py
@asset(group_name="transforms")
def customer_segments(context, mysql_orders_summary):
    """Process small aggregated data"""
    df = mysql_orders_summary
    
    # Categorize customers
    df['segment'] = pd.cut(
        df['lifetime_value'],
        bins=[0, 100, 500, float('inf')],
        labels=['Bronze', 'Silver', 'Gold']
    )
    
    return df

# exports.py
@asset(group_name="exports")
def customer_segments_csv(context, customer_segments):
    """Export manageable dataset"""
    customer_segments.to_csv('output/segments.csv')
    return 'output/segments.csv'
```

## Key Takeaway 🎯

**Don't load entire tables into memory!**

1. **Aggregate in database** (SQL pushdown)
2. **Process in chunks** (batch processing)
3. **Use partitioning** (incremental processing)
4. **Stream data** (generators)
5. **Use efficient tools** (Dask, Polars)

Dagster supports all these patterns - choose what fits your data size and use case!
