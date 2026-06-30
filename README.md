# PyMICE

**Multivariate Imputation by Chained Equations (MICE)** — a clean-room Python implementation of Fully Conditional Specification (FCS), designed for PyPI publication and eventual integration with [WEPPCLIFF](https://github.com/ryanpmcg/WEPPCLIFF).

> **Status:** Phase 0–7a complete. Core MICE engine, 20+ imputation methods (incl. full `jomoImpute`/`panImpute`, multilevel `2l.*`), WEPPCLIFF adapter (6a–6d), `post`/`squeeze`, `quickpred`, and `ampute` (MCAR/MAR/MNAR). See [`agent.md`](agent.md#implementation-inventory-2026-06) for the full implemented / not-implemented list and [`REPRODUCIBILITY.md`](Documentation/REPRODUCIBILITY.md) for RNG notes.

## Why this project exists

The R [`mice`](https://cran.r-project.org/package=mice) package (van Buuren & Groothuis-Oudshoorn, 2011) is the reference implementation of MICE/FCS. WEPPCLIFF uses `mice` for gap-filling; the Python port uses **`pymice.integrations.weppcliff`** (FCS by default, optional `-jm t` multivariate JOMO block). This repository delivers a **standalone, MIT-licensed** Python library with minimal dependencies (NumPy + SciPy core).

## Repository layout

| Path | Purpose |
|------|---------|
| [`Documentation/IMPLEMENTATION_PLAN.md`](Documentation/IMPLEMENTATION_PLAN.md) | Phased build plan |
| [`agent.md`](agent.md) | Developer / AI agent guide |
| [`Vignettes/`](Vignettes/) | R tutorial snapshots + extracted code for parity tests |
| [`Reference/`](Reference/) | R `mice` source snapshots (GPL, not shipped) |
| `src/pymice/` | Installable package |
| `tests/` | Unit tests + R golden parity |
| [`Documentation/REPRODUCIBILITY.md`](Documentation/REPRODUCIBILITY.md) | RNG / cross-language parity (for publication) |

## Theoretical foundation

- van Buuren, S., & Groothuis-Oudshoorn, K. (2011). *mice: Multivariate Imputation by Chained Equations in R.* JSS 45(3). [doi:10.18637/jss.v045.i03](https://doi.org/10.18637/jss.v045.i03)
- van Buuren, S. (2018). *Flexible Imputation of Missing Data* (2nd ed.). [doi:10.1201/9780429492259](https://doi.org/10.1201/9780429492259)

Full bibliography: [`Documentation/BIBLIOGRAPHY.md`](Documentation/BIBLIOGRAPHY.md)

## Vignettes (verification)

Eight vignettes from [gerkovink.com/miceVignettes](https://www.gerkovink.com/miceVignettes/) are stored under `Vignettes/` with R code extracted to `vignette_extracted.R`. These drive golden tests against R `mice`.

## License

- **Python package (`src/pymice/`):** MIT — see `LICENSE`
- **Reference R snapshots:** GPL-2|GPL-3 (upstream `mice`); development reference only, not distributed in the wheel
- **Vignettes:** third-party tutorial material; see [Documentation/ATTRIBUTION.md](file:///Users/home/Software/Grok/PyMICE/Documentation/ATTRIBUTION.md)

## Getting started (developers)

### On UNIX (Linux / macOS):
```bash
# Clone and enter the repository
cd PyMICE

# Set up local virtual environment and install package in editable mode
bash Commands/setup_venv.sh
source Commands/.venv/bin/activate

# Run tests
pytest

# Compile visual parity reports
python Commands/run_vignettes.py
open Commands/output/index.html
```

### On Windows (Command Prompt / PowerShell):
```powershell
# Clone and enter the repository
cd PyMICE

# Set up local virtual environment
python -m venv Commands\.venv
Commands\.venv\Scripts\activate

# Install package with development dependencies
python -m pip install -e .[dev,plot,pandas,ml]

# Run tests
pytest

# Compile visual parity reports
python Commands/run_vignettes.py
# Open Commands\output\index.html in your browser
```

See [Commands/README.md](file:///Users/home/Software/Grok/PyMICE/Commands/README.md) for more details. This folder is excluded from the published package.