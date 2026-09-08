"""
train.py — fits the shared preprocessing pipeline + five regressors
(Linear, RandomForest, XGBoost, LightGBM, Stacking ensemble), mirroring
notebooks/exploration.ipynb section 4.
"""
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor

import config
from src.feature_engineering import get_model_matrix
from src.utils import get_logger, save_model

log = get_logger(__name__)


def build_preprocessor(X):
    cat_cols = config.CATEGORICAL_COLS
    num_cols = [c for c in X.columns if c not in cat_cols]
    return ColumnTransformer([
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ])


def build_models():
    return {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(**config.MODEL_PARAMS["RandomForest"]),
        "XGBoost": XGBRegressor(**config.MODEL_PARAMS["XGBoost"]),
        "LightGBM": LGBMRegressor(**config.MODEL_PARAMS["LightGBM"]),
    }


def build_stacking_model():
    p = config.STACKING_PARAMS
    return StackingRegressor(
        estimators=[
            ("rf", RandomForestRegressor(**p["rf"])),
            ("xgb", XGBRegressor(**p["xgb"])),
            ("lgbm", LGBMRegressor(**p["lgbm"])),
        ],
        final_estimator=Ridge(),
        n_jobs=-1,
    )


def run(df_feat):
    """Split, fit every candidate pipeline, save each to models/, return
    fitted pipelines + predictions + the test split for evaluate.py."""
    X, y = get_model_matrix(df_feat)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE,
    )
    log.info(f"Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    preprocess = build_preprocessor(X)

    fitted_pipelines, predictions = {}, {}
    for name, model in build_models().items():
        pipe = Pipeline([("prep", preprocess), ("model", model)])
        pipe.fit(X_train, y_train)
        fitted_pipelines[name] = pipe
        predictions[name] = pipe.predict(X_test)
        log.info(f"Trained: {name}")

    stack_pipe = Pipeline([("prep", preprocess), ("model", build_stacking_model())])
    stack_pipe.fit(X_train, y_train)
    fitted_pipelines["StackingEnsemble"] = stack_pipe
    predictions["StackingEnsemble"] = stack_pipe.predict(X_test)
    log.info("Trained: StackingEnsemble")

    # Persist every model, plus a fitted copy of just the preprocessor
    # (config.SCALER_PATH) for structure parity with a classic scaler.pkl.
    model_folder_map = {
        "RandomForest": "Random Forest",
        "XGBoost": "XGBoost",
        "LightGBM": "LightGBM",
        "StackingEnsemble": "Stacking Ensemble",
    }
    for key, folder_name in model_folder_map.items():
        out_dir = config.MODELS_DIR / folder_name
        save_model(fitted_pipelines[key], out_dir / "model.joblib")
    save_model(fitted_pipelines["LinearRegression"], config.MODELS_DIR / "linear_regression.joblib")
    save_model(fitted_pipelines["StackingEnsemble"].named_steps["prep"], config.SCALER_PATH)
    log.info(f"Saved fitted preprocessor -> {config.SCALER_PATH}")

    return fitted_pipelines, predictions, X_test, y_test


if __name__ == "__main__":
    from src.feature_engineering import run as fe_run
    from src.preprocess import run as preprocess_run
    df_feat = fe_run(preprocess_run())
    run(df_feat)
