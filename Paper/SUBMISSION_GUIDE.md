# JOSS Submission and Publication Guide for PyMICE

This guide outlines the step-by-step process to submit and publish the `PyMICE` package to the **Journal of Open Source Software (JOSS)**.

---

## 1. Prerequisites Checklist

Before submitting to JOSS, ensure the repository meets the following mandatory criteria:

*   [x] **Open License:** PyMICE is licensed under the permissive **MIT License** (stored in `LICENSE` in the root directory).
*   [x] **No Placeholders:** All references, code examples, and docs are complete.
*   [x] **Tests and CI:** PyMICE has a complete suite of unit and parity tests under `tests/`. (Setting up a GitHub Action to run `pytest` on every push is highly recommended).
*   [x] **Documentation:** The repository contains detailed documentation (`README.md`, `agent.md`, and the generated HTML vignettes under `Commands/output/`).
*   [x] **Submission Files:** The JOSS paper draft (`paper.md`) and bibliography (`paper.bib`) are correctly located under the `Paper/` directory.

---

## 2. Submission Steps

Follow these steps to submit the paper to JOSS:

### Step A: Push code to a public GitHub repository
JOSS requires the codebase to be hosted publicly. Push the renamed repository to GitHub (e.g., `https://github.com/ryanpmcg/PyMICE`).

### Step B: Create a Release / Tag
Create a git tag representing your submission version:
```bash
git tag -a v0.1.0 -m "Initial release for JOSS submission"
git push origin v0.1.0
```

### Step C: Submit on the JOSS Portal
1.  Navigate to the JOSS submission page: [joss.theoj.org/papers/new](https://joss.theoj.org/papers/new).
2.  Log in using your **ORCID** credentials (or register a new ORCID iD if you do not have one).
3.  Fill in the submission form:
    *   **Repository URL:** `https://github.com/ryanpmcg/PyMICE`
    *   **Software Version:** `0.1.0` (or your current tag)
    *   **Title:** `PyMICE: A Python Package for Multivariate Imputation by Chained Equations with R Alignment`
    *   **Paper Directory:** `Paper` (this tells the JOSS compiler to look in the `Paper/` subdirectory for `paper.md` and `paper.bib`).
4.  Click **Submit Paper**.

---

## 3. The Review Process

JOSS uses a unique, open peer-review process conducted entirely on GitHub:

1.  **Pre-review Issue:** The JOSS editorial bot will automatically create a "Pre-review" issue on the JOSS GitHub repository.
2.  **PDF Compilation:** The bot will attempt to compile `paper.md` into a publication PDF. It will verify that all references in `paper.bib` resolve and are formatted correctly.
3.  **Editor Assignment:** An editor from the JOSS editorial board will be assigned. They will look for 2-3 independent reviewers (often users/developers of statistical packages in Python/R).
4.  **Review Thread:** A dedicated "Review" issue is opened on GitHub. Reviewers are given a checkbox list of criteria to verify:
    *   Does the installation succeed? (e.g., `pip install -e .`)
    *   Do the tests pass? (e.g., running `pytest`)
    *   Do the examples run and match the paper's claims? (e.g., running `python Demonstration/simulation_study.py` to check the bias/coverage results).
5.  **Addressing Feedback:** Any suggestions or bugs found by the reviewers will be reported as comments in the review issue. You can address them by pushing commits to your repository and responding to comments in the thread.

---

## 4. Finalizing Publication

Once the editor and reviewers approve the submission:

1.  **Archive the Repository:** To guarantee long-term reproducibility, JOSS requires archiving the final approved version of the codebase.
    *   Link your GitHub repository to **Zenodo** ([zenodo.org](https://zenodo.org)).
    *   Create a new release/tag on GitHub (e.g., `v0.1.1` or `v1.0.0`).
    *   Zenodo will automatically archive the release and issue a **persistent DOI**.
2.  **Provide the DOI:** Paste the Zenodo DOI into the JOSS review thread.
3.  **Publication:** The editor will close the review issue, and JOSS will publish your paper, issuing a JOSS DOI (e.g., `https://doi.org/10.21105/joss.XXXXX`). Your paper is now fully citable!
