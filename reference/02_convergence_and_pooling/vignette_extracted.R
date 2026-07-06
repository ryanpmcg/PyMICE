require(mice)
require(lattice)
set.seed(123)

# --- code block ---

imp <- mice(nhanes, m = 3, print=F)

# --- code block ---

imp$pred

# --- code block ---

##     age bmi hyp chl
## age   0   1   1   1
## bmi   1   0   1   1
## hyp   1   1   0   1
## chl   1   1   1   0

# --- code block ---

ini <- mice(nhanes, maxit=0, print=F)
pred <- ini$pred
pred

# --- code block ---

##     age bmi hyp chl
## age   0   1   1   1
## bmi   1   0   1   1
## hyp   1   1   0   1
## chl   1   1   1   0

# --- code block ---

pred[ ,"hyp"] <- 0
pred

# --- code block ---

##     age bmi hyp chl
## age   0   1   0   1
## bmi   1   0   0   1
## hyp   1   1   0   1
## chl   1   1   0   0

# --- code block ---

imp <- mice(nhanes, pred=pred, print=F)

# --- code block ---

ini <- mice(nhanes, pred=quickpred(nhanes, mincor=.3), print=F)
ini$pred

# --- code block ---

##     age bmi hyp chl
## age   0   0   0   0
## bmi   1   0   0   1
## hyp   1   0   0   1
## chl   1   1   1   0

# --- code block ---

imp <- mice(nhanes, print=F)
plot(imp)

# --- code block ---

imp <- mice(nhanes, seed=123, print=F)

# --- code block ---

imp$meth

# --- code block ---

##   age   bmi   hyp   chl 
##    "" "pmm" "pmm" "pmm"

# --- code block ---

summary(nhanes2)

# --- code block ---

##     age          bmi          hyp          chl       
##  20-39:12   Min.   :20.40   no  :13   Min.   :113.0  
##  40-59: 7   1st Qu.:22.65   yes : 4   1st Qu.:185.0  
##  60-99: 6   Median :26.75   NA's: 8   Median :187.0  
##             Mean   :26.56             Mean   :191.4  
##             3rd Qu.:28.93             3rd Qu.:212.0  
##             Max.   :35.30             Max.   :284.0  
##             NA's   :9                 NA's   :10

# --- code block ---

str(nhanes2)

# --- code block ---

## 'data.frame':    25 obs. of  4 variables:
##  $ age: Factor w/ 3 levels "20-39","40-59",..: 1 2 1 3 1 3 1 1 2 2 ...
##  $ bmi: num  NA 22.7 NA NA 20.4 NA 22.5 30.1 22 NA ...
##  $ hyp: Factor w/ 2 levels "no","yes": NA 1 1 NA 1 NA 1 1 1 NA ...
##  $ chl: num  NA 187 187 NA 113 184 118 187 238 NA ...

# --- code block ---

imp <- mice(nhanes2, print=F)
imp$meth

# --- code block ---

##      age      bmi      hyp      chl 
##       ""    "pmm" "logreg"    "pmm"

# --- code block ---

methods(mice)

# --- code block ---

##  [1] mice.impute.2l.bin       mice.impute.2l.lmer     
##  [3] mice.impute.2l.norm      mice.impute.2l.pan      
##  [5] mice.impute.2lonly.mean  mice.impute.2lonly.norm 
##  [7] mice.impute.2lonly.pmm   mice.impute.cart        
##  [9] mice.impute.jomoImpute   mice.impute.lda         
## [11] mice.impute.logreg       mice.impute.logreg.boot 
## [13] mice.impute.mean         mice.impute.midastouch  
## [15] mice.impute.norm         mice.impute.norm.boot   
## [17] mice.impute.norm.nob     mice.impute.norm.predict
## [19] mice.impute.panImpute    mice.impute.passive     
## [21] mice.impute.pmm          mice.impute.polr        
## [23] mice.impute.polyreg      mice.impute.quadratic   
## [25] mice.impute.rf           mice.impute.ri          
## [27] mice.impute.sample       mice.mids               
## [29] mice.theme              
## see '?methods' for accessing help and source code

# --- code block ---

ini <- mice(nhanes2, maxit = 0)
meth <- ini$meth
meth

# --- code block ---

##      age      bmi      hyp      chl 
##       ""    "pmm" "logreg"    "pmm"

# --- code block ---

meth["bmi"] <- "norm"
meth

# --- code block ---

##      age      bmi      hyp      chl 
##       ""   "norm" "logreg"    "pmm"

# --- code block ---

imp <- mice(nhanes2, meth = meth, print=F)

# --- code block ---

plot(imp)

# --- code block ---

imp40 <- mice.mids(imp, maxit=35, print=F)
plot(imp40)

# --- code block ---

stripplot(imp, chl~.imp, pch=20, cex=2)

# --- code block ---

stripplot(imp)

# --- code block ---

fit <- with(imp, lm(bmi ~ chl))
fit

# --- code block ---

## call :
## with.mids(data = imp, expr = lm(bmi ~ chl))
## 
## call1 :
## mice(data = nhanes2, method = meth, printFlag = F)
## 
## nmis :
## age bmi hyp chl 
##   0   9   8  10 
## 
## analyses :
## [[1]]
## 
## Call:
## lm(formula = bmi ~ chl)
## 
## Coefficients:
## (Intercept)          chl  
##     22.9566       0.0228  
## 
## 
## [[2]]
## 
## Call:
## lm(formula = bmi ~ chl)
## 
## Coefficients:
## (Intercept)          chl  
##    22.92350      0.02162  
## 
## 
## [[3]]
## 
## Call:
## lm(formula = bmi ~ chl)
## 
## Coefficients:
## (Intercept)          chl  
##    17.80342      0.04999  
## 
## 
## [[4]]
## 
## Call:
## lm(formula = bmi ~ chl)
## 
## Coefficients:
## (Intercept)          chl  
##    24.11469      0.01458  
## 
## 
## [[5]]
## 
## Call:
## lm(formula = bmi ~ chl)
## 
## Coefficients:
## (Intercept)          chl  
##    19.60360      0.03567

# --- code block ---

class(fit)

# --- code block ---

## [1] "mira"   "matrix"

# --- code block ---

ls(fit)

# --- code block ---

## [1] "analyses" "call"     "call1"    "nmis"

# --- code block ---

summary(fit$analyses[[2]])

# --- code block ---

## 
## Call:
## lm(formula = bmi ~ chl)
## 
## Residuals:
##     Min      1Q  Median      3Q     Max 
## -6.0682 -2.9742  0.4558  2.4361  7.6641 
## 
## Coefficients:
##             Estimate Std. Error t value Pr(>|t|)    
## (Intercept) 22.92350    3.56198   6.436 1.44e-06 ***
## chl          0.02162    0.01800   1.201    0.242    
## ---
## Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1
## 
## Residual standard error: 3.917 on 23 degrees of freedom
## Multiple R-squared:  0.05898,    Adjusted R-squared:  0.01807 
## F-statistic: 1.442 on 1 and 23 DF,  p-value: 0.2421

# --- code block ---

pool.fit <- pool(fit)
summary(pool.fit)

# --- code block ---

##               estimate  std.error statistic       df     p.value
## (Intercept) 21.4803588 5.35840067  4.008726 11.28773 0.001953701
## chl          0.0289319 0.02742604  1.054906 10.73032 0.314641727
