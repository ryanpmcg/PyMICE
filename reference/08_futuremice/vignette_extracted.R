set.seed(123)

small_covmat <- diag(4)
small_covmat[small_covmat == 0] <- 0.5
small_data <- MASS::mvrnorm(1000, 
                      mu = c(0, 0, 0, 0),
                      Sigma = small_covmat)

small_data_with_missings <- ampute(small_data, prop = 0.8, mech = "MCAR")$amp
head(small_data_with_missings)

# --- code block ---

imp <- futuremice(nhanes)

# --- code block ---

## Number of cores not specified. Based on your machine a value of n.core = 3 is chosen; the imputations are distributed about equally over the cores.

# --- code block ---

class(imp)

# --- code block ---

## [1] "mids"

# --- code block ---

imp$call

# --- code block ---

## [[1]]
## mice(data = data, m = x, printFlag = F, seed = seed)
## 
## [[2]]
## ibind(x = imp, y = imps[[i]])
## 
## [[3]]
## ibind(x = imp, y = imps[[i]])

# --- code block ---

imp$parallelseed

# --- code block ---

## [1] 198128673

# --- code block ---

imp <- futuremice(nhanes, method = "norm")

# --- code block ---

## Number of cores not specified. Based on your machine a value of n.core = 3 is chosen; the imputations are distributed about equally over the cores.

# --- code block ---

imp$method

# --- code block ---

##    age    bmi    hyp    chl 
##     "" "norm" "norm" "norm"

# --- code block ---

parallelly::availableCores(logical = TRUE)

# --- code block ---

## system 
##      4

# --- code block ---

imp$m

# --- code block ---

library(magrittr)
set.seed(123)
imp1 <- futuremice(nhanes, n.core = 3)
set.seed(123)
imp2 <- futuremice(nhanes, n.core = 3)

imp1 %$% lm(chl ~ bmi) %>% pool %$% pooled

# --- code block ---

imp2 %$% lm(chl ~ bmi) %>% pool %$% pooled

# --- code block ---

imp3 <- futuremice(nhanes, parallelseed = 123, n.core = 3)
imp4 <- futuremice(nhanes, parallelseed = 123, n.core = 3)

imp3 %$% lm(chl ~ bmi) %>% pool %$% pooled

# --- code block ---

imp4 %$% lm(chl ~ bmi) %>% pool %$% pooled

# --- code block ---

imp5 <- futuremice(nhanes, n.core = 3)
parallelseed <- imp5$parallelseed
imp6 <- futuremice(nhanes, parallelseed = parallelseed, n.core = 3)

imp5 %$% lm(chl ~ bmi) %>% pool %$% pooled

# --- code block ---

imp6 %$% lm(chl ~ bmi) %>% pool %$% pooled
