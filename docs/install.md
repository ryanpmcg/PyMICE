# Install

## PyPI

```bash
pip install pymice-fcs
```

The PyPI distribution is **`pymice-fcs`**; import as `pymice`. This avoids unrelated packages [`pymice`](https://pypi.org/project/pymice/) (lab-mice behavioral data) and [`mice`](https://pypi.org/project/mice/) (stochastic optimization).

## Optional extras

```bash
pip install pymice-fcs[pandas]     # DataFrame API
pip install pymice-fcs[plot]       # matplotlib diagnostics
pip install pymice-fcs[ml]         # scikit-learn backends (lasso, lda)
pip install pymice-fcs[survival]   # Cox pooling (lifelines)
pip install pymice-fcs[dev]        # pytest, ruff, coverage
```

## Editable install (development)

```bash
git clone https://github.com/ryanpmcg/PyMICE.git
cd pymice
pip install -e ".[dev,plot,pandas,ml,survival,docs]"
```

**Requirements:** Python ≥ 3.10, NumPy ≥ 1.26, SciPy ≥ 1.11.