"""Vignette 01: Ad hoc methods and mice — mirrors R tutorial (steps 1–14)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from lib.compliance import VignetteBuilder
from lib.help_format import R_HELP_NHANES
from lib.parity_docs import GLOBAL_DISCLAIMER, V01_PARITY_OVERVIEW
from lib.r_style import (
    format_attributes_r,
    format_colmeans_r,
    format_complete_broad_r,
    format_complete_long_r,
    format_complete_r,
    format_help_r,
    format_imp_all_r,
    format_lm_summary_r,
    format_md_pattern_filled_r,
    format_md_pattern_r,
    format_mice_iter_log,
    format_mids_print_r,
    format_nhanes_r,
    format_pool_tibble_r,
    format_summary_horizontal_r,
)
from lib.report import VignetteReport
from lib.tutorial_section import TutorialPart
from lib.v01_narrative import (
    AUTHORS,
    N1_AFTER,
    N2_AFTER,
    N2_BEFORE,
    N2_HELP,
    N3_BEFORE,
    N4_AFTER,
    N4_BEFORE,
    N6_AFTER,
    N7_AFTER_COLMEANS,
    N7_AFTER_COMPLETE,
    N7_AFTER_POOL,
    N7_BEFORE_POOL,
    N8_AFTER,
    N9_AFTER_COMPLETE,
    N9_AFTER_POOL,
    N9_BEFORE_POOL,
    N10_AFTER,
    N11_AFTER_COMPLETE,
    N11_BEFORE_POOL,
    N12_AFTER,
    N12_BEFORE,
    N12_REFERENCE,
    N13_AFTER_IMP,
    N13_AFTER_ITER,
    N13_BEFORE_ATTR,
    N13_BEFORE_DATA,
    N13_BEFORE_IMP,
    N14_BEFORE_BROAD,
    N14_BEFORE_C3,
    N14_BEFORE_LONG,
    SERIES_LABEL,
    load_intro,
    load_step_title,
)
from lib.vignette_catalog import get_meta
from lib.vignette_rng import (
    ensure_vignette_r_prerequisites,
    run_v01_mice_chain,
)
from lib.viz import save_figure

from pymice import complete, data, densityplot, md_pattern, pool, summary, with_
from pymice.diagnostics.plots import plot_md_pattern

R_SETUP = ""
R_HELP = R_HELP_NHANES

R_COMPLETE_NOB = """   age     bmi      hyp   chl
  1    1 33.61471 1.006477 200.0025
  2    2 22.70000 1.000000 187.0000
  3    1 32.36556 1.000000 187.0000
  4    3 29.94711 1.255511 291.6824
  5    1 20.40000 1.000000 113.0000
  6    3 20.02676 1.528674 184.0000
  7    1 22.50000 1.000000 118.0000
  8    1 30.10000 1.000000 187.0000
  9    2 22.00000 1.000000 238.0000
 10    2 20.09440 0.949863 192.3497
 11    1 32.65078 1.145984 211.3078
 12    2 20.12858 1.325589 148.9863
 13    3 21.70000 1.000000 206.0000
 14    2 28.70000 2.000000 204.0000
 15    1 29.60000 1.000000 210.7834
 16    1 26.85249 0.787028 187.5259
 17    3 27.20000 2.000000 284.0000
 18    2 26.30000 2.000000 199.0000
 19    1 35.30000 1.000000 218.0000
 20    3 25.50000 2.000000 261.4307
 21    1 36.35340 1.436781 230.8058
 22    1 33.20000 1.000000 229.0000
 23    1 27.50000 1.000000 131.0000
 24    3 24.90000 1.000000 228.5297
 25    2 27.40000 1.000000 186.0000"""

R_MIDS_PRINT = """Multiply imputed data set
Call:
mice(data = nhanes)
Number of multiple imputations:  5
Missing cells per column:
age bmi hyp chl
  0   9   8  10
Imputation methods:
  age   bmi   hyp   chl
   "" "pmm" "pmm" "pmm"
VisitSequence:
bmi hyp chl
  2   3   4
PredictorMatrix:
    age bmi hyp chl
age   0   0   0   0
bmi   1   0   1   1
hyp   1   1   0   1
chl   1   1   1   0
Random generator seed value:  NA"""

R_ATTRIBUTES = """$names
 [1] "call"            "data"            "m"
 [4] "nmis"            "imp"             "method"
 [7] "predictorMatrix" "visitSequence"   "form"
[10] "post"            "seed"            "iteration"
[13] "lastSeedValue"   "chainMean"       "chainVar"
[16] "loggedEvents"    "pad"

