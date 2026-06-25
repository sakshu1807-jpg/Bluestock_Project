import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

def load_data_warehouse():
    print("\nProcess of Loading Datasets into SQLite ...\n")
    print("=" * 60)
    
    db_path = "bluestock_mf.db"
    processed_dir = "data/processed"
    engine = create_engine(f"sqlite:///{db_path}")
    schema_sql_path = './sql/schema.sql'

    # Phase 1: Building From Schema SQL
    print("\nCreating structural tables from schema.sql...\n")
    with open(schema_sql_path, "r") as f:
        schema_sql = f.read()
        
    with sqlite3.connect(db_path) as con:
        con.executescript(schema_sql)

    print("Core structural tables successfully established !!!\n")
    
    # Phase 2: Dynamic Calendar Generation
    print("\nGenerating dim_date metrics...\n")

    nav_df = pd.read_csv(os.path.join(processed_dir, '02_nav_history.csv'))
    nav_date = pd.to_datetime(nav_df['date'])

    tx_df = pd.read_csv(os.path.join(processed_dir, '08_investor_transactions.csv'))
    tx_date = pd.to_datetime(tx_df['transaction_date'])

    all_dates = pd.concat([nav_date, tx_date], axis= 0)
    min_date = all_dates.min()
    max_date = all_dates.max()

    # Date Range Ready
    date_range = pd.date_range(start=min_date, end=max_date)
    df_date = pd.DataFrame({"date_id": date_range})
    df_date['calendar_year'] = date_range.year
    df_date['calendar_month'] = date_range.month
    df_date['month_name'] = date_range.month_name()
    df_date['day_of_week'] = date_range.day_name()
    df_date['is_weekend'] = date_range.dayofweek.map(lambda x: 1 if x >= 5 else 0)

    # Pushing the table content into the bluestock.db
    df_date.to_sql("dim_date", con=engine, if_exists="append", index=False)
    print(f"Loaded {len(df_date)} days into 'dim_date'\n")

    # Phase 3: Pushing Datasets Automatically with all their native features
    mapping_dict = {
        '01_fund_master.csv': 'dim_fund',
        '08_investor_transactions.csv': 'fact_transactions',
        '02_nav_history.csv': 'fact_nav',
        '07_scheme_performance.csv': 'fact_performance',
        '03_aum_by_fund_house.csv': 'fact_aum'
    }

    for csv_file_name, table_name in mapping_dict.items():
        file_path = os.path.join(processed_dir, csv_file_name)
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            # Auto-formating of dates to string
            for col in df.columns:
                if 'date' in col.lower():
                    df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')

            df.to_sql(table_name, con=engine, if_exists='append', index=False)
            
            print(f"Successfully loaded {csv_file_name} to '{table_name}' table with {df.shape[1]} features and {len(df)} rows !!!")
        else:
            print(f"Error : {csv_file_name} cannot be found")
            
    print("\n" + "=" * 60)
    print(f"Success! 'bluestock_mf.db' compiled with all features preserved.")

load_data_warehouse()