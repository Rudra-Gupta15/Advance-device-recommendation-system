import pandas as pd
import numpy as np

class TechRecommender:
    def __init__(self, mobiles_path, laptops_path):
        self.mobiles_df = pd.read_csv(mobiles_path)
        self.laptops_df = pd.read_csv(laptops_path)

    def get_recommendations(self, category, budget, mode, preference=None, brand=None, min_ram=0, min_storage=0, min_cpu=0, needs_rtx=False):
        df = self.mobiles_df if category == 'mobile' else self.laptops_df
        df = df.copy()

        # Strict Filtering
        if min_ram:
            df = df[df['ram'] >= int(min_ram)]
        if min_storage:
            df = df[df['storage'] >= int(min_storage)]
        
        if category == 'laptop':
            if min_cpu:
                df = df[df['cpu_score'] >= int(min_cpu)]
            if needs_rtx:
                df = df[df['gpu_score'] >= 80]
        else:
            if min_cpu:
                df = df[df['processor_score'] >= int(min_cpu)]

        if df.empty:
            return []

        # Dynamic Normalization Helpers
        def normalize(series):
            if series.max() == series.min():
                return series * 0 + 1.0
            return (series - series.min()) / (series.max() - series.min())

        # budget_match: 1.0 if well within budget, drops off if over
        def calculate_budget_score(price, budget):
            if price <= budget:
                # Reward items that are significantly cheaper but still "good"
                # This contributes to value-for-money
                return 1.0 
            elif price <= budget * 1.15: # Allow up to 15% stretch for better performance
                return 1.0 - ((price - budget) / (budget * 0.15))
            return 0

        # Feature Scoring with Priority Boost
        if category == 'mobile':
            # Base scores
            df['n_ram'] = normalize(df['ram'])
            df['n_storage'] = normalize(df['storage'])
            df['n_battery'] = normalize(df['battery'])
            df['n_camera'] = normalize(df['camera'])
            df['n_perf'] = normalize(df['processor_score'])

            # Multipliers based on preference
            ram_m, stor_m, batt_m, cam_m, perf_m = 0.15, 0.15, 0.2, 0.2, 0.3
            if preference == 'gaming':
                perf_m, ram_m, batt_m = 0.5, 0.3, 0.2
                cam_m, stor_m = 0.1, 0.1
            elif preference == 'camera':
                cam_m, stor_m = 0.5, 0.3
                perf_m, ram_m, batt_m = 0.2, 0.1, 0.1
            elif preference == 'battery':
                batt_m, perf_m = 0.5, 0.3
                cam_m, ram_m, stor_m = 0.1, 0.1, 0.1

            df['spec_match'] = (
                df['n_ram'] * ram_m +
                df['n_storage'] * stor_m +
                df['n_battery'] * batt_m +
                df['n_camera'] * cam_m +
                df['n_perf'] * perf_m
            )
            df['perf_score'] = df['n_perf'] # for final composition
        else:
            # Base scores
            df['n_ram'] = normalize(df['ram'])
            df['n_storage'] = normalize(df['storage'])
            df['n_battery'] = normalize(df['battery'])
            df['n_cpu'] = normalize(df['cpu_score'])
            df['n_gpu'] = normalize(df['gpu_score'])

            # Multipliers based on preference
            ram_m, stor_m, batt_m, cpu_m, gpu_m = 0.15, 0.15, 0.1, 0.3, 0.3
            if preference == 'gaming':
                gpu_m, cpu_m, ram_m = 0.5, 0.3, 0.2
                batt_m, stor_m = 0.05, 0.05
            elif preference == 'office':
                cpu_m, ram_m, batt_m = 0.4, 0.3, 0.3
                gpu_m, stor_m = 0.1, 0.1
            elif preference == 'battery':
                batt_m, cpu_m = 0.6, 0.4
                ram_m, stor_m, gpu_m = 0.1, 0.1, 0.1

            df['spec_match'] = (
                df['n_ram'] * ram_m +
                df['n_storage'] * stor_m +
                df['n_battery'] * batt_m +
                df['n_cpu'] * cpu_m +
                df['n_gpu'] * gpu_m
            )
            df['perf_score'] = (df['n_cpu'] * 0.6 + df['n_gpu'] * 0.4)

        # Brand Match
        df['brand_score'] = df['brand'].apply(lambda x: 1.2 if brand and x.lower() == brand.lower() else 1.0)

        # Budget Match
        df['budget_match'] = df['price'].apply(lambda x: calculate_budget_score(x, budget))
        
        # Value-for-Money Score: Performance per Price
        df['vfm_score'] = normalize(df['perf_score'] / df['price'])

        # Final score calculation:
        # Heavily influenced by spec_match and budget_match
        # Advanced mode weights specifications even higher
        if mode == 'advanced':
            df['final_score'] = (
                (df['budget_match'] * 0.25) +
                (df['spec_match'] * 0.55) +
                (df['vfm_score'] * 0.10) +
                (df['brand_score'] * 0.10)
            )
        else:
            df['final_score'] = (
                (df['budget_match'] * 0.40) +
                (df['spec_match'] * 0.40) +
                (df['vfm_score'] * 0.10) +
                (df['brand_score'] * 0.10)
            )

        # Final score normalization to ensure 0-1 range for the badge
        # We multiply by brand score last as an override
        df['final_score'] = df['final_score'] * df['brand_score']
        df['final_score'] = normalize(df['final_score'])

        # Sort and take top 10
        top_10 = df.sort_values(by='final_score', ascending=False).head(10)
        return top_10.to_dict(orient='records')

    def compare_products(self, item1, item2, category):
        # Determine winners
        budget_winner = item1 if item1['price'] < item2['price'] else item2
        
        comparison_details = {
            'ram': {'item1': item1['ram'], 'item2': item2['ram'], 'winner': 'item1' if item1['ram'] > item2['ram'] else 'item2' if item2['ram'] > item1['ram'] else 'tie'},
            'storage': {'item1': item1['storage'], 'item2': item2['storage'], 'winner': 'item1' if item1['storage'] > item2['storage'] else 'item2' if item2['storage'] > item1['storage'] else 'tie'},
        }

        if category == 'mobile':
            spec1 = item1['processor_score'] + item1['camera'] + (item1['ram'] * 5)
            spec2 = item2['processor_score'] + item2['camera'] + (item2['ram'] * 5)
            comparison_details.update({
                'power': {'item1': item1['processor_score'], 'item2': item2['processor_score'], 'winner': 'item1' if item1['processor_score'] > item2['processor_score'] else 'item2'},
                'camera': {'item1': item1['camera'], 'item2': item2['camera'], 'winner': 'item1' if item1['camera'] > item2['camera'] else 'item2'},
                'battery': {'item1': item1['battery'], 'item2': item2['battery'], 'winner': 'item1' if item1['battery'] > item2['battery'] else 'item2'}
            })
        else:
            spec1 = item1['cpu_score'] + item1['gpu_score'] + (item1['ram'] * 2)
            spec2 = item2['cpu_score'] + item2['gpu_score'] + (item2['ram'] * 2)
            comparison_details.update({
                'power': {'item1': item1['cpu_score'] + item1['gpu_score'], 'item2': item2['cpu_score'] + item2['gpu_score'], 'winner': 'item1' if (item1['cpu_score'] + item1['gpu_score']) > (item2['cpu_score'] + item2['gpu_score']) else 'item2'},
                'cpu': {'item1': item1['cpu_score'], 'item2': item2['cpu_score'], 'winner': 'item1' if item1['cpu_score'] > item2['cpu_score'] else 'item2'},
                'gpu': {'item1': item1['gpu_score'], 'item2': item2['gpu_score'], 'winner': 'item1' if item1['gpu_score'] > item2['gpu_score'] else 'item2'},
                'battery': {'item1': item1['battery'], 'item2': item2['battery'], 'winner': 'item1' if item1['battery'] > item2['battery'] else 'item2'}
            })
            
        spec_winner = item1 if spec1 > spec2 else item2
        overall_winner = item1 if (item1.get('final_score', 0) or spec1) > (item2.get('final_score', 0) or spec2) else item2

        return {
            'budget_winner': budget_winner['name'],
            'spec_winner': spec_winner['name'],
            'overall_winner': overall_winner['name'],
            'details': comparison_details
        }
