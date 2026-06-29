require(mice)
require(lattice)
require(pan)
set.seed(123)

# --- code block ---

con <- url("https://www.gerkovink.com/mimp/popular.RData")
load(con)

# --- code block ---

ls()

# --- code block ---

## [1] "con"                      "icc"                     
## [3] "mice.impute.2lonly.mean2" "popMCAR"                 
## [5] "popMCAR2"                 "popNCR"                  
## [7] "popNCR2"                  "popNCR3"                 
## [9] "popular"

# --- code block ---

head(popNCR)

# --- code block ---

##   pupil class extrav  sex texp popular popteach
## 1     1     1      5    1   NA     6.3       NA
## 2     2     1     NA    0   24     4.9       NA
## 3     3     1      4    1   NA     5.3        6
## 4     4     1      3 <NA>   NA     4.7        5
## 5     5     1      5    1   24      NA        6
## 6     6     1     NA    0   NA     4.7        5

# --- code block ---

dim(popNCR)

# --- code block ---

## [1] 2000    7

# --- code block ---

nrow(popNCR)

# --- code block ---

## [1] 2000

# --- code block ---

ncol(popNCR)

# --- code block ---

## [1] 7

# --- code block ---

summary(popNCR)

# --- code block ---

##      pupil           class          extrav         sex           texp     
##  Min.   : 1.00   17     :  26   Min.   : 1.000   0   :661   Min.   : 2.0  
##  1st Qu.: 6.00   63     :  25   1st Qu.: 4.000   1   :843   1st Qu.: 7.0  
##  Median :11.00   10     :  24   Median : 5.000   NA's:496   Median :12.0  
##  Mean   :10.65   15     :  24   Mean   : 5.313              Mean   :11.8  
##  3rd Qu.:16.00   4      :  23   3rd Qu.: 6.000              3rd Qu.:16.0  
##  Max.   :26.00   21     :  23   Max.   :10.000              Max.   :25.0  
##                  (Other):1855   NA's   :516                 NA's   :976   
##     popular         popteach     
##  Min.   :0.000   Min.   : 1.000  
##  1st Qu.:3.900   1st Qu.: 4.000  
##  Median :4.800   Median : 5.000  
##  Mean   :4.829   Mean   : 4.834  
##  3rd Qu.:5.800   3rd Qu.: 6.000  
##  Max.   :9.100   Max.   :10.000  
##  NA's   :510     NA's   :528

# --- code block ---

md.pattern(popNCR)

# --- code block ---

##     pupil class sex popular extrav popteach texp     
## 308     1     1   1       1      1        1    1    0
## 279     1     1   1       1      1        1    0    1
## 110     1     1   1       1      1        0    1    1
## 115     1     1   1       1      1        0    0    2
## 114     1     1   1       1      0        1    1    1
## 98      1     1   1       1      0        1    0    2
## 33      1     1   1       1      0        0    1    2
## 24      1     1   1       1      0        0    0    3
## 119     1     1   1       0      1        1    1    1
## 113     1     1   1       0      1        1    0    2
## 50      1     1   1       0      1        0    1    2
## 75      1     1   1       0      1        0    0    3
## 29      1     1   1       0      0        1    1    2
## 21      1     1   1       0      0        1    0    3
## 2       1     1   1       0      0        0    1    3
## 14      1     1   1       0      0        0    0    4
## 102     1     1   0       1      1        1    1    1
## 89      1     1   0       1      1        1    0    2
## 25      1     1   0       1      1        0    1    2
## 29      1     1   0       1      1        0    0    3
## 85      1     1   0       1      0        1    1    2
## 56      1     1   0       1      0        1    0    3
## 9       1     1   0       1      0        0    1    3
## 14      1     1   0       1      0        0    0    4
## 19      1     1   0       0      1        1    1    2
## 27      1     1   0       0      1        1    0    3
## 13      1     1   0       0      1        0    1    3
## 11      1     1   0       0      1        0    0    4
## 4       1     1   0       0      0        1    1    3
## 9       1     1   0       0      0        1    0    4
## 2       1     1   0       0      0        0    1    4
## 2       1     1   0       0      0        0    0    5
##         0     0 496     510    516      528  976 3026

