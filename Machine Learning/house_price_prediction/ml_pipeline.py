"""
House Price Prediction - ML Pipeline
=====================================
Preprocessing + 6 Models + Evaluation
Models: Linear Regression, Decision Tree, Random Forest,
        Gradient Boosting, XGBoost, CatBoost

Run: python ml_pipeline.py
"""

import pandas as pd
import numpy as np
import warnings
import pickle
import json

warnings.filterwarnings("ignore")

from sklearn.linear_model    import LinearRegression
from sklearn.tree            import DecisionTreeRegressor
from sklearn.ensemble        import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing   import LabelEncoder
from sklearn.metrics         import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
    XGB_OK = True
except ImportError:
    XGB_OK = False
    print("⚠  XGBoost not installed. Run: pip install xgboost")

try:
    from catboost import CatBoostRegressor
    CAT_OK = True
except ImportError:
    CAT_OK = False
    print("⚠  CatBoost not installed. Run: pip install catboost")

def load_data(path: str = "zameen_islamabad.csv") -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"\nLoaded {len(df)} rows, {len(df.columns)} columns")
    print(f"   Columns: {list(df.columns)}")
    return df

def preprocess(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    print("\n" + "="*55)
    print("  TASK 2: DATA PREPROCESSING")
    print("="*55)

    original_shape = df.shape

    df = df.drop_duplicates()
    print(f"\n[1] Removed {original_shape[0] - len(df)} duplicate rows")

    df = df.dropna(subset=["price_pkr"])
    df = df[df["price_pkr"] > 0]
    print(f"[2] Rows after dropping missing/zero price: {len(df)}")

    Q1, Q3 = df["price_pkr"].quantile([0.01, 0.99])
    before = len(df)
    df = df[(df["price_pkr"] >= Q1) & (df["price_pkr"] <= Q3)]
    print(f"[3] Removed {before - len(df)} price outliers (1st–99th pct)")

    def to_marla(row):
        if row["area_unit"] == "Kanal":
            return row["area"] * 20
        elif row["area_unit"] == "Square Feet":
            return row["area"] / 272.251
        elif row["area_unit"] == "Square Yard":
            return row["area"] / 30.25
        return row["area"]

    if "area_unit" in df.columns:
        df["area_marla"] = df.apply(to_marla, axis=1)
    else:
        df["area_marla"] = df["area"]
    print("[4] Converted area → area_marla (standard unit)")

    num_cols = ["area_marla", "bedrooms", "bathrooms",
                "parking_spaces", "servant_quarters", "store_rooms",
                "kitchens", "drawing_rooms", "built_year"]
    for col in num_cols:
        if col in df.columns:
            median = df[col].median()
            n_missing = df[col].isna().sum()
            df[col] = df[col].fillna(median)
            if n_missing:
                print(f"[5] Filled {n_missing} missing '{col}' with median={median:.1f}")

    current_year = 2024
    if "built_year" in df.columns:
        df["property_age"] = current_year - df["built_year"].clip(1950, current_year)

    df["beds_baths_ratio"] = df["bedrooms"] / (df["bathrooms"] + 1)
    df["price_per_marla"] = df["price_pkr"] / (df["area_marla"] + 0.01)

    encoders = {}
    cat_cols = []
    for col in ["location", "property_type", "city", "purpose"]:
        if col in df.columns:
            le = LabelEncoder()
            df[col + "_enc"] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
            cat_cols.append(col)

    print(f"[6] Label-encoded: {cat_cols}")

    feature_cols = [
        "area_marla", "bedrooms", "bathrooms",
        "parking_spaces", "servant_quarters", "store_rooms",
        "kitchens", "drawing_rooms", "property_age", "beds_baths_ratio",
    ]
    for col in cat_cols:
        feature_cols.append(col + "_enc")

    feature_cols = [c for c in feature_cols if c in df.columns]

    print(f"\n[7] Final feature set ({len(feature_cols)} features):")
    print(f"    {feature_cols}")

    df["log_price"] = np.log1p(df["price_pkr"])

    df_clean = df[feature_cols + ["price_pkr", "log_price"]].dropna()
    print(f"\nClean dataset: {df_clean.shape[0]} rows x {df_clean.shape[1]} cols")

    meta = {
        "feature_cols": feature_cols,
        "cat_cols": cat_cols,
        "encoders": encoders,
    }
    return df_clean, meta


def split_data(df: pd.DataFrame, feature_cols: list, test_size=0.2):
    X = df[feature_cols]
    y = df["log_price"]   # train on log price → exponentiate predictions

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    print(f"\n[8] Train: {len(X_train)} rows | Test: {len(X_test)} rows (80/20 split)")
    return X_train, X_test, y_train, y_test

def evaluate(name: str, model, X_test, y_test) -> dict:
    """Evaluate on log-scale preds, convert back to PKR for readable metrics."""
    log_preds = model.predict(X_test)
    preds     = np.expm1(log_preds)
    actuals   = np.expm1(y_test)

    mae  = mean_absolute_error(actuals, preds)
    mse  = mean_squared_error(actuals, preds)
    rmse = np.sqrt(mse)
    r2   = r2_score(actuals, preds)

    return {
        "Model": name,
        "MAE":   round(mae),
        "MSE":   round(mse),
        "RMSE":  round(rmse),
        "R²":    round(r2, 4),
    }

def train_models(X_train, X_test, y_train, y_test) -> tuple[dict, pd.DataFrame]:
    print("\n" + "="*55)
    print("  TASK 3: MODEL TRAINING")
    print("="*55)

    models = {
        "Linear Regression":    LinearRegression(),
        "Decision Tree":        DecisionTreeRegressor(max_depth=10, random_state=42),
        "Random Forest":        RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1),
        "Gradient Boosting":    GradientBoostingRegressor(n_estimators=200, learning_rate=0.05, random_state=42),
    }
    if XGB_OK:
        models["XGBoost"] = XGBRegressor(
            n_estimators=200, learning_rate=0.05, max_depth=6,
            random_state=42, verbosity=0
        )
    if CAT_OK:
        models["CatBoost"] = CatBoostRegressor(
            iterations=200, learning_rate=0.05, depth=6,
            random_state=42, verbose=0
        )

    trained   = {}
    results   = []

    for name, model in models.items():
        print(f"\n  Training {name}...", end=" ")
        model.fit(X_train, y_train)
        metrics = evaluate(name, model, X_test, y_test)
        results.append(metrics)
        trained[name] = model
        print(f"R²={metrics['R²']:.4f}  MAE=PKR {metrics['MAE']:,.0f}  RMSE=PKR {metrics['RMSE']:,.0f}")

    results_df = pd.DataFrame(results).sort_values("R²", ascending=False).reset_index(drop=True)
    return trained, results_df

