"""Pluggable random number generators for PyMICE."""

from __future__ import annotations

import atexit
import os
import shutil
import subprocess
import weakref
from enum import Enum
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray

_R_SERVER = Path(__file__).resolve().parent / "methods" / "r_rng_server.R"
_ACTIVE_R_SERVERS: weakref.WeakSet[RRandomGenerator] = weakref.WeakSet()


class RngBackend(str, Enum):
    """Supported RNG backends for :func:`pymice.engine.mice`."""

    NUMPY = "numpy"
    LEGACY = "legacy"
    R = "r"


@runtime_checkable
class RandomGenerator(Protocol):
    """Subset of :class:`numpy.random.Generator` used by PyMICE methods."""

    def random(self, size: int | tuple[int, ...] | None = None) -> Any: ...
    def standard_normal(self, size: int | tuple[int, ...] | None = None) -> Any: ...
    def chisquare(self, df: float, size: int | tuple[int, ...] | None = None) -> Any: ...
    def gamma(
        self, shape: float, scale: float = 1.0, size: int | tuple[int, ...] | None = None
    ) -> Any: ...
    def integers(
        self,
        low: int,
        high: int | None = None,
        size: int | tuple[int, ...] | None = None,
        *,
        endpoint: bool = False,
    ) -> Any: ...
    def permutation(self, x: int | NDArray[Any]) -> Any: ...
    def multivariate_normal(
        self, mean: NDArray[np.float64], cov: NDArray[np.float64]
    ) -> NDArray[np.float64]: ...
    def choice(
        self,
        a: NDArray[Any],
        size: int | None = None,
        replace: bool = True,
        p: NDArray[np.float64] | None = None,
    ) -> Any: ...
    def normal(
        self,
        loc: float = 0.0,
        scale: float = 1.0,
        size: int | tuple[int, ...] | None = None,
    ) -> Any: ...
    def binomial(self, n: int, p: float, size: int | tuple[int, ...] | None = None) -> Any: ...
    def uniform(
        self,
        low: float = 0.0,
        high: float = 1.0,
        size: int | tuple[int, ...] | None = None,
    ) -> Any: ...


def _normalize_backend(rng: str | RngBackend | RandomGenerator | None) -> str | RandomGenerator:
    if rng is None:
        return RngBackend.NUMPY.value
    if isinstance(rng, RngBackend):
        return rng.value
    if isinstance(rng, str):
        key = rng.strip().lower()
        aliases = {
            "pcg64": RngBackend.NUMPY.value,
            "mt19937": RngBackend.LEGACY.value,
            "mersenne": RngBackend.LEGACY.value,
            "r": RngBackend.R.value,
            "r-mersenne": RngBackend.R.value,
            "r_compat": RngBackend.R.value,
        }
        return aliases.get(key, key)
    return rng


def r_rng_available() -> bool:
    """Return whether the R-backed RNG server can be started."""
    return shutil.which("Rscript") is not None and _R_SERVER.is_file()


def resolve_rng_backend_name(rng: str | RngBackend | RandomGenerator | None) -> str:
    """Return the backend name that will be used."""
    normalized = _normalize_backend(rng)
    if not isinstance(normalized, str):
        return RngBackend.NUMPY.value
    return normalized


class _SessionRRandomGenerator:
    """Proxy that keeps the underlying R server alive across :func:`pymice.mice` calls."""

    def __init__(self, inner: RRandomGenerator) -> None:
        self._inner = inner

    def close(self) -> None:
        """No-op: :class:`RSession` owns server lifecycle."""

    def __getattr__(self, name: str) -> object:
        return getattr(self._inner, name)