# --- code block ---

md.pattern(popNCR[ , -5])

# --- code block ---

##     pupil class sex popular extrav popteach     
## 587     1     1   1       1      1        1    0
## 225     1     1   1       1      1        0    1
## 212     1     1   1       1      0        1    1
## 57      1     1   1       1      0        0    2
## 232     1     1   1       0      1        1    1
## 125     1     1   1       0      1        0    2
## 50      1     1   1       0      0        1    2
## 16      1     1   1       0      0        0    3
## 191     1     1   0       1      1        1    1
## 54      1     1   0       1      1        0    2
## 141     1     1   0       1      0        1    2
## 23      1     1   0       1      0        0    3
## 46      1     1   0       0      1        1    2
## 24      1     1   0       0      1        0    3
## 13      1     1   0       0      0        1    3
## 4       1     1   0       0      0        0    4
##         0     0 496     510    516      528 2050

# --- code block ---

is.na(popNCR$popular)

# --- code block ---

##    [1] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE
##   [13] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
##   [25] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##   [37]  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
##   [49] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##   [61] FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE
##   [73] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE
##   [85] FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE
##   [97] FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
##  [109] FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE
##  [121] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [133]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
##  [145] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [157]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [169]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
##  [181] FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [193]  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE
##  [205] FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE
##  [217]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [229] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [241] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE
##  [253]  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE
##  [265] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
##  [277]  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
##  [289] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE  TRUE
##  [301]  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
##  [313] FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
##  [325] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE
##  [337] FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [349] FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE
##  [361] FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE
##  [373] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
##  [385] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
##  [397] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
##  [409] FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [421] FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE FALSE  TRUE FALSE
##  [433] FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE
##  [445] FALSE FALSE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE FALSE  TRUE
##  [457]  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE
##  [469] FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
##  [481] FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [493] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE
##  [505] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE
##  [517] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE
##  [529] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [541] FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE
##  [553] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
##  [565]  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE  TRUE
##  [577] FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE
##  [589]  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
##  [601] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE
##  [613] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [625] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
##  [637] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE
##  [649]  TRUE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE
##  [661]  TRUE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE
##  [673] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
##  [685]  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE
##  [697]  TRUE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE
##  [709]  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
##  [721] FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE
##  [733] FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE FALSE
##  [745] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
##  [757] FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE
##  [769] FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE
##  [781] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE  TRUE
##  [793]  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE
##  [805] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
##  [817] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
##  [829] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [841]  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
##  [853] FALSE  TRUE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE
##  [865] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE
##  [877] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
##  [889]  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
##  [901]  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE
##  [913] FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
##  [925] FALSE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE
##  [937] FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
##  [949] FALSE  TRUE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
##  [961] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
##  [973] FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE  TRUE
##  [985] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
##  [997]  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE
## [1009] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1021] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1033] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE
## [1045]  TRUE  TRUE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE FALSE  TRUE FALSE
## [1057] FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
## [1069] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1081]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1093] FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE
## [1105] FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1117] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
## [1129] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1141] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE
## [1153] FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
## [1165] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE
## [1177] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
## [1189] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1201]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE
## [1213] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
## [1225] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE
## [1237] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1249] FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1261] FALSE FALSE FALSE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE FALSE
## [1273]  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE
## [1285] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE
## [1297] FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE
## [1309] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE
## [1321] FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE
## [1333]  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE
## [1345] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
## [1357] FALSE  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
## [1369] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE
## [1381] FALSE FALSE  TRUE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1393] FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE
## [1405]  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE
## [1417] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE
## [1429]  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1441]  TRUE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
## [1453]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
## [1465] FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE
## [1477]  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
## [1489] FALSE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
## [1501]  TRUE  TRUE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE
## [1513] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE
## [1525] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
## [1537]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1549]  TRUE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE
## [1561] FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE
## [1573] FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
## [1585] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
## [1597] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
## [1609] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1621] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1633] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1645] FALSE  TRUE  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE  TRUE
## [1657] FALSE  TRUE FALSE  TRUE FALSE  TRUE  TRUE FALSE  TRUE  TRUE  TRUE FALSE
## [1669]  TRUE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE
## [1681] FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE FALSE  TRUE FALSE FALSE
## [1693] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE
## [1705] FALSE  TRUE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE
## [1717] FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE
## [1729] FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1741] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
## [1753] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
## [1765] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
## [1777] FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE
## [1789]  TRUE FALSE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE  TRUE
## [1801]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
## [1813] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
## [1825] FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1837] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE
## [1849] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
## [1861] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1873] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1885] FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE  TRUE FALSE  TRUE  TRUE
## [1897] FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE  TRUE  TRUE FALSE
## [1909] FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE
## [1921]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [1933]  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
## [1945] FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE  TRUE
## [1957] FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE
## [1969] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
## [1981] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE
## [1993] FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE

