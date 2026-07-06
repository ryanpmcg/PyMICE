# PyMICE Vignette Parity — Post-release maintenance

Last updated: 2026-07-05

**PyMICE 0.1.0 is publication-ready.** See [`PUBLICATION.md`](PUBLICATION.md) for the release checklist.

**Status snapshot:** [`PARITY_STATUS.md`](PARITY_STATUS.md) records completed work. This file tracks **non-blocking** follow-ups only — cosmetic rendering, optional RNG backends, and documented sampler tolerances.

Tier A (report structure) is **complete** for V01–V08. Tier D (bit-for-bit RNG) is optional and documented as expected difference under default `rng="numpy"`.

---

## Recently completed (2026-07)

| Item | Vignette | Notes |
|------|----------|-------|
| Draw-order goldens refresh | V02–V04 | `regenerate_draw_order_goldens.py`; 12 keys updated |
| Chain helpers wired | V01–V06 | `vignette_rng.py`; RNG audit steps match |
| `print(imp)` formatter | V01 | `_mids_imputed_vars()` excludes non-imputed `age` from visit sequence |
| Passive circular BMI | V04 | Visit order (`hgt`/`wgt` before `bmi`); constraint check exact |
| V05 step 16 golden | V05 | `regenerate_v05_goldens.py`; promoted to `exact=True` |
| V05 steps 21–26 labels | V05 | moment tolerance ~0.15 documented on multilevel diagnostics |
| Cox PH + pool + qbar | V06 | `regenerate_v06_goldens.py`; steps 11–13 `exact=True` |
| V06 δ-chains | V06 | `run_v06_leiden_delta_chain()` / `run_v06_mammalsleep_delta_chain()` |
| R ampute backend | V07 | `PYMICE_R_AMPUTE`; steps 4/9/10/11 exact with R |
| `futuremice` | V08 | `parallel_mice()`, process pool, `ibind`, `parallelseed` |
| V02 steps 7–8 | V02 | `exact=True` on mira/pool main blocks (goldens refreshed) |
| Label hygiene | V05/V06 | Stale draw-order `partial_reason` strings swept |
| Structural audit | All | `audit_vignette` 0 errors / 0 warnings |
| r_gaps closure | All | 35 methods registered; mids utilities |
| Optional backends | — | `PYMICE_R_LMER`, `PYMICE_SKLEARN` |
| V08 print fix | V08 | `futuremice(print=False)` no longer crashes |

---

## Active queue

### P1 — Maintenance

- [x] `audit_rng_parity.py` — 27/27 chain steps match (2026-07-05)
- [x] `maintain_parity.py` — structural + RNG audit wrapper; refreshes `parity_backlog.json`

### P2 — Optional algorithm / RNG

- [ ] V01 steps 8–9: `norm.predict` OLS tolerance (optional R `lm` backend)
- [ ] V07 steps 3.3, 5.5, 10.7: native ampute vs R 4.5.2 golden drift
- [ ] V08 steps 5–7: pooled tables without R snapshot; `parallelseed` when unset

### P3 — Cosmetic / rendering

- [ ] Factor labels vs numeric codes in `summary()` / `str()` (V01, V03, V05)
- [ ] matplotlib diagnostic parity notes (all vignettes) — shape match, not pixel-identical
- [ ] V06 Kaplan–Meier / fluxplot rendering
- [ ] V04 step 9 triple-passive iteration event log format vs R
- [ ] V08 wall-clock benchmark figures (R-only; keep skipped)

### P4 — Method fidelity (optional)

- [x] **r_gaps.py methods** — all V02-listed imputation methods registered (2026-07-05)
- [x] **mids utilities** — `as_mids()`, `cbind_mids()`, `rbind_mids()` in `mids_construct.py`
- [x] Optional R `lme4` backend for `2l.lmer` / `2l.bin` (`PYMICE_R_LMER`; NumPy fallback)
- [x] `lasso.*` / `lda` sklearn auto-detect (`PYMICE_SKLEARN`)

---

## Per-vignette remaining items

### V01
- Steps 8–9: `norm.predict` OLS tolerance (optional R `lm` backend)
- Steps 11–12: PMM RNG under default `rng="numpy"` (exact with `rng="r"` + chain)

### V02
- Plots only (trace, stripplot)

### V03
- Factor label layout in summaries (cosmetic)

### V04
- Step 9 triple-passive: iteration event log format vs R
- Diagnostic plots (matplotlib)

### V05
- Step 9.24: imputed norm summary atol=0.2 (documented)
- Steps 21–26: diagnostic plots only; sampler moment tolerance ~0.15 (documented)

### V06
- Kaplan–Meier / fluxplot / δ diagnostic plots (cosmetic)

### V07
- Steps 3.3, 5.5, 10.7: native vs R 4.5.2 golden drift
- Reference-only step 12 documents `patterns` / `odds` / `run` API sections

### V08
- Steps 5–7: pooled tables (no R snapshot); `parallelseed` without global seed

---

## Verification

```bash
cd PyMICE
source ~/.venvs/brain-pymice/bin/activate
python devtools/maintain_parity.py
# or individually:
python devtools/audit_vignette_alignment.py
python devtools/audit_rng_parity.py
python devtools/regenerate_draw_order_goldens.py   # V02–V04
python devtools/regenerate_v05_goldens.py          # V05 step 16
python devtools/regenerate_v06_goldens.py          # V06 Cox/pool/qbar
pytest tests/vignettes/ tests/unit/test_vignette_blocks.py -q
```

## References

- Accomplishments: [`PARITY_STATUS.md`](PARITY_STATUS.md)
- RNG: [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md)
- Report blurbs: `devtools/lib/parity_docs.py`
- R snapshots: `reference/*/vignette_extracted.R`