import sqlite3

import pandas as pd


INPUT_PATH = "data/processed/company_comparison.csv"
DATABASE_PATH = "data/processed/financial_health.db"
TABLE_NAME = "financial_health"


def main():
    df = pd.read_csv(INPUT_PATH)

    with sqlite3.connect(DATABASE_PATH) as connection:
        df.to_sql(
            TABLE_NAME,
            connection,
            if_exists="replace",
            index=False,
        )

        row_count = connection.execute(
            f"SELECT COUNT(*) FROM {TABLE_NAME}"
        ).fetchone()[0]

        company_count = connection.execute(
            f"SELECT COUNT(DISTINCT ticker) FROM {TABLE_NAME}"
        ).fetchone()[0]

        preview = pd.read_sql_query(
            f"""
            SELECT
                ticker,
                end,
                revenue,
                operating_margin,
                free_cash_flow
            FROM {TABLE_NAME}
            ORDER BY ticker, end
            LIMIT 10
            """,
            connection,
        )

    print("Built SQLite database")
    print("---------------------")
    print(f"Database path: {DATABASE_PATH}")
    print(f"Table: {TABLE_NAME}")
    print(f"Rows loaded: {row_count}")
    print(f"Companies loaded: {company_count}")
    print()
    print(preview.to_string(index=False))


if __name__ == "__main__":
    main()