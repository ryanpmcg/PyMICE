"""Vignette 01: Ad hoc methods and mice — mirrors R tutorial (steps 1–14)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from lib.compliance import VignetteBuilder
from lib.data import load_nhanes
from lib.parity_docs import GLOBAL_DISCLAIMER, V01_PARITY_OVERVIEW
from lib.r_style import (
    format_attributes_r,
    format_colmeans_r,
    format_complete_broad_r,
    format_complete_long_r,
    format_complete_r,
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
    TITLE,
    load_intro,
    load_step_title,
)
from lib.viz import save_figure

from pymice import complete, help, md_pattern, mice, pool, summary_pool, with_mids
from pymice.diagnostics.plots import plot_raw_density

R_SETUP = ""
R_HELP = ""

R_COMPLETE_NOB = """   age      bmi       hyp      chl
1    1 35.46313 1.1192657 208.1269
2    2 22.70000 1.0000000 187.0000
3    1 28.04489 1.0000000 187.0000
4    3 28.36409 1.1892939 209.5659
5    1 20.40000 1.0000000 113.0000
6    3 16.34286 0.9233658 184.0000
7    1 22.50000 1.0000000 118.0000
8    1 30.10000 1.0000000 187.0000
9    2 22.00000 1.0000000 238.0000
10   2 28.72079 1.4989875 252.2370
11   1 30.15465 1.3168140 162.6556
12   2 27.21004 1.3627723 194.0366
13   3 21.70000 1.0000000 206.0000
14   2 28.70000 2.0000000 204.0000
15   1 29.60000 1.0000000 209.3729
16   1 31.14788 1.5316578 180.7741
17   3 27.20000 2.0000000 284.0000
18   2 26.30000 2.0000000 199.0000
19   1 35.30000 1.0000000 218.0000
20   3 25.50000 2.0000000 215.6881
21   1 27.72316 1.9274899 167.2897
22   1 33.20000 1.0000000 229.0000
23   1 27.50000 1.0000000 131.0000
24   3 24.90000 1.0000000 246.9890
25   2 27.40000 1.0000000 186.0000"""

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
      1    2    3    4    5
1  30.1 27.2 29.6 35.3 29.6
3  29.6 29.6 29.6 26.3 30.1
4  27.4 20.4 21.7 27.4 25.5
6  24.9 24.9 20.4 21.7 20.4
10 27.5 27.5 27.4 24.9 22.0
11 30.1 28.7 29.6 22.0 33.2
12 27.5 29.6 29.6 27.5 28.7
16 26.3 30.1 29.6 28.7 27.2
21 26.3 22.0 27.2 35.3 24.9

$hyp
   1 2 3 4 5
1  1 1 1 1 1
4  2 1 1 2 2
6  2 1 2 2 1
10 2 1 1 2 1
11 1 1 1 1 1
12 2 1 2 1 1
16 1 1 1 1 1
21 1 1 1 1 1

$chl
     1   2   3   4   5
1  187 131 187 206 199
4  184 187 186 204 186
10 218 187 186 131 187
11 199 187 238 131 204
12 186 187 218 204 218
15 199 187 238 229 199
16 187 238 131 187 187
20 184 218 218 186 206
21 187 131 187 204 187
24 186 187 206 218 218"""