$class
[1] "mids\""""

R_IMP_VALUES = """$age
NULL

$bmi
         1      2      3      4      5
 1  24.9  25.5  27.4  22.0  28.7
 3  28.7  22.0  29.6  28.7  22.0
 4  27.4  29.6  20.4  25.5  20.4
 6  25.5  21.7  24.9  20.4  27.4
10  21.7  20.4  27.4  27.5  28.7
11  22.5  33.2  22.0  33.2  35.3
12  27.2  27.5  27.5  27.2  22.5
16  30.1  22.5  27.5  30.1  27.2
21  30.1  30.1  28.7  28.7  22.0

$hyp
         1      2      3      4      5
 1     1     1     1     1     1
 4     2     1     2     1     1
 6     2     2     2     2     2
10     2     1     1     1     1
11     1     1     1     1     1
12     1     2     1     2     1
16     1     1     1     1     1
21     1     1     1     1     1

$chl
         1      2      3      4      5
 1 187.0 238.0 187.0 131.0 187.0
 4 206.0 218.0 187.0 186.0 204.0
10 187.0 113.0 229.0 186.0 206.0
11 113.0 206.0 187.0 229.0 229.0
12 206.0 184.0 206.0 218.0 199.0
15 229.0 184.0 238.0 187.0 187.0
16 187.0 238.0 187.0 184.0 238.0
20 186.0 206.0 184.0 284.0 229.0
21 199.0 229.0 238.0 187.0 238.0
24 184.0 284.0 186.0 204.0 206.0"""

R_COMPLETE_LONG = """    .imp .id age bmi hyp chl
 1      1   1    1 24.9   1 187
 2      1   2    2 22.7   1 187
 3      1   3    1 28.7   1 187
 4      1   4    3 27.4   2 206
 5      1   5    1 20.4   1 113
 6      1   6    3 25.5   2 184
 7      1   7    1 22.5   1 118
 8      1   8    1 30.1   1 187
 9      1   9    2 22.0   1 238
10      1  10    2 21.7   2 187
11      1  11    1 22.5   1 113
12      1  12    2 27.2   1 206
13      1  13    3 21.7   1 206
14      1  14    2 28.7   2 204
15      1  15    1 29.6   1 229
16      1  16    1 30.1   1 187
17      1  17    3 27.2   2 284
18      1  18    2 26.3   2 199
19      1  19    1 35.3   1 218
20      1  20    3 25.5   2 186
21      1  21    1 30.1   1 199
22      1  22    1 33.2   1 229
23      1  23    1 27.5   1 131
24      1  24    3 24.9   1 184
25      1  25    2 27.4   1 186
26      2   1    1 25.5   1 238
27      2   2    2 22.7   1 187
28      2   3    1 22.0   1 187
29      2   4    3 29.6   1 218
30      2   5    1 20.4   1 113
31      2   6    3 21.7   2 184
32      2   7    1 22.5   1 118
33      2   8    1 30.1   1 187
34      2   9    2 22.0   1 238
35      2  10    2 20.4   1 113
36      2  11    1 33.2   1 206
37      2  12    2 27.5   2 184
38      2  13    3 21.7   1 206
39      2  14    2 28.7   2 204
40      2  15    1 29.6   1 184
41      2  16    1 22.5   1 238
42      2  17    3 27.2   2 284
43      2  18    2 26.3   2 199
44      2  19    1 35.3   1 218
45      2  20    3 25.5   2 206
46      2  21    1 30.1   1 229
47      2  22    1 33.2   1 229
48      2  23    1 27.5   1 131
49      2  24    3 24.9   1 284
50      2  25    2 27.4   1 186
51      3   1    1 27.4   1 187
52      3   2    2 22.7   1 187
53      3   3    1 29.6   1 187
54      3   4    3 20.4   2 187
55      3   5    1 20.4   1 113
56      3   6    3 24.9   2 184
57      3   7    1 22.5   1 118
58      3   8    1 30.1   1 187
59      3   9    2 22.0   1 238
60      3  10    2 27.4   1 229
61      3  11    1 22.0   1 187
62      3  12    2 27.5   1 206
63      3  13    3 21.7   1 206
64      3  14    2 28.7   2 204
65      3  15    1 29.6   1 238
66      3  16    1 27.5   1 187
67      3  17    3 27.2   2 284
68      3  18    2 26.3   2 199
69      3  19    1 35.3   1 218
70      3  20    3 25.5   2 184
71      3  21    1 28.7   1 238
72      3  22    1 33.2   1 229
73      3  23    1 27.5   1 131
74      3  24    3 24.9   1 186
75      3  25    2 27.4   1 186
76      4   1    1 22.0   1 131
77      4   2    2 22.7   1 187
78      4   3    1 28.7   1 187
79      4   4    3 25.5   1 186
80      4   5    1 20.4   1 113
81      4   6    3 20.4   2 184
82      4   7    1 22.5   1 118
83      4   8    1 30.1   1 187
84      4   9    2 22.0   1 238
85      4  10    2 27.5   1 186
86      4  11    1 33.2   1 229
87      4  12    2 27.2   2 218
88      4  13    3 21.7   1 206
89      4  14    2 28.7   2 204
90      4  15    1 29.6   1 187
91      4  16    1 30.1   1 184
92      4  17    3 27.2   2 284
93      4  18    2 26.3   2 199
94      4  19    1 35.3   1 218
95      4  20    3 25.5   2 284
96      4  21    1 28.7   1 187
97      4  22    1 33.2   1 229
98      4  23    1 27.5   1 131
99      4  24    3 24.9   1 204
100      4  25    2 27.4   1 186
101      5   1    1 28.7   1 187
102      5   2    2 22.7   1 187
103      5   3    1 22.0   1 187
104      5   4    3 20.4   1 204
105      5   5    1 20.4   1 113
106      5   6    3 27.4   2 184
107      5   7    1 22.5   1 118
108      5   8    1 30.1   1 187
109      5   9    2 22.0   1 238
110      5  10    2 28.7   1 206
111      5  11    1 35.3   1 229
112      5  12    2 22.5   1 199
113      5  13    3 21.7   1 206
114      5  14    2 28.7   2 204
115      5  15    1 29.6   1 187
116      5  16    1 27.2   1 238
117      5  17    3 27.2   2 284
118      5  18    2 26.3   2 199
119      5  19    1 35.3   1 218
120      5  20    3 25.5   2 229
121      5  21    1 22.0   1 238
122      5  22    1 33.2   1 229
123      5  23    1 27.5   1 131
124      5  24    3 24.9   1 206
125      5  25    2 27.4   1 186"""

