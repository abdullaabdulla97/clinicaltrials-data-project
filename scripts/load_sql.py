import pandas as pd
import sqlite3

CONDITION = "immunology"

def main():
    # 1. Path to the cleaned CSV file
    clean_path = f"data/processed/clinicaltrials_{CONDITION}_clean_latest.csv"

    # 2. Path to the SQLite database file (will be created if it does not exist)
    db_path = "data/clinicaltrials.db"

    print(f"\nLoading cleaned data from: {clean_path}")

    # 3. Read the cleaned CSV file into a pandas DataFrame
    df = pd.read_csv(clean_path)

    # 4. Connect to the SQLite database
    connect = sqlite3.connect(db_path)

    try:
        # 5. Write the DataFrame to a SQL table named 'trials'
        # if_exists='replace' means we overwrite the table each time we run this script
        df.to_sql("trials", connect, if_exists="replace", index=False)
        print(f"Data successfully loaded into the database at: {db_path}")
    finally:
        # 6. Close the database connection
        connect.close()
        print("Database connection closed.")

if __name__ == "__main__":
    main()
