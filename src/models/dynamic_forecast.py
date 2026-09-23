import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from src.data.dynamic_analysis import analyze_dynamic_profitability


def calculate_mape(actual, predicted):
    return (abs((actual - predicted) / actual).mean()) * 100


def forecast_revenue_for_ticker(ticker):
    result = analyze_dynamic_profitability(ticker)

    if result is None:
        return None

    if result["data"] is None:
        return {
            "company": result["company"],
            "forecast": None,
            "metrics": None,
            "error": result["error"],
        }

    df = result["data"].copy()
    df["year"] = pd.to_datetime(df["end"]).dt.year
    df["revenue_billions"] = df["revenue"] / 1e9
    df = df.sort_values("year")

    if len(df) < 6:
        return {
            "company": result["company"],
            "forecast": None,
            "metrics": None,
            "error": "Not enough annual revenue history to forecast.",
        }

    train = df.iloc[:-3].copy()
    test = df.iloc[-3:].copy()

    model = LinearRegression()
    model.fit(train[["year"]], train["revenue_billions"])

    test["linear_trend_prediction"] = model.predict(test[["year"]])
    test["naive_prediction"] = test["revenue_billions"].shift(1)
    test.loc[test.index[0], "naive_prediction"] = train.iloc[-1][
        "revenue_billions"
    ]

    linear_mae = mean_absolute_error(
        test["revenue_billions"],
        test["linear_trend_prediction"],
    )
    linear_rmse = mean_squared_error(
        test["revenue_billions"],
        test["linear_trend_prediction"],
    ) ** 0.5
    linear_mape = calculate_mape(
        test["revenue_billions"],
        test["linear_trend_prediction"],
    )

    naive_mae = mean_absolute_error(
        test["revenue_billions"],
        test["naive_prediction"],
    )
    naive_rmse = mean_squared_error(
        test["revenue_billions"],
        test["naive_prediction"],
    ) ** 0.5
    naive_mape = calculate_mape(
        test["revenue_billions"],
        test["naive_prediction"],
    )

    last_year = int(df["year"].max())
    future_years = pd.DataFrame(
        {"year": [last_year + 1, last_year + 2, last_year + 3]}
    )
    future_years["actual_revenue_billions"] = pd.NA
    future_years["linear_trend_prediction"] = model.predict(
        future_years[["year"]]
    )
    future_years["data_type"] = "forecast"

    historical = df[["year", "revenue_billions"]].copy()
    historical = historical.rename(
        columns={"revenue_billions": "actual_revenue_billions"}
    )
    historical["linear_trend_prediction"] = model.predict(
        historical[["year"]]
    )
    historical["data_type"] = "historical"

    forecast = pd.concat(
        [historical, future_years],
        ignore_index=True,
    )

    metrics = {
        "linear_mae": float(linear_mae),
        "linear_rmse": float(linear_rmse),
        "linear_mape": float(linear_mape),
        "naive_mae": float(naive_mae),
        "naive_rmse": float(naive_rmse),
        "naive_mape": float(naive_mape),
    }

    return {
        "company": result["company"],
        "forecast": forecast,
        "metrics": metrics,
        "error": None,
    }