# --- code block ---

histogram(~ popteach | is.na(popular), data=popNCR)

# --- code block ---

histogram(~ popteach | is.na(sex), data = popNCR)  

# --- code block ---

histogram(~ popteach | is.na(extrav), data = popNCR)

# --- code block ---

histogram(~ popteach | is.na(texp), data = popNCR)

# --- code block ---

histogram(~ popular | is.na(popteach), data = popNCR)

# --- code block ---

icc(aov(popular ~ as.factor(class), data = popNCR))

# --- code block ---

## [1] 0.328007

# --- code block ---

icc(aov(popteach ~ class, data = popNCR))

# --- code block ---

## [1] 0.3138658

# --- code block ---

icc(aov(texp ~ class, data = popNCR))

# --- code block ---

## [1] 1

# --- code block ---

ini <- mice(popNCR, maxit = 0)
meth <- ini$meth
meth

# --- code block ---

##    pupil    class   extrav      sex     texp  popular popteach 
##       ""       ""    "pmm" "logreg"    "pmm"    "pmm"    "pmm"

# --- code block ---

meth[c(3, 5, 6, 7)] <- "norm"
meth

# --- code block ---

##    pupil    class   extrav      sex     texp  popular popteach 
##       ""       ""   "norm" "logreg"   "norm"   "norm"   "norm"

# --- code block ---

pred <- ini$pred
pred

# --- code block ---

##          pupil class extrav sex texp popular popteach
## pupil        0     1      1   1    1       1        1
## class        1     0      1   1    1       1        1
## extrav       1     1      0   1    1       1        1
## sex          1     1      1   0    1       1        1
## texp         1     1      1   1    0       1        1
## popular      1     1      1   1    1       0        1
## popteach     1     1      1   1    1       1        0

# --- code block ---

pred[, "class"] <- 0
pred[, "pupil"] <- 0
pred

# --- code block ---

##          pupil class extrav sex texp popular popteach
## pupil        0     0      1   1    1       1        1
## class        0     0      1   1    1       1        1
## extrav       0     0      0   1    1       1        1
## sex          0     0      1   0    1       1        1
## texp         0     0      1   1    0       1        1
## popular      0     0      1   1    1       0        1
## popteach     0     0      1   1    1       1        0

# --- code block ---

imp1 <- mice(popNCR, meth = meth, pred = pred, print = FALSE)

# --- code block ---

summary(complete(imp1))

# --- code block ---