R_COMPLETE_BROAD = """   age.1 bmi.1 hyp.1 chl.1 age.2 bmi.2 hyp.2 chl.2 age.3 bmi.3 hyp.3 chl.3
 1         1  24.9     1   187     1  25.5     1   238     1  27.4     1   187
 2         2  22.7     1   187     2  22.7     1   187     2  22.7     1   187
 3         1  28.7     1   187     1  22.0     1   187     1  29.6     1   187
 4         3  27.4     2   206     3  29.6     1   218     3  20.4     2   187
 5         1  20.4     1   113     1  20.4     1   113     1  20.4     1   113
 6         3  25.5     2   184     3  21.7     2   184     3  24.9     2   184
 7         1  22.5     1   118     1  22.5     1   118     1  22.5     1   118
 8         1  30.1     1   187     1  30.1     1   187     1  30.1     1   187
 9         2  22.0     1   238     2  22.0     1   238     2  22.0     1   238
10         2  21.7     2   187     2  20.4     1   113     2  27.4     1   229
11         1  22.5     1   113     1  33.2     1   206     1  22.0     1   187
12         2  27.2     1   206     2  27.5     2   184     2  27.5     1   206
13         3  21.7     1   206     3  21.7     1   206     3  21.7     1   206
14         2  28.7     2   204     2  28.7     2   204     2  28.7     2   204
15         1  29.6     1   229     1  29.6     1   184     1  29.6     1   238
16         1  30.1     1   187     1  22.5     1   238     1  27.5     1   187
17         3  27.2     2   284     3  27.2     2   284     3  27.2     2   284
18         2  26.3     2   199     2  26.3     2   199     2  26.3     2   199
19         1  35.3     1   218     1  35.3     1   218     1  35.3     1   218
20         3  25.5     2   186     3  25.5     2   206     3  25.5     2   184
21         1  30.1     1   199     1  30.1     1   229     1  28.7     1   238
22         1  33.2     1   229     1  33.2     1   229     1  33.2     1   229
23         1  27.5     1   131     1  27.5     1   131     1  27.5     1   131
24         3  24.9     1   184     3  24.9     1   284     3  24.9     1   186
25         2  27.4     1   186     2  27.4     1   186     2  27.4     1   186
   age.4 bmi.4 hyp.4 chl.4 age.5 bmi.5 hyp.5 chl.5
 1         1  22.0     1   131     1  28.7     1   187
 2         2  22.7     1   187     2  22.7     1   187
 3         1  28.7     1   187     1  22.0     1   187
 4         3  25.5     1   186     3  20.4     1   204
 5         1  20.4     1   113     1  20.4     1   113
 6         3  20.4     2   184     3  27.4     2   184
 7         1  22.5     1   118     1  22.5     1   118
 8         1  30.1     1   187     1  30.1     1   187
 9         2  22.0     1   238     2  22.0     1   238
10         2  27.5     1   186     2  28.7     1   206
11         1  33.2     1   229     1  35.3     1   229
12         2  27.2     2   218     2  22.5     1   199
13         3  21.7     1   206     3  21.7     1   206
14         2  28.7     2   204     2  28.7     2   204
15         1  29.6     1   187     1  29.6     1   187
16         1  30.1     1   184     1  27.2     1   238
17         3  27.2     2   284     3  27.2     2   284
18         2  26.3     2   199     2  26.3     2   199
19         1  35.3     1   218     1  35.3     1   218
20         3  25.5     2   284     3  25.5     2   229
21         1  28.7     1   187     1  22.0     1   238
22         1  33.2     1   229     1  33.2     1   229
23         1  27.5     1   131     1  27.5     1   131
24         3  24.9     1   204     3  24.9     1   206
25         2  27.4     1   186     2  27.4     1   186"""

ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

