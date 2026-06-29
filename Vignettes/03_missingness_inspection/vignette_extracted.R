require(mice)
require(lattice)
set.seed(123)

# --- code block ---

help(boys)
?boys

# --- code block ---

head(boys)

# --- code block ---

##      age  hgt   wgt   bmi   hc  gen  phb tv   reg
## 3  0.035 50.1 3.650 14.54 33.7 <NA> <NA> NA south
## 4  0.038 53.5 3.370 11.77 35.0 <NA> <NA> NA south
## 18 0.057 50.0 3.140 12.56 35.2 <NA> <NA> NA south
## 23 0.060 54.5 4.270 14.37 36.7 <NA> <NA> NA south
## 28 0.062 57.5 5.030 15.21 37.3 <NA> <NA> NA south
## 36 0.068 55.5 4.655 15.11 37.0 <NA> <NA> NA south

# --- code block ---

nrow(boys)

# --- code block ---

## [1] 748

# --- code block ---

summary(boys)

# --- code block ---

##       age              hgt              wgt              bmi       
##  Min.   : 0.035   Min.   : 50.00   Min.   :  3.14   Min.   :11.77  
##  1st Qu.: 1.581   1st Qu.: 84.88   1st Qu.: 11.70   1st Qu.:15.90  
##  Median :10.505   Median :147.30   Median : 34.65   Median :17.45  
##  Mean   : 9.159   Mean   :132.15   Mean   : 37.15   Mean   :18.07  
##  3rd Qu.:15.267   3rd Qu.:175.22   3rd Qu.: 59.58   3rd Qu.:19.53  
##  Max.   :21.177   Max.   :198.00   Max.   :117.40   Max.   :31.74  
##                   NA's   :20       NA's   :4        NA's   :21     
##        hc          gen        phb            tv           reg     
##  Min.   :33.70   G1  : 56   P1  : 63   Min.   : 1.00   north: 81  
##  1st Qu.:48.12   G2  : 50   P2  : 40   1st Qu.: 4.00   east :161  
##  Median :53.00   G3  : 22   P3  : 19   Median :12.00   west :239  
##  Mean   :51.51   G4  : 42   P4  : 32   Mean   :11.89   south:191  
##  3rd Qu.:56.00   G5  : 75   P5  : 50   3rd Qu.:20.00   city : 73  
##  Max.   :65.00   NA's:503   P6  : 41   Max.   :25.00   NA's :  3  
##  NA's   :46                 NA's:503   NA's   :522

# --- code block ---

md.pattern(boys)

# --- code block ---

##     age reg wgt hgt bmi hc gen phb  tv     
## 223   1   1   1   1   1  1   1   1   1    0
## 19    1   1   1   1   1  1   1   1   0    1
## 1     1   1   1   1   1  1   1   0   1    1
## 1     1   1   1   1   1  1   0   1   0    2
## 437   1   1   1   1   1  1   0   0   0    3
## 43    1   1   1   1   1  0   0   0   0    4
## 16    1   1   1   0   0  1   0   0   0    5
## 1     1   1   1   0   0  0   0   0   0    6
## 1     1   1   0   1   0  1   0   0   0    5
## 1     1   1   0   0   0  1   1   1   1    3
## 1     1   1   0   0   0  0   1   1   1    4
## 1     1   1   0   0   0  0   0   0   0    7
## 3     1   0   1   1   1  1   0   0   0    4
##       0   3   4  20  21 46 503 503 522 1622

# --- code block ---

mpat <- md.pattern(boys)

# --- code block ---

sum(mpat[, "gen"] == 0)

# --- code block ---

## [1] 8

# --- code block ---

R <- is.na(boys$gen) 
R

# --- code block ---