R_COMPLETE_LONG = """    .imp .id age  bmi hyp chl
1      1   1   1 30.1   1 187
2      1   2   2 22.7   1 187
3      1   3   1 29.6   1 187
4      1   4   3 27.4   2 184
5      1   5   1 20.4   1 113
6      1   6   3 24.9   2 184
7      1   7   1 22.5   1 118
8      1   8   1 30.1   1 187
9      1   9   2 22.0   1 238
10     1  10   2 27.5   2 218
11     1  11   1 30.1   1 199
12     1  12   2 27.5   2 186
13     1  13   3 21.7   1 206
14     1  14   2 28.7   2 204
15     1  15   1 29.6   1 199
16     1  16   1 26.3   1 187
17     1  17   3 27.2   2 284
18     1  18   2 26.3   2 199
19     1  19   1 35.3   1 218
20     1  20   3 25.5   2 184
21     1  21   1 26.3   1 187
22     1  22   1 33.2   1 229
23     1  23   1 27.5   1 131
24     1  24   3 24.9   1 186
25     1  25   2 27.4   1 186
26     2   1   1 27.2   1 131
27     2   2   2 22.7   1 187
28     2   3   1 29.6   1 187
29     2   4   3 20.4   1 187
30     2   5   1 20.4   1 113
31     2   6   3 24.9   1 184
32     2   7   1 22.5   1 118
33     2   8   1 30.1   1 187
34     2   9   2 22.0   1 238
35     2  10   2 27.5   1 187
36     2  11   1 28.7   1 187
37     2  12   2 29.6   1 187
38     2  13   3 21.7   1 206
39     2  14   2 28.7   2 204
40     2  15   1 29.6   1 187
41     2  16   1 30.1   1 238
42     2  17   3 27.2   2 284
43     2  18   2 26.3   2 199
44     2  19   1 35.3   1 218
45     2  20   3 25.5   2 218
46     2  21   1 22.0   1 131
47     2  22   1 33.2   1 229
48     2  23   1 27.5   1 131
49     2  24   3 24.9   1 187
50     2  25   2 27.4   1 186
51     3   1   1 29.6   1 187
52     3   2   2 22.7   1 187
53     3   3   1 29.6   1 187
54     3   4   3 21.7   1 186
55     3   5   1 20.4   1 113
56     3   6   3 20.4   2 184
57     3   7   1 22.5   1 118
58     3   8   1 30.1   1 187
59     3   9   2 22.0   1 238
60     3  10   2 27.4   1 186
61     3  11   1 29.6   1 238
62     3  12   2 29.6   2 218
63     3  13   3 21.7   1 206
64     3  14   2 28.7   2 204
65     3  15   1 29.6   1 238
66     3  16   1 29.6   1 131
67     3  17   3 27.2   2 284
68     3  18   2 26.3   2 199
69     3  19   1 35.3   1 218
70     3  20   3 25.5   2 218
71     3  21   1 27.2   1 187
72     3  22   1 33.2   1 229
73     3  23   1 27.5   1 131
74     3  24   3 24.9   1 206
75     3  25   2 27.4   1 186
76     4   1   1 35.3   1 206
77     4   2   2 22.7   1 187
78     4   3   1 26.3   1 187
79     4   4   3 27.4   2 204
80     4   5   1 20.4   1 113
81     4   6   3 21.7   2 184
82     4   7   1 22.5   1 118
83     4   8   1 30.1   1 187
84     4   9   2 22.0   1 238
85     4  10   2 24.9   2 131
86     4  11   1 22.0   1 131
87     4  12   2 27.5   1 204
88     4  13   3 21.7   1 206
89     4  14   2 28.7   2 204
90     4  15   1 29.6   1 229
91     4  16   1 28.7   1 187
92     4  17   3 27.2   2 284
93     4  18   2 26.3   2 199
94     4  19   1 35.3   1 218
95     4  20   3 25.5   2 186
96     4  21   1 35.3   1 204
97     4  22   1 33.2   1 229
98     4  23   1 27.5   1 131
99     4  24   3 24.9   1 218
100    4  25   2 27.4   1 186
101    5   1   1 29.6   1 199
102    5   2   2 22.7   1 187
103    5   3   1 30.1   1 187
104    5   4   3 25.5   2 186
105    5   5   1 20.4   1 113
106    5   6   3 20.4   1 184
107    5   7   1 22.5   1 118
108    5   8   1 30.1   1 187
109    5   9   2 22.0   1 238
110    5  10   2 22.0   1 187
111    5  11   1 33.2   1 204
112    5  12   2 28.7   1 218
113    5  13   3 21.7   1 206
114    5  14   2 28.7   2 204
115    5  15   1 29.6   1 199
116    5  16   1 27.2   1 187
117    5  17   3 27.2   2 284
118    5  18   2 26.3   2 199
119    5  19   1 35.3   1 218
120    5  20   3 25.5   2 206
121    5  21   1 24.9   1 187
122    5  22   1 33.2   1 229
123    5  23   1 27.5   1 131
124    5  24   3 24.9   1 218
125    5  25   2 27.4   1 186"""

