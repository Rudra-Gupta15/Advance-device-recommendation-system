import pandas as pd
import os

def inspect():
    base_path = os.path.join(os.getcwd(), 'versustech', 'backend')
    
    files = ['mobiles_large.csv', 'laptops_large.csv']
    
    for f in files:
        path = os.path.join(base_path, f)
        print(f"\n--- Inspecting {f} ---")
        try:
            df = pd.read_csv(path)
            print(f"Columns: {list(df.columns)}")
            
            # Check for storage related columns
            storage_cols = [c for c in df.columns if 'gb' in c.lower() or 'storage' in c.lower() or 'rom' in c.lower()]
            print(f"Storage variables: {storage_cols}")
            
            for col in storage_cols:
                vals = df[col].astype(str).unique()
                print(f"Unique values in {col} (first 20): {sorted(vals)[:20]}")
                
        except Exception as e:
            print(f"Error reading {f}: {e}")

if __name__ == "__main__":
    inspect()
