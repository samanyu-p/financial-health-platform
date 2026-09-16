import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error


INPUT_PATH = "data/processed/walmart_revenue.csv"
OUTPUT_PATH = "data/processed/walmart_revenue_forecast.csv"


def calculate_mape(actual, predicted):
    return (abs((actual - predicted) / actual).mean()) * 100


def print_error_metrics(label, actual, predicted):
    mae = mean_absolute_error(actual, predicted)
    rmse = mean_squared_error(actual, predicted) ** 0.5
    mape = calculate_mape(actual, predicted)

    print(label)
    print(f"MAE:  {mae:.2f} billion")
    print(f"RMSE: {rmse:.2f} billion")
    print(f"MAPE: {mape:.2f}%")
    print()

    return mae, rmse, mape


def main():
    revenue = pd.read_csv(INPUT_PATH)

    revenue["end"] = pd.to_datetime(revenue["end"])
    revenue["year"] = revenue["end"].dt.year
    revenue = revenue.sort_values("year")

    revenue["revenue_billions"] = revenue["val"] / 1e9

    train = revenue[revenue["year"] <= 2023].copy()
    test = revenue[revenue["year"] > 2023].copy()

    x_train = train[["year"]]
    y_train = train["revenue_billions"]

    x_test = test[["year"]]
    y_test = test["revenue_billions"]

    model = LinearRegression()
    model.fit(x_train, y_train)

    test["linear_trend_prediction"] = model.predict(x_test)
    test["naive_prediction"] = test["revenue_billions"].shift(1)
    test.loc[test.index[0], "naive_prediction"] = train.iloc[-1]["revenue_billions"]

    future_years = pd.DataFrame({"year": [2027, 2028, 2029]})
    future_years["linear_trend_prediction"] = model.predict(future_years)
    future_years["naive_prediction"] = pd.NA
    future_years["actual_revenue_billions"] = pd.NA
    future_years["data_type"] = "forecast"

    historical_predictions = revenue[["year", "revenue_billions"]].copy()
    historical_predictions["linear_trend_prediction"] = model.predict(
    historical_predictions[["year"]]
    )
    historical_predictions["naive_prediction"] = historical_predictions[
    "revenue_billions"
    ].shift(1)
    historical_predictions = historical_predictions.rename(
    columns={"revenue_billions": "actual_revenue_billions"}
    )
    historical_predictions["data_type"] = "historical"

    forecast = pd.concat(
        [historical_predictions, future_years],
        ignore_index=True,
    )

    forecast.to_csv(OUTPUT_PATH, index=False)

    print("Revenue Forecast Model")
    print("----------------------")
    print(f"Training years: {train['year'].min()}-{train['year'].max()}")
    print(f"Testing years: {test['year'].min()}-{test['year'].max()}")
    print()

    print("Test Set Error Metrics:")
    linear_metrics = print_error_metrics(
        "Linear Trend Model",
        y_test,
        test["linear_trend_prediction"],
    )
    naive_metrics = print_error_metrics(
        "Naive Baseline",
        y_test,
        test["naive_prediction"],
    )

    if linear_metrics[0] < naive_metrics[0]:
        print("The linear trend model had lower MAE than the naive baseline.")
    else:
        print("The naive baseline had lower MAE than the linear trend model.")

    print()
    print("Forecast:")
    print(forecast.tail(6).to_string(index=False))
    print()
    print(f"Saved forecast to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()