def save_best_model(trained: dict, results_df: pd.DataFrame, meta: dict):
    best_name = results_df.iloc[0]["Model"]
    best_model = trained[best_name]
    print(f"\nBest model: {best_name} (R²={results_df.iloc[0]['R²']})")

    with open("best_model.pkl", "wb") as f:
        pickle.dump(best_model, f)

    meta_to_save = {
        "best_model_name": best_name,
        "feature_cols": meta["feature_cols"],
        "cat_cols": meta["cat_cols"],
        "location_classes":       list(meta["encoders"]["location"].classes_)   if "location"      in meta["encoders"] else [],
        "property_type_classes":  list(meta["encoders"]["property_type"].classes_) if "property_type" in meta["encoders"] else [],
    }
    with open("model_meta.json", "w") as f:
        json.dump(meta_to_save, f, indent=2)

    with open("all_models.pkl", "wb") as f:
        pickle.dump(trained, f)

    results_df.to_csv("model_results.csv", index=False)
    print("Saved: best_model.pkl, all_models.pkl, model_meta.json, model_results.csv")
    return best_name, best_model

def main():
    print("\n" + "="*55)
    print("  HOUSE PRICE PREDICTION SYSTEM — ML PIPELINE")
    print("  City: Islamabad | Data: Zameen.com")
    print("="*55)

    df = load_data("zameen_islamabad.csv")
    df_clean, meta = preprocess(df)

    feature_cols = meta["feature_cols"]
    X_train, X_test, y_train, y_test = split_data(df_clean, feature_cols)

    trained, results_df = train_models(X_train, X_test, y_train, y_test)

    print("\n" + "="*55)
    print("  TASK 4: MODEL EVALUATION RESULTS")
    print("="*55)
    print(results_df.to_string(index=False))

    best_name, best_model = save_best_model(trained, results_df, meta)

    print("\n" + "="*55)
    print("  PIPELINE COMPLETE")
    print("="*55)
    print("  Next: run  streamlit run app.py  for the prediction UI")

    return trained, results_df, meta
if __name__ == "__main__":
    main()
    main()
