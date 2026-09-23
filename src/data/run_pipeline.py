import subprocess
import sys


COMPANIES = ["walmart", "target", "costco"]


def run_command(command):
    print()
    print(f"Running: {' '.join(command)}")
    print("-" * 80)

    subprocess.run(command, check=True)


def main():
    python = sys.executable

    for company in COMPANIES:
        run_command([python, "-m", "src.data.fetch_data", company])

    for company in COMPANIES:
        run_command([python, "-m", "src.data.check_tags", company])

    for company in COMPANIES:
        run_command([python, "-m", "src.data.clean_financial_data", company])

    for company in COMPANIES:
        run_command([python, "-m", "src.analysis.profitability", company])

    for company in COMPANIES:
        run_command([python, "-m", "src.analysis.working_capital", company])

    for company in COMPANIES:
        run_command([python, "-m", "src.analysis.free_cash_flow", company])

    for company in COMPANIES:
        run_command([python, "-m", "src.analysis.financial_health", company])

    run_command([python, "-m", "src.analysis.company_comparison"])

    for company in COMPANIES:
        run_command([python, "-m", "src.models.revenue_forecast", company])

    run_command([python, "-m", "src.models.scenario_analysis"])

    run_command([python, "-m", "src.data.build_database"])

    print()
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()