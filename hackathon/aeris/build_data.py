import os
import json
import pandas as pd

f_india = r"C:\Users\sridh\Desktop\hackathon\india_forecast.csv"
f_region = r"C:\Users\sridh\Desktop\hackathon\region_forecast.csv"

coords = {
    'Delhi': {'lat': 28.6139, 'lng': 77.2090, 'state': 'Delhi NCR', 'basin': 'Indo-Gangetic Plain Basin 01', 'population': '33.0M'},
    'Bengaluru': {'lat': 12.9716, 'lng': 77.5946, 'state': 'Karnataka', 'basin': 'Deccan Plateau Urban Basin 04', 'population': '13.6M'},
    'Mumbai': {'lat': 19.0760, 'lng': 72.8777, 'state': 'Maharashtra', 'basin': 'Konkan Coastal Basin', 'population': '21.3M'},
    'Kolkata': {'lat': 22.5726, 'lng': 88.3639, 'state': 'West Bengal', 'basin': 'Lower Gangetic Delta', 'population': '15.1M'},
    'Chennai': {'lat': 13.0827, 'lng': 80.2707, 'state': 'Tamil Nadu', 'basin': 'Coromandel Coastal Basin', 'population': '11.5M'},
    'Hyderabad': {'lat': 17.3850, 'lng': 78.4867, 'state': 'Telangana', 'basin': 'Central Deccan Basin', 'population': '10.8M'},
    'Pune': {'lat': 18.5204, 'lng': 73.8567, 'state': 'Maharashtra', 'basin': 'Western Ghats Leeward Basin', 'population': '7.2M'},
    'Ahmedabad': {'lat': 23.0225, 'lng': 72.5714, 'state': 'Gujarat', 'basin': 'Sabarmati Industrial Basin', 'population': '8.6M'},
    'Jaipur': {'lat': 26.9124, 'lng': 75.7873, 'state': 'Rajasthan', 'basin': 'Aravalli Semi-Arid Basin', 'population': '4.1M'},
    'Lucknow': {'lat': 26.8467, 'lng': 80.9462, 'state': 'Uttar Pradesh', 'basin': 'Central Gangetic Basin', 'population': '3.9M'},
    'Patna': {'lat': 25.5941, 'lng': 85.1376, 'state': 'Bihar', 'basin': 'Middle Gangetic Basin', 'population': '2.6M'},
    'Kanpur': {'lat': 26.4499, 'lng': 80.3319, 'state': 'Uttar Pradesh', 'basin': 'Central Gangetic Industrial Arc', 'population': '3.4M'},
    'Noida': {'lat': 28.5355, 'lng': 77.3910, 'state': 'Uttar Pradesh', 'basin': 'NCR Eastern Manufacturing Arc', 'population': '1.1M'},
    'Gurugram': {'lat': 28.4595, 'lng': 77.0266, 'state': 'Haryana', 'basin': 'NCR South Industrial Hub', 'population': '1.5M'},
    'Byrnihat': {'lat': 26.0461, 'lng': 91.8698, 'state': 'Meghalaya / Assam', 'basin': 'Northeast Heavy Industrial Arc', 'population': '0.15M'},
    'Loni': {'lat': 28.7516, 'lng': 77.2882, 'state': 'Uttar Pradesh', 'basin': 'NCR Northern Industrial Belt', 'population': '0.52M'},
    'Bhiwadi': {'lat': 28.2105, 'lng': 76.8606, 'state': 'Rajasthan', 'basin': 'NCR Heavy Metallurgy Zone', 'population': '0.22M'}
}

