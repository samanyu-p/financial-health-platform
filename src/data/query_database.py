import sqlite3

import pandas as pd


DATABASE_PATH = "data/processed/financial_health.db"


def run_query(connection, title, query):
    print()
    print(title)
    print("-" * len(title))

    result = pd.read_sql_query(query, connection)
    print(result.to_string(index=False))


def main():
    with sqlite3.connect(DATABASE_PATH) as connection:
        run_query(
            connection,
            "Latest Year by Company",
            """
            SELECT
                ticker,
                MAX(end) AS latest_year
            FROM financial_health
            GROUP BY ticker
            ORDER BY ticker
            """,
        )

        run_query(
            connection,
            "Average Operating Margin by Company",
            """
            SELECT
                ticker,
                AVG(operating_margin) AS avg_operating_margin
            FROM financial_health
            GROUP BY ticker
            ORDER BY avg_operating_margin DESC
            """,
        )

        run_query(
            connection,
            "Most Recent Free Cash Flow by Company",
            """
            SELECT
                f.ticker,
                f.end,
                f.free_cash_flow
            FROM financial_health AS f
            INNER JOIN (
                SELECT
                    ticker,
                    MAX(end) AS latest_year
                FROM financial_health
                GROUP BY ticker
            ) AS latest
                ON f.ticker = latest.ticker
                AND f.end = latest.latest_year
            ORDER BY f.free_cash_flow DESC
            """,
        )


if __name__ == "__main__":
    main()