##      pupil           class          extrav       sex           texp       
##  Min.   : 1.00   17     :  26   Min.   : 1.000   0: 985   Min.   :-6.465  
##  1st Qu.: 6.00   63     :  25   1st Qu.: 4.139   1:1015   1st Qu.: 8.000  
##  Median :11.00   10     :  24   Median : 5.000            Median :12.253  
##  Mean   :10.65   15     :  24   Mean   : 5.269            Mean   :12.509  
##  3rd Qu.:16.00   4      :  23   3rd Qu.: 6.000            3rd Qu.:16.698  
##  Max.   :26.00   21     :  23   Max.   :10.000            Max.   :35.745  
##                  (Other):1855                                             
##     popular          popteach     
##  Min.   : 0.000   Min.   : 1.000  
##  1st Qu.: 4.100   1st Qu.: 4.000  
##  Median : 5.000   Median : 5.000  
##  Mean   : 5.006   Mean   : 5.021  
##  3rd Qu.: 5.971   3rd Qu.: 6.000  
##  Max.   :10.547   Max.   :10.000  
## 

# --- code block ---

summary(popNCR)

# --- code block ---

##      pupil           class          extrav         sex           texp     
##  Min.   : 1.00   17     :  26   Min.   : 1.000   0   :661   Min.   : 2.0  
##  1st Qu.: 6.00   63     :  25   1st Qu.: 4.000   1   :843   1st Qu.: 7.0  
##  Median :11.00   10     :  24   Median : 5.000   NA's:496   Median :12.0  
##  Mean   :10.65   15     :  24   Mean   : 5.313              Mean   :11.8  
##  3rd Qu.:16.00   4      :  23   3rd Qu.: 6.000              3rd Qu.:16.0  
##  Max.   :26.00   21     :  23   Max.   :10.000              Max.   :25.0  
##                  (Other):1855   NA's   :516                 NA's   :976   
##     popular         popteach     
##  Min.   :0.000   Min.   : 1.000  
##  1st Qu.:3.900   1st Qu.: 4.000  
##  Median :4.800   Median : 5.000  
##  Mean   :4.829   Mean   : 4.834  
##  3rd Qu.:5.800   3rd Qu.: 6.000  
##  Max.   :9.100   Max.   :10.000  
##  NA's   :510     NA's   :528

# --- code block ---

data.frame(vars = names(popNCR[c(6, 7, 5)]), 
           observed = c(icc(aov(popular ~ class, popNCR)), 
                        icc(aov(popteach ~ class, popNCR)), 
                        icc(aov(texp ~ class, popNCR))), 
           norm     = c(icc(aov(popular ~ class, complete(imp1))), 
                        icc(aov(popteach ~ class, complete(imp1))), 
                        icc(aov(texp ~ class, complete(imp1)))))

# --- code block ---

##       vars  observed      norm
## 1  popular 0.3280070 0.2798518
## 2 popteach 0.3138658 0.2639095
## 3     texp 1.0000000 0.4595004

# --- code block ---

pred <- ini$pred
pred[, "pupil"] <- 0
imp2 <- mice(popNCR, meth = meth, pred = pred, print = FALSE)

# --- code block ---

## Warning: Number of logged events: 90

# --- code block ---

data.frame(vars = names(popNCR[c(6, 7, 5)]), 
           observed  = c(icc(aov(popular ~ class, popNCR)), 
                         icc(aov(popteach ~ class, popNCR)), 
                         icc(aov(texp ~ class, popNCR))), 
           norm      = c(icc(aov(popular ~ class, complete(imp1))), 
                         icc(aov(popteach ~ class, complete(imp1))), 
                         icc(aov(texp ~ class, complete(imp1)))), 
           normclass = c(icc(aov(popular ~ class, complete(imp2))), 
                         icc(aov(popteach ~ class, complete(imp2))), 
                         icc(aov(texp ~ class, complete(imp2)))))

# --- code block ---

##       vars  observed      norm normclass
## 1  popular 0.3280070 0.2798518 0.3629046
## 2 popteach 0.3138658 0.2639095 0.3326133
## 3     texp 1.0000000 0.4595004 1.0000000

# --- code block ---

plot(imp2, c("popular", "texp", "popteach"))

# --- code block ---

imp3 <- mice.mids(imp2, maxit = 10)

# --- code block ---

