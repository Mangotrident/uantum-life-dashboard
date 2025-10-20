# train_model.py
import joblib, pandas as pd, numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from xgboost import XGBRegressor

def train_and_save_model(csv_path="phase2_benchmark_results.csv"):
    df = pd.read_csv(csv_path)
    categorical = ["topology"]
    numeric = ["J","gamma","sigma"]
    pre = ColumnTransformer([
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
        ("num", "passthrough", numeric),
    ])
    model = XGBRegressor(n_estimators=300, max_depth=5, learning_rate=0.06, random_state=42)
    pipe = Pipeline(steps=[("pre", pre), ("model", model)])
    pipe.fit(df[["topology","J","gamma","sigma"]], df["QLS"])
    joblib.dump(pipe, "model.pkl")
    print("✅ Model trained and saved as model.pkl")