##   [1]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
##  [12]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
##  [23]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
##  [34]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
##  [45]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
##  [56]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
##  [67]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
##  [78]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
##  [89]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [100]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [111]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [122]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [133]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [144]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [155]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [166]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [177]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [188]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [199]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [210]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [221]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [232]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [243]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [254]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [265]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [276]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [287]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [298]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [309]  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE
## [320]  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE
## [331] FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE FALSE FALSE
## [342] FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE
## [353] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE  TRUE  TRUE FALSE
## [364] FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE FALSE
## [375]  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE
## [386] FALSE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE
## [397] FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE
## [408] FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
## [419] FALSE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE  TRUE
## [430] FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE FALSE  TRUE
## [441] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE  TRUE
## [452]  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE
## [463] FALSE  TRUE  TRUE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE  TRUE
## [474] FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE
## [485] FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE FALSE
## [496]  TRUE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE  TRUE
## [507] FALSE FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE  TRUE
## [518]  TRUE FALSE FALSE FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE
## [529] FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE  TRUE
## [540]  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE
## [551]  TRUE FALSE FALSE  TRUE  TRUE  TRUE FALSE  TRUE  TRUE FALSE FALSE
## [562]  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE
## [573] FALSE  TRUE FALSE  TRUE FALSE FALSE FALSE  TRUE FALSE FALSE FALSE
## [584]  TRUE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE  TRUE  TRUE  TRUE
## [595] FALSE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE  TRUE FALSE
## [606] FALSE FALSE  TRUE  TRUE FALSE  TRUE FALSE FALSE  TRUE FALSE FALSE
## [617] FALSE  TRUE  TRUE FALSE FALSE FALSE FALSE FALSE  TRUE FALSE FALSE
## [628]  TRUE  TRUE  TRUE FALSE FALSE FALSE FALSE  TRUE  TRUE  TRUE FALSE
## [639] FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE FALSE FALSE  TRUE  TRUE
## [650]  TRUE  TRUE  TRUE FALSE  TRUE FALSE  TRUE  TRUE  TRUE FALSE  TRUE
## [661]  TRUE  TRUE  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE  TRUE FALSE
## [672]  TRUE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE
## [683]  TRUE FALSE  TRUE  TRUE  TRUE FALSE  TRUE FALSE  TRUE  TRUE  TRUE
## [694] FALSE FALSE  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE  TRUE
## [705]  TRUE  TRUE  TRUE FALSE FALSE FALSE  TRUE  TRUE FALSE  TRUE  TRUE
## [716]  TRUE FALSE FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE  TRUE
## [727] FALSE  TRUE FALSE FALSE  TRUE  TRUE FALSE FALSE FALSE  TRUE FALSE
## [738] FALSE  TRUE FALSE FALSE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE  TRUE

# --- code block ---

histogram(boys$gen)

# --- code block ---

histogram(~ gen, data = boys)

# --- code block ---

histogram(~age|R, data=boys)

# --- code block ---

imp1 <- mice(boys, print=FALSE)

# --- code block ---

summary(boys)

# --- code block ---

##       age              hgt              wgt              bmi       
##  Min.   : 0.035   Min.   : 50.00   Min.   :  3.14   Min.   :11.77  
##  1st Qu.: 1.581   1st Qu.: 84.88   1st Qu.: 11.70   1st Qu.:15.90  
##  Median :10.505   Median :147.30   Median : 34.65   Median :17.45  
##  Mean   : 9.159   Mean   :132.15   Mean   : 37.15   Mean   :18.07  
##  3rd Qu.:15.267   3rd Qu.:175.22   3rd Qu.: 59.58   3rd Qu.:19.53  
##  Max.   :21.177   Max.   :198.00   Max.   :117.40   Max.   :31.74  
##                   NA's   :20       NA's   :4        NA's   :21     
##        hc          gen        phb            tv           reg     
##  Min.   :33.70   G1  : 56   P1  : 63   Min.   : 1.00   north: 81  
##  1st Qu.:48.12   G2  : 50   P2  : 40   1st Qu.: 4.00   east :161  
##  Median :53.00   G3  : 22   P3  : 19   Median :12.00   west :239  
##  Mean   :51.51   G4  : 42   P4  : 32   Mean   :11.89   south:191  
##  3rd Qu.:56.00   G5  : 75   P5  : 50   3rd Qu.:20.00   city : 73  
##  Max.   :65.00   NA's:503   P6  : 41   Max.   :25.00   NA's :  3  
##  NA's   :46                 NA's:503   NA's   :522

# --- code block ---

summary(complete(imp1))

# --- code block ---

##       age              hgt              wgt              bmi       
##  Min.   : 0.035   Min.   : 50.00   Min.   :  3.14   Min.   :11.77  
##  1st Qu.: 1.581   1st Qu.: 83.53   1st Qu.: 11.70   1st Qu.:15.87  
##  Median :10.505   Median :145.75   Median : 34.65   Median :17.45  
##  Mean   : 9.159   Mean   :131.08   Mean   : 37.12   Mean   :18.03  
##  3rd Qu.:15.267   3rd Qu.:174.85   3rd Qu.: 59.35   3rd Qu.:19.44  
##  Max.   :21.177   Max.   :198.00   Max.   :117.40   Max.   :31.74  
##        hc        gen      phb            tv            reg     
##  Min.   :33.70   G1:394   P1:401   Min.   : 1.000   north: 81  
##  1st Qu.:48.45   G2: 72   P2: 62   1st Qu.: 2.000   east :162  
##  Median :53.10   G3: 34   P3: 28   Median : 3.000   west :240  
##  Mean   :51.62   G4: 91   P4: 66   Mean   : 8.445   south:192  
##  3rd Qu.:56.00   G5:157   P5: 94   3rd Qu.:15.000   city : 73  
##  Max.   :65.00            P6: 97   Max.   :25.000

