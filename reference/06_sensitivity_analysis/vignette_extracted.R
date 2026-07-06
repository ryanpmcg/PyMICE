set.seed(123)
library("mice")
library("lattice")
library("survival")

# --- code block ---

summary(leiden)

# --- code block ---

##       sexe           lftanam           rrsyst         rrdiast      
##  Min.   :0.0000   Min.   : 85.48   Min.   : 90.0   Min.   : 50.00  
##  1st Qu.:0.0000   1st Qu.: 87.50   1st Qu.:135.0   1st Qu.: 75.00  
##  Median :0.0000   Median : 89.07   Median :150.0   Median : 80.00  
##  Mean   :0.2709   Mean   : 89.78   Mean   :152.9   Mean   : 82.78  
##  3rd Qu.:1.0000   3rd Qu.: 91.52   3rd Qu.:170.0   3rd Qu.: 90.00  
##  Max.   :1.0000   Max.   :103.54   Max.   :260.0   Max.   :140.00  
##                                    NA's   :121     NA's   :126     
##       dwa             survda            alb             chol       
##  Min.   :0.0000   Min.   :   2.0   Min.   :21.00   Min.   : 2.700  
##  1st Qu.:0.0000   1st Qu.: 534.8   1st Qu.:39.00   1st Qu.: 4.800  
##  Median :0.0000   Median :1196.5   Median :41.00   Median : 5.700  
##  Mean   :0.2437   Mean   :1195.4   Mean   :40.77   Mean   : 5.704  
##  3rd Qu.:0.0000   3rd Qu.:1889.0   3rd Qu.:43.00   3rd Qu.: 6.400  
##  Max.   :1.0000   Max.   :2610.0   Max.   :52.00   Max.   :10.900  
##                                    NA's   :229     NA's   :232     
##       mmse            woon      
##  Min.   : 1.00   Min.   :0.000  
##  1st Qu.:21.00   1st Qu.:0.000  
##  Median :26.00   Median :3.000  
##  Mean   :23.67   Mean   :1.775  
##  3rd Qu.:29.00   3rd Qu.:3.000  
##  Max.   :30.00   Max.   :4.000  
##  NA's   :85

# --- code block ---

str(leiden)

# --- code block ---

## 'data.frame':    956 obs. of  10 variables:
##  $ sexe   : num  0 0 0 0 0 0 0 1 1 0 ...
##  $ lftanam: num  87.8 87.8 89.1 90.3 87.8 ...
##  $ rrsyst : num  160 140 155 155 110 120 180 135 130 160 ...
##  $ rrdiast: num  100 70 85 90 60 80 75 80 60 90 ...
##  $ dwa    : num  0 0 0 0 0 0 0 0 0 0 ...
##  $ survda : num  1082 27 1604 528 1100 ...
##  $ alb    : num  41 NA 41 44 37 NA 42 NA 45 46 ...
##  $ chol   : num  4.4 NA 4.6 3.9 5.3 NA 7.2 NA 5.1 6.5 ...
##  $ mmse   : num  12 9 25 27 14 NA 28 26 30 14 ...
##  $ woon   : num  4 3 0 1 0 3 3 0 4 4 ...

# --- code block ---

head(leiden)

# --- code block ---

##   sexe lftanam rrsyst rrdiast dwa survda alb chol mmse woon
## 1    0   87.80    160     100   0   1082  41  4.4   12    4
## 2    0   87.75    140      70   0     27  NA   NA    9    3
## 3    0   89.08    155      85   0   1604  41  4.6   25    0
## 4    0   90.29    155      90   0    528  44  3.9   27    1
## 5    0   87.76    110      60   0   1100  37  5.3   14    0
## 6    0   91.39    120      80   0      5  NA   NA   NA    3

# --- code block ---

tail(leiden)

# --- code block ---

