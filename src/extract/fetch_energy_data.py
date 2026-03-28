import requests
from datetime import datetime, timedelta, timezone
import xml.etree.ElementTree as ET
import pandas as pd

# --- CONFIGURATION ---
API_KEY = "YOUR_API_KEY_HERE" 
BASE_URL = "https://web-api.tp.entsoe.eu/api"
ZONE_CODE = "10Y1001A1001A82H"

print("=== PHASE 1: EXTRACTION ===")
now_utc = datetime.now(timezone.utc)
start_time = (now_utc - timedelta(days=1)).strftime('%Y%m%d%H00')
end_time = now_utc.strftime('%Y%m%d%H00')

params = {
    'securityToken': API_KEY,
    'documentType': 'A44', 
    'in_Domain': ZONE_CODE,
    'out_Domain': ZONE_CODE,
    'periodStart': start_time,
    'periodEnd': end_time
}

print("Fetching latest data from ENTSO-E...")
response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    raw_file_path = '/Volumes/energy_workspace/default/raw_data/day_ahead_prices.xml'
    
    with open(raw_file_path, 'w', encoding='utf-8') as file:
        file.write(response.text)
    print(f"✅ Raw XML successfully saved to cloud: {raw_file_path}")
    
    print("\n=== PHASE 2: TRANSFORMATION ===")
    print("Parsing XML structure and calculating exact timestamps...")
    tree = ET.parse(raw_file_path)
    root = tree.getroot()

    # Clean namespaces
    for elem in root.iter():
        if '}' in elem.tag:
            elem.tag = elem.tag.split('}', 1)[1]

    extracted_data = []
    
    # Loop through every TimeSeries block
    for ts in root.findall('.//TimeSeries'):
        
        # 1. THE DUPLICATE FILTER: Only accept auction data marked as position '1'
        auction_pos = ts.find('.//classificationSequence_AttributeInstanceComponent.position')
        if auction_pos is not None and auction_pos.text != '1':
            continue 
            
        period = ts.find('.//Period')
        if period is None:
            continue
            
        # 2. THE TIME TRAVEL MATH: Get the exact start time of this block
        start_str = period.find('timeInterval/start').text
        block_start = datetime.strptime(start_str, "%Y-%m-%dT%H:%MZ")
        
        for point in period.findall('.//Point'):
            pos = int(point.find('position').text)
            price = float(point.find('price.amount').text)
            
            # Calculate true timestamp: start_time + ((position - 1) * 15 minutes)
            true_time = block_start + timedelta(minutes=(pos - 1) * 15)
            
            extracted_data.append({
                "Timestamp": true_time, 
                "Price_EUR_per_MWh": price
            })

    print("Converting to PySpark DataFrame...")
    # Convert to Pandas, sort it cleanly by time, then push to Spark
    pdf = pd.DataFrame(extracted_data)
    pdf = pdf.sort_values(by="Timestamp").reset_index(drop=True)
    spark_df = spark.createDataFrame(pdf)

    print("Saving as Enterprise Parquet file...")
    clean_output_path = "/Volumes/energy_workspace/default/raw_data/cleaned_prices.parquet"
    spark_df.write.mode("overwrite").parquet(clean_output_path)
    
    print(f"✅ Success! Pipeline Complete. Clean data ready at {clean_output_path}")
    display(spark_df)

else:
    print(f"❌ Extraction failed. HTTP Status Code: {response.status_code}")
    print(response.text)