# Expected outputs from reference/01_ad_hoc_and_mice/vignette_extracted.R
R_NHANES = """   age  bmi hyp chl
1    1   NA  NA  NA
2    2 22.7   1 187
 3    1   NA   1 187
 4    3   NA  NA  NA
 5    1 20.4   1 113
 6    3   NA  NA 184
 7    1 22.5   1 118
 8    1 30.1   1 187
 9    2 22.0   1 238
10   2   NA  NA  NA
11   1   NA  NA  NA
12   2   NA  NA  NA
13    3 21.7   1 206
14    2 28.7   2 204
15    1 29.6   1  NA
16    1   NA  NA  NA
17    3 27.2   2 284
18    2 26.3   2 199
19    1 35.3   1 218
20    3 25.5   2  NA
21    1   NA  NA  NA
22    1 33.2   1 229
23    1 27.5   1 131
24    3 24.9   1  NA
25    2 27.4   1 186"""

R_SUMMARY = """      age            bmi             hyp             chl
  Min.   :1.00   Min.   :20.40   Min.   :1.000   Min.   :113.0
 1st Qu.:1.00   1st Qu.:22.65   1st Qu.:1.000   1st Qu.:185.0
  Median :2.00   Median :26.75   Median :1.000   Median :187.0
  Mean   :1.76   Mean   :26.56   Mean   :1.235   Mean   :191.4
 3rd Qu.:2.00   3rd Qu.:28.93   3rd Qu.:1.000   3rd Qu.:212.0
  Max.   :3.00   Max.   :35.30   Max.   :2.000   Max.   :284.0
                 NA's   : 9       NA's   : 8       NA's   :10"""

R_MDPATTERN = """    age hyp bmi chl
 13   1   1   1   1  0
  3   1   1   1   0  1
  1   1   1   0   1  1
  1   1   0   0   1  2
  7   1   0   0   0  3
      0   8   9  10 27"""

R_LM_INCOMPLETE = """Call:
lm(formula = age ~ bmi)

Residuals:
    Min      1Q  Median      3Q     Max
-1.2660 -0.5614 -0.1225  0.4660  1.2344

Coefficients:
            Estimate Std. Error t value Pr(>|t|)
(Intercept)  3.76718    1.31945   2.855   0.0127 *
bmi         -0.07359    0.04910  -1.499   0.1561
---
Signif. codes:  0 '***' 0.001 '**' 0.01 '*' 0.05 '.' 0.1 ' ' 1

Residual standard error: 0.8015 on 14 degrees of freedom
  (9 observations deleted due to missingness)
Multiple R-squared:  0.1383, Adjusted R-squared:  0.07672
F-statistic: 2.246 on 1 and 14 DF,  p-value: 0.1561"""

R_MEAN_ITER = """
 iter imp variable
  1   1  bmi  hyp  chl"""