##      sexe lftanam rrsyst rrdiast dwa survda alb chol mmse woon
## 1229    1   93.85    130      70   0    523  40  5.3   28    0
## 1230    0   92.20    190      90   0   1182  44  5.8   26    3
## 1232    0   95.02    150      80   0    861  35  5.0   28    0
## 1233    0   88.30    120      60   0    129  42  8.6   21    0
## 1235    1   89.02    140      80   0    374  40  5.2   23    0
## 1236    0   85.70    130      65   0   1744  36  7.2   27    3

# --- code block ---

ini <- mice(leiden, maxit = 0)
ini$nmis

# --- code block ---

##    sexe lftanam  rrsyst rrdiast     dwa  survda     alb    chol    mmse 
##       0       0     121     126       0       0     229     232      85 
##    woon 
##       0

# --- code block ---

md.pattern(leiden)

# --- code block ---

##     sexe lftanam dwa survda woon mmse rrsyst rrdiast alb chol    
## 621    1       1   1      1    1    1      1       1   1    1   0
## 2      1       1   1      1    1    1      1       1   1    0   1
## 1      1       1   1      1    1    1      1       1   0    1   1
## 149    1       1   1      1    1    1      1       1   0    0   2
## 2      1       1   1      1    1    1      1       0   1    1   1
## 2      1       1   1      1    1    1      1       0   0    0   3
## 72     1       1   1      1    1    1      0       0   1    1   2
## 2      1       1   1      1    1    1      0       0   1    0   3
## 20     1       1   1      1    1    1      0       0   0    0   4
## 21     1       1   1      1    1    0      1       1   1    1   1
## 36     1       1   1      1    1    0      1       1   0    0   3
## 1      1       1   1      1    1    0      1       0   0    0   4
## 7      1       1   1      1    1    0      0       0   1    1   3
## 20     1       1   1      1    1    0      0       0   0    0   5
##        0       0   0      0    0   85    121     126 229  232 793

# --- code block ---

fx <- fluxplot(leiden)

# --- code block ---

fx

# --- code block ---

##              pobs     influx   outflux      ainb       aout      fico
## sexe    1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184
## lftanam 1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184
## rrsyst  0.8734310 0.09798107 0.5573770 0.7887971 0.05881570 0.2562874
## rrdiast 0.8682008 0.10231550 0.5422446 0.7910053 0.05756359 0.2518072
## dwa     1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184
## survda  1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184
## alb     0.7604603 0.19311053 0.2471627 0.8214459 0.02995568 0.1458047
## chol    0.7573222 0.19573400 0.2383354 0.8218391 0.02900552 0.1422652
## mmse    0.9110879 0.06798221 0.6796974 0.7790850 0.06875877 0.2870264
## woon    1.0000000 0.00000000 1.0000000 0.0000000 0.09216643 0.3504184

# --- code block ---

km <- survfit(Surv(survda/365, 1-dwa) ~ is.na(rrsyst), data = leiden) 
plot(km, 
     lty  = 1, 
     lwd  = 1.5, 
     xlab = "Years since intake",
     ylab = "K-M Survival probability", las=1, 
     col  = c(mdc(4), mdc(5)), 
     mark.time = FALSE)
text(4, 0.7, "BP measured")
text(2, 0.3, "BP missing")

# --- code block ---

delta <- c(0, -5, -10, -15, -20)

# --- code block ---

imp.all <- vector("list", length(delta))
post <- ini$post
for (i in 1:length(delta)){
  d <- delta[i]
  cmd <- paste("imp[[j]][,i] <- imp[[j]][,i] +", d)
  post["rrsyst"] <- cmd
  imp <- mice(leiden, post = post, maxit = 5, seed = i, print = FALSE)
  imp.all[[i]] <- imp
}

# --- code block ---

bwplot(imp.all[[1]])

# --- code block ---

bwplot(imp.all[[5]])

# --- code block ---

densityplot(imp.all[[1]], lwd = 3)

# --- code block ---

densityplot(imp.all[[5]], lwd = 3)

# --- code block ---

xyplot(imp.all[[1]], rrsyst ~ rrdiast | .imp)

# --- code block ---

xyplot(imp.all[[5]], rrsyst ~ rrdiast | .imp)

