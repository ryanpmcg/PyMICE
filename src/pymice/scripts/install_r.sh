#!/usr/bin/env bash
# Install R and vignette CRAN packages for PyMICE (best-effort, non-interactive).
set -euo pipefail

install_r_base() {
  if command -v Rscript >/dev/null 2>&1; then
    return 0
  fi
  case "$(uname -s)" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        brew install r
      else
        echo "Homebrew not found. Install from https://brew.sh then re-run." >&2
        return 1
      fi
      ;;
    Linux)
      if command -v apt-get >/dev/null 2>&1; then
        sudo apt-get update -qq
        sudo apt-get install -y r-base r-base-dev
      elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y R
      elif command -v yum >/dev/null 2>&1; then
        sudo yum install -y R
      else
        echo "No supported Linux package manager found (apt/dnf/yum)." >&2
        return 1
      fi
      ;;
    MINGW*|MSYS*|CYGWIN*)
      if command -v choco >/dev/null 2>&1; then
        choco install r.project -y
      else
        echo "Chocolatey not found. Install R from https://cran.r-project.org/bin/windows/base/." >&2
        return 1
      fi
      ;;
    *)
      echo "Unsupported platform for automatic R install: $(uname -s)" >&2
      return 1
      ;;
  esac
}

install_r_base

Rscript -e '
repos <- "https://cloud.r-project.org"
need <- c("mice", "pan")
missing <- need[!vapply(need, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing)) {
  install.packages(missing, repos = repos, quiet = TRUE)
}
for (pkg in need) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    stop("Failed to install R package: ", pkg)
  }
}
cat("R prerequisites OK\n")
'