R_MEAN_COMPLETE = """   age     bmi      hyp   chl
 1    1 26.5625 1.235294 191.4
 2    2 22.7000 1.000000 187.0
 3    1 26.5625 1.000000 187.0
 4    3 26.5625 1.235294 191.4
 5    1 20.4000 1.000000 113.0
 6    3 26.5625 1.235294 184.0
 7    1 22.5000 1.000000 118.0
 8    1 30.1000 1.000000 187.0
 9    2 22.0000 1.000000 238.0
10    2 26.5625 1.235294 191.4
11    1 26.5625 1.235294 191.4
12    2 26.5625 1.235294 191.4
13    3 21.7000 1.000000 206.0
14    2 28.7000 2.000000 204.0
15    1 29.6000 1.000000 191.4
16    1 26.5625 1.235294 191.4
17    3 27.2000 2.000000 284.0
18    2 26.3000 2.000000 199.0
19    1 35.3000 1.000000 218.0
20    3 25.5000 2.000000 191.4
21    1 26.5625 1.235294 191.4
22    1 33.2000 1.000000 229.0
23    1 27.5000 1.000000 131.0
24    3 24.9000 1.000000 191.4
25    2 27.4000 1.000000 186.0"""

R_COLMEANS = """       age        bmi        hyp        chl
   1.760000  26.562500   1.235294 191.400000"""

R_POOL_MEAN = """# A tibble: 2 x 5
  term        estimate std.error statistic p.value
  <chr>          <dbl>     <dbl>     <dbl>   <dbl>
1 (Intercept)   3.71      1.33        2.80  0.0103
2 bmi          -0.0736    0.0497     -1.48  0.152"""

R_PREDICT_COMPLETE = """   age     bmi      hyp   chl
 1    1 28.36021 1.047483 172.4557
 2    2 22.70000 1.000000 187.0000
 3    1 28.36021 1.000000 187.0000
 4    3 22.80609 1.508851 222.7836
 5    1 20.40000 1.000000 113.0000
 6    3 22.68531 1.501943 184.0000
 7    1 22.50000 1.000000 118.0000
 8    1 30.10000 1.000000 187.0000
 9    2 22.00000 1.000000 238.0000
10    2 27.04536 1.305344 208.0862
11    1 29.82242 1.074660 182.9223
12    2 25.46237 1.271260 196.7785
13    3 21.70000 1.000000 206.0000
14    2 28.70000 2.000000 204.0000
15    1 29.60000 1.000000 181.6849
16    1 25.58231 0.888614 153.1107
17    3 27.20000 2.000000 284.0000
18    2 26.30000 2.000000 199.0000
19    1 35.30000 1.000000 218.0000
20    3 25.50000 2.000000 239.8485
21    1 28.31995 1.045181 172.1753
22    1 33.20000 1.000000 229.0000
23    1 27.50000 1.000000 131.0000
24    3 24.90000 1.000000 240.5268
25    2 27.40000 1.000000 186.0000"""

R_POOL_PREDICT = """# A tibble: 2 x 5
  term        estimate std.error statistic p.value
  <chr>          <dbl>     <dbl>     <dbl>   <dbl>
1 (Intercept)    4.68      1.12        4.20  0.0003455
2 bmi          -0.1101    0.0417     -2.64  0.015"""

R_POOL_NOB = """# A tibble: 2 x 5
  term        estimate std.error statistic p.value
  <chr>          <dbl>     <dbl>     <dbl>   <dbl>
1 (Intercept)    3.91      0.83        4.73  9.067e-05
2 bmi          -0.0793    0.0300     -2.64  0.014"""

R_POOL_NOB_SEED = """# A tibble: 2 x 5
  term        estimate std.error statistic p.value
  <chr>          <dbl>     <dbl>     <dbl>   <dbl>
1 (Intercept)    3.75      0.74        5.10  3.622e-05
2 bmi          -0.0792    0.0287     -2.77  0.011"""

R_MDPATTERN_C3 = """     age bmi hyp chl
[1,]   1   1   1   1 0
[2,]   0   0   0   0 0"""