# --- code block ---

summary(with(imp1, mean(tv)))

# --- code block ---

## Warning: 'tidy.numeric' is deprecated.
## See help("Deprecated")

## Warning: 'tidy.numeric' is deprecated.
## See help("Deprecated")

## Warning: 'tidy.numeric' is deprecated.
## See help("Deprecated")

## Warning: 'tidy.numeric' is deprecated.
## See help("Deprecated")

## Warning: 'tidy.numeric' is deprecated.
## See help("Deprecated")

# --- code block ---

## # A tibble: 5 x 1
##       x
##   <dbl>
## 1  8.45
## 2  8.43
## 3  8.41
## 4  8.62
## 5  8.14

# --- code block ---

help(mammalsleep)

# --- code block ---

head(mammalsleep)

# --- code block ---

##                     species       bw    brw sws  ps   ts  mls  gt pi sei
## 1          African elephant 6654.000 5712.0  NA  NA  3.3 38.6 645  3   5
## 2 African giant pouched rat    1.000    6.6 6.3 2.0  8.3  4.5  42  3   1
## 3                Arctic Fox    3.385   44.5  NA  NA 12.5 14.0  60  1   1
## 4    Arctic ground squirrel    0.920    5.7  NA  NA 16.5   NA  25  5   2
## 5            Asian elephant 2547.000 4603.0 2.1 1.8  3.9 69.0 624  3   5
## 6                    Baboon   10.550  179.5 9.1 0.7  9.8 27.0 180  4   4
##   odi
## 1   3
## 2   3
## 3   1
## 4   3
## 5   4
## 6   4

# --- code block ---

summary(mammalsleep)

# --- code block ---

##                       species         bw                brw         
##  African elephant         : 1   Min.   :   0.005   Min.   :   0.14  
##  African giant pouched rat: 1   1st Qu.:   0.600   1st Qu.:   4.25  
##  Arctic Fox               : 1   Median :   3.342   Median :  17.25  
##  Arctic ground squirrel   : 1   Mean   : 198.790   Mean   : 283.13  
##  Asian elephant           : 1   3rd Qu.:  48.203   3rd Qu.: 166.00  
##  Baboon                   : 1   Max.   :6654.000   Max.   :5712.00  
##  (Other)                  :56                                       
##       sws               ps              ts             mls         
##  Min.   : 2.100   Min.   :0.000   Min.   : 2.60   Min.   :  2.000  
##  1st Qu.: 6.250   1st Qu.:0.900   1st Qu.: 8.05   1st Qu.:  6.625  
##  Median : 8.350   Median :1.800   Median :10.45   Median : 15.100  
##  Mean   : 8.673   Mean   :1.972   Mean   :10.53   Mean   : 19.878  
##  3rd Qu.:11.000   3rd Qu.:2.550   3rd Qu.:13.20   3rd Qu.: 27.750  
##  Max.   :17.900   Max.   :6.600   Max.   :19.90   Max.   :100.000  
##  NA's   :14       NA's   :12      NA's   :4       NA's   :4        
##        gt               pi             sei             odi       
##  Min.   : 12.00   Min.   :1.000   Min.   :1.000   Min.   :1.000  
##  1st Qu.: 35.75   1st Qu.:2.000   1st Qu.:1.000   1st Qu.:1.000  
##  Median : 79.00   Median :3.000   Median :2.000   Median :2.000  
##  Mean   :142.35   Mean   :2.871   Mean   :2.419   Mean   :2.613  
##  3rd Qu.:207.50   3rd Qu.:4.000   3rd Qu.:4.000   3rd Qu.:4.000  
##  Max.   :645.00   Max.   :5.000   Max.   :5.000   Max.   :5.000  
##  NA's   :4

# --- code block ---

str(mammalsleep)

# --- code block ---

