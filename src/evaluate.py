"""
evaluate.py — scores every trained pipeline (RMSE/MAE/R2), saves
outputs/metrics.json + reports/-style CSV, renders comparison plots into
outputs/plots/, and copies the best pipeline to models/trained_model.pkl
so backend/main.py always has one canonical model to load.
"""
import matplotlib
matplotlib.use("Agg")  # headless — safe for CI / servers with no display
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import config
from src.utils import get_logger, save_json, save_model

log = get_logger(__name__)

REPORT_CSV = config.OUTPUTS_DIR / "model_report.csv"


def score_all(predictions: dict, y_test) -> pd.DataFrame:
    results = {}
    for name, pred in predictions.items():
        rmse = mean_squared_error(y_test, pred) ** 0.5
        mae = mean_absolute_error(y_test, pred)
        r2 = r2_score(y_test, pred)
        results[name] = {"RMSE": rmse, "MAE": mae, "R2": r2}
    report_df = pd.DataFrame(results).T.sort_values("RMSE")
    return report_df


def plot_best_model_diagnostics(best_name, y_test, best_pred):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].scatter(y_test, best_pred, alpha=0.3, color="#3b6ea5")
    lims = [min(y_test.min(), best_pred.min()), max(y_test.max(), best_pred.max())]
    axes[0].plot(lims, lims, "k--", lw=1)
    axes[0].set_xlabel("Actual Price")
    axes[0].set_ylabel("Predicted Price")
    axes[0].set_title(f"Actual vs. Predicted — {best_name}")

    residuals = y_test - best_pred
    axes[1].scatter(best_pred, residuals, alpha=0.3, color="#c96a3c")
    axes[1].axhline(0, color="k", linestyle="--", lw=1)
    axes[1].set_xlabel("Predicted Price")
    axes[1].set_ylabel("Residual (Actual - Predicted)")
    axes[1].set_title(f"Residual Plot — {best_name}")

    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / f"actual_vs_predicted_{best_name}.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_model_comparison(report_df: pd.DataFrame):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    metrics = ["RMSE", "MAE", "R2"]
    colors = ["#3b6ea5", "#c96a3c", "#4c9f70"]
    for ax, metric, color in zip(axes, metrics, colors):
        sns.barplot(x=report_df.index, y=report_df[metric], ax=ax, color=color)
        ax.set_title(metric)
        ax.set_xlabel("")
        ax.tick_params(axis="x", rotation=40)
    plt.suptitle("Model Comparison")
    plt.tight_layout()
    plt.savefig(config.PLOTS_DIR / "model_comparison.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def run(fitted_pipelines: dict, predictions: dict, y_test):
    report_df = score_all(predictions, y_test)
    report_df.to_csv(REPORT_CSV)
    log.info(f"Saved model report -> {REPORT_CSV}\n{report_df}")

    best_name = report_df.index[0]
    best_pred = predictions[best_name]
    plot_best_model_diagnostics(best_name, y_test, best_pred)
    plot_model_comparison(report_df)

    # Canonical model the backend/API always loads
    save_model(fitted_pipelines[best_name], config.TRAINED_MODEL_PATH)
    log.info(f"Best model: {best_name} -> saved as {config.TRAINED_MODEL_PATH}")

    metrics = {
        "best_model": best_name,
        "leaderboard": report_df.to_dict(orient="index"),
        "n_test_rows": int(len(y_test)),
    }
    save_json(metrics, config.METRICS_PATH)
    log.info(f"Saved metrics -> {config.METRICS_PATH}")

    return report_df, best_name


if __name__ == "__main__":
    from src.feature_engineering import run as fe_run
    from src.preprocess import run as preprocess_run
    from src.train import run as train_run

    df_feat = fe_run(preprocess_run())
    fitted_pipelines, predictions, X_test, y_test = train_run(df_feat)
    run(fitted_pipelines, predictions, y_test)
