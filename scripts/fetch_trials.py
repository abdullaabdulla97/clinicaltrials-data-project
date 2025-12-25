# Fetches the clinical trials data from ClinicalTrials.gov API for a specific condition (in this case, immunology) and saves it to a CSV file.

import requests # Imported this so I can use the API
import pandas as pd # Imported this so I can build a table (DataFrame) and save CSV
from datetime import datetime # So I can use today's date in the filename

URL = "https://clinicaltrials.gov/api/v2/studies" # This is the ClinicalTrials.gov API endpoint we are talking to

CONDITION = "immunology" # The condition I am interested in and searching for
PAGE_SIZE = 100 # The number of trials per page we ask the API for

def get_nested(data, *keys): # data will be the starting dictionary (like the study object), *keys takes any number of extra positional arguments and bundles them into a tuple called keys ("protocolSection", "identificationModule", "nctId")
    for key in keys: # keys is tuple of keys ("protocolSection", "identificationModule", "nctId"), we loop through each key (first loop: "protocolSection", second loop: "identificationModule", etc unil all the keys are processed)
        if not isinstance(data, dict): # If data is not a dictionary at any point, we can't go deeper.
            return None # So we return None
        data = data.get(key) # We get the key from the current data disctionary and if it exists returns the value, if does not exist then it will return None instead of crashing (1. Start: data = study 2. key = "protocolSection" -> data = study.get("protocolSection") 3. key = "identificationModule" -> data = protocolSection.get("identificationModule"), 4. key = "nctId" -> data = identificationModule.get("nctId") now the data will be the actual ID string)
        if data is None: # If data is None, that is after if key does not exist
            return None # Then we return None
    return data # If we successfully loop through all keys (every .get(key) worked and not returned None) then we return the final value.

# Extract the fields I care about from the study dictionary
def extract_study(study):
    nct_id = get_nested(study, "protocolSection", "identificationModule", "nctId") # Trial ID
    title = get_nested(study, "protocolSection", "identificationModule", "briefTitle") # Title
    status = get_nested(study, "protocolSection", "statusModule", "overallStatus") # Status of the trial (Like, Recruiting, Completed, etc.)
    study_type = get_nested(study, "protocolSection", "designModule", "studyType") # study type (Interventional, Observational, etc.)
    phases = get_nested(study, "protocolSection", "designModule", "phases") # Phases of the trial (Phase 1, Phase 2, etc.)

    if isinstance(phases, list): # If phases is a list (because some trials have multiple phases)
        phases = "; ".join(phases) # Joins them into a single string (Phase 2; Phase 3)
    
    start_date = get_nested(study, "protocolSection", "statusModule", "startDateStruct", "date") # Start date of the trial
    sponsor = get_nested(study, "protocolSection", "sponsorCollaboratorsModule", "leadSponsor", "name") # The name of the lead sponsor (ex. Pfizer, NIH, etc.)
    locations = get_nested(study, "protocolSection", "contactsLocationsModule", "locations") # List of locations (dictionaries ex. {"country": "United States"}, {"country": "Canada"}, etc.) when we get locations we get a list of dictionairies that does not contain just country but other info as well
    
    countries = [] # Initialize an empty list to hold country names
    if isinstance(locations, list): # If locations is a list (we used list because of multiple locations not a single location)
        for location in locations: # Loop through each location dictionary
            country = location.get("country") # Looks inside that one location dictionary for the "country" key ("country": "Canada") and stores it in the country variable
            if country: # If country has a value
                countries.append(country) # Then it will add the country to the countries list (ex. countries = ["United States", "Canada", etc.])
    if countries: # If countries list is not empty
        countries = "; ".join(sorted(set(countries))) # Remove duplicates with set(), sort them alphabetically with sorted(), and join them into a single string seperated by ; (e.g., "Canada; United States")
    else: # If countries list is empty (no locations contained country information)
        countries = None # Then we set the countries to none

    return { # Return flat row dictionary for each study as one level not nested easy for DataFrame (like a table on Excel)
        "nct_id": nct_id,
        "brief_title": title,
        "overall_status": status,
        "study_type": study_type,
        "phase": phases,
        "start_date": start_date,
        "lead_sponsor": sponsor,
        "countries": countries
    }

def main(): # Main function to download all pages of results and save to CSV
    print(f"\nFetching clinical trials for condition: {CONDITION}\n") # Print message to indicate start of fetching process

    params = { # It is a dictionary of query parameters we are sending to the API (clinicaltrials.gov uses these specific parameter names)
        "query.cond": CONDITION, # The condition we are searching for (immunology)
        "pageSize": PAGE_SIZE, # Number of trials per page (100)
        "countTotal": "true", # Ask the API to include the total count of matching studies
        "format": "json" # We want the response in JSON format
    }

    all_studies = [] # Initialize an empty list to hold all studies across pages, Each API response contains a page of results and will keep adding them to the list until all pages are fetched

    while True: # Loop to fetch each pages of the results until there are no more pages
        response = requests.get(URL, params=params, timeout=30) # By using requests.get we are sending a GET request to the API with the specified URL and query parameters(params=params, left is parameter name and right is parameter variable(ex. query.cond: immunology)), with a timeout of 30 seconds (if the server does not repond in 30 seconds it will raise an error)
        response.raise_for_status() # This will raise an error if the request was not successful (e.g., network issues, server errors)
        data = response.json() # Converts the JSON response from the API into a Python dictionary

        studies = data.get("studies", []) # Gets the list of studies from the response data (if "studies" key does not exist, it returns an empty list instead of crashing)
        all_studies.extend(studies) # Used extend instead of append to add each study (not add studies all at once, we add each study thats why used extend) from the current page to the all_studies list 
        
        # Checks for the next page token to see if there are more pages to fetch
        next_token = data.get("nextPageToken") # Gets the next page token from the response data ()
        params["pageToken"] = next_token # If there is a next page token, we update the query parameters to include it for the next request (this tells the API which page to fetch next)
        if not next_token: # If there is no next page token, it means we have fetched all pages
            break # So we break out of the loop
    
    rows = [extract_study(s) for s in all_studies] # For each study(s) in all_studies list we call extract_study(s) function to extract the relevant fields and create a flat dictionary for each study, resulting in a list of dictionaries (rows)
    df = pd.DataFrame(rows) # Turns the list of dictionaries(rows) into a pandas DataFrame (like a table with rows and columns)
    today = datetime.now().strftime("%Y%m%d") # Gets today's date in YYYYMMDD (20251220) format for the filename, now() gets current date and time, strftime formats to the string format we want (in this case YYYYMMDD)
    dated_path = f"data/raw/clinicaltrials_{CONDITION}_raw_{today}.csv" # Creates a filename with the condition and today's date (data/raw/clinicaltrials_immunology_raw_20251220.csv) (If something goes wrong then have a dated file to refer to)
    latest_path = f"data/raw/clinicaltrials_{CONDITION}_raw_latest.csv" # Creates another filename for the latest data (data/raw/clinicaltrials_immunology_raw_latest.csv) (This is the most recent data file we can always refer to this file(clean_analyze.py reads from this file))

    # Save the DataFrame to CSV files
    df.to_csv(dated_path, index=False)
    df.to_csv(latest_path, index=False)

    # Print summary so I know it worked by showing where the files are saved and how many rows there are
    print("Raw files saved:")
    print(f" - {dated_path}")
    print(f" - {latest_path}")
    print(f" Total rows collected: {len(df)}\n")

if __name__ == "__main__":
    main() # Call the main function to execute the script