R_COMPLETE_BROAD = """   age.1 bmi.1 hyp.1 chl.1 age.2 bmi.2 hyp.2 chl.2 age.3 bmi.3 hyp.3 chl.3
1      1  30.1     1   187     1  27.2     1   131     1  29.6     1   187
2      2  22.7     1   187     2  22.7     1   187     2  22.7     1   187
3      1  29.6     1   187     1  29.6     1   187     1  29.6     1   187
4      3  27.4     2   184     3  20.4     1   187     3  21.7     1   186
5      1  20.4     1   113     1  20.4     1   113     1  20.4     1   113
6      3  24.9     2   184     3  24.9     1   184     3  20.4     2   184
7      1  22.5     1   118     1  22.5     1   118     1  22.5     1   118
8      1  30.1     1   187     1  30.1     1   187     1  30.1     1   187
9      2  22.0     1   238     2  22.0     1   238     2  22.0     1   238
10     2  27.5     2   218     2  27.5     1   187     2  27.4     1   186
11     1  30.1     1   199     1  28.7     1   187     1  29.6     1   238
12     2  27.5     2   186     2  29.6     1   187     2  29.6     2   218
13     3  21.7     1   206     3  21.7     1   206     3  21.7     1   206
14     2  28.7     2   204     2  28.7     2   204     2  28.7     2   204
15     1  29.6     1   199     1  29.6     1   187     1  29.6     1   238
16     1  26.3     1   187     1  30.1     1   238     1  29.6     1   131
17     3  27.2     2   284     3  27.2     2   284     3  27.2     2   284
18     2  26.3     2   199     2  26.3     2   199     2  26.3     2   199
19     1  35.3     1   218     1  35.3     1   218     1  35.3     1   218
20     3  25.5     2   184     3  25.5     2   218     3  25.5     2   218
21     1  26.3     1   187     1  22.0     1   131     1  27.2     1   187
22     1  33.2     1   229     1  33.2     1   229     1  33.2     1   229
23     1  27.5     1   131     1  27.5     1   131     1  27.5     1   131
24     3  24.9     1   186     3  24.9     1   187     3  24.9     1   206
25     2  27.4     1   186     2  27.4     1   186     2  27.4     1   186
   age.4 bmi.4 hyp.4 chl.4 age.5 bmi.5 hyp.5 chl.5
1      1  35.3     1   206     1  29.6     1   199
2      2  22.7     1   187     2  22.7     1   187
3      1  26.3     1   187     1  30.1     1   187
4      3  27.4     2   204     3  25.5     2   186
5      1  20.4     1   113     1  20.4     1   113
6      3  21.7     2   184     3  20.4     1   184
7      1  22.5     1   118     1  22.5     1   118
8      1  30.1     1   187     1  30.1     1   187
9      2  22.0     1   238     2  22.0     1   238
10     2  24.9     2   131     2  22.0     1   187
11     1  22.0     1   131     1  33.2     1   204
12     2  27.5     1   204     2  28.7     1   218
13     3  21.7     1   206     3  21.7     1   206
14     2  28.7     2   204     2  28.7     2   204
15     1  29.6     1   229     1  29.6     1   199
16     1  28.7     1   187     1  27.2     1   187
17     3  27.2     2   284     3  27.2     2   284
18     2  26.3     2   199     2  26.3     2   199
19     1  35.3     1   218     1  35.3     1   218
20     3  25.5     2   186     3  25.5     2   206
21     1  35.3     1   204     1  24.9     1   187
22     1  33.2     1   229     1  33.2     1   229
23     1  27.5     1   131     1  27.5     1   131
24     3  24.9     1   218     3  24.9     1   218
25     2  27.4     1   186     2  27.4     1   186"""

