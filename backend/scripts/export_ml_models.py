"""Train and export the pipelines defined by the project ML notebooks.

Run from backend/: python -m scripts.export_ml_models
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "paimana_features.csv"
COST_ARTIFACTS = ROOT / "app" / "ml" / "cost" / "artifacts"
TIME_ARTIFACTS = ROOT / "app" / "ml" / "time" / "artifacts"
RANDOM_STATE = 42


def clean_numeric_value(value):
    if pd.isna(value):
        return np.nan
    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)
    text = str(value).strip()
    if not text:
        return np.nan
    if re.match(r"^-?\d{1,3}(,\d{3})*(\.\d+)?$|^-?\d+(\.\d+)?$", text):
        return float(text.replace(",", ""))
    numbers = re.findall(r"\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?", text)
    if len(numbers) > 1 or (re.search(r"[(){}\[\]]", text) and re.search(r"\d", text)):
        return np.nan
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return np.nan


def clean_numeric_series(series):
    return series.apply(clean_numeric_value)


def make_preprocessor(numeric_features, categorical_features):
    numeric = Pipeline(steps=[("imputer", SimpleImputer(strategy="median"))])
    categorical = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric, numeric_features),
            ("cat", categorical, categorical_features),
        ]
    )


def export_cost(df):
    target = "cumulative_expenditure_cr"
    numeric_candidates = [
        "original_cost_cr", "revised_cost_cr", "physical_progress_pct", "previous_progress",
        "previous_expenditure", "progress_change", "expenditure_change", "cost_utilization_pct",
        "expenditure_progress_gap", "project_age_days", "days_to_original_completion", "days_overdue",
    ]
    for column in [target, *numeric_candidates]:
        if column in df:
            df[column] = clean_numeric_series(df[column])
    df = df.dropna(subset=[target]).copy()
    for column in ["report_month", "approval_date", "start_date"]:
        if column in df:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    derived = []
    if "report_month" in df:
        df["report_year"] = df["report_month"].dt.year
        df["report_month_number"] = df["report_month"].dt.month
        derived += ["report_year", "report_month_number"]
    if "start_date" in df:
        df["project_start_year"] = df["start_date"].dt.year
        derived.append("project_start_year")
    numeric_present = [c for c in numeric_candidates if c in df.columns]
    categorical = [c for c in ["agency", "state"] if c in df.columns]
    leakage = {target, "expenditure_change", "cost_utilization_pct", "expenditure_progress_gap"}
    selected = list(dict.fromkeys([c for c in numeric_present if c not in leakage] + derived + categorical))
    numeric = [c for c in selected if c in numeric_present + derived]
    categorical = [c for c in selected if c in categorical]
    X, y = df[selected], df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=RANDOM_STATE)
    preprocessor = make_preprocessor(numeric, categorical)
    rf = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=300, max_depth=None, min_samples_split=5, min_samples_leaf=2, random_state=RANDOM_STATE, n_jobs=-1)),
    ])
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_metrics = (mean_absolute_error(y_test, rf_pred), np.sqrt(mean_squared_error(y_test, rf_pred)), r2_score(y_test, rf_pred))
    xgb = Pipeline(steps=[
        ("preprocessor", make_preprocessor(numeric, categorical)),
        ("regressor", XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=6, subsample=0.8, colsample_bytree=0.8, objective="reg:squarederror", random_state=RANDOM_STATE, n_jobs=-1)),
    ])
    xgb.fit(X_train, y_train)
    xgb_pred = xgb.predict(X_test)
    xgb_metrics = (mean_absolute_error(y_test, xgb_pred), np.sqrt(mean_squared_error(y_test, xgb_pred)), r2_score(y_test, xgb_pred))
    candidates = [("Random Forest", rf, rf_metrics), ("XGBoost", xgb, xgb_metrics)]
    best_name, best_pipeline, metrics = max(candidates, key=lambda item: item[2][2])
    COST_ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, COST_ARTIFACTS / "model.pkl")
    (COST_ARTIFACTS / "feature_config.json").write_text(json.dumps({"features": numeric, "categorical": categorical, "target": target, "model_name": best_name, "mae": metrics[0], "rmse": metrics[1], "r2": metrics[2]}, indent=2), encoding="utf-8")
    print(f"cost: {best_name}, features={numeric + categorical}, MAE={metrics[0]:.2f}, R2={metrics[2]:.4f}")


def export_time(df):
    target = "days_overdue"
    df[target] = pd.to_numeric(df[target], errors="coerce")
    df = df.dropna(subset=[target]).reset_index(drop=True)
    cap = df[target].quantile(0.995)
    df = df[df[target] <= cap].reset_index(drop=True)
    numeric = [c for c in ["project_age_days", "physical_progress_pct", "previous_progress", "progress_change", "original_cost_cr", "revised_cost_cr", "cumulative_expenditure_cr", "previous_expenditure", "expenditure_change", "cost_utilization_pct", "expenditure_progress_gap"] if c in df.columns]
    categorical = [c for c in ["agency", "state"] if c in df.columns]
    features = numeric + categorical
    X, y = df[features], df[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)
    rf = Pipeline(steps=[
        ("preprocessor", make_preprocessor(numeric, categorical)),
        ("regressor", RandomForestRegressor(n_estimators=300, max_depth=12, min_samples_split=5, min_samples_leaf=2, random_state=42, n_jobs=-1)),
    ])
    rf.fit(X_train, y_train)
    rf_pred = rf.predict(X_test)
    rf_metrics = (mean_absolute_error(y_test, rf_pred), np.sqrt(mean_squared_error(y_test, rf_pred)), r2_score(y_test, rf_pred))
    xgb = Pipeline(steps=[
        ("preprocessor", make_preprocessor(numeric, categorical)),
        ("regressor", XGBRegressor(n_estimators=500, learning_rate=0.05, max_depth=6, subsample=0.8, colsample_bytree=0.8, objective="reg:squarederror", random_state=42, n_jobs=-1)),
    ])
    xgb.fit(X_train, y_train)
    xgb_pred = xgb.predict(X_test)
    xgb_metrics = (mean_absolute_error(y_test, xgb_pred), np.sqrt(mean_squared_error(y_test, xgb_pred)), r2_score(y_test, xgb_pred))
    best_name, best_pipeline, metrics = min([("Random Forest", rf, rf_metrics), ("XGBoost", xgb, xgb_metrics)], key=lambda item: (item[2][0], item[2][1], -item[2][2]))
    TIME_ARTIFACTS.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, TIME_ARTIFACTS / "model.pkl")
    (TIME_ARTIFACTS / "feature_config.json").write_text(json.dumps({"features": numeric, "categorical": categorical, "target": target, "model_name": best_name, "mae": metrics[0], "rmse": metrics[1], "r2": metrics[2]}, indent=2), encoding="utf-8")
    print(f"time: {best_name}, features={features}, MAE={metrics[0]:.2f}, R2={metrics[2]:.4f}")


if __name__ == "__main__":
    source = pd.read_csv(CSV_PATH)
    export_cost(source.copy())
    export_time(source.copy())
