"""Monte Carlo simulation study for the PyMICE JOSS paper.

Compares mean imputation, regression imputation (norm.predict), and
predictive mean matching (pmm) on simulated MAR data. Evaluates bias,
standard errors, and 95% CI coverage for the X1 coefficient.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from scipy import stats

from pymice import mice, pool, summary_pool, with_mids

PAPER_DIR = Path(__file__).resolve().parent


def generate_data(n_obs: int = 500, seed: int | None = None) -> tuple[np.ndarray, list[str]]:
    """Generate synthetic complete data with known regression parameters.

    Model: Y = 2.0 + 1.5 * X1 - 0.8 * X2 + error
    """
    rng = np.random.default_rng(seed)

    mean = [0.0, 0.0]
    cov = [[1.0, 0.4], [0.4, 1.0]]
    X = rng.multivariate_normal(mean, cov, size=n_obs)
    X1, X2 = X[:, 0], X[:, 1]

    error = rng.normal(0.0, 1.0, size=n_obs)
    Y = 2.0 + 1.5 * X1 - 0.8 * X2 + error

    data = np.column_stack([Y, X1, X2])
    names = ["Y", "X1", "X2"]
    return data, names


def induce_missingness_mar(
    data: np.ndarray, names: list[str], seed: int | None = None
) -> np.ndarray:
    """Induce MAR missingness in X1 and Y dependent on X2."""
    rng = np.random.default_rng(seed)
    n_obs = data.shape[0]
    x2_idx = names.index("X2")
    x1_idx = names.index("X1")
    y_idx = names.index("Y")

    x2 = data[:, x2_idx]
    p_missing_x1 = 1.0 / (1.0 + np.exp(-(x2 - 0.5)))
    p_missing_y = 1.0 / (1.0 + np.exp(-(x2 + 0.2)))

    mask_x1 = rng.random(n_obs) < p_missing_x1 * 0.6
    mask_y = rng.random(n_obs) < p_missing_y * 0.5

    incomplete_data = data.copy()
    incomplete_data[mask_x1, x1_idx] = np.nan
    incomplete_data[mask_y, y_idx] = np.nan
    return incomplete_data


def run_simulation(
    n_trials: int = 50, n_obs: int = 500, seed: int = 42
) -> dict[str, dict[str, list[float]]]:
    """Run Monte Carlo simulation comparing three imputation methods."""
    results = {
        "Mean": {"est": [], "se": [], "cover": []},
        "Regression": {"est": [], "se": [], "cover": []},
        "PMM": {"est": [], "se": [], "cover": []},
    }

    print(f"Running {n_trials} simulation trials (N = {n_obs} per trial)...")
    for trial in range(n_trials):
        trial_seed = seed + trial
        complete_data, names = generate_data(n_obs, seed=trial_seed)
        incomplete_data = induce_missingness_mar(complete_data, names, seed=trial_seed)

        imp_mean = mice(
            incomplete_data,
            column_names=names,
            method="mean",
            m=5,
            maxit=2,
            seed=trial_seed,
            verbose=False,
        )
        fit_mean = with_mids(imp_mean, formula="Y ~ X1 + X2")
        pool_mean = summary_pool(pool(fit_mean))

        imp_reg = mice(
            incomplete_data,
            column_names=names,
            method="norm.predict",
            m=5,
            maxit=2,
            seed=trial_seed,
            verbose=False,
        )
        fit_reg = with_mids(imp_reg, formula="Y ~ X1 + X2")
        pool_reg = summary_pool(pool(fit_reg))

        imp_pmm = mice(
            incomplete_data,
            column_names=names,
            method="pmm",
            m=5,
            maxit=5,
            seed=trial_seed,
            verbose=False,
        )
        fit_pmm = with_mids(imp_pmm, formula="Y ~ X1 + X2")
        pool_pmm = summary_pool(pool(fit_pmm))

        methods_map = {"Mean": pool_mean, "Regression": pool_reg, "PMM": pool_pmm}

        for method_name, pool_res in methods_map.items():
            x1_row = next(r for r in pool_res if r["term"] == "X1")
            est = x1_row["estimate"]
            se = x1_row["std_error"]
            df = x1_row["df"]

            t_crit = stats.t.ppf(0.975, df=df)
            ci_lo = est - t_crit * se
            ci_hi = est + t_crit * se
            cover = 1.0 if (ci_lo <= 1.5 <= ci_hi) else 0.0

            results[method_name]["est"].append(est)
            results[method_name]["se"].append(se)
            results[method_name]["cover"].append(cover)

        if (trial + 1) % 10 == 0:
            print(f"  Completed trial {trial + 1}/{n_trials}")

    return results


def print_summary_table(results: dict[str, dict[str, list[float]]]) -> None:
    """Print simulation summary results to console."""
    print("\n" + "=" * 70)
    print(
        f"{'Imputation Method':<22} | {'Mean Est.':<10} | {'Bias':<8} | "
        f"{'Avg. SE':<8} | {'95% CI Cover':<12}"
    )
    print("=" * 70)
    for method_name, metrics in results.items():
        est_mean = np.mean(metrics["est"])
        bias = est_mean - 1.5
        se_mean = np.mean(metrics["se"])
        coverage = np.mean(metrics["cover"])
        print(
            f"{method_name:<22} | {est_mean:<10.4f} | {bias:<+8.4f} | "
            f"{se_mean:<8.4f} | {coverage:<12.1%}"
        )
    print("=" * 70)
    print("True parameter value for X1 (beta_1) = 1.5\n")


def plot_results(results: dict[str, dict[str, list[float]]], save_path: Path) -> None:
    """Plot boxplot comparing parameter estimates to the true parameter value."""
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("Matplotlib not installed. Skipping plot generation.")
        return

    _fig, ax = plt.subplots(figsize=(7, 5))

    data_to_plot = [results[m]["est"] for m in ["Mean", "Regression", "PMM"]]
    ax.boxplot(
        data_to_plot, tick_labels=["Mean Imputation", "Regression (norm.predict)", "PMM (pmm)"]
    )
    ax.axhline(1.5, color="red", linestyle="--", linewidth=1.5, label="True Parameter (1.5)")

    ax.set_ylabel("Estimate for X1 coefficient (beta_1)")
    ax.set_title("PyMICE Simulation: Parameter Recovery across Imputation Methods")
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.6)

    save_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Results plot saved to {save_path}")


if __name__ == "__main__":
    sim_results = run_simulation(n_trials=50, n_obs=500, seed=42)
    print_summary_table(sim_results)
    plot_results(sim_results, PAPER_DIR / "simulation_results.png")
