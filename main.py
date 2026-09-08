"""
main.py — main entry point to run the complete pipeline:
raw data -> clean -> synthetic price -> feature engineering -> train
5 models -> evaluate -> save best model + metrics + plots.

Usage:
    python main.py
"""
from src import evaluate, feature_engineering, preprocess, train
from src.utils import get_logger

log = get_logger("main")


def run_pipeline():
    log.info("STEP 1/4 — Preprocessing raw data")
    df_clean = preprocess.run()

    log.info("STEP 2/4 — Feature engineering")
    df_feat = feature_engineering.run(df_clean)

    log.info("STEP 3/4 — Training models")
    fitted_pipelines, predictions, X_test, y_test = train.run(df_feat)

    log.info("STEP 4/4 — Evaluating models")
    report_df, best_name = evaluate.run(fitted_pipelines, predictions, y_test)

    log.info(f"Pipeline complete. Best model: {best_name}")
    log.info(f"\n{report_df}")
    return report_df, best_name


if __name__ == "__main__":
    run_pipeline()
