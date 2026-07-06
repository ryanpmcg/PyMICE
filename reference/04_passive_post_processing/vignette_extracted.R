require(mice)
require(lattice)
set.seed(123)

# --- code block ---

ini <- mice(mammalsleep[, -1], maxit=0, print=F)
meth<- ini$meth
meth

# --- code block ---

##    bw   brw   sws    ps    ts   mls    gt    pi   sei   odi 
##    ""    "" "pmm" "pmm" "pmm" "pmm" "pmm"    ""    ""    ""

# --- code block ---

pred <- ini$pred
pred

# --- code block ---

##     bw brw sws ps ts mls gt pi sei odi
## bw   0   1   1  1  1   1  1  1   1   1
## brw  1   0   1  1  1   1  1  1   1   1
## sws  1   1   0  1  1   1  1  1   1   1
## ps   1   1   1  0  1   1  1  1   1   1
## ts   1   1   1  1  0   1  1  1   1   1
## mls  1   1   1  1  1   0  1  1   1   1
## gt   1   1   1  1  1   1  0  1   1   1
## pi   1   1   1  1  1   1  1  0   1   1
## sei  1   1   1  1  1   1  1  1   0   1
## odi  1   1   1  1  1   1  1  1   1   0

# --- code block ---

pred[c("sws", "ps"), "ts"] <- 0
pred

# --- code block ---

##     bw brw sws ps ts mls gt pi sei odi
## bw   0   1   1  1  1   1  1  1   1   1
## brw  1   0   1  1  1   1  1  1   1   1
## sws  1   1   0  1  0   1  1  1   1   1
## ps   1   1   1  0  0   1  1  1   1   1
## ts   1   1   1  1  0   1  1  1   1   1
## mls  1   1   1  1  1   0  1  1   1   1
## gt   1   1   1  1  1   1  0  1   1   1
## pi   1   1   1  1  1   1  1  0   1   1
## sei  1   1   1  1  1   1  1  1   0   1
## odi  1   1   1  1  1   1  1  1   1   0

# --- code block ---

meth["ts"]<- "~ I(sws + ps)"
pas.imp <- mice(mammalsleep[, -1], meth=meth, pred=pred, maxit=10, seed=123, print=F)

# --- code block ---

plot(pas.imp)

# --- code block ---

ini <- mice(boys, maxit = 0)
meth <- ini$meth
meth["tv"] <- "norm"
post <- ini$post
post["tv"] <- "imp[[j]][, i] <- squeeze(imp[[j]][, i], c(1, 25))"
imp <- mice(boys, meth=meth, post=post, print=FALSE)

# --- code block ---

imp.pmm <- mice(boys, print=FALSE)

# --- code block ---

table(complete(imp)$tv)

# --- code block ---

