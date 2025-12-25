# Cleans the latest raw data and generates simple KPI tables
import pandas as pd
from datetime import datetime

CONDITION = "immunology" # Matches the condition in fetch_trials.py

def main():
    # Load raw data
    raw_path = f"data/raw/clinicaltrials_{CONDITION}_raw_latest.csv" # Path to the latest raw data file
    df = pd.read_csv(raw_path) # Loads the raw data into a DataFrame

    # Basic cleaning
    df = df.drop_duplicates(subset=["nct_id"]) # Remove duplicate trials based on nct_id
    df = df[df["nct_id"].notna()] # Remove rows that have no nct_id
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce") # Converts start_date from string to datetime object, the error is for if we have an invalid date pandas will set it to NaT
    df["start_year"] = df["start_date"].dt.year # Extracts the year from start_date into a new column start_year

    #KPI 1: trials by status
    kpi_status = df.groupby("overall_status")["nct_id"].count().reset_index(name="trials").sort_values("trials", ascending=False) # Groups all rows by status and counts how many trials there are for each status, reset_index is to turn the groupby result into a DataFrame with columns overall_status and trials, then use sort_values to sort by trials in descending order

    #KPI 2: trials by phase
    kpi_phase = (df.groupby("phase")["nct_id"].count().reset_index(name="trials").sort_values("trials", ascending=False)) # Groups all rows by phase and counts how many trials there are for each phase, reset_index is to turn the groupby result into a DataFrame with columns phase and trials, then use sort_values to sort by trials in descending order

    #KPI 3: trials by year
    kpi_year = (df.groupby("start_year")["nct_id"].count().reset_index(name="trials").sort_values("start_year")) # Groups all rows by start_year and counts how many trials there are for each year, reset_index is to turn the groupby result into a DataFrame with columns start_year and trials, then use sort_values to sort by start_year in ascending order

    #KPI 4: trials by country
    country_counts = (df["countries"].dropna().str.split("; ").explode().value_counts().reset_index()) # Takes the countries column that contains (Canada; USA; UK, etc.), dropna() ignores rows with no country data, str.split("; ") splits the string into a list of countries (["Canada", "USA", "UK"]), explode() creates a new row for each country in the list, value_counts() counts how many times each country appears, reset_index() turns the result into a DataFrame with columns country and trials
    country_counts.columns = ["country", "trials"] # Renames the columns to country and trials

    # Summary KPI Table
    kpi_summary = pd.DataFrame({
        "metric": [
            "total_trials",
            "unique_statuses",
            "unique_phases",
            "unique_countries_with_trials"
        ],
        "value": [
            int(df["nct_id"].count()),
            int(df["overall_status"].nunique(dropna=True)),
            int(df["phase"].nunique(dropna=True)),
            int(country_counts["country"].nunique())
        ]
    })

    today = datetime.now().strftime("%Y%m%d") # Get today's date in YYYYMMDD format
    clean_dated = f"data/processed/clinicaltrials_{CONDITION}_clean_{today}.csv" # Path to save the cleaned data with date
    clean_latest = f"data/processed/clinicaltrials_{CONDITION}_clean_latest.csv" # Path to save the cleaned data as latest

    df.to_csv(clean_dated, index=False) # Save cleaned data with date
    df.to_csv(clean_latest, index=False) # Save cleaned data as latest

    kpi_status_dated = f"data/processed/clinicaltrials_{CONDITION}_kpi_status_{today}.csv"
    kpi_phase_dated = f"data/processed/clinicaltrials_{CONDITION}_kpi_phase_{today}.csv"
    kpi_year_dated = f"data/processed/clinicaltrials_{CONDITION}_kpi_year_{today}.csv"
    kpi_country_dated = f"data/processed/clinicaltrials_{CONDITION}_kpi_country_{today}.csv"
    kpi_summary_dated = f"data/processed/clinicaltrials_{CONDITION}_kpi_summary_{today}.csv"
    kpi_status_latest = f"data/processed/clinicaltrials_{CONDITION}_kpi_status_latest.csv"
    kpi_phase_latest = f"data/processed/clinicaltrials_{CONDITION}_kpi_phase_latest.csv"
    kpi_year_latest = f"data/processed/clinicaltrials_{CONDITION}_kpi_year_latest.csv"
    kpi_country_latest = f"data/processed/clinicaltrials_{CONDITION}_kpi_country_latest.csv"
    kpi_summary_latest = f"data/processed/clinicaltrials_{CONDITION}_kpi_summary_latest.csv"

    kpi_status.to_csv(kpi_status_dated, index=False)
    kpi_phase.to_csv(kpi_phase_dated, index=False)
    kpi_year.to_csv(kpi_year_dated, index=False)
    country_counts.to_csv(kpi_country_dated, index=False)
    kpi_summary.to_csv(kpi_summary_dated, index=False)
    kpi_status.to_csv(kpi_status_latest, index=False)
    kpi_phase.to_csv(kpi_phase_latest, index=False)
    kpi_year.to_csv(kpi_year_latest, index=False)
    country_counts.to_csv(kpi_country_latest, index=False)
    kpi_summary.to_csv(kpi_summary_latest, index=False)

    print("Cleaned files saved:")
    print(f" - {clean_latest}")
    print(f" - {clean_dated}\n")

    print("KPI files saved:")
    print("Quick summary:")
    print(kpi_summary.to_string(index=False))

    print("\nTop 3 phases:")
    print(kpi_phase.head(3).to_string(index=False))

    print("\nTop 3 statuses:")
    print(kpi_status.head(3).to_string(index=False))

    print("\nDone!\n")


if __name__ == "__main__":
    main() # Call the main function to execute the script


