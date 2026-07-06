"""Vignette MICE defaults: session R RNG (R ``set.seed`` once) with prerequisite installer."""

from __future__ import annotations

from typing import Any

VIGNETTE_RNG = "r"
VIGNETTE_DEFAULT_SEED = 123


def ensure_vignette_r_prerequisites() -> None:
    """Check for R (and mice/pan); start a fresh vignette RNG session."""
    from pymice.r_prerequisite import ensure_r_prerequisites

    ensure_r_prerequisites(install=True)
    start_vignette_rng_session()


def start_vignette_rng_session(seed: int = VIGNETTE_DEFAULT_SEED) -> None:
    """Start a fresh R RNG session (mirrors R ``set.seed`` at vignette open)."""
    from pymice.rng import RSession

    RSession.start(seed)


def close_vignette_rng_session() -> None:
    """Close the vignette R RNG session."""
    from pymice.rng import RSession

    RSession.close()


def run_v02_mice_chain(
    data: Any,
    names: list[str],
    data2: Any,
    names2: list[str],
    variable_specs: Any,
) -> dict[str, Any]:
    """
    R V02 ``mice()`` draw order on session stream (seed only on ``mice(..., seed=123)``).

    Returns imp_m3, ini0, imp_conv, imp_conv_seed, imp2, ini2, imp3.
    """
    from pymice import quickpred

    imp_m3 = mice_vignette(data, column_names=names, m=3, maxit=5, print_flag=False)
    ini0 = mice_vignette(data, column_names=names, maxit=0, print_flag=False)
    pred_mod = ini0.predictor_matrix.copy()
    pred_mod[:, names.index("hyp")] = 0
    pred_quick = quickpred(data, mincor=0.3, column_names=names)

    mice_vignette(data, column_names=names, predictor_matrix=pred_mod, print_flag=False)
    mice_vignette(
        data,
        column_names=names,
        predictor_matrix=pred_quick,
        maxit=0,
        print_flag=False,
    )

    imp_conv = mice_vignette(data, column_names=names, m=5, maxit=5, print_flag=False)
    imp_conv_seed = mice_vignette(
        data, column_names=names, m=5, maxit=5, seed=123, print_flag=False
    )
    imp2 = mice_vignette(
        data2,
        column_names=names2,
        variable_specs=variable_specs,
        m=5,
        maxit=5,
        print_flag=False,
    )
    ini2 = mice_vignette(
        data2,
        column_names=names2,
        variable_specs=variable_specs,
        maxit=0,
        print_flag=False,
    )
    meth = dict(ini2.method)
    meth["bmi"] = "norm"
    imp3 = mice_vignette(
        data2,
        column_names=names2,
        variable_specs=variable_specs,
        method=meth,
        m=5,
        maxit=5,
        print_flag=False,
    )
    return {
        "imp_m3": imp_m3,
        "ini0": ini0,
        "imp_conv": imp_conv,
        "imp_conv_seed": imp_conv_seed,
        "imp2": imp2,
        "ini2": ini2,
        "imp3": imp3,
    }


def run_v03_boys_chain(boys: Any, boy_names: list[str]) -> Any:
    """R V03: ``mice(boys, print=FALSE)`` after setup (no per-call seed)."""
    return mice_vignette(boys, column_names=boy_names, m=5, maxit=5, print_flag=False)


def run_v03_mammalsleep_chain(
    ms_full: Any,
    ms_names: list[str],
    ms_no_sp: Any,
    ms_no_names: list[str],
) -> tuple[Any, Any]:
    """R V03: ``mice(mammalsleep)`` then ``mice(mammalsleep[,-1])`` (session stream)."""
    imp_ms = mice_vignette(ms_full, column_names=ms_names, m=5, maxit=10, print_flag=False)
    impnew = mice_vignette(ms_no_sp, column_names=ms_no_names, m=5, maxit=10, print_flag=False)
    return imp_ms, impnew