## 
##                1 1.21710148525462 1.43588483352455 1.51201882679116 
##              323                1                1                1 
## 1.53292756925877 1.53884163903632 1.58285408167725 1.80802667422845 
##                1                1                1                1 
##                2 2.07663165624588 2.24979678211323 2.92335718014784 
##               26                1                1                1 
## 2.94117422338134 2.95084234692005                3 3.02364296734824 
##                1                1               19                1 
## 3.53970347137679 3.57972881016042 3.74672076785238 3.96039115719309 
##                1                1                1                1 
##                4 4.04754711531009 4.08248223904697 4.14754362271122 
##               17                1                1                1 
## 4.17913738746458  4.5108993044032 4.57883711875945 4.72773944856595 
##                1                1                1                1 
## 4.78039105160729 4.87498648012577 4.95790683812151                5 
##                1                1                1                5 
## 5.22626498342572 5.27699780349692 5.29699542293051  5.5135973716855 
##                1                1                1                1 
## 5.58961218020009 5.69794944880459                6 6.25631547711316 
##                1                1               10                1 
## 6.35152222227269 6.50171770177514 7.15463206998544 7.41565552751217 
##                1                1                1                1 
## 7.91305727094718 7.93871120477867                8 8.05174592128119 
##                1                1               13                1 
## 8.05700045665079 8.16362288564921 8.21549432374612 8.49997598070039 
##                1                1                1                1 
## 8.51370505398192 8.58764399352692 8.61845893470197 8.97364475446134 
##                1                1                1                1 
##                9 9.00919768391507 9.63183636229161 9.63562902483335 
##                1                1                1                1 
## 9.76095833349053 9.84465985091274               10 10.2674945703833 
##                1                1               16                1 
## 10.4662560634783 10.5268192284329 10.5687382671324 10.6082021769037 
##                1                1                1                1 
## 10.6737703082101 10.8772940701329 10.8854812337215  10.930532331179 
##                1                1                1                1 
## 11.0093322524732 11.1652748123109 11.2642535206875 11.5290193322052 
##                1                1                1                1 
## 11.7584784239471 11.7965517201956 11.8064326042326               12 
##                1                1                1               15 
## 12.1696703772424  12.592892417515  12.618204518511 12.6689878607267 
##                1                1                1                1 
## 12.7081972517136 12.8979961443309               13 13.0240980425785 
##                1                1                1                1 
## 13.0587048153365  13.106348108398 13.5405375517151 13.9431160205217 
##                1                1                1                1 
##               14 14.2482185768873 14.2798608007013 14.3315252653246 
##                1                1                1                1 
## 14.4076303004689 14.4338076497289 14.5138128344765 14.6788476362263 
##                1                1                1                1 
## 14.6824007199852 14.7441518164776 14.8078250873427 14.9525753157757 
##                1                1                1                1 
## 14.9981738657718               15 15.1258748162893 15.1835169459907 
##                1               27                1                1 
## 15.4911886491463 15.5120235066289 15.6264815503803 15.6348463939284 
##                1                1                1                1 
## 15.6933134568447 15.7497016188987 15.7977063752737 15.8513524150625 
##                1                1                1                1 
## 15.9198411082574 15.9284148402579               16  16.340697942133 
##                1                1                1                1 
## 16.3716211968936 16.4317068195426 16.4699630810462 16.5178617262188 
##                1                1                1                1 
## 16.6654847715227 16.6721133690251 16.6871350554192 16.7050893382433 
##                1                1                1                1 
## 16.7500877350959  16.919505854755 16.9696935240149               17 
##                1                1                1                1 
## 17.0607955750451  17.061123780778 17.0975117585518 17.1863794919946 
##                1                1                1                1 
## 17.2885587826642 17.3213750660243 17.3288063082604 17.3371972081781 
##                1                1                1                1 
## 17.4139221505318 17.5083623700701  17.525693552751 17.5536295065084 
##                1                1                1                1 
## 17.7355682743341 17.7543354628357 17.7767055311222 17.7892576850834 
##                1                1                1                1 
## 17.8020025078871 17.9058272130569 17.9861341293521               18 
##                1                1                1                1 
## 18.0089953938541 18.0125066085225 18.0780752065915 18.0894548325433 
##                1                1                1                1 
## 18.1085713536776 18.4853383062642 18.4943336555561 18.6076606087712 
##                1                1                1                1 
## 18.6213898628289 18.7328605098401 18.8458099353893 18.8627827329173 
##                1                1                1                1 
## 19.0764930131297 19.2910290679375 19.3288860993901 19.4126039248187 
##                1                1                1                1 
## 19.6064318553331  19.653890171068 19.6670241312546 19.8448125657382 
##                1                1                1                1 
## 19.8516466793385               20  20.006279627252 20.1685051396209 
##                1               38                1                1 
## 20.2483453303049 20.4090716225676 20.5489240439564 20.7075019374611 
##                1                1                1                1 
##  20.848944671593 20.8504396969632 20.9256973033623 21.2111117512718 
##                1                1                1                1 
## 21.2988437259828 21.4887083820786 21.6632008465181 21.8584346902023 
##                1                1                1                1 
## 21.9017081211805 22.0705004778976 22.3764963365167 22.4619460041735 
##                1                1                1                1 
## 22.6563991359074 22.9207287921778 22.9263656773065 23.0539049074043 
##                1                1                1                1 
## 23.0557994938662 23.4243509549263  23.554099918438 23.7245812810879 
##                1                1                1                1 
## 23.7401686860153 23.8808526223058 23.9241225232408 24.4052538064194 
##                1                1                1                1 
## 24.4395463953961 24.6699887395728               25 
##                1                1               44

# --- code block ---

table(complete(imp.pmm)$tv)

# --- code block ---

## 
##   1   2   3   4   5   6   8   9  10  12  13  14  15  16  17  18  20  25 
##  73 219  99  29   6  16  26   1  37  29   3   5  47   1   1   4  88  64

# --- code block ---

densityplot(imp, ~tv)

# --- code block ---

