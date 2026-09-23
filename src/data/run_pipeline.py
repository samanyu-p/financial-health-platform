import subprocess
import sys
from pathlib import Path


COMPANIES = ["walmart", "target", "costco"]


def run_command(command):
    print(f"\nRunning: {' '.join(command)}")

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)


def ensure_directories():
    Path("data/raw").mkdir(parents=True, exist_ok=True)
    Path("data/processed").mkdir(parents=True, exist_ok=True)


def main():
    ensure_directories()

    print("Starting financial health data pipeline")
    print("---------------------------------------")

    for company in COMPANIES:
        run_command([sys.executable, "-m", "src.data.fetch_data", company])
        run_command([sys.executable, "-m", "src.data.check_tags", company])
        run_command([sys.executable, "-m", "src.data.clean_financial_data", company])
        run_command([sys.executable, "-m", "src.analysis.profitability", company])
        run_command([sys.executable, "-m", "src.analysis.working_capital", company])
        run_command([sys.executable, "-m", "src.analysis.free_cash_flow", company])
        run_command([sys.executable, "-m", "src.analysis.financial_health", company])
        run_command([sys.executable, "-m", "src.models.revenue_forecast", company])

    run_command([sys.executable, "-m", "src.models.scenario_analysis"])
    run_command([sys.executable, "-m", "src.analysis.company_comparison"])
    run_command([sys.executable, "-m", "src.data.build_database"])

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    main()