def run_v04_chain(
    ms_data: Any,
    ms_names: list[str],
    boys: Any,
    boy_names: list[str],
) -> dict[str, Any]:
    """
    R V04 draw order: mammalsleep passive (``pas.imp`` seed=123) → boys norm/post → boys PMM.

    Boys ``mice()`` calls use session stream; only ``pas.imp`` passes ``seed=123`` like R.
    """
    from pymice import post_squeeze

    ini_ms = mice_vignette(ms_data, column_names=ms_names, maxit=0, m=5, print_flag=False)
    pred_ms_mod = ini_ms.predictor_matrix.copy()
    for row in ("sws", "ps"):
        pred_ms_mod[ms_names.index(row), ms_names.index("ts")] = 0
    meth_ms = dict(ini_ms.method)
    meth_ms["ts"] = "~ I(sws + ps)"
    pas_imp = mice_vignette(
        ms_data,
        column_names=ms_names,
        method=meth_ms,
        predictor_matrix=pred_ms_mod,
        m=5,
        maxit=10,
        seed=123,
        print_flag=False,
    )

    ini_boys = mice_vignette(boys, column_names=boy_names, maxit=0, print_flag=False)
    meth_tv = dict(ini_boys.method)
    meth_tv["tv"] = "norm"
    imp_norm_post = mice_vignette(
        boys,
        column_names=boy_names,
        method=meth_tv,
        post={"tv": post_squeeze(1, 25)},
        m=5,
        maxit=5,
        print_flag=False,
    )
    imp_pmm = mice_vignette(boys, column_names=boy_names, m=5, maxit=5, print_flag=False)
    meth_bmi_circ = dict(ini_boys.method)
    meth_bmi_circ["bmi"] = "~ I(wgt / (hgt / 100)^2)"
    imp_bmi_circ = mice_vignette(
        boys,
        column_names=boy_names,
        method=meth_bmi_circ,
        m=5,
        maxit=5,
        print_flag=False,
    )
    return {
        "pas_imp": pas_imp,
        "imp_norm_post": imp_norm_post,
        "imp_pmm": imp_pmm,
        "imp_bmi_circ": imp_bmi_circ,
        "meth_bmi_circ": meth_bmi_circ,
        "ini_ms": ini_ms,
        "pred_ms_mod": pred_ms_mod,
        "meth_ms": meth_ms,
        "ini_boys": ini_boys,
    }


def advance_vignette_r_rng(n: int = 25) -> None:
    """
    Consume R RNG draws to mirror lattice ``densityplot`` side effects.

    R ``densityplot(nhanes$bmi)`` advances ``.Random.seed`` by 25 positions
    (V01 chain parity).
    """
    if n <= 0:
        return
    from pymice.rng import RSession

    if not RSession.is_active():
        return
    RSession.acquire(None).random(n)


def _v05_norm_setup(ini: Any, names: list[str]) -> tuple[dict[str, str], Any, Any]:
    """R V05: norm methods + pred with class/pupil zeroed (imp1) and pupil only (imp2)."""

    meth = dict(ini.method)
    for var in ("extrav", "texp", "popular", "popteach"):
        meth[var] = "norm"
    pred = ini.predictor_matrix.copy()
    pred_no_class = pred.copy()
    pred_no_class[:, names.index("class")] = 0
    pred_no_class[:, names.index("pupil")] = 0
    pred_class = pred.copy()
    pred_class[:, names.index("pupil")] = 0
    return meth, pred_no_class, pred_class


def _v05_popular_2l_pred(ini: Any, names: list[str], *, pan: bool = False) -> Any:

    pred = ini.predictor_matrix.copy()
    pop_i = names.index("popular")
    if pan:
        pred[pop_i, :] = [0, -2, 2, 2, 1, 0, 2]
    else:
        pred[pop_i, :] = [0, -2, 2, 2, 2, 0, 2]
    return pred


def _v05_popncr3_setup(ini: Any, names: list[str]) -> tuple[dict[str, str], Any]:

    pred = ini.predictor_matrix.copy()
    pred[names.index("extrav"), :] = [0, -2, 0, 2, 2, 2, 2]
    pred[names.index("sex"), :] = [0, 1, 1, 0, 1, 1, 1]
    pred[names.index("texp"), :] = [0, -2, 1, 1, 0, 1, 1]
    pred[names.index("popular"), :] = [0, -2, 2, 2, 1, 0, 2]
    pred[names.index("popteach"), :] = [0, -2, 2, 2, 1, 2, 0]
    meth = dict(ini.method)
    meth.update(
        {
            "extrav": "2l.norm",
            "sex": "logreg",
            "texp": "2lonly.mean",
            "popular": "2l.pan",
            "popteach": "2l.pan",
        }
    )
    return meth, pred