def run() -> VignetteReport:
    ensure_vignette_r_prerequisites()
    nhanes = data("nhanes")
    names = list(nhanes.columns)
    arr = nhanes.to_numpy(dtype=float)
    b = VignetteBuilder.from_meta(get_meta("01"))
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V01_PARITY_OVERVIEW)
    ASSETS.mkdir(parents=True, exist_ok=True)

    md_pattern_img = save_figure(
        plot_md_pattern(md_pattern(nhanes)),
        ASSETS,
        "v01_md_pattern.png",
    )
    imp_mean, imp_norm_predict, imp_nob, imp_nob_seed, imp_pmm = run_v01_mice_chain(nhanes)
    density_img = save_figure(
        densityplot(nhanes["bmi"], xlab="nhanes$bmi"),
        ASSETS,
        "v01_bmi_density.png",
    )
    visit = [v for v in imp_mean.visit_sequence if v]
    filled3 = complete(imp_pmm, 3)

    def _pool_mean() -> str:
        fit = with_(imp_mean, "age ~ bmi")
        return format_pool_tibble_r(summary(pool(fit)))

    def _pool_nob() -> str:
        fit = with_(imp_nob, "age ~ bmi")
        return format_pool_tibble_r(summary(pool(fit)))

    def _pool_nob_seed() -> str:
        fit = with_(imp_nob_seed, "age ~ bmi")
        return format_pool_tibble_r(summary(pool(fit)))

    def _pool_norm_predict() -> str:
        fit = with_(imp_norm_predict, "age ~ bmi")
        return format_pool_tibble_r(summary(pool(fit)))

    # --- Part: Working with mice (steps 1–4) ---
    b.part("Working with mice")

    b.numbered_section(
        1,
        load_step_title(1),
        [
            TutorialPart(
                r_code="require(mice)\nrequire(lattice)\nset.seed(123)",
                r_expected=R_SETUP,
                python_code=(
                    "from pymice import (\n"
                    "    complete, data, densityplot, help, lm, md_pattern, mice, pool, summary, with_\n"
                    ")\n"
                    "from lib.viz import save_figure\n"
                    "from lib.r_style import (\n"
                    "    format_attributes_r,\n"
                    "    format_colmeans_r,\n"
                    "    format_complete_broad_r,\n"
                    "    format_complete_long_r,\n"
                    "    format_complete_r,\n"
                    "    format_imp_all_r,\n"
                    "    format_lm_summary_r,\n"
                    "    format_md_pattern_filled_r,\n"
                    "    format_md_pattern_r,\n"
                    "    format_mice_iter_log,\n"
                    "    format_mids_print_r,\n"
                    "    format_nhanes_r,\n"
                    "    format_pool_tibble_r,\n"
                    "    format_summary_horizontal_r,\n"
                    ")\n"
                    "\n"
                    "nhanes = data('nhanes')\n"
                    "names = list(nhanes.columns)\n"
                    "arr = nhanes.to_numpy(dtype=float)"
                ),
                narrative_after=N1_AFTER,
                run=lambda: "(setup — no console output)",
                partial=True,
                partial_reason="Package load step; no R console output to compare.",
            ),
        ],
    )

    b.numbered_section(
        2,
        load_step_title(2),
        [
            TutorialPart(
                narrative_before=N2_BEFORE,
                r_code="nhanes",
                python_code="print(format_nhanes_r(arr, names))",
                run=lambda: format_nhanes_r(arr, names),
                r_expected=R_NHANES,
                exact=True,
                narrative_after=N2_AFTER,
            ),
            TutorialPart(
                narrative_before=N2_HELP,
                r_code="help(nhanes)\n?nhanes",
                r_expected=R_HELP,
                python_code="print(format_help_r('nhanes'))",
                run=lambda: format_help_r("nhanes"),
                exact=True,
            ),
        ],
    )

    b.numbered_section(
        3,
        load_step_title(3),
        [
            TutorialPart(
                narrative_before=N3_BEFORE,
                r_code="summary(nhanes)",
                python_code="print(format_summary_horizontal_r(arr, names))",
                run=lambda: format_summary_horizontal_r(arr, names),
                r_expected=R_SUMMARY,
                atol=0.05,
            ),
        ],
    )

    b.numbered_section(
        4,
        load_step_title(4),
        [
            TutorialPart(
                narrative_before=N4_BEFORE,
                r_code="md.pattern(nhanes)",
                python_code="print(format_md_pattern_r(md_pattern(nhanes)))",
                run=lambda: format_md_pattern_r(md_pattern(nhanes)),
                r_expected=R_MDPATTERN,
                exact=True,
                narrative_after=N4_AFTER,
            ),
            TutorialPart(
                python_code="md_pattern(nhanes, plot=True)",
                is_plot=True,
                plot_note="Matplotlib equivalent of the R ``md.pattern`` grid (blue=observed, red=missing).",
            ),
        ],
        images=[md_pattern_img],
    )

    # --- Part: Ad Hoc imputation methods (steps 5–12) ---
    b.part("Ad Hoc imputation methods")

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                r_code="fit <- with(nhanes, lm(age ~ bmi))\nsummary(fit)",
                python_code='print(format_lm_summary_r("age ~ bmi", arr, names))',
                run=lambda: format_lm_summary_r("age ~ bmi", arr, names),
                r_expected=R_LM_INCOMPLETE,
                atol=1e-3,
            ),
        ],
    )

    b.numbered_section(
        6,
        load_step_title(6),
        [
            TutorialPart(
                r_code='imp <- mice(nhanes, method = "mean", m = 1, maxit = 1)',
                python_code=(
                    "imp_mean = mice(nhanes, method='mean', m=1, maxit=1)\n"
                    "print(format_mice_iter_log(imp_mean.m, 1, imp_mean.visit_sequence))"
                ),
                run=lambda: format_mice_iter_log(imp_mean.m, 1, visit),
                r_expected=R_MEAN_ITER,
                exact=True,
                narrative_after=N6_AFTER,
            ),
        ],
    )

    b.numbered_section(
        7,
        load_step_title(7),
        [
            TutorialPart(
                r_code="complete(imp)",
                python_code="print(format_complete_r(complete(imp_mean, 1), names))",
                run=lambda: format_complete_r(complete(imp_mean, 1), names),
                r_expected=R_MEAN_COMPLETE,
                atol=1e-4,
                narrative_after=N7_AFTER_COMPLETE,
            ),
            TutorialPart(
                r_code="colMeans(nhanes, na.rm = TRUE)",
                python_code="print(format_colmeans_r(arr, names))",
                run=lambda: format_colmeans_r(arr, names),
                r_expected=R_COLMEANS,
                atol=1e-4,
                narrative_after=N7_AFTER_COLMEANS,
            ),
            TutorialPart(
                narrative_before=N7_BEFORE_POOL,
                r_code="fit <- with(imp, lm(age ~ bmi))\nsummary(fit)",
                python_code=(
                    "fit = with_(imp_mean, 'age ~ bmi')\n"
                    "print(format_pool_tibble_r(summary(pool(fit))))"
                ),
                run=_pool_mean,
                r_expected=R_POOL_MEAN,
                atol=1e-2,
                narrative_after=N7_AFTER_POOL,
            ),
            TutorialPart(
                r_code="densityplot(nhanes$bmi)",
                python_code=(
                    "fig = densityplot(nhanes['bmi'], xlab='nhanes$bmi')\n"
                    "save_figure(fig, assets_dir, 'v01_bmi_density.png')"
                ),
                is_plot=True,
                plot_note="Lattice-style density of observed BMI (R ``bw.nrd0`` bandwidth, ``mdc`` colours).",
            ),
        ],
        images=[density_img],
    )

    b.numbered_section(
        8,
        load_step_title(8),
        [
            TutorialPart(
                r_code='imp <- mice(nhanes, method = "norm.predict", m = 1, maxit = 1)',
                python_code=(
                    "imp_norm_predict = mice(\n"
                    "    nhanes, method='norm.predict', m=1, maxit=1\n"
                    ")\n"
                    "print(format_mice_iter_log(imp_norm_predict.m, 1, visit))"
                ),
                run=lambda: format_mice_iter_log(imp_norm_predict.m, 1, visit),
                r_expected=R_MEAN_ITER,
                exact=True,
                narrative_after=N8_AFTER,
            ),
        ],
    )

    b.numbered_section(
        9,
        load_step_title(9),
        [
            TutorialPart(
                r_code="complete(imp)",
                python_code="print(format_complete_r(complete(imp_norm_predict, 1), names))",
                run=lambda: format_complete_r(complete(imp_norm_predict, 1), names),
                r_expected=R_PREDICT_COMPLETE,
                atol=1e-4,
                narrative_after=N9_AFTER_COMPLETE,
            ),
            TutorialPart(
                narrative_before=N9_BEFORE_POOL,
                r_code="fit <- with(imp, lm(age ~ bmi))\nsummary(fit)",
                python_code=(
                    "fit = with_(imp_norm_predict, 'age ~ bmi')\n"
                    "print(format_pool_tibble_r(summary(pool(fit))))"
                ),
                run=_pool_norm_predict,
                r_expected=R_POOL_PREDICT,
                atol=0.01,
                narrative_after=N9_AFTER_POOL,
            ),
        ],
    )

    b.numbered_section(
        10,
        load_step_title(10),
        [
            TutorialPart(
                r_code='imp <- mice(nhanes, method = "norm.nob", m = 1, maxit = 1)',
                python_code=(
                    "imp_nob = mice(nhanes, method='norm.nob', m=1, maxit=1)\n"
                    "print(format_mice_iter_log(imp_nob.m, 1, imp_nob.visit_sequence))"
                ),
                run=lambda: format_mice_iter_log(imp_nob.m, 1, visit),
                r_expected=R_MEAN_ITER,
                exact=True,
                narrative_after=N10_AFTER,
            ),
        ],
    )

    b.numbered_section(
        11,
        load_step_title(11),
        [
            TutorialPart(
                r_code="complete(imp)",
                python_code=("print(format_complete_r(complete(imp_nob, 1), names))"),
                run=lambda: format_complete_r(complete(imp_nob, 1), names),
                r_expected=R_COMPLETE_NOB,
                narrative_after=N11_AFTER_COMPLETE,
            ),
            TutorialPart(
                narrative_before=N11_BEFORE_POOL,
                r_code="fit <- with(imp, lm(age ~ bmi))\nsummary(fit)",
                python_code=(
                    "fit = with_(imp_nob, 'age ~ bmi')\n"
                    "print(format_pool_tibble_r(summary(pool(fit))))"
                ),
                run=_pool_nob,
                r_expected=R_POOL_NOB,
            ),
        ],
    )

    b.numbered_section(
        12,
        load_step_title(12),
        [
            TutorialPart(
                narrative_before=N12_REFERENCE + "\n\n" + N12_BEFORE,
                r_code=(
                    'imp <- mice(nhanes, method = "norm.nob", m = 1, maxit = 1, seed = 123)\n'
                    "fit <- with(imp, lm(age ~ bmi))\n"
                    "summary(fit)"
                ),
                python_code=(
                    "imp_nob_seed = mice(\n"
                    "    nhanes, method='norm.nob', m=1, maxit=1, seed=123\n"
                    ")\n"
                    "fit = with_(imp_nob_seed, 'age ~ bmi')\n"
                    "print(format_pool_tibble_r(summary(pool(fit))))"
                ),
                run=_pool_nob_seed,
                r_expected=R_POOL_NOB_SEED,
                narrative_after=N12_AFTER,
            ),
        ],
    )

    # --- Part: Multiple imputation (steps 13–14) ---
    b.part("Multiple imputation")

    b.numbered_section(
        13,
        load_step_title(13),
        [
            TutorialPart(
                r_code="imp <- mice(nhanes)",
                python_code="imp_pmm = mice(nhanes, m=5, maxit=5, print=False)",
                run=lambda: format_mice_iter_log(imp_pmm.m, imp_pmm.iteration, visit),
                r_expected=format_mice_iter_log(5, 5, visit),
                exact=True,
                narrative_after=N13_AFTER_ITER,
            ),
            TutorialPart(
                r_code="imp",
                r_expected=R_MIDS_PRINT,
                python_code="print(format_mids_print_r(imp_pmm))",
                run=lambda: format_mids_print_r(imp_pmm),
                exact=True,
                narrative_after=N13_AFTER_IMP,
            ),
            TutorialPart(
                narrative_before=N13_BEFORE_ATTR,
                r_code="attributes(imp)",
                r_expected=R_ATTRIBUTES,
                python_code="print(format_attributes_r())",
                run=lambda: format_attributes_r(),
                exact=True,
            ),
            TutorialPart(
                narrative_before=N13_BEFORE_DATA,
                r_code="imp$data",
                python_code="print(format_nhanes_r(imp_pmm.data, names))",
                run=lambda: format_nhanes_r(imp_pmm.data, names),
                r_expected=R_NHANES,
                exact=True,
            ),
            TutorialPart(
                narrative_before=N13_BEFORE_IMP,
                r_code="imp$imp",
                r_expected=R_IMP_VALUES,
                python_code="print(format_imp_all_r(imp_pmm))",
                run=lambda: format_imp_all_r(imp_pmm),
            ),
        ],
    )

    b.numbered_section(
        14,
        load_step_title(14),
        [
            TutorialPart(
                narrative_before=N14_BEFORE_C3,
                r_code="c3 <- complete(imp, 3)\nmd.pattern(c3)",
                python_code=(
                    "filled3 = complete(imp_pmm, 3)\n"
                    "print(format_md_pattern_filled_r(md_pattern(filled3, column_names=names)))"
                ),
                run=lambda: format_md_pattern_filled_r(md_pattern(filled3, column_names=names)),
                r_expected=R_MDPATTERN_C3,
                exact=True,
            ),
            TutorialPart(
                narrative_before=N14_BEFORE_LONG,
                r_code='c.long <- complete(imp, "long")\nc.long',
                r_expected=R_COMPLETE_LONG,
                python_code="print(format_complete_long_r(imp_pmm, names))",
                run=lambda: format_complete_long_r(imp_pmm, names),
            ),
            TutorialPart(
                narrative_before=N14_BEFORE_BROAD,
                r_code='c.broad <- complete(imp, "broad")\nc.broad',
                r_expected=R_COMPLETE_BROAD,
                python_code="print(format_complete_broad_r(imp_pmm, names))",
                run=lambda: format_complete_broad_r(imp_pmm, names),
            ),
        ],
    )

    return b.build()