## 
##  iter imp variable
##   6   1  extrav  sex  texp  popular  popteach
##   6   2  extrav  sex  texp  popular  popteach
##   6   3  extrav  sex  texp  popular  popteach
##   6   4  extrav  sex  texp  popular  popteach
##   6   5  extrav  sex  texp  popular  popteach
##   7   1  extrav  sex  texp  popular  popteach
##   7   2  extrav  sex  texp  popular  popteach
##   7   3  extrav  sex  texp  popular  popteach
##   7   4  extrav  sex  texp  popular  popteach
##   7   5  extrav  sex  texp  popular  popteach
##   8   1  extrav  sex  texp  popular  popteach
##   8   2  extrav  sex  texp  popular  popteach
##   8   3  extrav  sex  texp  popular  popteach
##   8   4  extrav  sex  texp  popular  popteach
##   8   5  extrav  sex  texp  popular  popteach
##   9   1  extrav  sex  texp  popular  popteach
##   9   2  extrav  sex  texp  popular  popteach
##   9   3  extrav  sex  texp  popular  popteach
##   9   4  extrav  sex  texp  popular  popteach
##   9   5  extrav  sex  texp  popular  popteach
##   10   1  extrav  sex  texp  popular  popteach
##   10   2  extrav  sex  texp  popular  popteach
##   10   3  extrav  sex  texp  popular  popteach
##   10   4  extrav  sex  texp  popular  popteach
##   10   5  extrav  sex  texp  popular  popteach
##   11   1  extrav  sex  texp  popular  popteach
##   11   2  extrav  sex  texp  popular  popteach
##   11   3  extrav  sex  texp  popular  popteach
##   11   4  extrav  sex  texp  popular  popteach
##   11   5  extrav  sex  texp  popular  popteach
##   12   1  extrav  sex  texp  popular  popteach
##   12   2  extrav  sex  texp  popular  popteach
##   12   3  extrav  sex  texp  popular  popteach
##   12   4  extrav  sex  texp  popular  popteach
##   12   5  extrav  sex  texp  popular  popteach
##   13   1  extrav  sex  texp  popular  popteach
##   13   2  extrav  sex  texp  popular  popteach
##   13   3  extrav  sex  texp  popular  popteach
##   13   4  extrav  sex  texp  popular  popteach
##   13   5  extrav  sex  texp  popular  popteach
##   14   1  extrav  sex  texp  popular  popteach
##   14   2  extrav  sex  texp  popular  popteach
##   14   3  extrav  sex  texp  popular  popteach
##   14   4  extrav  sex  texp  popular  popteach
##   14   5  extrav  sex  texp  popular  popteach
##   15   1  extrav  sex  texp  popular  popteach
##   15   2  extrav  sex  texp  popular  popteach
##   15   3  extrav  sex  texp  popular  popteach
##   15   4  extrav  sex  texp  popular  popteach
##   15   5  extrav  sex  texp  popular  popteach

# --- code block ---

plot(imp3, c("popular", "texp", "popteach"))

# --- code block ---

imp3b <- mice.mids(imp3, maxit = 20, print = FALSE)
plot(imp3b, c("popular", "texp", "popteach"))

# --- code block ---

densityplot(imp2)

# --- code block ---

densityplot(imp2, ~ popular)

# --- code block ---

densityplot(imp2, ~ popular | .imp)

# --- code block ---

complete(imp2, 1)[1:15, ]

# --- code block ---

##    pupil class   extrav sex texp  popular popteach
## 1      1     1 5.000000   1   24 6.300000 6.314991
## 2      2     1 3.616012   0   24 4.900000 4.343070
## 3      3     1 4.000000   1   24 5.300000 6.000000
## 4      4     1 3.000000   0   24 4.700000 5.000000
## 5      5     1 5.000000   1   24 5.656993 6.000000
## 6      6     1 3.564456   0   24 4.700000 5.000000
## 7      7     1 5.000000   0   24 5.900000 5.000000
## 8      8     1 4.000000   0   24 4.484762 4.389721
## 9      9     1 5.000000   0   24 4.686309 5.000000
## 10    10     1 5.000000   0   24 3.900000 3.000000
## 11    11     1 3.217854   1   24 5.700000 5.000000
## 12    12     1 5.000000   0   24 4.800000 5.000000
## 13    13     1 5.000000   0   24 5.000000 5.000000
## 14    14     1 5.000000   1   24 6.157194 6.000000
## 15    15     1 5.000000   1   24 6.000000 5.000000