## 'data.frame':    62 obs. of  11 variables:
##  $ species: Factor w/ 62 levels "African elephant",..: 1 2 3 4 5 6 7 8 9 10 ...
##  $ bw     : num  6654 1 3.38 0.92 2547 ...
##  $ brw    : num  5712 6.6 44.5 5.7 4603 ...
##  $ sws    : num  NA 6.3 NA NA 2.1 9.1 15.8 5.2 10.9 8.3 ...
##  $ ps     : num  NA 2 NA NA 1.8 0.7 3.9 1 3.6 1.4 ...
##  $ ts     : num  3.3 8.3 12.5 16.5 3.9 9.8 19.7 6.2 14.5 9.7 ...
##  $ mls    : num  38.6 4.5 14 NA 69 27 19 30.4 28 50 ...
##  $ gt     : num  645 42 60 25 624 180 35 392 63 230 ...
##  $ pi     : int  3 3 1 5 3 4 1 4 1 1 ...
##  $ sei    : int  5 1 1 2 5 4 1 5 2 1 ...
##  $ odi    : int  3 3 1 3 4 4 1 4 1 1 ...

# --- code block ---

md.pattern(mammalsleep)

# --- code block ---

##    species bw brw pi sei odi ts mls gt ps sws   
## 42       1  1   1  1   1   1  1   1  1  1   1  0
## 9        1  1   1  1   1   1  1   1  1  0   0  2
## 3        1  1   1  1   1   1  1   1  0  1   1  1
## 2        1  1   1  1   1   1  1   0  1  1   1  1
## 1        1  1   1  1   1   1  1   0  1  0   0  3
## 1        1  1   1  1   1   1  1   0  0  1   1  2
## 2        1  1   1  1   1   1  0   1  1  1   0  2
## 2        1  1   1  1   1   1  0   1  1  0   0  3
##          0  0   0  0   0   0  4   4  4 12  14 38

# --- code block ---

imp <- mice(mammalsleep, maxit = 10, print=F)

# --- code block ---

## Warning: Number of logged events: 525

# --- code block ---

plot(imp)

# --- code block ---

fit1 <- with(imp, lm(sws ~ log10(bw) + odi), print=F)

# --- code block ---

pool(fit1)

# --- code block ---

## Class: mipo    m = 5 
##               estimate       ubar          b         t dfcom        df
## (Intercept) 10.0739157 0.71206627 0.83964136 1.7196359    59  7.805051
## log10(bw)   -1.4513424 0.10052200 0.30175131 0.4626236    59  4.277824
## odi         -0.5504494 0.08902854 0.01146902 0.1027914    59 40.480414
##                   riv    lambda       fmi
## (Intercept) 1.4149942 0.5859203 0.6625659
## log10(bw)   3.6022121 0.7827132 0.8424252
## odi         0.1545889 0.1338909 0.1737299

# --- code block ---

summary(pool(fit1))

# --- code block ---

##               estimate std.error statistic        df      p.value
## (Intercept) 10.0739157 1.3113489  7.682102  7.805051 6.666925e-05
## log10(bw)   -1.4513424 0.6801644 -2.133811  4.277824 9.530451e-02
## odi         -0.5504494 0.3206109 -1.716876 40.480414 9.364526e-02

# --- code block ---

impnew <- mice(mammalsleep[ , -1], maxit = 10, print = F)

# --- code block ---

## Warning: Number of logged events: 18

# --- code block ---

fit2 <- with(impnew, lm(sws ~ log10(bw) + odi))
pool(fit2)

# --- code block ---

## Class: mipo    m = 5 
##               estimate       ubar           b          t dfcom       df
## (Intercept) 11.5358123 0.62179318 0.013395200 0.63786742    59 55.17044
## log10(bw)   -1.0908770 0.08777820 0.001202722 0.08922146    59 55.96750
## odi         -0.8745217 0.07774184 0.001686524 0.07976567    59 55.15415
##                    riv     lambda        fmi
## (Intercept) 0.02585143 0.02519997 0.05871528
## log10(bw)   0.01644219 0.01617622 0.04954456
## odi         0.02603268 0.02537217 0.05889094

# --- code block ---

summary(pool(fit2))

# --- code block ---

##               estimate std.error statistic       df      p.value
## (Intercept) 11.5358123 0.7986660 14.443850 55.17044 0.0000000000
## log10(bw)   -1.0908770 0.2986996 -3.652087 55.96750 0.0005739797
## odi         -0.8745217 0.2824282 -3.096439 55.15415 0.0030767681

# --- code block ---

plot(impnew)
