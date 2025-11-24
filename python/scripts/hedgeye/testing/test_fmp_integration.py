#!/usr/bin/env python3
"""
Test script for FMP price integration and enhanced plotting.
"""

import sys
sys.path.append('/Users/rk/gh/randykerber/hedgeye-kb/src')

import pandas as pd
from datetime import datetime, timedelta
import os

def test_fmp_price_fetcher():
    """Test basic FMP price fetching functionality."""
    print("=== Testing FMP Price Fetcher ===")
    
    try:
        from hedgeye.ds.fmp.price_fetcher import get_latest_price, get_historical_price
        
        # Test cases with different entity types
        test_cases = [
            ('AAPL', 'stocks', 'Apple stock'),
            ('SPY', 'etfs', 'S&P 500 ETF'),
            ('^SPX', 'indexes', 'S&P 500 Index'),
        ]
        
        for symbol, etype, description in test_cases:
            print(f"\nTesting {description} ({symbol}):")
            
            # Test latest price
            try:
                latest = get_latest_price(symbol, etype)
                if latest:
                    print(f"  ✅ Latest price: ${latest['price']:.2f}")
                else:
                    print(f"  ❌ Could not fetch latest price")
            except Exception as e:
                print(f"  ❌ Latest price error: {e}")
            
            # Test historical price (yesterday)
            try:
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                historical = get_historical_price(symbol, etype, yesterday)
                if historical:
                    print(f"  ✅ {yesterday} price: ${historical['price']:.2f}")
                else:
                    print(f"  ❌ Could not fetch historical price")
            except Exception as e:
                print(f"  ❌ Historical price error: {e}")
                
    except ImportError as e:
        print(f"❌ Could not import FMP modules: {e}")
        return False
    except Exception as e:
        print(f"❌ FMP test failed: {e}")
        return False
    
    return True

def test_mapping_integration():
    """Test integration with symbol mappings."""
    print("\n=== Testing Symbol Mapping Integration ===")
    
    try:
        from hedgeye.ds.fmp.price_fetcher import get_prices_for_symbols
        
        # Load mappings
        fmp_path = os.path.expanduser("~/d/downloads/fmp/he_to_fmp.csv")
        if not os.path.exists(fmp_path):
            print(f"❌ Mapping file not found: {fmp_path}")
            return False
        
        mappings = pd.read_csv(fmp_path)
        print(f"✅ Loaded {len(mappings)} symbol mappings")
        
        # Test with a small subset
        test_mappings = mappings.head(5)
        print(f"\nTesting with {len(test_mappings)} symbols:")
        
        for _, row in test_mappings.iterrows():
            print(f"  {row['he_symbol']} -> {row['fmp_etype']}:{row['fmp_symbol']}")
        
        # Get prices for test symbols
        try:
            prices = get_prices_for_symbols(test_mappings, latest=True)
            print(f"\n✅ Successfully fetched {len(prices)} prices")
            
            if not prices.empty:
                print("\nSample results:")
                for _, row in prices.head(3).iterrows():
                    print(f"  {row['he_symbol']}: ${row['price']:.2f}")
            
        except Exception as e:
            print(f"❌ Failed to fetch prices: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Mapping integration test failed: {e}")
        return False
    
    return True

def test_enhanced_plotting():
    """Test enhanced plotting functionality."""
    print("\n=== Testing Enhanced Plotting ===")
    
    try:
        from hedgeye.ds.rr.enhanced_rr_plotting import display_rr_with_latest_price, load_symbol_mappings
        from hedgeye.ds.rr.use_rr import load_all_risk_range_data
        
        # Load data
        print("Loading Hedgeye risk range data...")
        he_data = load_all_risk_range_data()
        print(f"✅ Loaded {len(he_data)} risk range observations")
        
        print("Loading symbol mappings...")
        mappings = load_symbol_mappings()
        print(f"✅ Loaded {len(mappings)} symbol mappings")
        
        # Test with one symbol
        test_symbol = 'AAPL'  # Start with a common stock
        
        print(f"\nTesting enhanced plot for {test_symbol}...")
        
        # Check if symbol exists in data
        symbol_data = he_data[he_data['index'] == test_symbol]
        if symbol_data.empty:
            print(f"❌ No Hedgeye data found for {test_symbol}")
            # Try with another symbol
            available_symbols = he_data['index'].unique()[:5]
            print(f"Available symbols: {list(available_symbols)}")
            test_symbol = available_symbols[0]
            print(f"Testing with {test_symbol} instead...")
        
        # Create enhanced plot (without showing it)
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        
        fig = display_rr_with_latest_price(he_data, test_symbol)
        
        if fig:
            print(f"✅ Successfully created enhanced plot for {test_symbol}")
            
            # Save test plot
            test_output = f"/tmp/test_plot_{test_symbol.replace('/', '_')}.png"
            fig.savefig(test_output, dpi=100)
            print(f"✅ Test plot saved: {test_output}")
            
        else:
            print(f"❌ Failed to create plot for {test_symbol}")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import plotting modules: {e}")
        return False
    except Exception as e:
        print(f"❌ Enhanced plotting test failed: {e}")
        return False
    
    return True

def check_api_key():
    """Check if FMP API key is configured."""
    print("=== Checking API Key Configuration ===")
    
    # Check environment variable
    env_key = os.getenv('FMP_API_KEY')
    if env_key:
        print("✅ FMP_API_KEY environment variable found")
        return True
    
    # Check config file
    config_file = os.path.expanduser('~/.fmp_api_key')
    if os.path.exists(config_file):
        print("✅ ~/.fmp_api_key file found")
        return True
    
    print("❌ No FMP API key found!")
    print("To set up FMP API key:")
    print("  1. Get free API key from: https://financialmodelingprep.com/")
    print("  2. Set environment variable: export FMP_API_KEY='your_key_here'")
    print("  3. Or create file: echo 'your_key_here' > ~/.fmp_api_key")
    print("  4. Add to ~/.bashrc or ~/.zshrc for persistence")
    
    return False

def main():
    """Run all tests."""
    print("🧪 FMP Integration Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Key Configuration", check_api_key),
        ("FMP Price Fetcher", test_fmp_price_fetcher),
        ("Symbol Mapping Integration", test_mapping_integration),
        ("Enhanced Plotting", test_enhanced_plotting),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASS" if passed_test else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FMP integration is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        
        if not results.get("API Key Configuration", False):
            print("\n💡 Most failures are likely due to missing API key.")
            print("   Set up your FMP API key first, then re-run tests.")

if __name__ == "__main__":
    main()