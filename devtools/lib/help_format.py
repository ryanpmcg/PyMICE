"""R ``help()`` pager snapshots for vignette parity."""

from __future__ import annotations

R_HELP_NHANES = """nhanes                  package:mice                   R Documentation

_N_H_A_N_E_S _e_x_a_m_p_l_e - _a_l_l _v_a_r_i_a_b_l_e_s _n_u_m_e_r_i_c_a_l

_D_e_s_c_r_i_p_t_i_o_n:

     A small data set with non-monotone missing values.

_F_o_r_m_a_t:

     A data frame with 25 observations on the following 4 variables.

     age Age group (1=20-39, 2=40-59, 3=60+)

     bmi Body mass index (kg/m**2)

     hyp Hypertensive (1=no,2=yes)

     chl Total serum cholesterol (mg/dL)

_D_e_t_a_i_l_s:

     A small data set with all numerical variables. The data set
     ‘nhanes2’ is the same data set, but with ‘age’ and ‘hyp’ treated
     as factors.

_S_o_u_r_c_e:

     Schafer, J.L. (1997).  _Analysis of Incomplete Multivariate Data._
     London: Chapman & Hall. Table 6.14.

_S_e_e _A_l_s_o:

     ‘nhanes2’

_E_x_a_m_p_l_e_s:

     # create 5 imputed data sets
     imp <- mice(nhanes)
     
     # print the first imputed data set
     complete(imp)
     """

R_HELP_BOYS = """boys                   package:mice                    R Documentation

_G_r_o_w_t_h _o_f _D_u_t_c_h _b_o_y_s

_D_e_s_c_r_i_p_t_i_o_n:

     Height, weight, head circumference and puberty of 748 Dutch boys.

_F_o_r_m_a_t:

     A data frame with 748 rows on the following 9 variables:

     age Decimal age (0-21 years)

     hgt Height (cm)

     wgt Weight (kg)

     bmi Body mass index

     hc Head circumference (cm)

     gen Genital Tanner stage (G1-G5)

     phb Pubic hair (Tanner P1-P6)

     tv Testicular volume (ml)

     reg Region (north, east, west, south, city)

_D_e_t_a_i_l_s:

     Random sample of 10\\ Dutch growth references 1997. Variables ‘gen’
     and ‘phb’ are ordered factors. ‘reg’ is a factor.

_S_o_u_r_c_e:

     Fredriks, A.M,, van Buuren, S., Burgmeijer, R.J., Meulmeester JF,
     Beuker, R.J., Brugman, E., Roede, M.J., Verloove-Vanhorick, S.P.,
     Wit, J.M. (2000) Continuing positive secular growth change in The
     Netherlands 1955-1997.  _Pediatric Research_, *47*, 316-323.

     Fredriks, A.M., van Buuren, S., Wit, J.M., Verloove-Vanhorick,
     S.P. (2000). Body index measurements in 1996-7 compared with 1980.
     _Archives of Disease in Childhood_, *82*, 107-112.

_E_x_a_m_p_l_e_s:

     # create two imputed data sets
     imp <- mice(boys, m = 1, maxit = 2)
     z <- complete(imp, 1)
     
     # create imputations for age <8yrs
     plot(z$age, z$gen,
       col = mdc(1:2)[1 + is.na(boys$gen)],
       xlab = "Age (years)", ylab = "Tanner Stage Genital"
     )
     
     # figure to show that the default imputation method does not impute BMI
     # consistently
     plot(z$bmi, z$wgt / (z$hgt / 100)^2,
       col = mdc(1:2)[1 + is.na(boys$bmi)],
       xlab = "Imputed BMI", ylab = "Calculated BMI"
     )
     
     # also, BMI distributions are somewhat different
     oldpar <- par(mfrow = c(1, 2))
     MASS::truehist(z$bmi[!is.na(boys$bmi)],
       h = 1, xlim = c(10, 30), ymax = 0.25,
       col = mdc(1), xlab = "BMI observed"
     )
     MASS::truehist(z$bmi[is.na(boys$bmi)],
       h = 1, xlim = c(10, 30), ymax = 0.25,
       col = mdc(2), xlab = "BMI imputed"
     )
     par(oldpar)
     
     # repair the inconsistency problem by passive imputation
     meth <- imp$meth
     meth["bmi"] <- "~I(wgt/(hgt/100)^2)"
     pred <- imp$predictorMatrix
     pred["hgt", "bmi"] <- 0
     pred["wgt", "bmi"] <- 0
     imp2 <- mice(boys, m = 1, maxit = 2, meth = meth, pred = pred)
     z2 <- complete(imp2, 1)
     
     # show that new imputations are consistent
     plot(z2$bmi, z2$wgt / (z2$hgt / 100)^2,
       col = mdc(1:2)[1 + is.na(boys$bmi)],
       ylab = "Calculated BMI"
     )
     
     # and compare distributions
     oldpar <- par(mfrow = c(1, 2))
     MASS::truehist(z2$bmi[!is.na(boys$bmi)],
       h = 1, xlim = c(10, 30), ymax = 0.25, col = mdc(1),
       xlab = "BMI observed"
     )
     MASS::truehist(z2$bmi[is.na(boys$bmi)],
       h = 1, xlim = c(10, 30), ymax = 0.25, col = mdc(2),
       xlab = "BMI imputed"
     )
     par(oldpar)
     """

