"""R prerequisite checks and optional installer (engaged only for ``rng='r'``)."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_DEFAULT_PACKAGES: tuple[str, ...] = ("mice", "pan")
_INSTALL_SCRIPT = Path(__file__).resolve().parent / "scripts" / "install_r.sh"


@dataclass(frozen=True)
class RPrerequisiteStatus:
    """Outcome of an R environment check."""

    rscript: str | None
    r_version: str | None
    missing_packages: tuple[str, ...]
    ok: bool
    message: str


def find_rscript() -> str | None:
    """Return the path to ``Rscript`` if available."""
    return shutil.which("Rscript")


def _r_version(rscript: str) -> str | None:
    try:
        proc = subprocess.run(
            [rscript, "-e", "cat(as.character(getRversion()))"],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    return proc.stdout.strip() or None


def _missing_r_packages(
    rscript: str,
    packages: Sequence[str],
) -> tuple[str, ...]:
    if not packages:
        return ()
    pkg_list = ", ".join(repr(p) for p in packages)
    code = (
        f"pkgs <- c({pkg_list}); "
        "missing <- pkgs[!vapply(pkgs, requireNamespace, logical(1), quietly=TRUE)]; "
        "cat(paste(missing, collapse='\\n'))"
    )
    try:
        proc = subprocess.run(
            [rscript, "-e", code],
            capture_output=True,
            text=True,
            timeout=60,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return tuple(packages)
    lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    return tuple(lines)


def check_r_prerequisites(
    packages: Sequence[str] = _DEFAULT_PACKAGES,
) -> RPrerequisiteStatus:
    """Check for ``Rscript`` and required CRAN packages."""
    rscript = find_rscript()
    if rscript is None:
        return RPrerequisiteStatus(
            rscript=None,
            r_version=None,
            missing_packages=tuple(packages),
            ok=False,
            message="Rscript not found on PATH.",
        )

    version = _r_version(rscript)
    if version is None:
        return RPrerequisiteStatus(
            rscript=rscript,
            r_version=None,
            missing_packages=tuple(packages),
            ok=False,
            message=f"Rscript found at {rscript} but failed to report a version.",
        )

    missing = _missing_r_packages(rscript, packages)
    if missing:
        return RPrerequisiteStatus(
            rscript=rscript,
            r_version=version,
            missing_packages=missing,
            ok=False,
            message=f"R {version} is installed; missing packages: {', '.join(missing)}.",
        )

    return RPrerequisiteStatus(
        rscript=rscript,
        r_version=version,
        missing_packages=(),
        ok=True,
        message=f"R {version} with {', '.join(packages)} is available.",
    )


def install_r_packages(
    packages: Sequence[str] = _DEFAULT_PACKAGES,
    *,
    rscript: str | None = None,
) -> None:
    """Install missing CRAN packages via ``Rscript``."""
    rscript_path = rscript or find_rscript()
    if rscript_path is None:
        raise RuntimeError("Cannot install R packages: Rscript not found.")

    pkg_list = ", ".join(repr(p) for p in packages)
    code = f'install.packages(c({pkg_list}), repos="https://cloud.r-project.org", quiet=TRUE)'
    proc = subprocess.run(
        [rscript_path, "-e", code],
        capture_output=True,
        text=True,
        timeout=600,
        check=False,
    )
    if proc.returncode != 0:
        err = proc.stderr.strip() or proc.stdout.strip() or "unknown R install error"
        raise RuntimeError(f"R package installation failed: {err}")


def install_r(
    *,
    packages: Sequence[str] = _DEFAULT_PACKAGES,
    allow_script: bool = True,
) -> RPrerequisiteStatus:
    """
    Install R (if needed) and required CRAN packages.

    Uses the bundled ``install_r.sh`` when present; otherwise installs packages only.
    """
    status = check_r_prerequisites(packages)
    if status.ok:
        return status

    if status.rscript is None and allow_script and _INSTALL_SCRIPT.is_file():
        proc = subprocess.run(
            ["bash", str(_INSTALL_SCRIPT)],
            capture_output=True,
            text=True,
            timeout=1800,
            check=False,
        )
        if proc.returncode != 0:
            err = proc.stderr.strip() or proc.stdout.strip() or "install_r.sh failed"
            raise RuntimeError(err)
        status = check_r_prerequisites(packages)
        if status.ok:
            return status

    if status.rscript is None:
        hint = _install_hint()
        raise RuntimeError(
            "R is not installed. Automatic installation failed or is unsupported "
            f"on {platform.system()}. {hint}"
        )

    if status.missing_packages:
        install_r_packages(status.missing_packages, rscript=status.rscript)
        status = check_r_prerequisites(packages)

    if not status.ok:
        raise RuntimeError(status.message)
    return status


def _install_hint() -> str:
    system = platform.system()
    if system == "Darwin":
        return "Install with: brew install r"
    if system == "Linux":
        return "Install with your package manager, e.g. sudo apt-get install r-base"
    if system == "Windows":
        return "Install from https://cran.r-project.org/bin/windows/base/"
    return "Install R from https://cran.r-project.org/"


@lru_cache(maxsize=1)
def _ensure_cached(
    install: bool,
    packages_key: tuple[str, ...],
) -> RPrerequisiteStatus:
    packages = packages_key or _DEFAULT_PACKAGES
    status = check_r_prerequisites(packages)
    if status.ok:
        return status
    if not install:
        raise RuntimeError(
            f"{status.message} Re-run with install=True or install R manually. {_install_hint()}"
        )
    return install_r(packages=packages)


def ensure_r_prerequisites(
    *,
    install: bool = False,
    packages: Sequence[str] = _DEFAULT_PACKAGES,
) -> RPrerequisiteStatus:
    """
    Ensure R and required packages are available.

    Called automatically by :func:`pymice.rng.make_rng` when ``rng='r'``.
    Set ``install=True`` to run the bundled installer on failure.
    """
    if os.environ.get("PYMICE_SKIP_R_INSTALL", "").strip().lower() in {"1", "true", "yes"}:
        install = False
    packages_key = tuple(packages)
    if install:
        _ensure_cached.cache_clear()
    return _ensure_cached(install, packages_key)


def needs_r_rng(rng: str | None) -> bool:
    """Return whether the requested backend requires R."""
    if rng is None:
        return False
    return str(rng).strip().lower() in {"r", "r-mersenne", "r_compat", "r-compat"}