class RSession:
    """Persistent R RNG stream shared across sequential :func:`pymice.mice` calls."""

    _generator: RRandomGenerator | None = None
    _proxy: _SessionRRandomGenerator | None = None
    _seed: int | None = None

    @classmethod
    def is_active(cls) -> bool:
        return cls._generator is not None

    @classmethod
    def session_seed(cls) -> int | None:
        """Seed used to start the active session, if any."""
        return cls._seed

    @classmethod
    def start(cls, seed: int) -> _SessionRRandomGenerator:
        """Start or restart a vignette-style session (R ``set.seed`` once)."""
        cls.close()
        cls._generator = RRandomGenerator(int(seed))
        cls._proxy = _SessionRRandomGenerator(cls._generator)
        cls._seed = int(seed)
        return cls._proxy

    @classmethod
    def close(cls) -> None:
        if cls._generator is not None:
            cls._generator.close()
        cls._generator = None
        cls._proxy = None
        cls._seed = None

    @classmethod
    def acquire(cls, seed: int | None) -> _SessionRRandomGenerator:
        """Return the session generator, optionally resetting with ``seed``."""
        if cls._generator is None:
            if seed is None:
                raise ValueError("seed is required when rng='r' and no R RNG session is active")
            return cls.start(seed)
        if seed is not None:
            cls._generator._send(f"seed {int(seed)}")
            cls._seed = int(seed)
        assert cls._proxy is not None
        return cls._proxy