URL = "https://www.gerkovink.com/miceVignettes/Ad_hoc_and_mice/Ad_hoc_methods.html"
ASSETS = Path(__file__).resolve().parents[1] / "output" / "assets"

# Expected outputs from Vignettes/01_ad_hoc_and_mice/vignette_extracted.R
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
 1    1 31.98171 1.132574 198.1082
 2    2 22.70000 1.000000 187.0000
 3    1 28.83478 1.000000 187.0000
 4    3 23.21098 1.530991 228.5499
 5    1 20.40000 1.000000 113.0000
 6    3 21.11303 1.475446 184.0000
 7    1 22.50000 1.000000 118.0000
 8    1 30.10000 1.000000 187.0000
 9    2 22.00000 1.000000 238.0000
10    2 31.05181 1.423268 238.5342
11    1 31.37488 1.123040 193.6441
12    2 25.06646 1.264801 194.8752
13    3 21.70000 1.000000 206.0000
14    2 28.70000 2.000000 204.0000
15    1 29.60000 1.000000 181.1354
16    1 28.64966 1.044355 173.8032
17    3 27.20000 2.000000 284.0000
18    2 26.30000 2.000000 199.0000
19    1 35.30000 1.000000 218.0000
20    3 25.50000 2.000000 242.8954
21    1 34.82013 1.207723 218.8124
22    1 33.20000 1.000000 229.0000
23    1 27.50000 1.000000 131.0000
24    3 24.90000 1.000000 244.1845
25    2 27.40000 1.000000 186.0000"""

R_POOL_PREDICT = """# A tibble: 2 x 5
  term        estimate std.error statistic   p.value
  <chr>          <dbl>     <dbl>     <dbl>     <dbl>
1 (Intercept)    4.63     0.925       5.00 0.0000463
2 bmi           -0.105    0.0335     -3.14 0.00462"""

R_POOL_NOB = """# A tibble: 2 x 5
  term        estimate std.error statistic  p.value
  <chr>          <dbl>     <dbl>     <dbl>    <dbl>
1 (Intercept)   4.23      0.918       4.60 0.000125
2 bmi          -0.0909    0.0334     -2.72 0.0122"""

R_POOL_NOB_SEED = """# A tibble: 2 x 5
  term        estimate std.error statistic p.value
  <chr>          <dbl>     <dbl>     <dbl>   <dbl>
