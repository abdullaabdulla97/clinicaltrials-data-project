import sqlite3

DB_PATH = "data/clinicaltrials.db"

def run_query(title, sql):
    """Helper function to run a query and print the results."""
    print(f"\n=== {title} ===")
    print(sql)
    print("-" * 60)

    connect = sqlite3.connect(DB_PATH)
    current = connect.cursor()

    try:
        current.execute(sql)
        rows = current.fetchall()

        # Print up to first 20 rows to keep output readable
        for row in rows[:20]:
            print(row)

        if len(rows) > 20:
            print(f"...({len(rows)} rows total, showing first 20)")
    finally:
        connect.close()

def main():
    # 1. Trials by phase
    sql_phase = """
    SELECT phase, COUNT(*) AS trials
    FROM trials
    GROUP BY phase
    ORDER BY trials DESC;
    """

    run_query("Trials by Phase", sql_phase)

    # 2. Trials by status
    sql_status = """
    SELECT overall_status, COUNT(*) AS trials
    FROM trials
    GROUP BY overall_status
    ORDER BY trials DESC;
    """
    run_query("Trials by Status", sql_status)

    # 3. Trials by start year
    sql_year = """
    SELECT start_year, COUNT(*) AS trials
    FROM trials
    GROUP BY start_year
    ORDER BY start_year;
    """
    run_query("Trials by Start Year", sql_year)

    #4. Top 10 sponsors by number of trials
    sql_sponsor = """
    SELECT lead_sponsor, COUNT(*) AS trials
    FROM trials
    WHERE lead_sponsor IS NOT NULL
    GROUP BY lead_sponsor
    ORDER BY trials DESC
    LIMIT 10;
    """
    run_query("Top 10 Sponsors by Number of Trials", sql_sponsor)

if __name__ == "__main__":
    main()