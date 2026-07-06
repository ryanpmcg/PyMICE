library("mice")
help(ampute)

# --- code block ---

set.seed(2016)
testdata <- as.data.frame(MASS::mvrnorm(n = 10000, 
                                        mu = c(10, 5, 0), 
                                        Sigma = matrix(data = c(1.0, 0.2, 0.2, 
                                                                0.2, 1.0, 0.2, 
                                                                0.2, 0.2, 1.0), 
                                                       nrow = 3, 
                                                       byrow = T)))
summary(testdata)

# --- code block ---

##        V1               V2               V3           
##  Min.   : 6.346   Min.   :0.9789   Min.   :-3.799124  
##  1st Qu.: 9.317   1st Qu.:4.3199   1st Qu.:-0.690542  
##  Median :10.003   Median :4.9963   Median :-0.009941  
##  Mean   : 9.998   Mean   :4.9973   Mean   : 0.000759  
##  3rd Qu.:10.677   3rd Qu.:5.6759   3rd Qu.: 0.673069  
##  Max.   :13.770   Max.   :8.6579   Max.   : 3.810729

# --- code block ---

result <- ampute(data = testdata)
class(result)

# --- code block ---

## [1] "mads"

# --- code block ---

head(result$amp)

# --- code block ---

##          V1       V2         V3
## 1        NA 6.018999  0.3681981
## 2  9.668991 4.391821 -1.1127595
## 3 10.273415 4.662521  0.1796964
## 4 10.124800 4.055544         NA
## 5        NA 7.171578  1.7141378
## 6 10.803311 5.038649         NA

# --- code block ---

names(result)

# --- code block ---

##  [1] "call"     "prop"     "patterns" "freq"     "mech"     "weights" 
##  [7] "cont"     "std"      "type"     "odds"     "amp"      "cand"    
## [13] "scores"   "data"

# --- code block ---

md.pattern(result$amp)

# --- code block ---

##        V3   V1   V2     
## 5014    1    1    1    0
## 1670    1    1    0    1
## 1670    1    0    1    1
## 1646    0    1    1    1
##      1646 1670 1670 4986

# --- code block ---

result$prop

# --- code block ---

## [1] 0.5

# --- code block ---

result <- ampute(testdata, prop = 0.2, bycases = FALSE)
md.pattern(result$amp)

# --- code block ---

##        V3   V1   V2     
## 4046    1    1    1    0
## 1998    1    1    0    1
## 1987    1    0    1    1
## 1969    0    1    1    1
##      1969 1987 1998 5954

# --- code block ---

result$prop

# --- code block ---

## [1] 0.6

# --- code block ---

mypatterns <- result$patterns
mypatterns

# --- code block ---

##   V1 V2 V3
## 1  0  1  1
## 2  1  0  1
## 3  1  1  0

# --- code block ---

mypatterns[2, 1] <- 0
mypatterns <- rbind(mypatterns, c(0, 1, 0))
mypatterns

# --- code block ---

##   V1 V2 V3
## 1  0  1  1
## 2  0  0  1
## 3  1  1  0
## 4  0  1  0

# --- code block ---

result <- ampute(testdata, patterns = mypatterns)
md.pattern(result$amp)

# --- code block ---

##        V2   V3   V1     
## 5079    1    1    1    0
## 1216    1    1    0    1
## 1248    1    0    1    1
## 1200    1    0    0    2
## 1257    0    1    0    2
##      1257 2448 3673 7378

# --- code block ---

result$freq

# --- code block ---

## [1] 0.25 0.25 0.25 0.25

# --- code block ---

myfreq <- c(0.7, 0.1, 0.1, 0.1)

# --- code block ---

result <- ampute(testdata, freq = myfreq, patterns = mypatterns)
md.pattern(result$amp)

# --- code block ---

##       V2  V3   V1     
## 4982   1   1    1    0
## 3555   1   1    0    1
## 524    1   0    1    1
## 473    1   0    0    2
## 466    0   1    0    2
##      466 997 4494 5957

# --- code block ---

result$mech

# --- code block ---

## [1] "MAR"

# --- code block ---

result$weights

# --- code block ---