# --- code block ---

head(complete(imp2, 1), n = 15)

# --- code block ---

##    pupil class   extrav sex texp  popular popteach
## 1      1     1 5.000000   1   24 6.300000 6.314991
## 2      2     1 3.616012   0   24 4.900000 4.343070
## 3      3     1 4.000000   1   24 5.300000 6.000000
## 4      4     1 3.000000   0   24 4.700000 5.000000
## 5      5     1 5.000000   1   24 5.656993 6.000000
## 6      6     1 3.564456   0   24 4.700000 5.000000
## 7      7     1 5.000000   0   24 5.900000 5.000000
## 8      8     1 4.000000   0   24 4.484762 4.389721
## 9      9     1 5.000000   0   24 4.686309 5.000000
## 10    10     1 5.000000   0   24 3.900000 3.000000
## 11    11     1 3.217854   1   24 5.700000 5.000000
## 12    12     1 5.000000   0   24 4.800000 5.000000
## 13    13     1 5.000000   0   24 5.000000 5.000000
## 14    14     1 5.000000   1   24 6.157194 6.000000
## 15    15     1 5.000000   1   24 6.000000 5.000000

# --- code block ---

imp4 <- mice(popNCR)

# --- code block ---

## 
##  iter imp variable
##   1   1  extrav  sex  texp  popular  popteach
##   1   2  extrav  sex  texp  popular  popteach
##   1   3  extrav  sex  texp  popular  popteach
##   1   4  extrav  sex  texp  popular  popteach
##   1   5  extrav  sex  texp  popular  popteach
##   2   1  extrav  sex  texp  popular  popteach
##   2   2  extrav  sex  texp  popular  popteach
##   2   3  extrav  sex  texp  popular  popteach
##   2   4  extrav  sex  texp  popular  popteach
##   2   5  extrav  sex  texp  popular  popteach
##   3   1  extrav  sex  texp  popular  popteach
##   3   2  extrav  sex  texp  popular  popteach
##   3   3  extrav  sex  texp  popular  popteach
##   3   4  extrav  sex  texp  popular  popteach
##   3   5  extrav  sex  texp  popular  popteach
##   4   1  extrav  sex  texp  popular  popteach
##   4   2  extrav  sex  texp  popular  popteach
##   4   3  extrav  sex  texp  popular  popteach
##   4   4  extrav  sex  texp  popular  popteach
##   4   5  extrav  sex  texp  popular  popteach
##   5   1  extrav  sex  texp  popular  popteach
##   5   2  extrav  sex  texp  popular  popteach
##   5   3  extrav  sex  texp  popular  popteach
##   5   4  extrav  sex  texp  popular  popteach
##   5   5  extrav  sex  texp  popular  popteach

# --- code block ---

## Warning: Number of logged events: 90

# --- code block ---

densityplot(imp4)

# --- code block ---

data.frame(vars      = names(popNCR[c(6, 7, 5)]), 
           observed  = c(icc(aov(popular ~ class, popNCR)), 
                         icc(aov(popteach ~ class, popNCR)), 
                         icc(aov(texp ~ class, popNCR))), 
           norm      = c(icc(aov(popular ~ class, complete(imp1))), 
                         icc(aov(popteach ~ class, complete(imp1))), 
                         icc(aov(texp ~ class, complete(imp1)))), 
           normclass = c(icc(aov(popular ~ class, complete(imp2))), 
                         icc(aov(popteach ~ class, complete(imp2))), 
                         icc(aov(texp ~ class, complete(imp2)))), 
           pmm       = c(icc(aov(popular ~ class, complete(imp4))), 
                         icc(aov(popteach ~ class, complete(imp4))), 
                         icc(aov(texp ~ class, complete(imp4)))), 
           orig      = c(icc(aov(popular ~ as.factor(class), popular)), 
                         icc(aov(popteach ~ as.factor(class), popular)), 
                         icc(aov(texp ~ as.factor(class), popular))))