# --- code block ---

cda <- expression(
  sbpgp <- cut(rrsyst, breaks = c(50, 124, 144, 164, 184, 200, 500)),
  agegp <- cut(lftanam, breaks = c(85, 90, 95, 110)),
  dead  <- 1 - dwa,
  coxph(Surv(survda, dead) ~ C(sbpgp, contr.treatment(6, base = 3)) + strata(sexe, agegp))
  )

# --- code block ---

fit1 <- with(imp.all[[1]], cda)
fit2 <- with(imp.all[[2]], cda)
fit3 <- with(imp.all[[3]], cda)
fit4 <- with(imp.all[[4]], cda)
fit5 <- with(imp.all[[5]], cda)

# --- code block ---

fit3

# --- code block ---

## call :
## with.mids(data = imp.all[[3]], expr = cda)
## 
## call1 :
## mice(data = leiden, post = post, maxit = 5, printFlag = FALSE, 
##     seed = i)
## 
## nmis :
##    sexe lftanam  rrsyst rrdiast     dwa  survda     alb    chol    mmse 
##       0       0     121     126       0       0     229     232      85 
##    woon 
##       0 
## 
## analyses :
## [[1]]
## Call:
## coxph(formula = Surv(survda, dead) ~ C(sbpgp, contr.treatment(6, 
##     base = 3)) + strata(sexe, agegp))
## 
##                                             coef exp(coef) se(coef)      z
## C(sbpgp, contr.treatment(6, base = 3))1  0.49844   1.64616  0.11663  4.274
## C(sbpgp, contr.treatment(6, base = 3))2  0.34497   1.41194  0.10339  3.337
## C(sbpgp, contr.treatment(6, base = 3))4  0.07444   1.07728  0.11748  0.634
## C(sbpgp, contr.treatment(6, base = 3))5  0.09172   1.09606  0.14593  0.629
## C(sbpgp, contr.treatment(6, base = 3))6 -0.16959   0.84401  0.28744 -0.590
##                                                p
## C(sbpgp, contr.treatment(6, base = 3))1 1.92e-05
## C(sbpgp, contr.treatment(6, base = 3))2 0.000848
## C(sbpgp, contr.treatment(6, base = 3))4 0.526339
## C(sbpgp, contr.treatment(6, base = 3))5 0.529659
## C(sbpgp, contr.treatment(6, base = 3))6 0.555183
## 
## Likelihood ratio test=25.95  on 5 df, p=9.118e-05
## n= 956, number of events= 723 
## 
## [[2]]
## Call:
## coxph(formula = Surv(survda, dead) ~ C(sbpgp, contr.treatment(6, 
##     base = 3)) + strata(sexe, agegp))
## 
##                                             coef exp(coef) se(coef)      z
## C(sbpgp, contr.treatment(6, base = 3))1  0.57702   1.78073  0.11727  4.921
## C(sbpgp, contr.treatment(6, base = 3))2  0.36627   1.44235  0.10322  3.549
## C(sbpgp, contr.treatment(6, base = 3))4  0.09947   1.10458  0.12041  0.826
## C(sbpgp, contr.treatment(6, base = 3))5  0.10371   1.10928  0.14784  0.702
## C(sbpgp, contr.treatment(6, base = 3))6 -0.07801   0.92495  0.27835 -0.280
##                                                p
## C(sbpgp, contr.treatment(6, base = 3))1 8.63e-07
## C(sbpgp, contr.treatment(6, base = 3))2 0.000387
## C(sbpgp, contr.treatment(6, base = 3))4 0.408747
## C(sbpgp, contr.treatment(6, base = 3))5 0.482988
## C(sbpgp, contr.treatment(6, base = 3))6 0.779266
## 
## Likelihood ratio test=31.33  on 5 df, p=8.045e-06
## n= 956, number of events= 723 
## 
## [[3]]
## Call:
## coxph(formula = Surv(survda, dead) ~ C(sbpgp, contr.treatment(6, 
##     base = 3)) + strata(sexe, agegp))
## 
##                                             coef exp(coef) se(coef)      z
## C(sbpgp, contr.treatment(6, base = 3))1  0.50643   1.65936  0.11836  4.279
## C(sbpgp, contr.treatment(6, base = 3))2  0.34137   1.40687  0.10269  3.324
## C(sbpgp, contr.treatment(6, base = 3))4  0.07230   1.07497  0.11737  0.616
## C(sbpgp, contr.treatment(6, base = 3))5  0.08921   1.09331  0.14743  0.605
## C(sbpgp, contr.treatment(6, base = 3))6 -0.22193   0.80097  0.28780 -0.771
##                                                p
## C(sbpgp, contr.treatment(6, base = 3))1 1.88e-05
## C(sbpgp, contr.treatment(6, base = 3))2 0.000887
## C(sbpgp, contr.treatment(6, base = 3))4 0.537906
## C(sbpgp, contr.treatment(6, base = 3))5 0.545115
## C(sbpgp, contr.treatment(6, base = 3))6 0.440634
## 
## Likelihood ratio test=26.58  on 5 df, p=6.879e-05
## n= 956, number of events= 723 
## 
## [[4]]
## Call:
## coxph(formula = Surv(survda, dead) ~ C(sbpgp, contr.treatment(6, 
##     base = 3)) + strata(sexe, agegp))
## 
##                                             coef exp(coef) se(coef)      z
## C(sbpgp, contr.treatment(6, base = 3))1  0.52667   1.69329  0.11807  4.461
## C(sbpgp, contr.treatment(6, base = 3))2  0.37985   1.46206  0.10272  3.698
## C(sbpgp, contr.treatment(6, base = 3))4  0.04290   1.04383  0.11773  0.364
## C(sbpgp, contr.treatment(6, base = 3))5  0.09629   1.10107  0.14531  0.663
## C(sbpgp, contr.treatment(6, base = 3))6 -0.16181   0.85060  0.28752 -0.563
##                                                p
## C(sbpgp, contr.treatment(6, base = 3))1 8.17e-06
## C(sbpgp, contr.treatment(6, base = 3))2 0.000218
## C(sbpgp, contr.treatment(6, base = 3))4 0.715583
## C(sbpgp, contr.treatment(6, base = 3))5 0.507558
## C(sbpgp, contr.treatment(6, base = 3))6 0.573578
## 
## Likelihood ratio test=30.29  on 5 df, p=1.294e-05
## n= 956, number of events= 723 
## 
## [[5]]
## Call:
## coxph(formula = Surv(survda, dead) ~ C(sbpgp, contr.treatment(6, 
##     base = 3)) + strata(sexe, agegp))
## 
##                                             coef exp(coef) se(coef)      z
## C(sbpgp, contr.treatment(6, base = 3))1  0.55054   1.73419  0.11582  4.753
## C(sbpgp, contr.treatment(6, base = 3))2  0.36464   1.43999  0.10339  3.527
## C(sbpgp, contr.treatment(6, base = 3))4  0.06843   1.07083  0.12012  0.570
## C(sbpgp, contr.treatment(6, base = 3))5  0.09692   1.10177  0.14854  0.652
## C(sbpgp, contr.treatment(6, base = 3))6 -0.15071   0.86010  0.28786 -0.524
##                                                p
## C(sbpgp, contr.treatment(6, base = 3))1    2e-06
## C(sbpgp, contr.treatment(6, base = 3))2 0.000421
## C(sbpgp, contr.treatment(6, base = 3))4 0.568872
## C(sbpgp, contr.treatment(6, base = 3))5 0.514115
## C(sbpgp, contr.treatment(6, base = 3))6 0.600589
## 
## Likelihood ratio test=31.22  on 5 df, p=8.486e-06
## n= 956, number of events= 723

