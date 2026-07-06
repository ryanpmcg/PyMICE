#!/usr/bin/env Rscript
# Persistent RNG server for PyMICE (R default Mersenne-Twister).
# Protocol: one command per line on stdin; one whitespace-separated response line on stdout.
# Commands:
#   seed <int>
#   runif <n> [<min> <max>]
#   rnorm <n> [<mean> <sd>]
#   rchisq <n> <df>
#   rchisqv <n> <df1> <df2> ...   # n draws with distinct df
#   rgamma <n> <shape> <scale>
#   rgammav <n> <shape1> <scale1> <shape2> <scale2> ...
#   rint <n> <low> <high>   # integers inclusive
#   perm <n>                # 0-based permutation of 0:(n-1)
#   rbinom <n> <size> <prob>
#   choice <n> <x1> <x2> ...  # sample with replacement from listed values
#   choicep <n> <p1> <p2> ... <x1> <x2> ...  # probs then values
#   quit

invisible(lapply(c("stats"), require, character.only = TRUE))

respond <- function(values) {
  if (length(values) == 0) {
    cat("ERR empty result\n")
  } else {
    cat(paste(values, collapse = " "), "\n", sep = "")
  }
  flush.console()
}

handle <- function(line) {
  parts <- strsplit(trimws(line), " ", fixed = TRUE)[[1]]
  op <- parts[1]
  if (op == "seed") {
    set.seed(as.integer(parts[2]))
    return(invisible(NULL))
  }
  if (op == "runif") {
    n <- as.integer(parts[2])
    if (length(parts) >= 5) {
      return(runif(n, min = as.numeric(parts[3]), max = as.numeric(parts[4])))
    }
    return(runif(n))
  }
  if (op == "rnorm") {
    n <- as.integer(parts[2])
    if (length(parts) >= 5) {
      return(rnorm(n, mean = as.numeric(parts[3]), sd = as.numeric(parts[4])))
    }
    return(rnorm(n))
  }
  if (op == "rchisq") {
    return(rchisq(as.integer(parts[2]), df = as.numeric(parts[3])))
  }
  if (op == "rchisqv") {
    n <- as.integer(parts[2])
    dfs <- as.numeric(parts[3:(2 + n)])
    return(rchisq(n, df = dfs))
  }
  if (op == "rgamma") {
    return(rgamma(as.integer(parts[2]), shape = as.numeric(parts[3]), scale = as.numeric(parts[4])))
  }
  if (op == "rgammav") {
    n <- as.integer(parts[2])
    shapes <- as.numeric(parts[3:(2 + n)])
    scales <- as.numeric(parts[(3 + n):(2 + 2 * n)])
    return(rgamma(n, shape = shapes, scale = scales))
  }
  if (op == "rint") {
    n <- as.integer(parts[2])
    low <- as.integer(parts[3])
    high <- as.integer(parts[4])
    return(sample(low:high, n, replace = TRUE))
  }
  if (op == "perm") {
    n <- as.integer(parts[2])
    return(sample.int(n, n, replace = FALSE) - 1L)
  }
  if (op == "rbinom") {
    return(rbinom(as.integer(parts[2]), size = as.integer(parts[3]), prob = as.numeric(parts[4])))
  }
  if (op == "choice") {
    n <- as.integer(parts[2])
    vals <- as.numeric(parts[3:length(parts)])
    return(sample(vals, n, replace = TRUE))
  }
  if (op == "choicep") {
    n <- as.integer(parts[2])
    k <- as.integer(parts[3])
    probs <- as.numeric(parts[4:(3 + k)])
    vals <- as.numeric(parts[(4 + k):length(parts)])
    return(sample(vals, n, replace = TRUE, prob = probs))
  }
  stop(paste("unknown command:", op))
}

cat("OK\n")
flush.console()
repeat {
  line <- readLines(file("stdin"), n = 1, warn = FALSE)
  if (length(line) == 0 || identical(line, "quit")) {
    break
  }
  out <- tryCatch(
    {
      vals <- handle(line)
      if (is.null(vals)) {
        ""
      } else {
        paste(vals, collapse = " ")
      }
    },
    error = function(e) paste0("ERR ", conditionMessage(e))
  )
  cat(out, "\n", sep = "")
  flush.console()
}