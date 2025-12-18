#!/usr/bin/env python3
"""
Comprehensive test suite for the RRG Dashboard
Tests all components: data loading, calculation, and plotting
"""

import sys
import traceback

def test_imports():
    """Test that all required modules can be imported"""
    print("=" * 60)
    print("TEST 1: Module Imports")
    print("=" * 60)
    try:
        import plotly.graph_objects as go
        import numpy as np
        import pandas as pd
        from backend.data import load_price_data, SECTOR_TICKERS
        from backend.rrg import calculate_rrg
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_data_loading():
    """Test data loading functionality"""
    print("\n" + "=" * 60)
    print("TEST 2: Data Loading")
    print("=" * 60)
    try:
        from backend.data import load_price_data, SECTOR_TICKERS
        
        test_sectors = {
            "IT": SECTOR_TICKERS["IT"],
            "Bank": SECTOR_TICKERS["Bank"],
        }
        
        price_data = load_price_data(
            sectors=test_sectors,
            benchmark="^NSEI",
            period="1mo"
        )
        
        # Validate structure
        assert "^NSEI" in price_data, "Benchmark missing"
        assert "IT" in price_data, "IT sector missing"
        assert "Bank" in price_data, "Bank sector missing"
        
        # Validate data
        for key, df in price_data.items():
            assert not df.empty, f"{key} data is empty"
            assert "Close" in df.columns, f"{key} missing Close column"
        
        print(f"✅ Data loaded successfully for {len(price_data)} items")
        return True
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        traceback.print_exc()
        return False

def test_rrg_calculation():
    """Test RRG calculation"""
    print("\n" + "=" * 60)
    print("TEST 3: RRG Calculation")
    print("=" * 60)
    try:
        from backend.data import load_price_data, SECTOR_TICKERS
        from backend.rrg import calculate_rrg
        
        test_sectors = {
            "IT": SECTOR_TICKERS["IT"],
            "Bank": SECTOR_TICKERS["Bank"],
        }
        
        price_data = load_price_data(
            sectors=test_sectors,
            benchmark="^NSEI",
            period="1mo"
        )
        
        rrg_metrics = calculate_rrg(
            data=price_data,
            rs_period=10,
            roc_period=12,
            tail_length=5
        )
        
        # Validate structure
        assert "sector" in rrg_metrics.columns, "Missing sector column"
        assert "rs_ratio" in rrg_metrics.columns, "Missing rs_ratio column"
        assert "rs_momentum" in rrg_metrics.columns, "Missing rs_momentum column"
        
        # Validate data
        assert not rrg_metrics.empty, "RRG metrics is empty"
        assert len(rrg_metrics) > 0, "No RRG data generated"
        
        print(f"✅ RRG calculation successful")
        print(f"   Shape: {rrg_metrics.shape}")
        print(f"   Sectors: {rrg_metrics['sector'].unique().tolist()}")
        return True
    except Exception as e:
        print(f"❌ RRG calculation failed: {e}")
        traceback.print_exc()
        return False

def test_plotting():
    """Test plot generation"""
    print("\n" + "=" * 60)
    print("TEST 4: Plot Generation")
    print("=" * 60)
    try:
        import plotly.graph_objects as go
        import numpy as np
        from backend.data import load_price_data, SECTOR_TICKERS
        from backend.rrg import calculate_rrg
        
        # Load and calculate
        test_sectors = {
            "IT": SECTOR_TICKERS["IT"],
            "Bank": SECTOR_TICKERS["Bank"],
        }
        
        price_data = load_price_data(
            sectors=test_sectors,
            benchmark="^NSEI",
            period="1mo"
        )
        
        rrg_metrics = calculate_rrg(
            data=price_data,
            rs_period=10,
            roc_period=12,
            tail_length=5
        )
        
        # Create a simple plot
        fig = go.Figure()
        
        # Test that we can add traces
        for sector in rrg_metrics["sector"].unique():
            df = rrg_metrics[rrg_metrics["sector"] == sector]
            fig.add_trace(go.Scatter(
                x=df["rs_ratio"],
                y=df["rs_momentum"],
                mode="markers",
                name=sector
            ))
        
        # Validate figure
        assert len(fig.data) > 0, "No traces added to figure"
        
        print(f"✅ Plot generation successful")
        print(f"   Number of traces: {len(fig.data)}")
        return True
    except Exception as e:
        print(f"❌ Plot generation failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "🧪 COMPREHENSIVE RRG DASHBOARD TEST SUITE 🧪\n")
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Data Loading", test_data_loading()))
    results.append(("RRG Calculation", test_rrg_calculation()))
    results.append(("Plot Generation", test_plotting()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Your RRG Dashboard is ready to use!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