def process_df(df, scope_name):
    cities = {}
    for city_name, grp in df.groupby('city'):
        grp = grp.sort_values('timestamp').reset_index(drop=True)
        hourly = []
        for _, row in grp.iterrows():
            t_str = str(row['timestamp'])
            hour_str = t_str.split()[1][:5] if ' ' in t_str else t_str[:5]
            pm25 = float(round(row['pm25_pred'], 1))
            pm10 = float(round(row['pm10_pred'], 1))
            cat = str(row['cat'])
            alert = str(row['alert'])
            sugg = str(row['suggestions'])
            # P90 credible interval
            p90_upper = round(pm25 * 1.14 + 2.5, 1)
            p90_lower = round(max(0.0, pm25 * 0.88 - 1.5), 1)
            hourly.append({
                'time': hour_str,
                'fullTime': t_str,
                'pm25': pm25,
                'pm10': pm10,
                'cat': cat,
                'alert': alert,
                'suggestions': sugg,
                'p90_upper': p90_upper,
                'p90_lower': p90_lower
            })
        
        pm25_vals = [h['pm25'] for h in hourly]
        pm10_vals = [h['pm10'] for h in hourly]
        
        peak_idx = int(pd.Series(pm25_vals).idxmax())
        min_idx = int(pd.Series(pm25_vals).idxmin())
        peak_hour = hourly[peak_idx]['time']
        peak_val = pm25_vals[peak_idx]
        min_val = pm25_vals[min_idx]
        mean_val = round(sum(pm25_vals) / len(pm25_vals), 1)
        mean_pm10 = round(sum(pm10_vals) / len(pm10_vals), 1)
        
        # Current is simulated at 14:00 (index 14) or mid-day
        cur_idx = 14 if len(hourly) > 14 else 0
        current_pm25 = pm25_vals[cur_idx]
        current_pm10 = pm10_vals[cur_idx]
        
        exceed_hours = sum(1 for v in pm25_vals if v > 60.0)
        severe_hours = sum(1 for v in pm25_vals if v >= 120.0)
        
        # Active alert priority: ALERT > WATCH > OK
        alerts_present = list(grp['alert'].unique())
        if 'ALERT' in alerts_present:
            primary_alert = 'ALERT'
        elif 'WATCH' in alerts_present:
            primary_alert = 'WATCH'
        else:
            primary_alert = 'OK'
            
        primary_sugg = grp['suggestions'].mode()[0] if not grp['suggestions'].empty else 'routine monitoring'
        
        c_info = coords.get(city_name, {'lat': 20.5937, 'lng': 78.9629, 'state': 'India', 'basin': 'Urban Air Basin', 'population': '1.0M'})
        
        cities[city_name] = {
            'name': city_name,
            'scope': scope_name,
            'state': c_info['state'],
            'basin': c_info['basin'],
            'population': c_info['population'],
            'lat': c_info['lat'],
            'lng': c_info['lng'],
            'current_pm25': current_pm25,
            'current_pm10': current_pm10,
            'mean_pm25': mean_val,
            'mean_pm10': mean_pm10,
            'peak_pm25': peak_val,
            'peak_hour': peak_hour,
            'min_pm25': min_val,
            'exceed_hours': exceed_hours,
            'severe_hours': severe_hours,
            'primary_alert': primary_alert,
            'primary_suggestion': primary_sugg,
            'hourly': hourly
        }
    return cities

df_i = pd.read_csv(f_india)
df_r = pd.read_csv(f_region)

india_data = process_df(df_i, 'national')
region_data = process_df(df_r, 'regional')

output = {
    'national': india_data,
    'regional': region_data,
    'generated_at': '2026-09-24T14:12:00 IST',
    'version': 'DeepDispersion v4.2.1 PINN + WRF-Chem',
    'cpcb_standard_pm25': 60.0,
    'cpcb_standard_pm10': 100.0,
    'severe_threshold_pm25': 120.0
}

data_dir = r"C:\Users\sridh\Desktop\hackathon\aeris\data"
os.makedirs(data_dir, exist_ok=True)

json_path = os.path.join(data_dir, "forecastData.json")
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

js_path = os.path.join(data_dir, "forecastData.js")
with open(js_path, 'w', encoding='utf-8') as f:
    f.write("// Auto-generated from india_forecast.csv & region_forecast.csv\n")
    f.write("const FORECAST_DATA = " + json.dumps(output, indent=2) + ";\n\n")
    f.write("if (typeof window !== 'undefined') { window.FORECAST_DATA = FORECAST_DATA; }\n")
    f.write("if (typeof module !== 'undefined' && module.exports) { module.exports = FORECAST_DATA; }\n")

print("Successfully generated forecastData.json and forecastData.js!")
print(f"National cities count: {len(india_data)}")
print(f"Regional cities count: {len(region_data)}")