R_HELP_MAMMAL = """mammalsleep                package:mice                R Documentation

_M_a_m_m_a_l _s_l_e_e_p _d_a_t_a

_D_e_s_c_r_i_p_t_i_o_n:

     Dataset from Allison and Cicchetti (1976) of 62 mammal species on
     the interrelationship between sleep, ecological, and
     constitutional variables. The dataset contains missing values on
     five variables.

_F_o_r_m_a_t:

     ‘mammalsleep’ is a data frame with 62 rows and 11 columns:

     species Species of animal

     bw Body weight (kg)

     brw Brain weight (g)

     sws Slow wave ("nondreaming") sleep (hrs/day)

     ps Paradoxical ("dreaming") sleep (hrs/day)

     ts Total sleep (hrs/day) (sum of slow wave and paradoxical sleep)

     mls Maximum life span (years)

     gt Gestation time (days)

     pi Predation index (1-5), 1 = least likely to be preyed upon

     sei Sleep exposure index (1-5), 1 = least exposed (e.g. animal
          sleeps in a well-protected den), 5 = most exposed

     odi Overall danger index (1-5) based on the above two indices and
          other information, 1 = least danger (from other animals), 5 =
          most danger (from other animals)

_D_e_t_a_i_l_s:

     Allison and Cicchetti (1976) investigated the interrelationship
     between sleep, ecological, and constitutional variables.  They
     assessed these variables for 39 mammalian species. The authors
     concluded that slow-wave sleep is negatively associated with a
     factor related to body size. This suggests that large amounts of
     this sleep phase are disadvantageous in large species.  Also,
     paradoxical sleep (REM sleep) was associated with a factor related
     to predatory danger, suggesting that large amounts of this sleep
     phase are disadvantageous in prey species.

_S_o_u_r_c_e:

     Allison, T., Cicchetti, D.V. (1976). Sleep in Mammals: Ecological
     and Constitutional Correlates. Science, 194(4266), 732-734.

_E_x_a_m_p_l_e_s:

     sleep <- data(mammalsleep)
     """

_HELP_PAGES = {
    "nhanes": R_HELP_NHANES,
    "boys": R_HELP_BOYS,
    "mammalsleep": R_HELP_MAMMAL,
}


def format_help_r(topic: str, *, max_lines: int | None = None) -> str:
    """Return R ``help(topic)`` pager text for vignette datasets."""
    key = topic.strip().lower().lstrip("?")
    try:
        text = _HELP_PAGES[key]
    except KeyError as exc:
        raise KeyError(topic) from exc
    if max_lines is None:
        return text
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    omitted = len(lines) - max_lines
    return (
        "\n".join(lines[:max_lines]) + f"\n\n... ({omitted} more lines — full R help page omitted)"
    )
