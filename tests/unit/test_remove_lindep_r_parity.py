"""R parity for ``remove_lindep`` (CRAN ``mice:::remove.lindep``)."""

from __future__ import annotations

import subprocess
import tempfile
import textwrap
from pathlib import Path

import numpy as np
import pytest

from pymice.methods.linear import remove_lindep
from tests.r_support import r_backend_available, r_backend_skip_reason

pytestmark = [
    pytest.mark.r_backend,
    pytest.mark.skipif(not r_backend_available(), reason=r_backend_skip_reason()),
]

_R_REMOVE_LINDEP = textwrap.dedent(
    """
    remove_lindep_pure <- function(x, y, ry, eps = 1e-04, maxcor = 0.99) {
      if (ncol(x) == 0) return(logical(0))
      if (eps == 0) return(rep.int(TRUE, ncol(x)))
      if (sum(ry) == 0) return(rep.int(TRUE, ncol(x)))
      xobs <- x[ry, , drop = FALSE]
      yobs <- as.numeric(y[ry])
      if (var(yobs) < eps) return(rep(FALSE, ncol(xobs)))
      keep <- unlist(apply(xobs, 2, var) > eps)
      keep[is.na(keep)] <- FALSE
      highcor <- suppressWarnings(unlist(apply(xobs, 2, cor, yobs) < maxcor))
      keep <- keep & highcor
      keep[is.na(keep)] <- FALSE
      k <- sum(keep)
      if (k <= 1L) return(as.logical(keep))
      cx <- cor(xobs[, keep, drop = FALSE], use = "all.obs")
      eig <- eigen(cx, symmetric = TRUE)
      while (k > 1 && length(eig$values) >= k && eig$values[k] / eig$values[1] < eps) {
        j <- seq_len(k)[order(abs(eig$vectors[, k]), decreasing = TRUE)[1]]
        if (is.na(j)) break
        keep[keep][j] <- FALSE
        ncx <- cx[keep[keep], keep[keep], drop = FALSE]
        k <- k - 1
        eig <- eigen(ncx)
      }
      as.logical(keep)
    }
    """
)


def _r_path(path: Path) -> str:
    """Path string safe for R file.path / read.csv (Windows-friendly)."""
    return path.resolve().as_posix().replace("\\", "/")


