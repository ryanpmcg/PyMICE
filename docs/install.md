# Install

## PyPI

```bash
pip install pymice
```

## Optional extras

```bash
pip install pymice[pandas]    # DataFrame API
pip install pymice[plot]      # matplotlib diagnostics
pip install pymice[ml]        # scikit-learn backends (lasso, lda)
pip install pymice[survival]  # Cox pooling (lifelines)
pip install pymice[dev]       # pytest, ruff, coverage
```

## Editable install (development)

```bash
git clone https://github.com/ryanpmcg/pymice.git
cd pymice
pip install -e ".[dev,plot,pandas,ml,survival,docs]"
```

**Requirements:** Python ≥ 3.10, NumPy ≥ 1.26, SciPy ≥ 1.11.