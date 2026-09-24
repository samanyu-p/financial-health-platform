from src.data import validate_outputs


def test_required_files_include_company_comparison():
    assert "company_comparison.csv" in validate_outputs.REQUIRED_FILES


def test_required_files_include_database():
    assert "financial_health.db" in validate_outputs.REQUIRED_FILES


def test_company_outputs_include_configured_companies():
    assert "walmart" in validate_outputs.COMPANY_FILES
    assert "target" in validate_outputs.COMPANY_FILES
    assert "costco" in validate_outputs.COMPANY_FILES


def test_company_outputs_include_core_analyses():
    for analyses in validate_outputs.COMPANY_FILES.values():
        assert "profitability" in analyses
        assert "working_capital" in analyses
        assert "free_cash_flow" in analyses
        assert "financial_health" in analyses
        assert "revenue_forecast" in analyses