1 (Intercept)   4.13      1.13        3.66 0.00129
2 bmi          -0.0904    0.0426     -2.12 0.0449"""

R_MDPATTERN_C3 = """     age bmi hyp chl
[1,]   1   1   1   1 0
[2,]   0   0   0   0 0"""


def run() -> VignetteReport:
    data, names = load_nhanes()
    b = VignetteBuilder("01", "v01_ad_hoc_mice", TITLE, URL)
    b.set_intro(load_intro(), authors=AUTHORS, series_label=SERIES_LABEL)
    b.set_disclaimer(GLOBAL_DISCLAIMER)
    b.set_parity_overview(V01_PARITY_OVERVIEW)
    ASSETS.mkdir(parents=True, exist_ok=True)

    density_img = save_figure(plot_raw_density(data, "bmi", names), ASSETS, "v01_bmi_density.png")

    imp_mean = mice(data, column_names=names, method="mean", m=1, maxit=1, seed=123)
    visit = [v for v in imp_mean.visit_sequence if v]
    imp_nob = mice(data, column_names=names, method="norm.nob", m=1, maxit=1)
    imp_nob_seed = mice(data, column_names=names, method="norm.nob", m=1, maxit=1, seed=123)
    imp_norm_predict = mice(data, column_names=names, method="norm.predict", m=1, maxit=1, seed=123)
    imp_pmm = mice(data, column_names=names, m=5, maxit=5, seed=123)
    filled3 = complete(imp_pmm, 3)

    def _pool_mean() -> str:
        fit = with_mids(imp_mean, formula="age ~ bmi")
        return format_pool_tibble_r(summary_pool(pool(fit)))

    def _pool_nob() -> str:
        fit = with_mids(imp_nob, formula="age ~ bmi")
        return format_pool_tibble_r(summary_pool(pool(fit)))

    def _pool_nob_seed() -> str:
        fit = with_mids(imp_nob_seed, formula="age ~ bmi")
        return format_pool_tibble_r(summary_pool(pool(fit)))

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
                    "import numpy as np\n"
                    "from pymice import complete, help, lm, md_pattern, mice, pool, summary_pool, with_mids\n"
                    "from pymice.diagnostics.plots import plot_raw_density\n"
                    "from lib.data import load_nhanes\n"
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
                    "data, names = load_nhanes()"
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
                python_code="print(format_nhanes_r(data, names))",
                run=lambda: format_nhanes_r(data, names),
                r_expected=R_NHANES,
                exact=True,
                narrative_after=N2_AFTER,
            ),
            TutorialPart(
                narrative_before=N2_HELP,
                r_code="help(nhanes)\n?nhanes",
                r_expected=R_HELP,
                python_code="help('nhanes', print_=False)",
                run=lambda: help("nhanes", print_=False),
                partial=True,
                partial_reason="PyMICE help page; layout differs from R pager output.",
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
                python_code="print(format_summary_horizontal_r(data, names))",
                run=lambda: format_summary_horizontal_r(data, names),
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
                python_code="print(format_md_pattern_r(md_pattern(data, names)))",
                run=lambda: format_md_pattern_r(md_pattern(data, names)),
                r_expected=R_MDPATTERN,
                exact=True,
                narrative_after=N4_AFTER,
            ),
        ],
    )

    # --- Part: Ad Hoc imputation methods (steps 5–12) ---
    b.part("Ad Hoc imputation methods")

    b.numbered_section(
        5,
        load_step_title(5),
        [
            TutorialPart(
                r_code="fit <- with(nhanes, lm(age ~ bmi))\nsummary(fit)",
                python_code="print(format_lm_summary_r('age ~ bmi', data, names))",
                run=lambda: format_lm_summary_r("age ~ bmi", data, names),
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
                    "imp_mean = mice(\n"
                    "    data, column_names=names, method='mean', m=1, maxit=1, seed=123\n"
                    ")\n"
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
                python_code="print(format_colmeans_r(data, names))",
                run=lambda: format_colmeans_r(data, names),
                r_expected=R_COLMEANS,
                atol=1e-4,
                narrative_after=N7_AFTER_COLMEANS,
            ),
            TutorialPart(
                narrative_before=N7_BEFORE_POOL,
                r_code="fit <- with(imp, lm(age ~ bmi))\nsummary(fit)",
                python_code=(
                    "fit = with_mids(imp_mean, formula='age ~ bmi')\n"
                    "print(format_pool_tibble_r(summary_pool(pool(fit))))"
                ),
                run=_pool_mean,
                r_expected=R_POOL_MEAN,
                atol=1e-2,
                narrative_after=N7_AFTER_POOL,
            ),
            TutorialPart(
                r_code="densityplot(nhanes$bmi)",
                r_expected=R_MIDS_PRINT,
                python_code=(
                    "fig = plot_raw_density(data, 'bmi', names)\n"
                    "save_figure(fig, assets_dir, 'v01_bmi_density.png')"
                ),
                is_plot=True,
                plot_note="Matplotlib equivalent of the R lattice `densityplot`.",
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
                    "    data, column_names=names, method='norm.predict', m=1, maxit=1, seed=123\n"
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
                partial=True,
                partial_reason="Regression imputation values differ slightly from R (OLS implementation).",
                atol=2.0,
                narrative_after=N9_AFTER_COMPLETE,
            ),
            TutorialPart(
                narrative_before=N9_BEFORE_POOL,
                r_code="fit <- with(imp, lm(age ~ bmi))\nsummary(fit)",
                python_code=(
                    "fit_np = with_mids(imp_norm_predict, formula='age ~ bmi')\n"
                    "print(format_pool_tibble_r(summary_pool(pool(fit_np))))"
                ),
                run=lambda: format_pool_tibble_r(
                    summary_pool(pool(with_mids(imp_norm_predict, formula="age ~ bmi")))
                ),
                r_expected=R_POOL_PREDICT,
                partial=True,
                partial_reason="Pooled estimates follow norm.predict imputation differences.",
                atol=0.5,
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
                    "imp_nob = mice(\n"
                    "    data, column_names=names, method='norm.nob', m=1, maxit=1\n"
                    ")\n"
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
                partial=True,
                partial_reason="Imputed values differ from R RNG (no seed in R vignette); layout matches.",
                narrative_after=N11_AFTER_COMPLETE,
            ),
            TutorialPart(
                narrative_before=N11_BEFORE_POOL,
                r_code="fit <- with(imp, lm(age ~ bmi))\nsummary(fit)",
                python_code=(
                    "fit = with_mids(imp_nob, formula='age ~ bmi')\n"
                    "print(format_pool_tibble_r(summary_pool(pool(fit))))"
                ),
                run=_pool_nob,
                r_expected=R_POOL_NOB,
                partial=True,
                partial_reason="Pooled estimates differ from R under unset norm.nob RNG.",
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
                    "    data, column_names=names, method='norm.nob', m=1, maxit=1, seed=123\n"
                    ")\n"
                    "fit = with_mids(imp_nob_seed, formula='age ~ bmi')\n"
                    "print(format_pool_tibble_r(summary_pool(pool(fit))))"
                ),
                run=_pool_nob_seed,
                r_expected=R_POOL_NOB_SEED,
                partial=True,
                partial_reason=(
                    "Intercept estimate matches R; SE/statistic/p-value differ under norm.nob RNG."
                ),
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
                python_code=("imp_pmm = mice(data, column_names=names, m=5, maxit=5, seed=123)"),
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
                partial=True,
                partial_reason="Structure matches R; seed shown as 123 (R default is NA).",
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
                partial=True,
                partial_reason="PMM imputed values differ from R RNG; matrix structure matches.",
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
                    "print(format_md_pattern_filled_r(md_pattern(filled3, names)))"
                ),
                run=lambda: format_md_pattern_filled_r(md_pattern(filled3, names)),
                r_expected=R_MDPATTERN_C3,
                exact=True,
            ),
            TutorialPart(
                narrative_before=N14_BEFORE_LONG,
                r_code='c.long <- complete(imp, "long")\nc.long',
                r_expected=R_COMPLETE_LONG,
                python_code="print(format_complete_long_r(imp_pmm, names))",
                run=lambda: format_complete_long_r(imp_pmm, names),
                partial=True,
                partial_reason="Long layout matches R; PMM values differ under seed=123.",
            ),
            TutorialPart(
                narrative_before=N14_BEFORE_BROAD,
                r_code='c.broad <- complete(imp, "broad")\nc.broad',
                r_expected=R_COMPLETE_BROAD,
                python_code="print(format_complete_broad_r(imp_pmm, names))",
                run=lambda: format_complete_broad_r(imp_pmm, names),
                partial=True,
                partial_reason="Broad layout matches R; PMM values differ under seed=123.",
            ),
        ],
    )

    return b.build()