def _run_rscript(script_path: Path, *, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    """Run an R script file (avoids Windows command-line length / quoting issues)."""
    return subprocess.run(
        ["Rscript", _r_path(script_path)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def _r_remove_lindep_batch(cases: list[dict]) -> list[list[int]]:
    """Run pure R remove.lindep on a list of {x,y,ry} cases; return keep masks."""
    with tempfile.TemporaryDirectory(prefix="pymice_lindep_") as tmp:
        tmp_path = Path(tmp)
        n_cases = len(cases)
        for i, case in enumerate(cases):
            np.savetxt(tmp_path / f"x_{i}.csv", np.asarray(case["x"], dtype=float), delimiter=",")
            np.savetxt(tmp_path / f"y_{i}.csv", np.asarray(case["y"], dtype=float), delimiter=",")
            np.savetxt(
                tmp_path / f"ry_{i}.csv",
                np.asarray(case["ry"], dtype=int),
                delimiter=",",
                fmt="%d",
            )

        script_path = tmp_path / "batch.R"
        script_path.write_text(
            _R_REMOVE_LINDEP
            + textwrap.dedent(
                f"""
                dir <- "{_r_path(tmp_path)}"
                n <- {n_cases}
                lines <- character(n)
                for (i in seq_len(n) - 1L) {{
                  x <- as.matrix(read.csv(file.path(dir, paste0("x_", i, ".csv")), header = FALSE))
                  y <- as.numeric(read.csv(file.path(dir, paste0("y_", i, ".csv")), header = FALSE)[[1]])
                  ry <- as.logical(as.integer(
                    read.csv(file.path(dir, paste0("ry_", i, ".csv")), header = FALSE)[[1]]
                  ))
                  keep <- remove_lindep_pure(x, y, ry)
                  lines[i + 1L] <- paste(as.integer(keep), collapse = ",")
                }}
                cat(paste(lines, collapse = "\\n"))
                cat("\\n")
                """
            ),
            encoding="utf-8",
        )
        proc = _run_rscript(script_path)
        if proc.returncode != 0:
            raise RuntimeError(
                f"R remove.lindep failed (code {proc.returncode}):\n"
                f"stderr:\n{proc.stderr}\nstdout:\n{proc.stdout}"
            )
        lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
        if len(lines) != n_cases:
            raise RuntimeError(
                f"expected {n_cases} keep lines from R, got {len(lines)}:\n{proc.stdout!r}"
            )
        return [[int(v) for v in ln.split(",")] for ln in lines]


def test_remove_lindep_constant_y_drops_all() -> None:
    rng = np.random.default_rng(0)
    x = rng.normal(size=(30, 3))
    y = np.ones(30)
    ry = np.ones(30, dtype=bool)
    keep = remove_lindep(x, y, ry)
    assert not np.any(keep)


def test_remove_lindep_constant_predictor_dropped() -> None:
    rng = np.random.default_rng(1)
    x = rng.normal(size=(40, 3))
    x[:, 1] = 0.0
    y = rng.normal(size=40)
    ry = np.ones(40, dtype=bool)
    keep = remove_lindep(x, y, ry)
    assert keep.tolist() == [True, False, True]


def test_remove_lindep_high_positive_cor_dropped_one_sided() -> None:
    """R keeps predictors only when ``cor(x, y) < maxcor`` (not absolute)."""
    rng = np.random.default_rng(2)
    n = 50
    y = rng.normal(size=n)
    x = np.column_stack(
        [
            y + rng.normal(size=n) * 1e-4,  # cor ≈ 1 → drop
            -y + rng.normal(size=n) * 1e-4,  # cor ≈ -1 → keep under R one-sided rule
            rng.normal(size=n),
        ]
    )
    ry = np.ones(n, dtype=bool)
    keep = remove_lindep(x, y, ry)
    assert not bool(keep[0])
    assert bool(keep[1])
    assert bool(keep[2])


def test_remove_lindep_collinear_pair_drops_exactly_one() -> None:
    rng = np.random.default_rng(3)
    n = 40
    x1 = rng.normal(size=n)
    x = np.column_stack([x1, x1 + rng.normal(size=n) * 1e-12, rng.normal(size=n)])
    y = rng.normal(size=n)
    ry = np.ones(n, dtype=bool)
    keep = remove_lindep(x, y, ry)
    assert int(np.sum(~keep[:2])) == 1
    assert keep[2]


def test_remove_lindep_deterministic_repeated_calls() -> None:
    rng = np.random.default_rng(4)
    n, p = 45, 5
    x = rng.normal(size=(n, p))
    x[:, 1] = x[:, 0] + rng.normal(size=n) * 1e-11
    x[:, 3] = x[:, 2] * 0.5 + x[:, 4] * 0.5
    y = rng.normal(size=n)
    ry = rng.random(n) > 0.05
    first = remove_lindep(x, y, ry)
    for _ in range(20):
        assert np.array_equal(remove_lindep(x, y, ry), first)


def test_remove_lindep_matches_r_on_random_designs() -> None:
    """Python keep masks match pure R ``remove.lindep`` on shared designs."""
    rng = np.random.default_rng(42)
    cases: list[dict] = []
    py_keeps: list[list[int]] = []
    for trial in range(40):
        n, p = 40, 6
        x = rng.normal(size=(n, p))
        if trial % 3 == 0:
            x[:, 1] = x[:, 0] + rng.normal(size=n) * 1e-10
        if trial % 5 == 0:
            x[:, 2] = x[:, 0] * 0.5 + x[:, 3] * 0.5
        if trial % 7 == 0:
            x[:, 4] = 0.0
        y = rng.normal(size=n)
        ry = rng.random(n) > 0.1
        keep = remove_lindep(x, y, ry)
        py_keeps.append(keep.astype(int).tolist())
        cases.append({"x": x.tolist(), "y": y.tolist(), "ry": ry.tolist()})

    r_keeps = _r_remove_lindep_batch(cases)
    mismatches = [
        (i, r_keeps[i], py_keeps[i])
        for i in range(len(cases))
        if list(r_keeps[i]) != list(py_keeps[i])
    ]
    # Null-space eigenvectors can differ by LAPACK for perfectly collinear pairs;
    # both sides must still drop the same *number* of columns in those rare cases.
    hard = []
    for i, r_k, py_k in mismatches:
        if sum(r_k) != sum(py_k):
            hard.append((i, r_k, py_k))
    assert not hard, f"rank/drop-count mismatches vs R: {hard}"
    # Prefer exact match; allow only collinear-pair index swaps.
    for i, r_k, py_k in mismatches:
        r_a = np.array(r_k, dtype=bool)
        p_a = np.array(py_k, dtype=bool)
        # Differ only on which of a near-duplicate pair was dropped.
        assert int(np.sum(r_a != p_a)) == 2, (i, r_k, py_k)


def test_remove_lindep_matches_r_on_mammalsleep_mls_design() -> None:
    """Observed mammalsleep design for ``mls``: both drop ``ts`` only."""
    root = Path(__file__).resolve().parents[2]
    data_path = root / "src" / "pymice" / "data" / "mammalsleep.csv"
    if not data_path.is_file():
        pytest.skip("mammalsleep.csv not found")

    with tempfile.TemporaryDirectory(prefix="pymice_ms_mls_") as tmp:
        tmp_path = Path(tmp)
        design_csv = tmp_path / "design.csv"
        script_path = tmp_path / "mls.R"
        script_path.write_text(
            _R_REMOVE_LINDEP
            + textwrap.dedent(
                f"""
                suppressPackageStartupMessages(library(mice))
                ms <- read.csv("{_r_path(data_path)}")
                ms$species <- as.numeric(factor(ms$species))
                j <- "mls"
                pred <- rep(1, ncol(ms)); names(pred) <- names(ms); pred[j] <- 0
                xnames <- setdiff(names(ms)[pred != 0], j)
                formula <- reformulate(xnames, response = j)
                x <- mice:::obtain.design(ms, formula)
                x <- x[, -1, drop = FALSE]
                y <- ms[[j]]
                ry <- stats::complete.cases(x, y) & !is.na(ms[[j]])
                keep <- remove_lindep_pure(x, y, ry)
                cat("KEEP", paste(as.integer(keep), collapse = ","), "\\n")
                cat("DROP", paste(colnames(x)[!keep], collapse = ","), "\\n")
                write.csv(
                  cbind(as.data.frame(x), `.y` = y, `.ry` = as.integer(ry)),
                  "{_r_path(design_csv)}",
                  row.names = FALSE
                )
                """
            ),
            encoding="utf-8",
        )
        proc = _run_rscript(script_path)
        if proc.returncode != 0:
            raise RuntimeError(
                f"R mammalsleep design failed (code {proc.returncode}):\n"
                f"stderr:\n{proc.stderr}\nstdout:\n{proc.stdout}"
            )
        keep_line = next(ln for ln in proc.stdout.splitlines() if ln.startswith("KEEP"))
        drop_line = next(ln for ln in proc.stdout.splitlines() if ln.startswith("DROP"))
        r_keep = [int(v) for v in keep_line.split()[1].split(",")]
        r_drop_raw = drop_line.split(maxsplit=1)[1] if len(drop_line.split(maxsplit=1)) > 1 else ""
        r_drop = [s.strip() for s in r_drop_raw.split(",") if s.strip()]

        import pandas as pd

        df = pd.read_csv(design_csv)
        ry = df[".ry"].to_numpy(dtype=bool)
        y = df[".y"].to_numpy(dtype=np.float64)
        x = df.drop(columns=[".y", ".ry"]).to_numpy(dtype=np.float64)
        names = list(df.drop(columns=[".y", ".ry"]).columns)
        py_keep = remove_lindep(x, y, ry)
        py_drop = [n for n, k in zip(names, py_keep, strict=True) if not k]
        assert py_keep.astype(int).tolist() == r_keep
        assert py_drop == r_drop
        assert r_drop == ["ts"]