# --- code block ---

##       vars  observed      norm normclass       pmm      orig
## 1  popular 0.3280070 0.2798518 0.3629046 0.3700960 0.3629933
## 2 popteach 0.3138658 0.2639095 0.3326133 0.3385374 0.3414766
## 3     texp 1.0000000 0.4595004 1.0000000 1.0000000 1.0000000

# --- code block ---

ini <- mice(popNCR2, maxit = 0)
pred <- ini$pred
pred["popular", ] <- c(0, -2, 2, 2, 2, 0, 2)

# --- code block ---

meth <- ini$meth
meth <- c("", "", "", "", "", "2l.norm", "")
imp5 <- mice(popNCR2, pred = pred, meth=meth, print = FALSE)

# --- code block ---

densityplot(imp5, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))

# --- code block ---

densityplot(imp4, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))

# --- code block ---

plot(density(popular$popular))  #true data 
lines(density(complete(imp5)$popular), col = "red", lwd = 2)  #2l.norm
lines(density(complete(imp4)$popular), col = "green", lwd = 2)  #PMM

# --- code block ---

plot(imp5)

# --- code block ---

imp5.b <- mice.mids(imp5, maxit = 10, print = FALSE)
plot(imp5.b)

# --- code block ---

ini <- mice(popNCR2, maxit = 0)
pred <- ini$pred
pred["popular", ] <- c(0, -2, 2, 2, 1, 0, 2)
meth <- ini$meth
meth <- c("", "", "", "", "", "2l.pan", "")
imp6 <- mice(popNCR2, pred = pred, meth = meth, print = FALSE)

# --- code block ---

densityplot(imp6, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))

# --- code block ---

densityplot(imp4, ~popular, ylim = c(0, 0.35), xlim = c(-1.5, 10))

# --- code block ---

plot(density(popular$popular), main = "black = truth | green = PMM | red = 2l.pan")  # 
lines(density(complete(imp6)$popular), col = "red", lwd = 2)  #2l.pan
lines(density(complete(imp4)$popular), col = "green", lwd = 2)  #PMM

# --- code block ---

plot(imp6)

# --- code block ---

imp6.b <- mice.mids(imp5, maxit = 10, print = FALSE)
plot(imp6.b)

# --- code block ---

ini <- mice(popNCR3, maxit = 0)
pred <- ini$pred
pred["extrav", ] <- c(0, -2, 0, 2, 2, 2, 2)  #2l.norm
pred["sex", ] <- c(0, 1, 1, 0, 1, 1, 1)  #2logreg
pred["texp", ] <- c(0, -2, 1, 1, 0, 1, 1)  #2lonly.mean
pred["popular", ] <- c(0, -2, 2, 2, 1, 0, 2)  #2l.pan
pred["popteach", ] <- c(0, -2, 2, 2, 1, 2, 0)  #2l.pan
meth <- ini$meth
meth <- c("", "", "2l.norm", "logreg", "2lonly.mean", "2l.pan", "2l.pan")
imp7 <- mice(popNCR3, pred = pred, meth = meth, print = FALSE)

# --- code block ---

densityplot(imp7)

# --- code block ---

plot(imp7)

# --- code block ---

pmmdata <- popNCR3
pmmdata$class <- as.factor(popNCR3$class)
imp8 <- mice(pmmdata, m = 5, print = FALSE)

# --- code block ---

## Warning: Number of logged events: 90

# --- code block ---

densityplot(imp8)

# --- code block ---

plot(imp8)