##   V1 V2 V3
## 1  0  1  1
## 2  0  0  1
## 3  1  1  0
## 4  0  1  0

# --- code block ---

myweights <- result$weights
myweights[1, ] <- c(0, 0.8, 0.4)

# --- code block ---

myweights[3, ] <- c(3.0, 1.0, 0)
myweights

# --- code block ---

##   V1  V2  V3
## 1  0 0.8 0.4
## 2  0 0.0 1.0
## 3  3 1.0 0.0
## 4  0 1.0 0.0

# --- code block ---

result <- ampute(testdata, freq = myfreq, 
                 patterns = mypatterns, mech = "MNAR")
result$patterns

# --- code block ---

##   V1 V2 V3
## 1  0  1  1
## 2  0  0  1
## 3  1  1  0
## 4  0  1  0

# --- code block ---

result$weights

# --- code block ---

##   V1 V2 V3
## 1  1  0  0
## 2  1  1  0
## 3  0  0  1
## 4  1  0  1

# --- code block ---

bwplot(result, which.pat = 1, descriptives = TRUE)

# --- code block ---

## $Descriptives
## , , Variable =  V1
## 
##        Descriptives
## Pattern Amp     Mean     Var    N
##       1   1  0.11770 0.96079 3552
##       1   0 -0.12512 0.99905 3495
## 
## , , Variable =  V2
## 
##        Descriptives
## Pattern Amp     Mean     Var    N
##       1   1  0.36608 0.84028 3552
##       1   0 -0.39542 0.85435 3495
## 
## , , Variable =  V3
## 
##        Descriptives
## Pattern Amp     Mean     Var    N
##       1   1  0.22595 0.96457 3552
##       1   0 -0.26021 0.90809 3495
## 
## 
## $`Boxplot pattern 1`

# --- code block ---

BSDA::tsum.test(mean.x = 0.39077, mean.y = -0.38992, s.x = sqrt(0.83774), s.y = sqrt(0.87721), n.x = 3473, n.y = 3493)

# --- code block ---

## 
##  Welch Modified Two-Sample t-Test
## 
## data:  Summarized x and y
## t = 35.184, df = 6961.9, p-value < 2.2e-16
## alternative hypothesis: true difference in means is not equal to 0
## 95 percent confidence interval:
##  0.7371929 0.8241871
## sample estimates:
## mean of x mean of y 
##   0.39077  -0.38992

# --- code block ---

result <- ampute(testdata, freq = myfreq, patterns = mypatterns, 
                 weights = myweights, cont = TRUE, 
                 type = c("RIGHT", "TAIL", "MID", "LEFT"))
bwplot(result, which.pat = 2, descriptives = FALSE)

# --- code block ---

## $`Boxplot pattern 2`

# --- code block ---

xyplot(result, which.pat = 4)

# --- code block ---

## $`Scatterplot Pattern 4`

# --- code block ---

emptyresult <- ampute(testdata, run = FALSE)
emptyresult$amp

# --- code block ---

## data frame with 0 columns and 0 rows

# --- code block ---

data <- MASS::Boston
dim(data)

# --- code block ---

## [1] 506  14

# --- code block ---

# for instance for i = 1
# step 1 and 2
data_withoutvar1 <- data[, c(2:14)]
std_datawithoutvar1 <- scale(data_withoutvar1)

# step 3
# we generate only 1 pattern so the weights matrix has to contain 1 row
# specify the weights as desired
# here we use 1 for all variables, 
# indicating that we use all variables - i to create missingness in variable i 
# which is a MAR mechanism
weights <- matrix(rep(1, 13), nrow = 1)
my_scores <- apply(std_datawithoutvar1, 1, function (x) weights %*% x)

# step 4
# P has to be set to 2 for all rows in the dataset
# meaning that all rows are candidates for this pattern
# specify the probability distribution with argument type
# and the desired missingness proportion
mask_var1 <- ampute.continuous(P = rep(2, nrow(data_withoutvar1)),
                               scores = list(my_scores), prop = 0.3, type = "RIGHT")

# in the mask, 0 indicates the row should become incomplete, 
# 1 means the row should stay complete
mask_var1

# --- code block ---

