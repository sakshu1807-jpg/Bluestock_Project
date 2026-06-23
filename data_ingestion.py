import os
import pandas as pd

def run_data_ingestion():
    
    # Defining directories
    raw_dir = "./data/raw"
    processed_dir = "./data/processed"

    target_files = [
        '01_fund_master.csv', '02_nav_history.csv', '03_aum_by_fund_house.csv',
        '04_monthly_sip_inflows.csv', '05_category_inflows.csv', '06_industry_folio_count.csv',
        '07_scheme_performance.csv', '08_investor_transactions.csv', '09_portfolio_holdings.csv',
        '10_benchmark_indices.csv'
    ]
    
    data_df = {}

    # Taking file name and then doing the anomaly check
    for file in target_files:
        raw_path = os.path.join(raw_dir, file)
            
        # Making the dataframe
        df = pd.read_csv(raw_path)
        data_df[file] = df
        
        # Cheking the shape of each df
        print(f"\n\nFile Name: {file} and the shape: {df.shape}\n")
        
        # Cheking the missing or null values
        null_counts_df = df.isnull().sum()
        missing_cols = null_counts_df[null_counts_df > 0]
        if not missing_cols.empty:
            print(f"\n\nMissing rows found: {dict(missing_cols)}\n")
            
        # Cheking the duplicate rows
        duplicate_count = df.duplicated().sum()
        if duplicate_count > 0:
            print(f"\n\nDuplicate rows found {duplicate_count} duplicate rows.\n")
            
        # Writing the copy out to processed directory zone
        processed_path = os.path.join(processed_dir, file)
        df.to_csv(processed_path, index=False)

    # Cheking the AMFI code in both the fund master and the nav history file
    master_key = '01_fund_master.csv'
    history_key = '02_nav_history.csv'
       
    master_df = data_df[master_key]
    history_df = data_df[history_key]
        
    master_codes = set(master_df['amfi_code'].unique())
    history_codes = set(history_df['amfi_code'].unique())

    #Cheking that all the unique codes exist in both or not 
    in_master = master_codes - history_codes
    in_history = history_codes - master_codes
        
    print(f"Unique AMFI codes in Master Database: {len(master_codes)}")
    print(f"Unique AMFI codes found in Price History: {len(history_codes)}")
    print("-" * 40)
        
    if in_master:
            print(f"Validation Alert: {len(in_master)} master fund profiles have ZERO nav_history records.")
            print(f"Mismatched master codes: {list(in_master)[:5]}")
    else:
            print("🎯 Integrity Pass: All operational master profiles have historical data alignments.")
            
    if in_history:
        print(f"Warning: Found {len(in_history)} historical price records missing in master profile data.")
        print(f"Unmapped history codes: {list(in_history)[:5]}")

    print("\n\n")
    print("Process complete!\n")
    print(f"Verified data copies have been generated in: '{processed_dir}'")

run_data_ingestion()