def run_v05_multilevel_chain(
    data: Any,
    names: list[str],
    data2: Any,
    names2: list[str],
    data3: Any,
    names3: list[str],
    specs3: Any,
    *,
    specs: Any = None,
    specs2: Any = None,
) -> dict[str, Any]:
    """
    R V05 ``mice()`` draw order on session stream (``set.seed(123)`` once; no per-call seed).

    Order: popNCR ini → imp1 → imp2 → imp3/imp3b → imp4;
    popNCR2 ini → imp5 → imp5.b; fresh ini → imp6 → imp6.b (extends imp6, not imp5);
    popNCR3 ini → imp7 → imp8 (class as unordered factor via ``specs3``).
    """
    from pymice import continue_imputation

    kwargs_ncr = {"variable_specs": specs} if specs is not None else {}
    kwargs_ncr2 = {"variable_specs": specs2} if specs2 is not None else {}

    ini = mice_vignette(data, column_names=names, maxit=0, print_flag=False, **kwargs_ncr)
    meth, pred_no_class, _pred_class = _v05_norm_setup(ini, names)

    imp1 = mice_vignette(
        data,
        column_names=names,
        method=meth,
        predictor_matrix=pred_no_class,
        m=5,
        maxit=5,
        print_flag=False,
        **kwargs_ncr,
    )

    pred2 = ini.predictor_matrix.copy()
    pred2[:, names.index("pupil")] = 0
    imp2 = mice_vignette(
        data,
        column_names=names,
        method=meth,
        predictor_matrix=pred2,
        m=5,
        maxit=5,
        print_flag=False,
        **kwargs_ncr,
    )

    imp3 = continue_imputation(imp2, maxit=10, print=False)
    imp3b = continue_imputation(imp3, maxit=20, print=False)

    imp4 = mice_vignette(
        data,
        column_names=names,
        m=5,
        maxit=5,
        print_flag=False,
        **kwargs_ncr,
    )

    ini2 = mice_vignette(data2, column_names=names2, maxit=0, print_flag=False, **kwargs_ncr2)
    pred5 = _v05_popular_2l_pred(ini2, names2)
    meth5 = dict(ini2.method)
    meth5["popular"] = "2l.norm"
    imp5 = mice_vignette(
        data2,
        column_names=names2,
        method=meth5,
        predictor_matrix=pred5,
        m=5,
        maxit=5,
        print_flag=False,
        **kwargs_ncr2,
    )
    imp5_15 = continue_imputation(imp5, maxit=10, print=False)

    ini2b = mice_vignette(data2, column_names=names2, maxit=0, print_flag=False, **kwargs_ncr2)
    pred6 = _v05_popular_2l_pred(ini2b, names2, pan=True)
    meth6 = dict(ini2b.method)
    meth6["popular"] = "2l.pan"
    imp6 = mice_vignette(
        data2,
        column_names=names2,
        method=meth6,
        predictor_matrix=pred6,
        m=5,
        maxit=5,
        print_flag=False,
        **kwargs_ncr2,
    )
    imp6_15 = continue_imputation(imp6, maxit=10, print=False)

    ini3 = mice_vignette(
        data3,
        column_names=names3,
        variable_specs=specs3,
        maxit=0,
        print_flag=False,
    )
    meth7, pred7 = _v05_popncr3_setup(ini3, names3)
    imp7 = mice_vignette(
        data3,
        column_names=names3,
        variable_specs=specs3,
        method=meth7,
        predictor_matrix=pred7,
        m=5,
        maxit=5,
        print_flag=False,
    )

    imp8 = mice_vignette(
        data3,
        column_names=names3,
        variable_specs=specs3,
        m=5,
        maxit=5,
        print_flag=False,
    )

    return {
        "ini": ini,
        "meth": meth,
        "pred_no_class": pred_no_class,
        "pred_class": pred2,
        "imp1": imp1,
        "imp2": imp2,
        "imp3": imp3,
        "imp3b": imp3b,
        "imp4": imp4,
        "ini2": ini2,
        "pred5": pred5,
        "meth5": meth5,
        "imp5": imp5,
        "imp5_15": imp5_15,
        "ini2b": ini2b,
        "pred6": pred6,
        "meth6": meth6,
        "imp6": imp6,
        "imp6_15": imp6_15,
        "ini3": ini3,
        "meth7": meth7,
        "pred7": pred7,
        "imp7": imp7,
        "imp8": imp8,
    }