tv <- c(complete(imp.pmm)$tv, complete(imp)$tv)
method <- rep(c("pmm", "norm"), each = nrow(boys))
tvm <- data.frame(tv = tv, method = method)

# --- code block ---

histogram( ~tv | method, data = tvm, nint = 25)

# --- code block ---

miss <- is.na(imp$data$bmi)
xyplot(imp, bmi ~ I (wgt / (hgt / 100)^2),
       na.groups = miss, cex = c(0.8, 1.2), pch = c(1, 20),
       ylab = "BMI (kg/m2) Imputed", xlab = "BMI (kg/m2) Calculated")

# --- code block ---

meth<- ini$meth
meth["bmi"]<- "~ I(wgt / (hgt / 100)^2)"
imp <- mice(boys, meth=meth, print=FALSE)

# --- code block ---

xyplot(imp, bmi ~ I(wgt / (hgt / 100)^2), na.groups = miss,
       cex = c(1, 1), pch = c(1, 20),
       ylab = "BMI (kg/m2) Imputed", xlab = "BMI (kg/m2) Calculated")

# --- code block ---

plot(imp, c("bmi"))

# --- code block ---

pred<-ini$pred
pred

# --- code block ---

##     age hgt wgt bmi hc gen phb tv reg
## age   0   1   1   1  1   1   1  1   1
## hgt   1   0   1   1  1   1   1  1   1
## wgt   1   1   0   1  1   1   1  1   1
## bmi   1   1   1   0  1   1   1  1   1
## hc    1   1   1   1  0   1   1  1   1
## gen   1   1   1   1  1   0   1  1   1
## phb   1   1   1   1  1   1   0  1   1
## tv    1   1   1   1  1   1   1  0   1
## reg   1   1   1   1  1   1   1  1   0

# --- code block ---

pred[c("hgt", "wgt"), "bmi"] <- 0
pred

# --- code block ---

##     age hgt wgt bmi hc gen phb tv reg
## age   0   1   1   1  1   1   1  1   1
## hgt   1   0   1   0  1   1   1  1   1
## wgt   1   1   0   0  1   1   1  1   1
## bmi   1   1   1   0  1   1   1  1   1
## hc    1   1   1   1  0   1   1  1   1
## gen   1   1   1   1  1   0   1  1   1
## phb   1   1   1   1  1   1   0  1   1
## tv    1   1   1   1  1   1   1  0   1
## reg   1   1   1   1  1   1   1  1   0

# --- code block ---

imp <-mice(boys, meth=meth, pred=pred, print=FALSE)

# --- code block ---

xyplot(imp, bmi ~ I(wgt / (hgt / 100)^2), na.groups = miss,
       cex=c(1, 1), pch=c(1, 20),
       ylab="BMI (kg/m2) Imputed", xlab="BMI (kg/m2) Calculated")

# --- code block ---

plot(imp, c("bmi"))

# --- code block ---

ini <- mice(boys, maxit=0)
meth<- ini$meth
pred <- ini$pred
pred

# --- code block ---

##     age hgt wgt bmi hc gen phb tv reg
## age   0   1   1   1  1   1   1  1   1
## hgt   1   0   1   1  1   1   1  1   1
## wgt   1   1   0   1  1   1   1  1   1
## bmi   1   1   1   0  1   1   1  1   1
## hc    1   1   1   1  0   1   1  1   1
## gen   1   1   1   1  1   0   1  1   1
## phb   1   1   1   1  1   1   0  1   1
## tv    1   1   1   1  1   1   1  0   1
## reg   1   1   1   1  1   1   1  1   0

# --- code block ---

meth["bmi"]<- "~ I(wgt/(hgt/100)^2)"
meth["wgt"]<- "~ I(bmi*(hgt/100)^2)"
meth["hgt"]<- "~ I(sqrt(wgt/bmi)*100)"
imp.path <- mice(boys, meth=meth, pred=pred, seed=123)

# --- code block ---

## 
##  iter imp variable
##   1   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   1   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   1   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   1   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   1   5  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   2   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   2   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   2   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   2   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   2   5  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   3   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   3   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   3   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   3   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   3   5  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   4   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   4   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   4   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   4   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   4   5  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   5   1  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   5   2  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   5   3  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   5   4  hgt  wgt  bmi  hc  gen  phb  tv  reg
##   5   5  hgt  wgt  bmi  hc  gen  phb  tv  reg

# --- code block ---

plot(imp.path, c("hgt", "wgt", "bmi"))
