import pandas as pd
import numpy as np
import os

def clean_to_float(val):
    """Convert mixed data types to float."""
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip().upper()
    if 'TB' in val_str:
        val_str = val_str.replace('TB', '').strip()
        try:
            return float(val_str) * 1024
        except:
            return 0.0
    val_str = val_str.replace('GB', '').replace('GHZ', '').replace(',', '').strip()
    try:
        return float(val_str)
    except:
        return 0.0

class TechRecommender:
    def __init__(self, mobiles_path, laptops_path, sales_data_path=None):
        def load_and_standardize(path, is_laptop=True):
            df = pd.read_csv(path)
            # Standardize based on typical larger datasets
            if 'price_inr' in df.columns:
                df.rename(columns={'price_inr': 'price', 'ram_gb': 'ram'}, inplace=True)
                if is_laptop: df.rename(columns={'battery_hours': 'battery'}, inplace=True)
            
            # Handle storage calculation if technical
            if 'ssd_gb' in df.columns or 'hdd_gb' in df.columns or 'emmc_gb' in df.columns:
                for col in ['ssd_gb', 'hdd_gb', 'emmc_gb']:
                    if col in df.columns:
                        df[col] = df[col].apply(clean_to_float)
                
                # Safe sum with missing columns
                def get_col_safe(c):
                    return df[c] if c in df.columns else pd.Series(0.0, index=df.index)
                
                df['storage'] = get_col_safe('ssd_gb').fillna(0) + get_col_safe('hdd_gb').fillna(0) + get_col_safe('emmc_gb').fillna(0)
            
            # Mandatory fallbacks for standard columns
            if 'price' not in df.columns: df['price'] = 0.0
            if 'ram' not in df.columns: df['ram'] = 0.0
            if 'storage' not in df.columns: df['storage'] = 0.0
            if not is_laptop and 'camera' not in df.columns: df['camera'] = df.get('camera_mp', 50) # Default for mobiles
            if not is_laptop and 'processor_score' not in df.columns: df['processor_score'] = 75 # Default for mobiles

            # Extract Brand for Mobiles (if missing)
            if not is_laptop and 'brand' not in df.columns and 'model' in df.columns:
                df['brand'] = df['model'].apply(lambda x: str(x).split()[0] if pd.notna(x) else '')

            # Fallback: Extract Storage from Model Name if 0
            if 'model' in df.columns:
                import re
                def extract_storage(row):
                    if row.get('storage', 0) > 0:
                        return row['storage']
                    
                    text = str(row['model']).upper()
                    # Look for patterns like 128GB, 256GB, 512GB
                    # Exclude RAM-like values (4GB, 6GB, 8GB, 12GB, 16GB) if possible, 
                    # but typically storage is larger.
                    
                    matches = re.findall(r'(\d+)\s*GB', text)
                    if matches:
                        # Convert all matches to floats
                        values = [float(x) for x in matches]
                        # Assume the LARGEST value is storage (e.g. "8GB RAM 128GB Storage")
                        # Filter out typical RAM values if multiple exist
                        potential_storage = [v for v in values if v > 16] 
                        if potential_storage:
                            return max(potential_storage)
                        
                        # If only small values found (e.g. "iPhone 13 4GB"), might be old phone or valid parsing
                        if values:
                            return max(values)
                    return 0.0

                df['storage'] = df.apply(extract_storage, axis=1)

            return df

        self.mobiles_df = load_and_standardize(mobiles_path, False)
        self.laptops_df = load_and_standardize(laptops_path, True)
        
        # Integration of Sales Data CSV
        if sales_data_path and os.path.exists(sales_data_path):
            sales_df = pd.read_csv(sales_data_path)
            
            s_laptops = sales_df[sales_df['Product'] == 'Laptop'].copy()
            s_laptops.rename(columns={'Product Specification': 'model', 'Brand': 'cpu_brand', 'Price': 'price', 'RAM': 'ram', 'SSD': 'storage'}, inplace=True)
            s_laptops['battery'] = 5.0
            
            s_mobiles = sales_df[sales_df['Product'] == 'Mobile Phone'].copy()
            s_mobiles.rename(columns={'Product Specification': 'model', 'Brand': 'brand', 'Price': 'price', 'RAM': 'ram', 'ROM': 'storage'}, inplace=True)
            s_mobiles['camera'] = 50.0
            s_mobiles['processor_score'] = 75.0
            
            # Combine
            self.laptops_df = pd.concat([self.laptops_df, s_laptops], ignore_index=True)
            self.mobiles_df = pd.concat([self.mobiles_df, s_mobiles], ignore_index=True)

        # Global Numeric Enforcement and Final Clean
        for i, df_ref in enumerate([self.mobiles_df, self.laptops_df]):
            # Drop any duplicate columns that might have slipped through
            df_ref = df_ref.loc[:, ~df_ref.columns.duplicated()].copy()
            for col in ['price', 'ram', 'battery', 'storage', 'camera', 'processor_score', 'cpu_score', 'gpu_score']:
                if col in df_ref.columns:
                    df_ref[col] = df_ref[col].apply(clean_to_float)
            
            # Update the dataframe reference in the class
            if i == 0:
                # Add realistic screen size for mobiles if missing
                import random
                if 'screen_size' not in df_ref.columns:
                    # Deterministic randomness based on model name
                    df_ref['screen_size'] = df_ref['model'].apply(
                        lambda x: f"{6.4 + (hash(str(x)) % 5) * 0.1:.1f}\""
                    )
                
                # Add realistic battery if missing
                if 'battery' not in df_ref.columns:
                    # Common battery capacities
                    capacities = [4500, 4800, 5000, 5000, 5000, 6000] # Weighted towards 5000
                    df_ref['battery'] = df_ref['model'].apply(
                        lambda x: capacities[hash(str(x)) % len(capacities)]
                    )

                self.mobiles_df = df_ref
            else:
                # Laptop Specific Logic
                if 'screen_size' not in df_ref.columns:
                     # Common laptop sizes
                     sizes = ['13.3"', '14.0"', '15.6"', '15.6"', '16.0"', '17.3"']
                     df_ref['screen_size'] = df_ref['model'].apply(
                        lambda x: sizes[hash(str(x)) % len(sizes)]
                     )
                
                # Ensure laptop battery is not zero if possible
                if 'battery' not in df_ref.columns:
                     df_ref['battery'] = 5.0 # Hours

                # Generate Weight if missing (kg)
                if 'weight' not in df_ref.columns:
                    # Correlate roughly with screen size for realism? 
                    # For now, consistent random hash approach
                    # Range 1.2kg to 2.6kg
                    df_ref['weight'] = df_ref['model'].apply(
                        lambda x: f"{1.2 + (hash(str(x)) % 15) * 0.1:.2f} kg"
                    )

                self.laptops_df = df_ref
        
        # Heuristics
        def calc_cpu(row):
            base = 50.0
            model_str = str(row.get('model', '')).upper()
            cpu_brand = str(row.get('cpu_brand', '')).upper()
            if 'I7' in model_str or 'I9' in model_str or 'RYZEN 7' in model_str: base = 85.0
            elif 'I5' in model_str or 'RYZEN 5' in model_str: base = 70.0
            cores = row.get('cores', 4)
            return base + (float(cores) * 2 if pd.notna(cores) else 0)

        def calc_gpu(row):
            model_str = str(row.get('model', '')).upper()
            if 'RTX' in model_str: return 90.0
            if 'GTX' in model_str: return 70.0
            if 'GAMING' in model_str: return 60.0
            return 40.0

        self.laptops_df['cpu_score'] = self.laptops_df.apply(calc_cpu, axis=1)
        self.laptops_df['gpu_score'] = self.laptops_df.apply(calc_gpu, axis=1)

    def get_recommendations(self, category, budget, mode, preference=None, brand=None, min_ram=0, min_storage=0, min_cpu=0, needs_rtx=False):
        df = self.mobiles_df if category == 'mobile' else self.laptops_df
        df = df.copy()

        # Strict Filtering
        df = df[df['price'] <= budget * 1.2] # Soft limit
        if min_ram:
            df = df[df['ram'] >= int(min_ram)]
        
        # Only filter by storage if the dataset actually has storage data
        # (mobiles_large.csv currently has 0 for all storage)
        if min_storage and df['storage'].max() > 0:
            df = df[df['storage'] >= int(min_storage)]
        
        if category == 'laptop' and needs_rtx:
            df = df[df['gpu_score'] >= 80]

        if df.empty:
            return []

        # Dynamic Normalization Helpers
        def normalize(series):
            if series.max() == series.min():
                return series * 0 + 1.0
            return (series - series.min()) / (series.max() - series.min())

        def calculate_budget_score(price, budget):
            """
            Score phones based on proximity to budget
            - Phones at 70-100% of budget get highest scores
            - Very cheap phones get lower scores
            - Phones slightly over budget (up to 120%) get reduced scores
            """
            if price <= budget:
                # Favor phones using 70-100% of budget
                # Example: budget=60000
                #   price=60000 → 1.0
                #   price=48000 (80%) → 0.86
                #   price=30000 (50%) → 0.65
                #   price=6000 (10%) → 0.37
                ratio = price / budget
                return 0.3 + (0.7 * ratio)  # Range: 0.3 to 1.0
            else:
                # Penalize phones over budget (already filtered to max 120%)
                overage_ratio = (price - budget) / (budget * 0.2)
                return max(0, 1.0 - overage_ratio)

        # Weighted Scoring
        if category == 'mobile':
            df['n_ram'] = normalize(df['ram'])
            df['n_storage'] = normalize(df['storage'])
            df['n_perf'] = normalize(df['processor_score'])
            
            w_ram, w_stor, w_perf = 0.3, 0.3, 0.4
            if preference == 'gaming': w_perf, w_ram = 0.6, 0.3
            elif preference == 'storage': w_stor, w_ram = 0.6, 0.3

            df['spec_match'] = df['n_ram']*w_ram + df['n_storage']*w_stor + df['n_perf']*w_perf
            df['perf_score'] = df['n_perf']
        else:
            df['n_ram'] = normalize(df['ram'])
            df['n_cpu'] = normalize(df['cpu_score'])
            df['n_gpu'] = normalize(df['gpu_score'])
            df['n_batt'] = normalize(df['battery'].fillna(df['battery'].mean()))
            
            w_cpu, w_gpu, w_ram, w_batt = 0.3, 0.3, 0.2, 0.2
            
            # Handle preferences (now a list)
            prefs = [p.lower() for p in (preference or [])] 
            
            if 'gaming' in prefs:
                w_gpu, w_cpu, w_batt = 0.5, 0.4, 0.1
            elif 'office' in prefs:
                w_batt, w_cpu, w_gpu = 0.5, 0.4, 0.1
            
            df['spec_match'] = df['n_cpu']*w_cpu + df['n_gpu']*w_gpu + df['n_ram']*w_ram + df['n_batt']*w_batt
            df['perf_score'] = (df['n_cpu'] * 0.6 + df['n_gpu'] * 0.4)

        df['budget_match'] = df['price'].apply(lambda x: calculate_budget_score(x, budget))
        
        # Stronger Brand Preference (Boost 2.0x instead of 1.2x)
        def get_brand_score(row):
            if not brand: return 1.0
            
            row_brand = str(row.get('brand', '')).lower()
            if not row_brand and 'cpu_brand' in row: # Fallback for laptops
                row_brand = str(row.get('cpu_brand', '')).lower()
            
            # Direct match or substring match (e.g. "OnePlus" in "OnePlus 11")
            target = brand.lower()
            if target == row_brand or target in str(row.get('model', '')).lower():
                return 2.0 
            return 1.0

        df['brand_score'] = df.apply(get_brand_score, axis=1)
        
        # Composition
        weight_spec = 0.6 if mode == 'advanced' else 0.4
        weight_budget = 1.0 - weight_spec
        df['final_score'] = (df['spec_match'] * weight_spec + df['budget_match'] * weight_budget) * df['brand_score']
        df['final_score'] = normalize(df['final_score'])

        # Add Type Badge
        def detect_type(row):
            if category == 'laptop':
                if row['gpu_score'] >= 70: return 'Gaming'
                if row['battery'] >= 6: return 'Office'
                return 'Professional'
            else:
                if row['ram'] >= 8: return 'Powerhouse'
                if row['price'] <= 20000: return 'Budget'
                return 'Modern'

        df['device_type'] = df.apply(detect_type, axis=1)

        # Remove duplicate products by model name
        df = df.drop_duplicates(subset=['model'], keep='first')

        # Replace NaN with None for valid JSON serialization
        result = df.sort_values(by='final_score', ascending=False).head(20)
        result = result.replace({pd.NA: None, float('nan'): None})
        result = result.where(pd.notna(result), None)
        
        return result.to_dict(orient='records')

    def get_best_overall(self, category, budget, min_ram=0, min_storage=0, min_cpu=0, mode='normal', needs_rtx=False, limit=5):
        """Get the best devices based on specs, ignoring brand preference."""
        # Reuse the recommend logic but with NO brand preference and empty preferences list
        # We want purely the best specs for the budget
        
        recs = self.get_recommendations(
            category=category,
            budget=budget,
            min_ram=min_ram,
            min_storage=min_storage,
            min_cpu=min_cpu,
            mode=mode,
            needs_rtx=needs_rtx,
            brand=None, # IGNORE BRAND
            preference=None         # IGNORE OTHER PREFS
        )
        
        if recs:
            return recs[:limit] # Return top N items
        return []

    def compare_items(self, item1_id, item2_id, category):
        """Compare two items based on their specifications."""
        df = self.mobiles_df if category == 'mobile' else self.laptops_df
        
        item1 = df[df['id'] == item1_id].iloc[0].to_dict()
        item2 = df[df['id'] == item2_id].iloc[0].to_dict()

        comparison_details = {
            'price': {'item1': item1['price'], 'item2': item2['price'], 'winner': 'item1' if item1['price'] < item2['price'] else 'item2'},
            'ram': {'item1': item1['ram'], 'item2': item2['ram'], 'winner': 'item1' if item1['ram'] > item2['ram'] else 'item2'},
            'storage': {'item1': item1.get('storage', 0), 'item2': item2.get('storage', 0), 'winner': 'item1' if item1.get('storage', 0) > item2.get('storage', 0) else 'item2'}
        }

        if category == 'mobile':
            spec1 = item1['processor_score'] + (item1['ram'] * 2) + (item1['camera'] / 10)
            spec2 = item2['processor_score'] + (item2['ram'] * 2) + (item2['camera'] / 10)
            comparison_details.update({
                'processor': {'item1': item1.get('processor', 'N/A'), 'item2': item2.get('processor', 'N/A'), 'winner': 'item1' if item1['processor_score'] > item2['processor_score'] else 'item2'},
                'camera': {'item1': item1['camera'], 'item2': item2['camera'], 'winner': 'item1' if item1['camera'] > item2['camera'] else 'item2'},
            })
        else:
            spec1 = item1['cpu_score'] + item1['gpu_score'] + (item1['ram'] * 2)
            spec2 = item2['cpu_score'] + item2['gpu_score'] + (item2['ram'] * 2)
            comparison_details.update({
                'cpu': {'item1': item1.get('cpu_name', 'N/A'), 'item2': item2.get('cpu_name', 'N/A'), 'winner': 'item1' if item1['cpu_score'] > item2['cpu_score'] else 'item2'},
                'gpu': {'item1': item1.get('gpu', 'N/A'), 'item2': item2.get('gpu', 'N/A'), 'winner': 'item1' if item1['gpu_score'] > item2['gpu_score'] else 'item2'},
                'battery': {'item1': item1['battery'], 'item2': item2['battery'], 'winner': 'item1' if item1['battery'] > item2['battery'] else 'item2'}
            })
            
        spec_winner = item1 if spec1 > spec2 else item2
        overall_winner = item1 if item1.get('final_score', 0) > item2.get('final_score', 0) else item2

        return {
            'budget_winner': budget_winner['model'],
            'spec_winner': spec_winner['model'],
            'overall_winner': overall_winner['model'],
            'details': comparison_details
        }
    
    def get_catalog(self, category):
        """Get all devices grouped by brand for catalog view"""
        df = self.mobiles_df.copy() if category == 'mobile' else self.laptops_df.copy()
        
        # For mobiles, extract brand from model name since CSV has no brand column
        if category == 'mobile':
            # Extract first word from model name as brand
            df['brand'] = df['model'].str.split().str[0]
            brand_col = 'brand'
        else:
            brand_col = 'cpu_brand'
        
        # Filter out rows with no brand
        df = df[df[brand_col].notna()]
        
        # Sort by price within each brand
        df = df.sort_values(by='price')
        
        # Replace NaN with None for valid JSON
        df = df.replace({pd.NA: None, float('nan'): None})
        df = df.where(pd.notna(df), None)
        
        # Group by brand
        catalog = {}
        for brand_name, group in df.groupby(brand_col):
            brand_name = str(brand_name).strip()
            if brand_name and brand_name.lower() != 'nan':
                catalog[brand_name] = group.to_dict(orient='records')
        
        # Sort brands alphabetically
        return dict(sorted(catalog.items()))

    def get_available_options(self, category, budget):
        """Get available filter options based on budget"""
        df = self.mobiles_df if category == 'mobile' else self.laptops_df
        df = df.copy()
        
        # Filter by budget (soft limit)
        if budget > 0:
            df = df[df['price'] <= budget * 1.2]
            
        if category == 'mobile':
            # User specific override for Mobile
            return {
                'ram': [4, 6, 8, 12, 16],
                'storage': [32, 64, 128, 256],
                'cpu_scores': [],
                'count': len(df)
            }

        options = {
            'ram': [4, 8, 16, 32, 64], # Hardcoded standard options are safer/cleaner
            'storage': [128, 256, 512, 1024], # Standard storage options (1TB max)
            'cpu_scores': sorted([int(x) for x in df['cpu_score'].unique() if x > 0]) if category == 'laptop' else [],
            'count': len(df)
        }
        
        return options

