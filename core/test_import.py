# core/test_import.py
try:
    from .data import get_price_data, get_pe_ratio
    print("Import successful!")
    print("Functions imported:", get_price_data, get_pe_ratio)
except ImportError as e:
    print(f"Import failed: {e}")