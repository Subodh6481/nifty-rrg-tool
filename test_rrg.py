#!/usr/bin/env python3
"""
Quick test script to verify RRG calculation works
"""

from backend.data import load_price_data, SECTOR_TICKERS
from backend.rrg import calculate_rrg

# Test with a small subset
test_sectors = {
    "IT": SECTOR_TICKERS["IT"],
    "Bank": SECTOR_TICKERS["Bank"],
}

print("Loading price data...")
try:
    price_data = load_price_data(
        sectors=test_sectors,
        benchmark="^NSEI",
        period="3mo"
    )
    print(f"✓ Loaded data for: {list(price_data.keys())}")
    
    # Check data structure
    for key, df in price_data.items():
        print(f"  {key}: {len(df)} rows, columns: {df.columns.tolist()}")
    
except Exception as e:
    print(f"✗ Failed to load data: {e}")
    exit(1)

print("\nCalculating RRG metrics...")
try:
    rrg_metrics = calculate_rrg(
        data=price_data,
        rs_period=10,
        roc_period=12,
        tail_length=5
    )
    print(f"✓ RRG calculation successful!")
    print(f"  Shape: {rrg_metrics.shape}")
    print(f"  Columns: {rrg_metrics.columns.tolist()}")
    print(f"  Sectors: {rrg_metrics['sector'].unique().tolist()}")
    print("\nSample data:")
    print(rrg_metrics.head(10))
    
except Exception as e:
    print(f"✗ Failed to calculate RRG: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n✓ All tests passed!")