LEIDEN_DELTA: tuple[float, ...] = (0.0, -5.0, -10.0, -15.0, -20.0)
MAMMALSLEEP_DELTA: tuple[float, ...] = (8.0, 6.0, 4.0, 2.0, 0.0, -2.0, -4.0, -6.0, -8.0)


def run_v06_leiden_delta_chain(data: Any, names: list[str]) -> list[Any]:
    """
    R V06 δ-adjusted ``mice(leiden, post=..., seed=i)`` for ``i in 1:5``.
    """
    from pymice import post_add

    return [
        mice_vignette(
            data,
            column_names=names,
            post={"rrsyst": post_add(d)},
            m=5,
            maxit=5,
            seed=i,
            print=False,
        )
        for i, d in enumerate(LEIDEN_DELTA, start=1)
    ]


def run_v06_mammalsleep_delta_chain(
    ms_data: Any,
    ms_names: list[str],
) -> tuple[list[float], ...]:
    """
    R V06 mammalsleep passive + δ on ``sws``; returns qbar rows per delta scenario.
    """
    from pymice import pool, post_add, with_mids

    ini = mice_vignette(ms_data, column_names=ms_names, maxit=0, print_flag=False)
    pred = ini.predictor_matrix.copy()
    for row in ("sws", "ps"):
        pred[ms_names.index(row), ms_names.index("ts")] = 0
    meth = dict(ini.method)
    meth["ts"] = "~ I(sws + ps)"

    qbars: list[list[float]] = []
    for i, d in enumerate(MAMMALSLEEP_DELTA, start=1):
        imp = mice_vignette(
            ms_data,
            column_names=ms_names,
            method=meth,
            predictor_matrix=pred,
            post={"sws": post_add(d)},
            m=5,
            maxit=10,
            seed=i * 22,
            print_flag=False,
        )
        pooled = pool(with_mids(imp, formula="sws ~ log10(bw) + odi"))
        qbars.append([float(row["estimate"]) for row in pooled.rows])
    return qbars


def run_v01_mice_chain(
    nhanes: Any, *, plot_bmi_density: bool = True
) -> tuple[Any, Any, Any, Any, Any]:
    """
    Run V01 ``mice()`` calls in R vignette draw order (session stream; seed only on ``norm.nob`` reset).

    Order: mean → (optional BMI density plot) → norm.predict → norm.nob → norm.nob(seed=123) → PMM.
    """
    from pymice import densityplot

    imp_mean = mice_vignette(nhanes, method="mean", m=1, maxit=1)
    if plot_bmi_density:
        densityplot(nhanes["bmi"], xlab="nhanes$bmi")
        advance_vignette_r_rng(25)
    imp_norm_predict = mice_vignette(nhanes, method="norm.predict", m=1, maxit=1)
    imp_nob = mice_vignette(nhanes, method="norm.nob", m=1, maxit=1)
    imp_nob_seed = mice_vignette(nhanes, method="norm.nob", m=1, maxit=1, seed=123)
    imp_pmm = mice_vignette(nhanes, m=5, maxit=5, print=False)
    return imp_mean, imp_norm_predict, imp_nob, imp_nob_seed, imp_pmm


def mice_vignette(*args: Any, **kwargs: Any):
    """
    Run :func:`pymice.mice` with vignette-default ``rng='r'``.

    Uses a persistent R stream across calls (``seed=None`` continues the session).
    Pass ``seed=...`` explicitly to reset like R ``mice(..., seed=123)``.
    """
    from pymice import mice

    kwargs.setdefault("rng", VIGNETTE_RNG)
    if kwargs.get("rng") in {VIGNETTE_RNG, "r"}:
        from pymice.rng import RSession

        if not RSession.is_active():
            RSession.start(VIGNETTE_DEFAULT_SEED)
        if "seed" not in kwargs:
            kwargs["seed"] = None
    return mice(*args, **kwargs)
