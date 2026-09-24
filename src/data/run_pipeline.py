import subprocess
import sys


PIPELINE_COMMANDS = [
    [sys.executable, "-m", "src.data.fetch_data", "walmart"],
    [sys.executable, "-m", "src.data.fetch_data", "target"],
    [sys.executable, "-m", "src.data.fetch_data", "costco"],
    [sys.executable, "-m", "src.data.clean_financial_data", "walmart"],
    [sys.executable, "-m", "src.data.clean_financial_data", "target"],
    [sys.executable, "-m", "src.data.clean_financial_data", "costco"],
    [sys.executable, "-m", "src.analysis.profitability", "walmart"],
    [sys.executable, "-m", "src.analysis.profitability", "target"],
    [sys.executable, "-m", "src.analysis.profitability", "costco"],
    [sys.executable, "-m", "src.analysis.working_capital", "walmart"],
    [sys.executable, "-m", "src.analysis.working_capital", "target"],
    [sys.executable, "-m", "src.analysis.working_capital", "costco"],
    [sys.executable, "-m", "src.analysis.free_cash_flow", "walmart"],
    [sys.executable, "-m", "src.analysis.free_cash_flow", "target"],
    [sys.executable, "-m", "src.analysis.free_cash_flow", "costco"],
    [sys.executable, "-m", "src.analysis.financial_health", "walmart"],
    [sys.executable, "-m", "src.analysis.financial_health", "target"],
    [sys.executable, "-m", "src.analysis.financial_health", "costco"],
    [sys.executable, "-m", "src.models.revenue_forecast", "walmart"],
    [sys.executable, "-m", "src.models.revenue_forecast", "target"],
    [sys.executable, "-m", "src.models.revenue_forecast", "costco"],
    [sys.executable, "-m", "src.analysis.company_comparison"],
    [sys.executable, "-m", "src.data.build_database"],
    [sys.executable, "-m", "src.data.validate_outputs"],
]


def run_command(command):
    print()
    print(f"Running: {' '.join(command)}")
    subprocess.run(command, check=True)


def main():
    print("Financial Health Pipeline")
    print("-------------------------")

    for command in PIPELINE_COMMANDS:
        run_command(command)

    print()
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()