# --- code block ---

r1 <- as.vector(t(exp(summary(pool(fit1))[, c(1)])))
r2 <- as.vector(t(exp(summary(pool(fit2))[, c(1)])))
r3 <- as.vector(t(exp(summary(pool(fit3))[, c(1)])))
r4 <- as.vector(t(exp(summary(pool(fit4))[, c(1)])))
r5 <- as.vector(t(exp(summary(pool(fit5))[, c(1)])))

summary(pool(fit1))

# --- code block ---

##                                            estimate std.error  statistic
## C(sbpgp, contr.treatment(6, base = 3))1  0.56130514 0.1239289  4.5292516
## C(sbpgp, contr.treatment(6, base = 3))2  0.36831156 0.1061004  3.4713499
## C(sbpgp, contr.treatment(6, base = 3))4  0.08882521 0.1246379  0.7126659
## C(sbpgp, contr.treatment(6, base = 3))5  0.08784716 0.1571882  0.5588660
## C(sbpgp, contr.treatment(6, base = 3))6 -0.09953872 0.2751397 -0.3617752
##                                                 df      p.value
## C(sbpgp, contr.treatment(6, base = 3))1 2336.33678 6.216963e-06
## C(sbpgp, contr.treatment(6, base = 3))2  909.51401 5.422176e-04
## C(sbpgp, contr.treatment(6, base = 3))4  222.32292 4.767998e-01
## C(sbpgp, contr.treatment(6, base = 3))5   99.17335 5.775130e-01
## C(sbpgp, contr.treatment(6, base = 3))6 2620.13541 7.175492e-01

