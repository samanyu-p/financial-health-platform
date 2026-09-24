from pathlib import Path

import pandas as pd


PROCESSED_DIR = Path("data/processed")


REQUIRED_FILES = {
    "company_comparison.csv": [
        "ticker",
        "company",
        "end",
        "year",
        "revenue",
        "revenue_growth",
        "operating_margin",
        "free_cash_flow",
    ],
    "financial_health.db": [],
}


COMPANY_FILES = {
    "walmart": [
        "profitability",
        "working_capital",
        "free_cash_flow",
        "financial_health",
        "revenue_forecast",
    ],
    "target": [
        "profitability",
        "working_capital",
        "free_cash_flow",
        "financial_health",
        "revenue_forecast",
    ],
    "costco": [
        "profitability",
        "working_capital",
        "free_cash_flow",
        "financial_health",
        "revenue_forecast",
    ],
}


def validate_file_exists(path):
    if not path.exists():
        return [f"Missing file: {path}"]

    return []


def validate_csv_columns(path, required_columns):
    errors = []

    if not path.exists():
        return [f"Missing file: {path}"]

    df = pd.read_csv(path)

    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"{path} is missing columns: {', '.join(missing_columns)}"
        )

    if df.empty:
        errors.append(f"{path} has no rows")

    return errors


def validate_company_outputs():
    errors = []

    for output_prefix, analysis_names in COMPANY_FILES.items():
        for analysis_name in analysis_names:
            path = PROCESSED_DIR / f"{output_prefix}_{analysis_name}.csv"
            errors.extend(validate_file_exists(path))

    return errors


def validate_required_outputs():
    errors = []

    for filename, required_columns in REQUIRED_FILES.items():
        path = PROCESSED_DIR / filename

        if path.suffix == ".csv":
            errors.extend(validate_csv_columns(path, required_columns))
        else:
            errors.extend(validate_file_exists(path))

    return errors


def main():
    errors = []
    errors.extend(validate_company_outputs())
    errors.extend(validate_required_outputs())

    print("Processed Data Validation")
    print("-------------------------")

    if errors:
        print("Validation failed:\n")
        for error in errors:
            print(f"- {error}")

        raise SystemExit(1)

    print("All required processed outputs are present.")
    print("Validation passed.")


if __name__ == "__main__":
    main()