## [[1]]
##   [1] 1 1 1 1 1 1 1 0 1 0 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1 0 0 1 1 1 1 0 1 1
##  [38] 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 1 1
##  [75] 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 1 1 1 1 1 1 1 1 1
## [112] 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1 0 0 0 1 0 0 1 0 1 0 0 0 0 0 0 0 0 1 0 1 1 0
## [149] 1 1 0 1 0 1 0 0 1 0 1 1 0 0 0 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
## [186] 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 0 0 0 0 1 1 1 0 1 0 1 0 1
## [223] 0 1 0 1 1 1 1 1 1 1 1 1 0 1 0 1 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 0 1 1 0 1 1
## [260] 1 1 1 0 1 1 1 1 1 1 0 1 1 1 0 1 1 0 0 1 1 1 1 0 0 0 1 1 1 0 1 1 1 1 1 1 1
## [297] 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1
## [334] 1 1 1 1 1 1 1 1 1 1 1 0 1 1 1 1 1 1 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0
## [371] 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
## [408] 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 0 0 1 1 0 1 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0
## [445] 1 0 0 0 0 0 1 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0
## [482] 0 0 0 0 0 0 0 0 0 0 0 0 1 1 1 1 1 1 1 0 1 1 1 1 1

# --- code block ---

my_pat <- matrix(c(rep(0, 5), rep(1, 9),
                   rep(1, 5), rep(0, 5), rep(1, 4),
                   rep(1, 10), rep(0, 4)), nrow = 3, byrow = TRUE)

# --- code block ---

solution2 <- ampute(data, prop = 0.3, patterns = my_pat)
md.pattern(solution2$amp, rotate.names = TRUE)

# --- code block ---

##     crim zn indus chas nox ptratio black lstat medv rm age dis rad tax    
## 346    1  1     1    1   1       1     1     1    1  1   1   1   1   1   0
## 60     1  1     1    1   1       1     1     1    1  0   0   0   0   0   5
## 50     1  1     1    1   1       0     0     0    0  1   1   1   1   1   4
## 50     0  0     0    0   0       1     1     1    1  1   1   1   1   1   5
##       50 50    50   50  50      50    50    50   50 60  60  60  60  60 750

# --- code block ---

# ampute the complete data once for every mechanism
ampdata1 <- ampute(testdata, patterns = c(0, 1, 1), prop = 0.2, mech = "MAR")$amp
ampdata2 <- ampute(testdata, patterns = c(1, 1, 0), prop = 0.8, mech = "MCAR")$amp

# create a random allocation vector
# use the prob argument to specify how much of each mechanism should be created
# here, 0.5 of the missingness should be MAR and 0.5 should be MCAR
indices <- sample(x = c(1, 2), size = nrow(testdata), 
                  replace = TRUE, prob = c(0.5, 0.5))

# create an empty data matrix
# fill this matrix with values from either of the two amputed datasets
ampdata <- matrix(NA, nrow = nrow(testdata), ncol = ncol(testdata))
ampdata[indices == 1, ] <- as.matrix(ampdata1[indices == 1, ])
ampdata[indices == 2, ] <- as.matrix(ampdata2[indices == 2, ])

# --- code block ---

myodds <- result$odds
myodds

# --- code block ---

##      [,1] [,2] [,3] [,4]
## [1,]    1    2    3    4
## [2,]    1    2    3    4
## [3,]    1    2    3    4
## [4,]    1    2    3    4

# --- code block ---

myodds[3, ] <- c(1, 0, 0, 1)
myodds[4, ] <- c(1, 1, 2, 2)
myodds <- cbind(myodds, matrix(c(NA, NA, NA, 1, NA, NA, NA, 1), nrow = 4, byrow = F))
myodds

# --- code block ---

##      [,1] [,2] [,3] [,4] [,5] [,6]
## [1,]    1    2    3    4   NA   NA
## [2,]    1    2    3    4   NA   NA
## [3,]    1    0    0    1   NA   NA
## [4,]    1    1    2    2    1    1

# --- code block ---

result <- ampute(testdata, freq = myfreq, patterns = mypatterns, 
                 weights = myweights, cont = FALSE, odds = myodds, prop = 0.3)