def make_rng(
    seed: int | None,
    rng: str | RngBackend | RandomGenerator | None = None,
) -> tuple[RandomGenerator, str]:
    """
    Build a random generator for MICE.

    Parameters
    ----------
    seed
        Seed for reproducible runs. Required for ``legacy`` and ``r`` backends.
    rng
        ``\"numpy\"`` (default PCG64), ``\"legacy\"`` (NumPy MT19937),
        ``\"r\"`` (R default Mersenne-Twister via ``Rscript``), or a custom
        :class:`numpy.random.Generator`.
    """
    normalized = _normalize_backend(rng)
    if not isinstance(normalized, str):
        return normalized, RngBackend.NUMPY.value

    backend = normalized
    if backend == RngBackend.NUMPY.value:
        return np.random.default_rng(seed), backend
    if backend == RngBackend.LEGACY.value:
        if seed is None:
            raise ValueError("seed is required when rng='legacy'")
        return np.random.Generator(np.random.MT19937(seed)), backend
    if backend == RngBackend.R.value:
        from pymice.r_prerequisite import ensure_r_prerequisites

        auto_install = os.environ.get("PYMICE_AUTO_INSTALL_R", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        ensure_r_prerequisites(install=auto_install)
        if not r_rng_available():
            raise RuntimeError(
                "rng='r' requires Rscript and pymice.methods.r_rng_server.R on PATH."
            )
        if RSession.is_active():
            return RSession.acquire(seed), backend
        if seed is None:
            raise ValueError("seed is required when rng='r'")
        return RRandomGenerator(seed), backend
    raise ValueError(
        f"unknown rng backend {rng!r}; expected 'numpy', 'legacy', 'r', or a numpy Generator"
    )


def _size_to_int(size: int | tuple[int, ...] | None) -> int:
    if size is None:
        return 1
    if isinstance(size, int):
        return size
    out = 1
    for dim in size:
        out *= int(dim)
    return out


def _reshape(values: NDArray[np.float64], size: int | tuple[int, ...] | None) -> Any:
    if size is None:
        return float(values[0])
    if isinstance(size, int):
        return values
    return values.reshape(size)


class RRandomGenerator:
    """R ``stats`` RNG stream exposed with a numpy Generator-like API."""

    def __init__(self, seed: int) -> None:
        rscript = shutil.which("Rscript")
        if rscript is None:
            raise RuntimeError("Rscript not found")
        self._proc = subprocess.Popen(
            [rscript, str(_R_SERVER)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        _ACTIVE_R_SERVERS.add(self)
        ready = self._proc.stdout.readline().strip() if self._proc.stdout else ""
        if ready != "OK":
            err = self._proc.stderr.read() if self._proc.stderr else ""
            raise RuntimeError(f"R RNG server failed to start: {err or ready}")
        self._send(f"seed {int(seed)}")

    def _send(self, command: str) -> list[str]:
        if self._proc.stdin is None or self._proc.stdout is None:
            raise RuntimeError("R RNG server is not running")
        self._proc.stdin.write(command + "\n")
        self._proc.stdin.flush()
        line = self._proc.stdout.readline()
        if not line:
            err = self._proc.stderr.read() if self._proc.stderr else ""
            raise RuntimeError(f"R RNG server closed unexpectedly: {err}")
        text = line.strip()
        if text.startswith("ERR "):
            raise RuntimeError(text[4:])
        if text == "":
            return []
        return text.split()

    def _fetch(
        self,
        command: str,
        *,
        size: int | tuple[int, ...] | None = None,
        dtype: type = np.float64,
    ) -> Any:
        count = _size_to_int(size)
        parts = self._send(f"{command} {count}")
        values = np.asarray(parts, dtype=dtype)
        if values.size != count:
            raise RuntimeError(
                f"R RNG server returned {values.size} values, expected {count} for {command!r}"
            )
        return _reshape(values, size)

    def close(self) -> None:
        if self._proc.stdin is not None:
            try:
                self._proc.stdin.write("quit\n")
                self._proc.stdin.flush()
            except OSError:
                pass
        if self._proc.poll() is None:
            self._proc.terminate()
            try:
                self._proc.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self._proc.kill()

    def random(self, size: int | tuple[int, ...] | None = None) -> Any:
        return self._fetch("runif", size=size)

    def standard_normal(self, size: int | tuple[int, ...] | None = None) -> Any:
        return self._fetch("rnorm", size=size)

    def chisquare(self, df: float, size: int | tuple[int, ...] | None = None) -> Any:
        df_arr = np.asarray(df, dtype=np.float64)
        if size is not None:
            count = _size_to_int(size)
            command = " ".join(["rchisq", str(count), str(float(df_arr))])
            parts = self._send(command)
            values = np.asarray(parts, dtype=np.float64)
            return _reshape(values, size)
        if df_arr.ndim == 0 or df_arr.size == 1:
            command = " ".join(["rchisq", "1", str(float(df_arr))])
            return float(self._send(command)[0])
        flat = df_arr.ravel()
        if flat.size == 1:
            return float(self._send(f"rchisq 1 {float(flat[0])}")[0])
        dfs = " ".join(str(float(d)) for d in flat)
        parts = self._send(f"rchisqv {flat.size} {dfs}")
        return np.asarray(parts, dtype=np.float64).reshape(df_arr.shape)

    def gamma(
        self,
        shape: float,
        scale: float = 1.0,
        size: int | tuple[int, ...] | None = None,
    ) -> Any:
        shape_arr = np.asarray(shape, dtype=np.float64)
        scale_arr = np.asarray(scale, dtype=np.float64)
        if size is not None:
            count = _size_to_int(size)
            command = " ".join(["rgamma", str(count), str(float(shape_arr)), str(float(scale_arr))])
            parts = self._send(command)
            values = np.asarray(parts, dtype=np.float64)
            return _reshape(values, size)
        out_shape = np.broadcast_shapes(shape_arr.shape, scale_arr.shape)
        b_shape, b_scale = np.broadcast_arrays(shape_arr, scale_arr)
        flat_shape = b_shape.ravel()
        flat_scale = b_scale.ravel()
        if flat_shape.size == 1:
            return float(self._send(f"rgamma 1 {float(flat_shape[0])} {float(flat_scale[0])}")[0])
        params = " ".join(
            f"{float(s)} {float(c)}" for s, c in zip(flat_shape, flat_scale, strict=True)
        )
        parts = self._send(f"rgammav {flat_shape.size} {params}")
        draws = np.asarray(parts, dtype=np.float64).reshape(out_shape)
        return draws

    def integers(
        self,
        low: int,
        high: int | None = None,
        size: int | tuple[int, ...] | None = None,
        *,
        endpoint: bool = False,
        dtype: Any = None,
    ) -> Any:
        del dtype  # numpy-compatible signature; R draws are int64
        if high is None:
            raise ValueError("high is required for RRandomGenerator.integers")
        if endpoint:
            high_inc = int(high)
        else:
            high_inc = int(high) - 1
        count = 1 if size is None else _size_to_int(size)
        command = " ".join(["rint", str(count), str(int(low)), str(high_inc)])
        parts = self._send(command)
        values = np.asarray(parts, dtype=np.int64)
        if size is None:
            return int(values[0])
        return _reshape(values, size)

    def permutation(self, x: int | NDArray[Any]) -> Any:
        if isinstance(x, (int, np.integer)):
            parts = self._send(f"perm {int(x)}")
            return np.asarray(parts, dtype=np.int_)
        base = np.asarray(x)
        idx = np.asarray(self._send(f"perm {base.size}"), dtype=np.int_)
        return base[idx]

    def multivariate_normal(
        self,
        mean: NDArray[np.float64],
        cov: NDArray[np.float64],
    ) -> NDArray[np.float64]:
        mean_arr = np.asarray(mean, dtype=np.float64).ravel()
        cov_arr = np.asarray(cov, dtype=np.float64)
        chol = np.linalg.cholesky((cov_arr + cov_arr.T) / 2.0 + np.eye(cov_arr.shape[0]) * 1e-8)
        z = np.asarray(self._fetch("rnorm", size=mean_arr.size), dtype=np.float64)
        return mean_arr + chol @ z

    def choice(
        self,
        a: NDArray[Any],
        size: int | None = None,
        replace: bool = True,
        p: NDArray[np.float64] | None = None,
    ) -> Any:
        if not replace:
            raise ValueError("RRandomGenerator.choice requires replace=True")
        arr = np.asarray(a)
        count = 1 if size is None else int(size)
        if p is None:
            vals = " ".join(str(float(v)) for v in arr.ravel())
            parts = self._send(f"choice {count} {vals}")
        else:
            probs = np.asarray(p, dtype=np.float64).ravel()
            vals = " ".join(
                [str(count), str(probs.size)]
                + [str(float(v)) for v in probs]
                + [str(float(v)) for v in arr.ravel()]
            )
            parts = self._send(f"choicep {vals}")
        out = np.asarray(parts, dtype=arr.dtype if arr.dtype != object else np.float64)
        if size is None:
            return out[0]
        return out

    def normal(
        self,
        loc: float = 0.0,
        scale: float = 1.0,
        size: int | tuple[int, ...] | None = None,
    ) -> Any:
        count = _size_to_int(size)
        command = " ".join(["rnorm", str(count), str(float(loc)), str(float(scale))])
        parts = self._send(command)
        values = np.asarray(parts, dtype=np.float64)
        return _reshape(values, size)

    def binomial(self, n: int, p: float, size: int | tuple[int, ...] | None = None) -> Any:
        count = _size_to_int(size)
        command = " ".join(["rbinom", str(count), str(int(n)), str(float(p))])
        parts = self._send(command)
        values = np.asarray(parts, dtype=np.int64)
        return _reshape(values, size)

    def uniform(
        self,
        low: float = 0.0,
        high: float = 1.0,
        size: int | tuple[int, ...] | None = None,
    ) -> Any:
        count = _size_to_int(size)
        command = " ".join(["runif", str(count), str(float(low)), str(float(high))])
        parts = self._send(command)
        values = np.asarray(parts, dtype=np.float64)
        return _reshape(values, size)


def _shutdown_r_servers() -> None:
    for server in list(_ACTIVE_R_SERVERS):
        server.close()


atexit.register(_shutdown_r_servers)
