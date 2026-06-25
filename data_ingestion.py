import os
import pandas as pd

def run_data_ingestion():
    
    # Defining directories
    raw_dir = "./data/raw"

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
    print("Process complete without any errors !!!\n")

def clean_and_save():
    raw_dir = './data/raw'
    processed_dir = './data/processed'

    #  1. CLEANING AND PROCESSING NAV_HISTORY.CSV

    nav_path = os.path.join(raw_dir, '02_nav_history.csv')

    if os.path.exists(nav_path):
        print("\n1. CLEANING AND PROCESSING NAV_HISTORY.CSV\n")
        df_nav = pd.read_csv(nav_path)

        # parsing date to datetime
        df_nav['date'] = pd.to_datetime(df_nav['date'])

        # Dropping duplicate rows (if any)
        df_nav = df_nav.drop_duplicates()

        # Sorting dataframw by amfi_code + date
        df_nav = df_nav.sort_values(by= ['amfi_code','date'])

        # Forward filling nav values 
        df_nav['nav'] = df_nav.groupby('amfi_code')['nav'].ffill()

        # Checking whether the transactions are positive
        total_rows = len(df_nav)
        df_nav = df_nav[df_nav['nav'] > 0]
        final_rows = len(df_nav)

        if total_rows - final_rows:
            print(f"\nRemoved {total_rows - final_rows} rows with nav < 0\n")

        output_path = os.path.join(processed_dir, '02_nav_history.csv')
        df_nav.to_csv(output_path, index= False)
        print("\nFile : 02_nav_history.csv is saved successfully !!!")

    else:
        print("File : 02_nav_history.csv cannot be found")

    #  2. CLEANING AND PROCESSING INVESTORS_TRANSACTIONS.CSV

    inv_path = os.path.join(raw_dir, '08_investor_transactions.csv')

    if os.path.exists(inv_path):
        print("\n2. CLEANING AND PROCESSING INVESTORS_TRANSACTIONS.CSV\n")
        df_inv = pd.read_csv(inv_path)

        print("\n\nBy running the code : data_df['08_investor_transactions']['transaction_type'].value_counts() in the colab notebook" \
        "it was found that the transaction_type is already standardized having the 3 values as (SIP, Lumpsum, Redemption)\n")

        # Fixing date format 
        df_inv['transaction_date'] = pd.to_datetime(df_inv['transaction_date'])

        # Validating amount > 0
        total_rows = len(df_inv)
        df_inv = df_inv[df_inv['amount_inr'] > 0]
        final_rows = len(df_inv)

        if total_rows - final_rows:
            print(f"\nRemoved {total_rows - final_rows} rows with amount < 0\n")

        # Checking KYC_status enum values
        df_inv['kyc_status'] = df_inv['kyc_status'].apply( lambda x : str(x).strip().upper())

        output_path = os.path.join(processed_dir, '08_investor_transactions.csv')
        df_inv.to_csv(output_path, index= False)
        print("\nFile : 08_investor_transactions.csv is saved successfully !!!")

    else:
        print("File : 08_investor_transactions.csv cannot be found")

    #  3. CLEANING AND PROCESSING SCHEME_PERFORMANCE.CSV

    scheme_path = os.path.join(raw_dir, '07_scheme_performance.csv')

    if os.path.exists(scheme_path):
        print("\n3. CLEANING AND PROCESSING SCHEME_PERFORMANCE.CSV\n")
        df_scheme = pd.read_csv(scheme_path)
        
        # Validating the return features as numeric
        return_cols = [col for col in df_scheme.columns if 'return' in col.strip().lower()]

        for col in return_cols:
            df_scheme[col] = pd.to_numeric(df_scheme[col])
        
        # For anomalies
        print("\nDuring the Day 1 when finding the anomalies, it was found that 07_scheme_performance.csv" \
        "has no null and duplicate rows/values.\n")

        # Validating the expense ratio range
        df_scheme = df_scheme[df_scheme['expense_ratio_pct'].between(0.1, 2.5)]

        output_path = os.path.join(processed_dir, '07_scheme_performance.csv')
        df_scheme.to_csv(output_path, index= False)
        print("\nFile : 07_scheme_performance.csv is saved successfully !!!")

    else:
        print("File : 07_scheme_performance.csv cannot be found")

    # 4. Dealing with the 04_monthly_sip_inflows null values
    print("-" * 70)
    print("\n\n NOTE : During the anomalies check at Day 1, it was found that in the csv file 04_monthly_sip_inflows" \
    "at column (yoy_growth_pct) 12 null values were present processing that null values and filling them with the their median.\n\n")
    print("-" * 70)

    inflow_path = os.path.join(raw_dir, '04_monthly_sip_inflows.csv')

    if os.path.exists(inflow_path):
        print("\n3. CLEANING AND PROCESSING MONTHLY_SIP_INFLOWS.CSV\n")
        df_inflow = pd.read_csv(inflow_path)

        yoy_median = df_inflow['yoy_growth_pct'].median()
        df_inflow['yoy_growth_pct'] = df_inflow['yoy_growth_pct'].fillna(yoy_median)

        output_path = os.path.join(processed_dir, '04_monthly_sip_inflows.csv')
        df_inflow.to_csv(output_path, index= False)
        print("\nFile : 04_monthly_sip_inflows.csv is saved successfully !!!")

    else:
        print("File : 04_monthly_sip_inflows.csv cannot be found")

    # 5. Saving the other files in data/prcessed

    print("\nRest of the csv files were clean during the inspection at Day 1\n")

    remaining_files = [
        '01_fund_master.csv', '03_aum_by_fund_house.csv',
        '05_category_inflows.csv', '06_industry_folio_count.csv', '09_portfolio_holdings.csv',
        '10_benchmark_indices.csv'
    ]

    for file in remaining_files:
        file_path = os.path.join(raw_dir, file)
        processed_path = os.path.join(processed_dir, file)

        if os.path.exists(file_path):
            df_file = pd.read_csv(file_path)
            df_file.to_csv(processed_path, index= False)
            print(f"\nFile : {file} is saved successfully !!!")
        else:
            print(f"File : {file} cannot be found")

print("=" * 60)
print("Bluestock Mutual Fund Pipeline for Day 1 and Day 2")
print("=" * 60)

run_data_ingestion()
clean_and_save()

print("\n" + "=" * 60)
print("Full pipeline sequence completed with friction!")
print("=" * 60)