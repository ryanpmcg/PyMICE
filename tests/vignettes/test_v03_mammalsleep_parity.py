"""V03 mammalsleep chain parity: logged events + pool vs goldens (R-aligned lindep)."""

from __future__ import annotations

import warnings

import pytest
from lib.data import load_boys_full_matrix, load_mammalsleep_full, load_mammalsleep_impute
from lib.golden import golden_output as g
from lib.r_style import (
    compare_output,
    format_logged_events_warning_r,
    format_pool_mipo_r,
    format_pool_v03_summary_r,
)
from lib.vignette_rng import (
    run_v03_boys_chain,
    run_v03_mammalsleep_chain,
    start_vignette_rng_session,
)

from pymice import pool, summary_pool, with_mids
from pymice.rng import RSession
from tests.r_support import r_backend_available, r_backend_skip_reason

pytestmark = [
    pytest.mark.parity,
    pytest.mark.r_backend,
    pytest.mark.slow,
    pytest.mark.skipif(not r_backend_available(), reason=r_backend_skip_reason()),
]


@pytest.fixture
def v03_mammalsleep_imps():
    """Boys then mammalsleep on session stream (vignette V03 steps 8–14)."""
    RSession.close()
    start_vignette_rng_session(123)
    boys, boy_names = load_boys_full_matrix()
    run_v03_boys_chain(boys, boy_names)
    ms_full, ms_names = load_mammalsleep_full()
    ms_no, ms_no_names = load_mammalsleep_impute()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        imp_ms, impnew = run_v03_mammalsleep_chain(ms_full, ms_names, ms_no, ms_no_names)
    return imp_ms, impnew


def test_v03_mammalsleep_logged_events_match_golden(v03_mammalsleep_imps) -> None:
    """Lock R-aligned logged-event counts (CI flake was 25 vs 26 on old lindep)."""
    imp_ms, impnew = v03_mammalsleep_imps
    act_ms = format_logged_events_warning_r(len(imp_ms.logged_events))
    act_new = format_logged_events_warning_r(len(impnew.logged_events))
    match_ms, _ = compare_output(g("03", 10, 21), act_ms, exact=True)
    match_new, _ = compare_output(g("03", 13, 26), act_new, exact=True)
    assert match_ms, f"imp logged events: {act_ms!r}"
    assert match_new, f"impnew logged events: {act_new!r}"
    # R-aligned remove_lindep path (was flaky 25/26 under old eigen loop).
    assert len(imp_ms.logged_events) == 26
    assert len(impnew.logged_events) == 21


def test_v03_mammalsleep_pool_matches_golden(v03_mammalsleep_imps) -> None:
    imp_ms, impnew = v03_mammalsleep_imps
    fit1 = with_mids(imp_ms, formula="sws ~ log10(bw) + odi")
    fit2 = with_mids(impnew, formula="sws ~ log10(bw) + odi")
    checks = [
        ("12 pool mipo", g("03", 12, 24), format_pool_mipo_r(pool(fit1))),
        (
            "12 pool summary",
            g("03", 12, 25),
            format_pool_v03_summary_r(summary_pool(pool(fit1))),
        ),
        ("14 pool mipo impnew", g("03", 14, 27), format_pool_mipo_r(pool(fit2))),
        (
            "14 pool summary impnew",
            g("03", 14, 28),
            format_pool_v03_summary_r(summary_pool(pool(fit2))),
        ),
    ]
    failures = []
    for label, expected, actual in checks:
        ok, _ = compare_output(expected, actual, atol=0.5)
        if not ok:
            failures.append(f"{label}\nexpected:\n{expected}\nactual:\n{actual}")
    assert not failures, "\n\n".join(failures)


def test_v03_mammalsleep_logged_events_stable_across_reruns() -> None:
    """Same seed/session must not flip 25↔26 (or 29↔other) on one machine."""
    counts: list[tuple[int, int]] = []
    for _ in range(3):
        RSession.close()
        start_vignette_rng_session(123)
        boys, boy_names = load_boys_full_matrix()
        run_v03_boys_chain(boys, boy_names)
        ms_full, ms_names = load_mammalsleep_full()
        ms_no, ms_no_names = load_mammalsleep_impute()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            imp_ms, impnew = run_v03_mammalsleep_chain(ms_full, ms_names, ms_no, ms_no_names)
        counts.append((len(imp_ms.logged_events), len(impnew.logged_events)))
    assert len(set(counts)) == 1, f"non-deterministic logged-event counts: {counts}"
    assert counts[0] == (26, 21)