# --- code block ---

pars <- round(t(matrix(c(r1,r2,r3,r4,r5), nrow = 5)),2)
pars <- pars[, c(1, 2, 5)]
dimnames(pars) <- list(delta, c("<125", "125-140", ">200"))
pars

# --- code block ---

##     <125 125-140 >200
## 0   1.75    1.45 0.91
## -5  1.69    1.41 0.90
## -10 1.70    1.43 0.86
## -15 1.77    1.50 0.87
## -20 1.74    1.43 0.86

# --- code block ---

lm(sws ~ log10(bw) + odi)

# --- code block ---

delta <- c(8, 6, 4, 2, 0, -2, -4, -6, -8)
ini <- mice(mammalsleep[, -1], maxit=0, print=F)
meth<- ini$meth
meth["ts"]<- "~ I(sws + ps)"
pred <- ini$pred
pred[c("sws", "ps"), "ts"] <- 0
post <- ini$post
imp.all.undamped <- vector("list", length(delta))
for (i in 1:length(delta)) {
  d <- delta[i]
  cmd <- paste("imp[[j]][, i] <- imp[[j]][, i] +", d)
  post["sws"] <- cmd
  imp <- mice(mammalsleep[, -1], meth=meth, pred=pred, post = post, maxit = 10, seed = i * 22, print=FALSE)
  imp.all.undamped[[i]] <- imp
}
output <- sapply(imp.all.undamped, function(x) pool(with(x, lm(sws ~ log10(bw) + odi)))$qbar)
cbind(delta, as.data.frame(t(output)))

# --- code block ---

##   delta   V1   V2   V3   V4   V5   V6   V7   V8   V9
## 1     8 NULL NULL NULL NULL NULL NULL NULL NULL NULL
## 2     6 NULL NULL NULL NULL NULL NULL NULL NULL NULL
## 3     4 NULL NULL NULL NULL NULL NULL NULL NULL NULL
## 4     2 NULL NULL NULL NULL NULL NULL NULL NULL NULL
## 5     0 NULL NULL NULL NULL NULL NULL NULL NULL NULL
## 6    -2 NULL NULL NULL NULL NULL NULL NULL NULL NULL
## 7    -4 NULL NULL NULL NULL NULL NULL NULL NULL NULL
## 8    -6 NULL NULL NULL NULL NULL NULL NULL NULL NULL
## 9    -8 NULL NULL NULL NULL NULL NULL NULL NULL NULL

# --- code block ---

summary(mammalsleep$sws)

# --- code block ---

##    Min. 1st Qu.  Median    Mean 3rd Qu.    Max.    NA's 
##   2.100   6.250   8.350   8.673  11.000  17.900      14
