###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

from Numeric import sum


############################
# Spectral density values. #
############################

"""
    The spectral density equation
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.jw
    Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
    Type:  Numeric matrix, Float64
    Dependencies:  None
    Required by:  data.ri, data.dri, data.d2ri


    Formulae
    ~~~~~~~~
                      _n_
                 2    \           /      1       \ 
        J(w)  =  - S2  >  ci . ti | ------------ |
                 5    /__         \ 1 + (w.ti)^2 /
                      i=m


                    _n_
                 2  \           /      S2             (1 - S2)(te + ti)te    \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                    i=m


                    _n_
                 2  \           /      S2            (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m


                    _n_
                 2  \           /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m


    Extended 2
    ~~~~~~~~~~

                       _n_
                 2     \           /      S2s           (1 - S2s)(ts + ti)ts    \ 
        J(w)  =  - S2f  >  ci . ti | ------------  +  ------------------------- |
                 5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=m


                    _n_
                 2  \           /   S2f . S2s        (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m
"""



# Original no params with or without diffusion parameters.
##########################################################

def calc_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with no parameters {}
    with or without diffusion tensor parameters.

    The formula is:

                    _n_
                 2  \           /      1       \ 
        J(w)  =  -   >  ci . ti | ------------ |
                 5  /__         \ 1 + (w.ti)^2 /
                    i=m
    """

    return 0.4 * sum(data.ci * data.ti * data.fact_ti, axis=2)



# Original {S2} with or without diffusion parameters.
#####################################################

def calc_S2_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with the single
    parameter {S2} with or without diffusion tensor parameters.

    The formula is:

                      _n_
                 2    \           /      1       \ 
        J(w)  =  - S2  >  ci . ti | ------------ |
                 5    /__         \ 1 + (w.ti)^2 /
                      i=m
    """

    return 0.4 * params[data.s2_index] * sum(data.ci * data.ti * data.fact_ti, axis=2)



# Original {S2, te} with or without diffusion parameters.
#########################################################

def calc_S2_te_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with the parameters
    {S2, te} with or without diffusion tensor parameters.

    The model-free formula is:

                    _n_
                 2  \           /      S2             (1 - S2)(te + ti)te    \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                    i=m
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2_index] * data.fact_ti + data.one_s2 * data.te_ti_te * data.inv_te_denom), axis=2)



# Extended {S2f, S2, ts} with or without diffusion parameters.
##############################################################

def calc_S2f_S2_ts_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, S2, ts} with or without diffusion tensor parameters.

    The model-free formula is:

                    _n_
                 2  \           /      S2            (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2_index] * data.fact_ti + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended {S2f, tf, S2, ts} with or without diffusion parameters.
##################################################################

def calc_S2f_tf_S2_ts_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, tf, S2, ts} with or without diffusion tensor parameters.

    The model-free formula is:

                    _n_
                 2  \           /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2_index] * data.fact_ti + data.one_s2f * data.tf_ti_tf * data.inv_tf_denom + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 {S2f, S2s, ts} with or without diffusion parameters.
#################################################################

def calc_S2f_S2s_ts_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, S2s, ts} with or without diffusion tensor parameters.

    The model-free formula is:

                       _n_
                 2     \           /      S2s           (1 - S2s)(ts + ti)ts    \ 
        J(w)  =  - S2f  >  ci . ti | ------------  +  ------------------------- |
                 5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=m
    """

    return 0.4 * params[data.s2f_index] * sum(data.ci * data.ti * (params[data.s2s_index] * data.fact_ti + data.one_s2s * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 {S2f, tf, S2s, ts} with or without diffusion parameters.
#####################################################################

def calc_S2f_tf_S2s_ts_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, tf, S2s, ts} with or without diffusion tensor parameters.

    The model-free formula is:

                    _n_
                 2  \           /   S2f . S2s        (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti + data.one_s2f * data.tf_ti_tf * data.inv_tf_denom + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)




###############################
# Spectral density gradients. #
###############################

"""
    The spectral density gradients
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.djw
    Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies,
        model-free parameters)
    Type:  Numeric 3D matrix, Float64
    Dependencies:  None
    Required by:  data.dri, data.d2ri


    Formulae
    ~~~~~~~~

    Original
    ~~~~~~~~

                     _n_
        dJ(w)     2  \   /      dti  /        1 - (w.ti)^2                         (te + ti)^2 - (w.te.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 . ----------------  +  (1 - S2) . te^2 ----------------------------- |
         dDj      5  /__ \      dDj  \      (1 + (w.ti)^2)^2                     ((te + ti)^2 + (w.te.ti)^2)^2 /
                     i=m

                              dci      /      S2             (1 - S2)(te + ti)te    \ \ 
                           +  --- . ti | ------------  +  ------------------------- | |
                              dDj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /


                     _n_
        dJ(w)     2  \    dci       /      S2             (1 - S2)(te + ti)te    \ 
        -----  =  -   >  ----- . ti | ------------  +  ------------------------- |
        dPsij     5  /__ dPsij      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=m


                     _n_
        dJ(w)     2  \           /      1                 (te + ti)te         \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |
         dS2      5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=m


                             _n_
        dJ(w)     2          \                 (te + ti)^2 - (w.te.ti)^2
        -----  =  - (1 - S2)  >  ci . ti^2 . -----------------------------
         dte      5          /__             ((te + ti)^2 + (w.te.ti)^2)^2
                             i=m


        dJ(w)
        -----  =  0
        dRex


        dJ(w)
        -----  =  0
        dcsa


        dJ(w)
        -----  =  0
         dr


    Extended
    ~~~~~~~~

                     _n_
        dJ(w)     2  \   /      dti  /        1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  (S2f - S2) . ts^2 ----------------------------- |
         dDj      5  /__ \      dDj  \      (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m

                              dci      /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ \ 
                           +  --- . ti | ------------  +  -------------------------  +  ------------------------- | |
                              dDj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                     _n_
        dJ(w)     2  \    dci       /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        -----  =  -   >  ----- . ti | ------------  +  -------------------------  +  ------------------------- |
        dPsij     5  /__ dPsij      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m


                     _n_
        dJ(w)     2  \           /      1                 (ts + ti).ts        \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |
         dS2      5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m


                       _n_
        dJ(w)       2  \           /       (tf + ti).tf                  (ts + ti).ts        \ 
        -----  =  - -   >  ci . ti | -------------------------  -  ------------------------- |
        dS2f        5  /__         \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=m


                              _n_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=m


                               _n_
        dJ(w)     2            \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - (S2f - S2)  >  ci . ti^2 -----------------------------
         dts      5            /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                               i=m


        dJ(w)
        -----  =  0
        dRex


        dJ(w)
        -----  =  0
        dcsa


        dJ(w)
        -----  =  0
         dr


    Extended 2
    ~~~~~~~~~~

                     _n_
        dJ(w)     2  \   /      dti  /               1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                             (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2f . S2s . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  S2f(1 - S2s) . ts^2 ----------------------------- |
         dDj      5  /__ \      dDj  \             (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                         ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m

                              dci      /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ \ 
                           +  --- . ti | ------------  +  -------------------------  +  ------------------------- | |
                              dDj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                     _n_
        dJ(w)     2  \    dci       /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        -----  =  -   >  ----- . ti | ------------  +  -------------------------  +  ------------------------- |
        dPsij     5  /__ dPsij      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m


                     _n_
        dJ(w)     2  \           /     S2s                (tf + ti).tf              (1 - S2s)(ts + ti).ts   \ 
        -----  =  -   >  ci . ti | ------------  -  -------------------------  +  ------------------------- |
        dS2f      5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m


                        _n_
        dJ(w)     2     \           /      1                 (ts + ti).ts        \ 
        -----  =  - S2f  >  ci . ti | ------------  -  ------------------------- |
        dS2s      5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=m


                              _n_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=m


                                 _n_
        dJ(w)     2              \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - S2f(1 - S2s)  >  ci . ti^2 -----------------------------
         dts      5              /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=m


        dJ(w)
        -----  =  0
        dRex


        dJ(w)
        -----  =  0
        dcsa


        dJ(w)
        -----  =  0
         dr
"""



# Original Dj partial derivative.
#################################

# {} with diffusion parameters.

def calc_diff_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the original model-free
    formula with no parameters {} together with diffusion tensor parameters.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \        dti  /   1 - (w.ti)^2   \ 
        -----  =  -   >  ci . ---  | ---------------- |
         dDj      5  /__      dDj  \ (1 + (w.ti)^2)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.dti[j] * data.fact_ti_djw_dti, axis=2)


def calc_aniso_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the original model-free
    formula with no parameters {} together with diffusion tensor parameters.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \   /      dti  /   1 - (w.ti)^2   \     dci      /      1       \ \ 
        -----  =  -   >  | ci . ---  | ---------------- |  +  --- . ti | ------------ | |
         dDj      5  /__ \      dDj  \ (1 + (w.ti)^2)^2 /     dDj      \ 1 + (w.ti)^2 / /
                     i=m

    return 0.4 * sum(data.dci[j] * data.ti * data.fact_ti, axis=2)

    """

    return 0.4 * sum(data.ci * data.dti[j] * data.fact_ti_djw_dti  +  data.dci[j] * data.ti * data.fact_ti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the original model-free
    formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free gradient is:

                       _n_
        dJ(w)     2    \        dti  /   1 - (w.ti)^2   \ 
        -----  =  - S2  >  ci . ---  | ---------------- |
         dDj      5    /__      dDj  \ (1 + (w.ti)^2)^2 /
                       i=m
    """

    return 0.4 * params[data.s2_index] * sum(data.ci * data.dti[j] * data.fact_ti_djw_dti, axis=2)


def calc_aniso_S2_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the original model-free
    formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free gradient is:

                       _n_
        dJ(w)     2    \   /      dti  /   1 - (w.ti)^2   \     dci      /      1       \ \ 
        -----  =  - S2  >  | ci . ---  | ---------------- |  +  --- . ti | ------------ | |
         dDj      5    /__ \      dDj  \ (1 + (w.ti)^2)^2 /     dDj      \ 1 + (w.ti)^2 / /
                       i=m
    """

    return 0.4 * params[data.s2_index] * sum(data.ci * data.dti[j] * data.fact_ti_djw_dti  +  data.dci[j] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the original model-free
    formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \        dti  /        1 - (w.ti)^2                         (te + ti)^2 - (w.te.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 . ----------------  +  (1 - S2) . te^2 ----------------------------- |
         dDj      5  /__      dDj  \      (1 + (w.ti)^2)^2                     ((te + ti)^2 + (w.te.ti)^2)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_index] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti), axis=2)


def calc_aniso_S2_te_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the original model-free
    formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \   /      dti  /        1 - (w.ti)^2                         (te + ti)^2 - (w.te.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 . ----------------  +  (1 - S2) . te^2 ----------------------------- |
         dDj      5  /__ \      dDj  \      (1 + (w.ti)^2)^2                     ((te + ti)^2 + (w.te.ti)^2)^2 /
                     i=m

                              dci      /      S2             (1 - S2)(te + ti)te    \ \ 
                           +  --- . ti | ------------  +  ------------------------- | |
                              dDj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_index] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2_index] * data.fact_ti + data.one_s2 * data.te_ti_te * data.inv_te_denom), axis=2)



# Original Psij partial derivative.
###################################

# {} with diffusion parameters.

def calc_diff_djw_dPsij(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Psi partial derivative of the original model-free
    formula with no parameters {} together with diffusion tensor parameters.

    The model-free gradient is:

                    _n_
        dJ(w)     2 \    dci       /      1       \ 
        -----  =  -  >  ----- . ti | ------------ |
        dPsij     5 /__ dPsij      \ 1 + (w.ti)^2 /
                    i=m
    """

    return 0.4 * sum(data.dci[j] * data.ti * data.fact_ti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_djw_dPsij(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Psi partial derivative of the original model-free
    formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free gradient is:

                       _n_
        dJ(w)     2    \    dci       /      1       \ 
        -----  =  - S2  >  ----- . ti | ------------ |
        dPsij     5    /__ dPsij      \ 1 + (w.ti)^2 /
                       i=m
    """

    return 0.4 * params[data.s2_index] * sum(data.dci[j] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_djw_dPsij(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Psi partial derivative of the original model-free
    formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \    dci       /      S2             (1 - S2)(te + ti)te    \ 
        -----  =  -   >  ----- . ti | ------------  +  ------------------------- |
        dPsij     5  /__ dPsij      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.dci[j] * data.ti * (params[data.s2_index] * data.fact_ti + data.one_s2 * data.te_ti_te * data.inv_te_denom), axis=2)



# Original S2 partial derivative.
#################################

# {S2} with or without diffusion parameters.

def calc_S2_djw_dS2(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the original model-free
    formula with the single parameter {S2} with or without diffusion tensor parameters.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \           /      1       \ 
        -----  =  -   >  ci . ti | ------------ |
         dS2      5  /__         \ 1 + (w.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.ti * data.fact_ti, axis=2)


# {S2, te} with or without diffusion parameters.

def calc_S2_te_djw_dS2(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the original model-free
    formula with the parameters {S2, te} with or without diffusion tensor parameters.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \           /      1                 (te + ti)te         \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |
         dS2      5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.ti * (data.fact_ti - data.te_ti_te * data.inv_te_denom), axis=2)



# Original te partial derivative.
#################################

# {S2, te} with or without diffusion parameters.

def calc_S2_te_djw_dte(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the te partial derivative of the original model-free
    formula with the parameters {S2, te} with or without diffusion tensor parameters.

    The model-free gradient is:

                             _n_
        dJ(w)     2          \                 (te + ti)^2 - (w.te.ti)^2
        -----  =  - (1 - S2)  >  ci . ti^2 . -----------------------------
         dte      5          /__             ((te + ti)^2 + (w.te.ti)^2)^2
                             i=m
    """

    return 0.4 * data.one_s2 * sum(data.ci * data.fact_djw_dte, axis=2)



# Extended Dj partial derivative.
#################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \        dti  /        1 - (w.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 . ----------------  +  (S2f - S2) . ts^2 ----------------------------- |
         dDj      5  /__      dDj  \      (1 + (w.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_index] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_aniso_S2f_S2_ts_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \   /      dti  /        1 - (w.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 . ----------------  +  (S2f - S2) . ts^2 ----------------------------- |
         dDj      5  /__ \      dDj  \      (1 + (w.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m

                              dci      /      S2            (S2f - S2)(ts + ti)ts   \ \ 
                           +  --- . ti | ------------  +  ------------------------- | |
                              dDj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_index] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2_index] * data.fact_ti + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \        dti  /        1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  (S2f - S2) . ts^2 ----------------------------- |
         dDj      5  /__      dDj  \      (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_index] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_aniso_S2f_tf_S2_ts_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \   /      dti  /        1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  (S2f - S2) . ts^2 ----------------------------- |
         dDj      5  /__ \      dDj  \      (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m

                              dci      /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ \ 
                           +  --- . ti | ------------  +  -------------------------  +  ------------------------- | |
                              dDj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_index] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2_index] * data.fact_ti + data.one_s2f * data.tf_ti_tf * data.inv_tf_denom + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended Psij partial derivative.
###################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_djw_dPsij(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Psi partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \    dci       /      S2            (S2f - S2)(ts + ti)ts   \ 
        -----  =  -   >  ----- . ti | ------------  +  ------------------------- |
        dPsij     5  /__ dPsij      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.dci[j] * data.ti * (params[data.s2_index] * data.fact_ti + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_djw_dPsij(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Psi partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \    dci       /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        -----  =  -   >  ----- . ti | ------------  +  -------------------------  +  ------------------------- |
        dPsij     5  /__ dPsij      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.dci[j] * data.ti * (params[data.s2_index] * data.fact_ti + data.one_s2f * data.tf_ti_tf * data.inv_tf_denom + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended S2 partial derivative.
#################################

# {S2f, S2, ts} and {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_djw_dS2(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} with or without diffusion tensor
    parameters.

    The formula is:

                     _n_
        dJ(w)     2  \           /      1                 (ts + ti).ts        \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |
         dS2      5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.ti * (data.fact_ti - data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended S2f partial derivative.
##################################

# {S2f, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_djw_dS2f(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} with or without diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \           /       (ts + ti).ts        \ 
        -----  =  -   >  ci . ti | ------------------------- |
        dS2f      5  /__         \ (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.ti * data.ts_ti_ts * data.inv_ts_denom, axis=2)


# {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_tf_S2_ts_djw_dS2f(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} with or without diffusion tensor parameters.

    The formula is:

                       _n_
        dJ(w)       2  \           /       (tf + ti).tf                  (ts + ti).ts        \ 
        -----  =  - -   >  ci . ti | -------------------------  -  ------------------------- |
        dS2f        5  /__         \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=m
    """

    return -0.4 * sum(data.ci * data.ti * (data.tf_ti_tf * data.inv_tf_denom - data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended tf partial derivative.
#################################

# {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_tf_S2_ts_djw_dtf(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the tf partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} with or without diffusion tensor parameters.

    The formula is:

                              _n_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=m
    """

    return 0.4 * data.one_s2f * sum(data.ci * data.fact_djw_dtf, axis=2)



# Extended ts partial derivative.
#################################

# {S2f, S2, ts} and {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_djw_dts(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the ts partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} with or without diffusion tensor
    parameters.

    The formula is:

                               _n_
        dJ(w)     2            \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - (S2f - S2)  >  ci . ti^2 -----------------------------
         dts      5            /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                               i=m
    """

    return 0.4 * data.s2f_s2 * sum(data.ci * data.fact_djw_dts, axis=2)



# Extended 2 Dj partial derivative.
###################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The formula is:

                        _n_
        dJ(w)     2     \        dti  /         1 - (w.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  - S2f  >  ci . ---  | S2s . ----------------  +  (1 - S2s) . ts^2 ----------------------------- |
         dDj      5     /__      dDj  \       (1 + (w.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=m
    """

    return 0.4 * params[data.s2f_index] * sum(data.ci * data.dti[j] * (params[data.s2s_index] * data.fact_ti_djw_dti + data.one_s2s * data.fact_ts_djw_dti), axis=2)


def calc_aniso_S2f_S2s_ts_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The formula is:

                        _n_
        dJ(w)     2     \   /      dti  /         1 - (w.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  - S2f  >  | ci . ---  | S2s . ----------------  +  (1 - S2s) . ts^2 ----------------------------- |
         dDj      5     /__ \      dDj  \       (1 + (w.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=m

                                 dci      /     S2s             (1 - S2s)(ts + ti)ts   \ \ 
                              +  --- . ti | ------------  +  ------------------------- | |
                                 dDj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * params[data.s2f_index] * sum(data.ci * data.dti[j] * (params[data.s2s_index] * data.fact_ti_djw_dti + data.one_s2s * data.fact_ts_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2s_index] * data.fact_ti + data.one_s2s * data.ts_ti_ts * data.inv_ts_denom), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \        dti  /               1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                             (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2f . S2s . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  S2f(1 - S2s) . ts^2 ----------------------------- |
         dDj      5  /__      dDj  \             (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                         ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_aniso_S2f_tf_S2s_ts_djw_dDj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Dj partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \   /      dti  /               1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                             (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2f . S2s . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  S2f(1 - S2s) . ts^2 ----------------------------- |
         dDj      5  /__ \      dDj  \             (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                         ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m

                              dci      /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ \ 
                           +  --- . ti | ------------  +  -------------------------  +  ------------------------- | |
                              dDj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti + data.one_s2f * data.tf_ti_tf * data.inv_tf_denom + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 Psij partial derivative.
#####################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_djw_dPsij(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Psi partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The formula is:

                        _n_
        dJ(w)     2     \    dci       /     S2s             (1 - S2s)(ts + ti)ts   \ 
        -----  =  - S2f  >  ----- . ti | ------------  +  ------------------------- |
        dPsij     5     /__ dPsij      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=m
    """

    return 0.4 * params[data.s2f_index] * sum(data.dci[j] * data.ti * (params[data.s2s_index] * data.fact_ti + data.one_s2s * data.ts_ti_ts * data.inv_ts_denom), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_djw_dPsij(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Psi partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \    dci       /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        -----  =  -   >  ----- . ti | ------------  +  -------------------------  +  ------------------------- |
        dPsij     5  /__ dPsij      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.dci[j] * data.ti * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti + data.one_s2f * data.tf_ti_tf * data.inv_tf_denom + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 S2f partial derivative.
###################################

# {S2f, S2s, ts} with or without diffusion parameters..

def calc_S2f_S2s_ts_djw_dS2f(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} with or without diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \           /     S2s            (1 - S2s)(ts + ti).ts   \ 
        -----  =  -   >  ci . ti | ------------  +  ------------------------- |
        dS2f      5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2s_index] * data.fact_ti + data.one_s2s * data.ts_ti_ts * data.inv_ts_denom), axis=2)


# {S2f, tf, S2s, ts} with or without diffusion parameters..

def calc_S2f_tf_S2s_ts_djw_dS2f(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} with or without diffusion tensor parameters.

    The formula is:

                     _n_
        dJ(w)     2  \           /     S2s                (tf + ti).tf              (1 - S2s)(ts + ti).ts   \ 
        -----  =  -   >  ci . ti | ------------  -  -------------------------  +  ------------------------- |
        dS2f      5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2s_index] * data.fact_ti - data.tf_ti_tf * data.inv_tf_denom + data.one_s2s * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 S2s partial derivative.
####################################

# {S2f, S2s, ts} and {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_tf_S2s_ts_djw_dS2s(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2s partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without diffusion
    tensor parameters.

    The formula is:

                        _n_
        dJ(w)     2     \           /      1                 (ts + ti).ts        \ 
        -----  =  - S2f  >  ci . ti | ------------  -  ------------------------- |
        dS2s      5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=m
    """

    return 0.4 * params[data.s2f_index] * sum(data.ci * data.ti * (data.fact_ti - data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 tf partial derivative.
###################################

# {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_tf_S2s_ts_djw_dtf(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the tf partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} with or without diffusion tensor parameters.

    The formula is:

                              _n_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=m
    """

    return 0.4 * data.one_s2f * sum(data.ci * data.fact_djw_dtf, axis=2)



# Extended 2 ts partial derivative.
###################################

# {S2f, S2s, ts} and {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_S2s_ts_djw_dts(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the ts partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without diffusion
    tensor parameters.

    The formula is:

                                 _n_
        dJ(w)     2              \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - S2f(1 - S2s)  >  ci . ti^2 -----------------------------
         dts      5              /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=m
    """

    return 0.4 * data.s2f_s2 * sum(data.ci * data.fact_djw_dts, axis=2)




##############################
# Spectral density Hessians. #
##############################

"""
    The spectral density Hessians
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Data structure:  data.d2jw
    Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free
        parameters, model-free parameters)
    Type:  Numeric 4D matrix, Float64
    Dependencies:  None
    Required by:  data.d2ri


    Formulae
    ~~~~~~~~

    Original:  Model-free parameter - Model-free parameter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                         _n_     /                            dti   dti                     d2ti
         d2J(w)       2  \       |    2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) -------
        -------  =  - -   >  ci  | S2                         dDj   dDk                    dDj.dDk
        dDj.dDk       5  /__     |    ------------------------------------------------------------
                         i=m     \                       (1 + (w.ti)^2)^3

                                                                                           dti   dti                                  d2ti    \ 
                                   2((te + ti)^3 + 3.w^2.te^3.ti(te + ti) - (w.te)^4.ti^3) --- . ---  +  ((te + ti)^4 - (w.te.ti)^4) -------  |
                                                                                           dDj   dDk                                 dDj.dDk  |
                +  (1 - S2) . te^2 ---------------------------------------------------------------------------------------------------------  |
                                                                        ((te + ti)^2 + (w.te.ti)^2)^3                                         /


                         _n_
          d2J(w)      2  \    dci    dti  /        1 - (w.ti)^2                         (te + ti)^2 - (w.te.ti)^2   \ 
        ---------  =  -   >  ----- . ---  | S2 . ----------------  +  (1 - S2) . te^2 ----------------------------- |
        dDj.dPsij     5  /__ dPsij   dDj  \      (1 + (w.ti)^2)^2                     ((te + ti)^2 + (w.te.ti)^2)^2 /
                         i=m


                       _n_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2              (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  ci . ---  | ----------------  -  te^2 ----------------------------- |
        dDj.dS2     5  /__      dDj  \ (1 + (w.ti)^2)^2          ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=m


                                    _n_
         d2J(w)     4               \        dti                   (te + ti)^2 - 3(w.te.ti)^2
        -------  =  - (1 - S2) . te  >  ci . --- . ti . (te + ti) -----------------------------
        dDj.dte     5               /__      dDj                  ((te + ti)^2 + (w.te.ti)^2)^3
                                    i=m


                           _n_
           d2J(w)       2  \       d2ci         /      S2             (1 - S2)(te + ti)te    \ 
        -----------  =  -   >  ----------- . ti | ------------  +  ------------------------- |
        dPsij.dPsik     5  /__ dPsij.dPsik      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                           i=m


                         _n_
          d2J(w)      2  \    dci       /      1                 (te + ti)te         \ 
        ---------  =  -   >  ----- . ti | ------------  -  ------------------------- |
        dPsij.dS2     5  /__ dPsij      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                         i=m


                                 _n_
          d2J(w)      2          \    dci             (te + ti)^2 - (w.te.ti)^2
        ---------  =  - (1 - S2)  >  ----- . ti^2 . -----------------------------
        dPsij.dte     5          /__ dPsij          ((te + ti)^2 + (w.te.ti)^2)^2
                                 i=m


        d2J(w)
        ------  =  0
        dS2**2


                        _n_
         d2J(w)       2 \               (te + ti)^2 - (w.te.ti)^2
        -------  =  - -  >  ci . ti^2 -----------------------------
        dS2.dte       5 /__           ((te + ti)^2 + (w.te.ti)^2)^2
                        i=m


                                _n_
        d2J(w)       4          \             (te + ti)^3 + 3.w^2.ti^3.te.(te + ti) - (w.ti)^4.te^3
        ------  =  - - (1 - S2)  >  ci . ti^2 -----------------------------------------------------
        dte**2       5          /__                        ((te + ti)^2 + (w.te.ti)^2)^3
                                i=m


    Original:  Other parameters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dS2.dRex             dS2.dcsa             dS2.dr


         d2J(w)              d2J(w)               d2J(w)
        --------  =  0   ,  --------  =  0   ,    ------  =  0
        dte.dRex            dte.dcsa              dte.dr


         d2J(w)              d2J(w)                d2J(w)
        -------  =  0   ,  ---------  =  0   ,    -------  =  0
        dRex**2            dRex.dcsa              dRex.dr


         d2J(w)             d2J(w)
        -------  =  0   ,  -------  =  0
        dcsa**2            dcsa.dr


        d2J(w)
        ------  =  0
        dr**2


    Extended:  Model-free parameter - Model-free parameter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                         _n_     /                            dti   dti                     d2ti
         d2J(w)       2  \       |    2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) -------
        -------  =  - -   >  ci  | S2                         dDj   dDk                    dDj.dDk
        dDj.dDk       5  /__     |    ------------------------------------------------------------
                         i=m     \                       (1 + (w.ti)^2)^3

                                                                                            dti   dti                                  d2ti
                                    2((tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3) --- . ---  +  ((tf + ti)^4 - (w.tf.ti)^4) -------
                                                                                            dDj   dDk                                 dDj.dDk
                +  (1 - S2f) . tf^2 ---------------------------------------------------------------------------------------------------------
                                                                         ((tf + ti)^2 + (w.tf.ti)^2)^3

                                                                                             dti   dti                                  d2ti    \ 
                                     2((ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3) --- . ---  +  ((ts + ti)^4 - (w.ts.ti)^4) -------  |
                                                                                             dDj   dDk                                 dDj.dDk  |
                +  (S2f - S2) . ts^2 ---------------------------------------------------------------------------------------------------------  |
                                                                          ((ts + ti)^2 + (w.ts.ti)^2)^3                                         /


                         _n_
          d2J(w)      2  \    dci    dti  /        1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        ---------  =  -   >  ----- . ---  | S2 . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  (S2f - S2) . ts^2 ----------------------------- |
        dDj.dPsij     5  /__ dPsij   dDj  \      (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                         i=m


                       _n_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dDj.dS2     5  /__      dDj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=m


                          _n_
         d2J(w)        2  \        dti  /        (tf + ti)^2 - (w.tf.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - -   >  ci . ---  | tf^2 -----------------------------  -  ts^2 ----------------------------- |
        dDj.dS2f       5  /__      dDj  \      ((tf + ti)^2 + (w.tf.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                          i=m


                                     _n_
         d2J(w)     4                \        dti                   (tf + ti)^2 - 3(w.tf.ti)^2
        -------  =  - (1 - S2f) . tf  >  ci . --- . ti . (tf + ti) -----------------------------
        dDj.dtf     5                /__      dDj                  ((tf + ti)^2 + (w.tf.ti)^2)^3
                                     i=m


                                      _n_
         d2J(w)     4                 \        dti                   (ts + ti)^2 - 3(w.ts.ti)^2
        -------  =  - (S2f - S2) . ts  >  ci . --- . ti . (ts + ti) -----------------------------
        dDj.dts     5                 /__      dDj                  ((ts + ti)^2 + (w.ts.ti)^2)^3
                                      i=m


                           _n_
           d2J(w)       2  \       d2ci         /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        -----------  =  -   >  ----------- . ti | ------------  +  -------------------------  +  ------------------------- |
        dPsij.dPsik     5  /__ dPsij.dPsik      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                           i=m


                         _n_
          d2J(w)      2  \    dci       /      1                 (ts + ti)ts         \ 
        ---------  =  -   >  ----- . ti | ------------  -  ------------------------- |
        dPsij.dS2     5  /__ dPsij      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                         i=m


                            _n_
          d2J(w)         2  \    dci       /       (tf + ti)tf                   (ts + ti)ts         \ 
        ----------  =  - -   >  ----- . ti | -------------------------  -  ------------------------- |
        dPsij.dS2f       5  /__ dPsij      \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                            i=m


                                  _n_
          d2J(w)      2           \    dci           (tf + ti)^2 - (w.tf.ti)^2
        ---------  =  - (1 - S2f)  >  ----- . ti^2 -----------------------------
        dPsij.dtf     5           /__ dPsij        ((tf + ti)^2 + (w.tf.ti)^2)^2
                                  i=m


                                   _n_
          d2J(w)      2            \    dci           (ts + ti)^2 - (w.ts.ti)^2
        ---------  =  - (S2f - S2)  >  ----- . ti^2 -----------------------------
        dPsij.dts     5            /__ dPsij        ((ts + ti)^2 + (w.ts.ti)^2)^2
                                   i=m


        d2J(w)              d2J(w)               d2J(w)
        ------  =  0   ,   --------  =  0   ,   -------  =  0
        dS2**2             dS2.dS2f             dS2.dtf


                         _n_
         d2J(w)       2  \               (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - -   >  ci . ti^2 -----------------------------
        dS2.dts       5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                         i=m


         d2J(w)
        -------  =  0
        dS2f**2


                          _n_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=m


                        _n_
         d2J(w)      2  \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  -   >  ci . ti^2 -----------------------------
        dS2f.dts     5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                        i=m


                                 _n_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=m


         d2J(w)
        -------  =  0
        dtf.dts


                                  _n_
        d2J(w)       4            \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - (S2f - S2)  >  ci . ti^2 -----------------------------------------------------
        dts**2       5            /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                  i=m


    Extended:  Other parameters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0   ,   ---------  =  0   ,   -------  =  0
        dS2f.dRex             dS2f.dcsa             dS2f.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dS2.dRex             dS2.dcsa             dS2.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dtf.dRex             dtf.dcsa             dtf.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dts.dRex             dts.dcsa             dts.dr


         d2J(w)               d2J(w)               d2J(w)
        -------  =  0   ,   ---------  =  0   ,   -------  =  0
        dRex**2             dRex.dcsa             dRex.dr


         d2J(w)              d2J(w)
        -------  =  0   ,   -------  =  0
        dcsa**2             dcsa.dr


        d2J(w)
        ------  =  0
        dr**2


    Extended 2:  Model-free parameter - Model-free parameter
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

                         _n_     /                                   dti   dti                     d2ti
         d2J(w)       2  \       |           2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) -------
        -------  =  - -   >  ci  | S2f . S2s                         dDj   dDk                    dDj.dDk
        dDj.dDk       5  /__     |           ------------------------------------------------------------
                         i=m     \                              (1 + (w.ti)^2)^3

                                                                                            dti   dti                                  d2ti
                                    2((tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3) --- . ---  +  ((tf + ti)^4 - (w.tf.ti)^4) -------
                                                                                            dDj   dDk                                 dDj.dDk
                +  (1 - S2f) . tf^2 ---------------------------------------------------------------------------------------------------------
                                                                         ((tf + ti)^2 + (w.tf.ti)^2)^3

                                                                                               dti   dti                                  d2ti    \ 
                                       2((ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3) --- . ---  +  ((ts + ti)^4 - (w.ts.ti)^4) -------  |
                                                                                               dDj   dDk                                 dDj.dDk  |
                +  S2f(1 - S2s) . ts^2 ---------------------------------------------------------------------------------------------------------  |
                                                                            ((ts + ti)^2 + (w.ts.ti)^2)^3                                         /


                         _n_
          d2J(w)      2  \    dci    dti  /               1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                             (ts + ti)^2 - (w.ts.ti)^2   \ 
        ---------  =  -   >  ----- . ---  | S2f . S2s . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  S2f(1 - S2s) . ts^2 ----------------------------- |
        dDj.dPsij     5  /__ dPsij   dDj  \             (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                         ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                         i=m


                        _n_
         d2J(w)      2  \        dti  /         1 - (w.ti)^2              (tf + ti)^2 - (w.tf.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  ci . ---  | S2s . ----------------  -  tf^2 -----------------------------  +  (1 - S2s) . ts^2 ----------------------------- |
        dDj.dS2f     5  /__      dDj  \       (1 + (w.ti)^2)^2          ((tf + ti)^2 + (w.tf.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=m


                           _n_
         d2J(w)      2     \        dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - S2f  >  ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dDj.dS2s     5     /__      dDj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                           i=m


                                     _n_
         d2J(w)     4                \        dti                   (tf + ti)^2 - 3(w.tf.ti)^2
        -------  =  - (1 - S2f) . tf  >  ci . --- . ti . (tf + ti) -----------------------------
        dDj.dtf     5                /__      dDj                  ((tf + ti)^2 + (w.tf.ti)^2)^3
                                     i=m


                                        _n_
         d2J(w)     4                   \        dti                   (ts + ti)^2 - 3(w.ts.ti)^2
        -------  =  - S2f(1 - S2s) . ts  >  ci . --- . ti . (ts + ti) -----------------------------
        dDj.dts     5                   /__      dDj                  ((ts + ti)^2 + (w.ts.ti)^2)^3
                                        i=m


                           _n_
           d2J(w)       2  \       d2ci         /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        -----------  =  -   >  ----------- . ti | ------------  +  -------------------------  +  ------------------------- |
        dPsij.dPsik     5  /__ dPsij.dPsik      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                           i=m


                          _n_
          d2J(w)       2  \    dci       /      S2s               (tf + ti)tf               (1 - S2s)(ts + ti)ts    \ 
        ----------  =  -   >  ----- . ti | ------------  -  -------------------------  +  ------------------------- |
        dPsij.dS2f     5  /__ dPsij      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                          i=m


                             _n_
          d2J(w)       2     \    dci       /      1                 (ts + ti)ts         \ 
        ----------  =  - S2f  >  ----- . ti | ------------  -  ------------------------- |
        dPsij.dS2s     5     /__ dPsij      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                             i=m


                                  _n_
          d2J(w)      2           \    dci           (tf + ti)^2 - (w.tf.ti)^2
        ---------  =  - (1 - S2f)  >  ----- . ti^2 -----------------------------
        dPsij.dtf     5           /__ dPsij        ((tf + ti)^2 + (w.tf.ti)^2)^2
                                  i=m


                                     _n_
          d2J(w)      2              \    dci           (ts + ti)^2 - (w.ts.ti)^2
        ---------  =  - S2f(1 - S2s)  >  ----- . ti^2 -----------------------------
        dPsij.dts     5              /__ dPsij        ((ts + ti)^2 + (w.ts.ti)^2)^2
                                     i=m


         d2J(w)
        -------  =  0
        dS2f**2


                         _n_
          d2J(w)      2  \           /      1                 (ts + ti).ts        \ 
        ---------  =  -   >  ci . ti | ------------  -  ------------------------- |
        dS2f.dS2s     5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                         i=m


                          _n_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=m


                                 _n_
         d2J(w)      2           \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  - (1 - S2s)  >  ci . ti^2 -----------------------------
        dS2f.dts     5           /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=m


         d2J(w)              d2J(w)
        -------  =  0   ,   --------  =  0
        dS2s**2             dS2s.dtf


                             _n_
         d2J(w)        2     \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  - - S2f  >  ci . ti^2 -----------------------------
        dS2s.dts       5     /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                             i=m


                                 _n_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=m


         d2J(w)
        -------  =  0
        dtf.dts


                                    _n_
        d2J(w)       4              \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - S2f(1 - S2s)  >  ci . ti^2 -----------------------------------------------------
        dts**2       5              /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                    i=m



    Extended 2:  Other parameters
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0   ,   ---------  =  0   ,   -------  =  0
        dS2f.dRex             dS2f.dcsa             dS2f.dr


          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0   ,   ---------  =  0   ,   -------  =  0
        dS2s.dRex             dS2s.dcsa             dS2s.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dtf.dRex             dtf.dcsa             dtf.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0   ,   --------  =  0   ,   ------  =  0
        dts.dRex             dts.dcsa             dts.dr


         d2J(w)               d2J(w)               d2J(w)
        -------  =  0   ,   ---------  =  0   ,   -------  =  0
        dRex**2             dRex.dcsa             dRex.dr


         d2J(w)              d2J(w)
        -------  =  0   ,   -------  =  0
        dcsa**2             dcsa.dr


        d2J(w)
        ------  =  0
        dr**2
"""


# Original Dj - Dk partial derivative.
######################################

# {} with diffusion parameters.

def calc_diff_d2jw_dDjdDk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dk double partial derivative of the original
    model-free formula with no parameters {} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_     /                         dti   dti                     d2ti   \ 
         d2J(w)       2  \       | 2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) ------- |
        -------  =  - -   >  ci  |                         dDj   dDk                    dDj.dDk |
        dDj.dDk       5  /__     | ------------------------------------------------------------ |
                         i=m     \                    (1 + (w.ti)^2)^3                          /
    """

    return -0.4 * sum(data.ci * (2 * data.ti * data.frq_sqrd_list_ext * (3.0 - data.w_ti_sqrd) * data.dti[j] * data.dti[k] - (1.0 - data.w_ti_sqrd**2) * data.d2ti[j, k]) * data.fact_ti**3, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dDjdDk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dk double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is:

                           _n_     /                         dti   dti                     d2ti   \ 
         d2J(w)       2    \       | 2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) ------- |
        -------  =  - - S2  >  ci  |                         dDj   dDk                    dDj.dDk |
        dDj.dDk       5    /__     | ------------------------------------------------------------ |
                           i=m     \                    (1 + (w.ti)^2)^3                          /
    """

    return -0.4 * params[data.s2_index] * sum(data.ci * (2 * data.ti * data.frq_sqrd_list_ext * (3.0 - data.w_ti_sqrd) * data.dti[j] * data.dti[k] - (1.0 - data.w_ti_sqrd**2) * data.d2ti[j, k]) * data.fact_ti**3, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dDjdDk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dk double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_     /                            dti   dti                     d2ti
         d2J(w)       2  \       |    2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) -------
        -------  =  - -   >  ci  | S2                         dDj   dDk                    dDj.dDk
        dDj.dDk       5  /__     |    ------------------------------------------------------------
                         i=m     \                       (1 + (w.ti)^2)^3

                                                                                           dti   dti                                  d2ti    \ 
                                   2((te + ti)^3 + 3.w^2.te^3.ti(te + ti) - (w.te)^4.ti^3) --- . ---  +  ((te + ti)^4 - (w.te.ti)^4) -------  |
                                                                                           dDj   dDk                                 dDj.dDk  |
                +  (1 - S2) . te^2 ---------------------------------------------------------------------------------------------------------  |
                                                                        ((te + ti)^2 + (w.te.ti)^2)^3                                         /
    """

    # ti.
    fact_ti = params[data.s2_index] * (2 * data.ti * data.frq_sqrd_list_ext * (3.0 - data.w_ti_sqrd) * data.dti[j] * data.dti[k] - (1.0 - data.w_ti_sqrd**2) * data.d2ti[j, k]) * data.fact_ti**3

    # te.
    fact_te = 2.0 * (data.te_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.te_index]**3 * data.ti * data.te_ti - (data.frq_list_ext * params[data.te_index])**4 * data.ti**3) * data.dti[j] * data.dti[k]  +  (data.te_ti**4 - data.w_te_ti_sqrd**2) * data.d2ti[j, k]
    fact_te = data.one_s2 * params[data.te_index]**2 * fact_te * data.inv_te_denom**3

    return -0.4 * sum(data.ci * (fact_ti + fact_te), axis=2)



# Original Dj - Psij partial derivative.
########################################


# {} with diffusion parameters.

def calc_diff_d2jw_dDjdPsij(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Psij double partial derivative of the original
    model-free formula with no parameters {} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci    dti     1 - (w.ti)^2
        ---------  =  -   >  ----- . --- . ----------------
        dDj.dPsij     5  /__ dPsij   dDj   (1 + (w.ti)^2)^2
                         i=m
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * data.fact_ti_djw_dti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dDjdPsij(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Psij double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is:

                           _n_
          d2J(w)      2    \    dci    dti     1 - (w.ti)^2
        ---------  =  - S2  >  ----- . --- . ----------------
        dDj.dPsij     5    /__ dPsij   dDj   (1 + (w.ti)^2)^2
                           i=m
    """

    return 0.4 * params[data.s2_index] * sum(data.dci[j] * data.dti[k] * data.fact_ti_djw_dti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dDjdPsij(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Psij double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci    dti  /        1 - (w.ti)^2                         (te + ti)^2 - (w.te.ti)^2   \ 
        ---------  =  -   >  ----- . ---  | S2 . ----------------  +  (1 - S2) . te^2 ----------------------------- |
        dDj.dPsij     5  /__ dPsij   dDj  \      (1 + (w.ti)^2)^2                     ((te + ti)^2 + (w.te.ti)^2)^2 /
                         i=m
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_index] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti), axis=2)



# Original Dj - S2 partial derivative.
######################################

# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dDjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2 double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is:

                       _n_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2   \ 
        -------  =  -   >  ci . ---  | ---------------- |
        dDj.dS2     5  /__      dDj  \ (1 + (w.ti)^2)^2 /
                       i=m
    """

    return 0.4 * sum(data.ci * data.dti[k] * data.fact_ti_djw_dti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dDjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2 double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is:

                       _n_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2              (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  ci . ---  | ----------------  -  te^2 ----------------------------- |
        dDj.dS2     5  /__      dDj  \ (1 + (w.ti)^2)^2          ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=m
    """

    return 0.4 * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_te_djw_dti), axis=2)



# Original Dj - te partial derivative.
#######################################

# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dDjdte(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - te double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is:

                                    _n_
         d2J(w)     4               \        dti                   (te + ti)^2 - 3(w.te.ti)^2
        -------  =  - (1 - S2) . te  >  ci . --- . ti . (te + ti) -----------------------------
        dDj.dte     5               /__      dDj                  ((te + ti)^2 + (w.te.ti)^2)^3
                                    i=m
    """

    return 0.8 * data.one_s2 * params[data.te_index] * sum(data.ci * data.dti[k] * data.ti * data.te_ti * (data.te_ti_sqrd - 3.0 * data.w_te_ti_sqrd) * data.inv_te_denom**3, axis=2)



# Original Psij - Psik partial derivative.
##########################################

# {} with diffusion parameters.

def calc_diff_d2jw_dPsijdPsik(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - Psik double partial derivative of the
    original model-free formula with no parameters {} together with diffusion tensor parameters.

    The model-free Hessian is:

                           _n_
           d2J(w)       2  \       d2ci           ti
        -----------  =  -   >  ----------- . ------------
        dPsij.dPsik     5  /__ dPsij.dPsik   1 + (w.ti)^2
                           i=m
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * data.fact_ti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dPsijdPsik(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - Psik double partial derivative of the
    original model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is:

                             _n_
           d2J(w)       2    \       d2ci           ti
        -----------  =  - S2  >  ----------- . ------------
        dPsij.dPsik     5    /__ dPsij.dPsik   1 + (w.ti)^2
                             i=m
    """

    return 0.4 * params[data.s2_index] * sum(data.d2ci[j, k] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dPsijdPsik(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - Psik double partial derivative of the
    original model-free formula with the parameters {S2, te} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                           _n_
           d2J(w)       2  \       d2ci         /      S2             (1 - S2)(te + ti)te    \ 
        -----------  =  -   >  ----------- . ti | ------------  +  ------------------------- |
        dPsij.dPsik     5  /__ dPsij.dPsik      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                           i=m
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2_index] * data.fact_ti + data.one_s2 * data.te_ti_te * data.inv_te_denom), axis=2)



# Original Psij - S2 partial derivative.
########################################

# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dPsijdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - S2 double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci       /      1       \ 
        ---------  =  -   >  ----- . ti | ------------ |
        dPsij.dS2     5  /__ dPsij      \ 1 + (w.ti)^2 /
                         i=m
    """

    return 0.4 * sum(data.dci[k] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dPsijdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - S2 double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci       /      1                 (te + ti)te         \ 
        ---------  =  -   >  ----- . ti | ------------  -  ------------------------- |
        dPsij.dS2     5  /__ dPsij      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                         i=m
    """

    return 0.4 * sum(data.dci[k] * data.ti * (data.fact_ti - data.te_ti_te * data.inv_te_denom), axis=2)



# Original Psij - te partial derivative.
########################################

# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dPsijdte(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - te double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is:

                                 _n_
          d2J(w)      2          \    dci             (te + ti)^2 - (w.te.ti)^2
        ---------  =  - (1 - S2)  >  ----- . ti^2 . -----------------------------
        dPsij.dte     5          /__ dPsij          ((te + ti)^2 + (w.te.ti)^2)^2
                                 i=m
    """

    return 0.4 * data.one_s2 * sum(data.dci[k] * data.fact_djw_dte, axis=2)



# Original S2 - te partial derivative.
######################################

# {S2, te} with or without diffusion parameters.

def calc_S2_te_d2jw_dS2dte(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2 - te double partial derivative of the original
    model-free formula with the parameters {S2, te} with or without diffusion tensor parameters.

    The model-free Hessian is:

                        _n_
         d2J(w)       2 \               (te + ti)^2 - (w.te.ti)^2
        -------  =  - -  >  ci . ti^2 -----------------------------
        dS2.dte       5 /__           ((te + ti)^2 + (w.te.ti)^2)^2
                        i=m
    """

    return -0.4 * sum(data.ci * data.fact_djw_dte, axis=2)



# Original te - te partial derivative.
######################################

# {S2, te} with or without diffusion parameters.

def calc_S2_te_d2jw_dte2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the te - te double partial derivative of the original
    model-free formula with the parameters {S2, te} with or without diffusion tensor parameters.

    The model-free Hessian is:

                                _n_
        d2J(w)       4          \             (te + ti)^3 + 3.w^2.ti^3.te.(te + ti) - (w.ti)^4.te^3
        ------  =  - - (1 - S2)  >  ci . ti^2 -----------------------------------------------------
        dte**2       5          /__                        ((te + ti)^2 + (w.te.ti)^2)^3
                                i=m
    """

    num = data.te_ti**3 + 3.0 * data.ti**3 * params[data.te_index] * data.frq_sqrd_list_ext * data.te_ti - data.w_ti_sqrd**2 * params[data.te_index]**3

    return -0.8 * data.one_s2 * sum(data.ci * data.ti**2 * num * data.inv_te_denom**3, axis=2)



# Extended Dj - Dk partial derivative.
######################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dDjdDk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dk double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_     /                            dti   dti                     d2ti
         d2J(w)       2  \       |    2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) -------
        -------  =  - -   >  ci  | S2                         dDj   dDk                    dDj.dDk
        dDj.dDk       5  /__     |    ------------------------------------------------------------
                         i=m     \                       (1 + (w.ti)^2)^3

                                                                                             dti   dti                                  d2ti    \ 
                                     2((ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3) --- . ---  +  ((ts + ti)^4 - (w.ts.ti)^4) -------  |
                                                                                             dDj   dDk                                 dDj.dDk  |
                +  (S2f - S2) . ts^2 ---------------------------------------------------------------------------------------------------------  |
                                                                          ((ts + ti)^2 + (w.ts.ti)^2)^3                                         /
    """

    # ti.
    fact_ti = params[data.s2_index] * (2 * data.ti * data.frq_sqrd_list_ext * (3.0 - data.w_ti_sqrd) * data.dti[j] * data.dti[k] - (1.0 - data.w_ti_sqrd**2) * data.d2ti[j, k]) * data.fact_ti**3

    # ts.
    fact_ts = 2.0 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_index]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_index])**4 * data.ti**3) * data.dti[j] * data.dti[k]  +  (data.ts_ti**4 - data.w_ts_ti_sqrd**2) * data.d2ti[j, k]
    fact_ts = data.s2f_s2 * params[data.ts_index]**2 * fact_ts * data.inv_ts_denom**3

    return -0.4 * sum(data.ci * (fact_ti + fact_ts), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dDjdDk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dk double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                         _n_     /                            dti   dti                     d2ti
         d2J(w)       2  \       |    2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) -------
        -------  =  - -   >  ci  | S2                         dDj   dDk                    dDj.dDk
        dDj.dDk       5  /__     |    ------------------------------------------------------------
                         i=m     \                       (1 + (w.ti)^2)^3

                                                                                            dti   dti                                  d2ti
                                    2((tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3) --- . ---  +  ((tf + ti)^4 - (w.tf.ti)^4) -------
                                                                                            dDj   dDk                                 dDj.dDk
                +  (1 - S2f) . tf^2 ---------------------------------------------------------------------------------------------------------
                                                                         ((tf + ti)^2 + (w.tf.ti)^2)^3

                                                                                             dti   dti                                  d2ti    \ 
                                     2((ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3) --- . ---  +  ((ts + ti)^4 - (w.ts.ti)^4) -------  |
                                                                                             dDj   dDk                                 dDj.dDk  |
                +  (S2f - S2) . ts^2 ---------------------------------------------------------------------------------------------------------  |
                                                                          ((ts + ti)^2 + (w.ts.ti)^2)^3                                         /
    """

    # ti.
    fact_ti = params[data.s2_index] * (2 * data.ti * data.frq_sqrd_list_ext * (3.0 - data.w_ti_sqrd) * data.dti[j] * data.dti[k] - (1.0 - data.w_ti_sqrd**2) * data.d2ti[j, k]) * data.fact_ti**3

    # tf.
    fact_tf = 2.0 * (data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.tf_index]**3 * data.ti * data.tf_ti - (data.frq_list_ext * params[data.tf_index])**4 * data.ti**3) * data.dti[j] * data.dti[k]  +  (data.tf_ti**4 - data.w_tf_ti_sqrd**2) * data.d2ti[j, k]
    fact_tf = data.one_s2f * params[data.tf_index]**2 * fact_tf * data.inv_tf_denom**3

    # ts.
    fact_ts = 2.0 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_index]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_index])**4 * data.ti**3) * data.dti[j] * data.dti[k]  +  (data.ts_ti**4 - data.w_ts_ti_sqrd**2) * data.d2ti[j, k]
    fact_ts = data.s2f_s2 * params[data.ts_index]**2 * fact_ts * data.inv_ts_denom**3

    return -0.4 * sum(data.ci * (fact_ti + fact_tf + fact_ts), axis=2)



# Extended Dj - Psij partial derivative.
########################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dDjdPsij(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Psij double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci    dti  /        1 - (w.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        ---------  =  -   >  ----- . ---  | S2 . ----------------  +  (S2f - S2) . ts^2 ----------------------------- |
        dDj.dPsij     5  /__ dPsij   dDj  \      (1 + (w.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                         i=m
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_index] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dDjdPsij(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Psij double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci    dti  /        1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        ---------  =  -   >  ----- . ---  | S2 . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  (S2f - S2) . ts^2 ----------------------------- |
        dDj.dPsij     5  /__ dPsij   dDj  \      (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                         i=m
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_index] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)



# Extended Dj - S2 partial derivative.
######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dDjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2 double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is:

                       _n_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dDj.dS2     5  /__      dDj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=m
    """

    return 0.4 * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_ts_djw_dti), axis=2)



# Extended Dj - S2f partial derivative.
#######################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dDjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is:

                        _n_
         d2J(w)      2  \        dti  /        (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  ci . ---  | ts^2 ----------------------------- |
        dDj.dS2f     5  /__      dDj  \      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=m
    """

    return 0.4 * sum(data.ci * data.dti[k] * data.fact_ts_djw_dti, axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dDjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                          _n_
         d2J(w)        2  \        dti  /        (tf + ti)^2 - (w.tf.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - -   >  ci . ---  | tf^2 -----------------------------  -  ts^2 ----------------------------- |
        dDj.dS2f       5  /__      dDj  \      ((tf + ti)^2 + (w.tf.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                          i=m
    """

    return -0.4 * sum(data.ci * data.dti[k] * (data.fact_tf_djw_dti - data.fact_ts_djw_dti), axis=2)



# Extended Dj - tf partial derivative.
######################################

# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dDjdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                                     _n_
         d2J(w)     4                \        dti                   (tf + ti)^2 - 3(w.tf.ti)^2
        -------  =  - (1 - S2f) . tf  >  ci . --- . ti . (tf + ti) -----------------------------
        dDj.dtf     5                /__      dDj                  ((tf + ti)^2 + (w.tf.ti)^2)^3
                                     i=m
    """

    return 0.8 * data.one_s2f * params[data.tf_index] * sum(data.ci * data.dti[k] * data.ti * data.tf_ti * (data.tf_ti_sqrd - 3.0 * data.w_tf_ti_sqrd) * data.inv_tf_denom**3, axis=2)



# Extended Dj - ts partial derivative.
######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dDjdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is:

                                      _n_
         d2J(w)     4                 \        dti                   (ts + ti)^2 - 3(w.ts.ti)^2
        -------  =  - (S2f - S2) . ts  >  ci . --- . ti . (ts + ti) -----------------------------
        dDj.dts     5                 /__      dDj                  ((ts + ti)^2 + (w.ts.ti)^2)^3
                                      i=m
    """

    return 0.8 * data.s2f_s2 * params[data.ts_index] * sum(data.ci * data.dti[k] * data.ti * data.ts_ti * (data.ts_ti_sqrd - 3.0 * data.w_ts_ti_sqrd) * data.inv_ts_denom**3, axis=2)



# Extended Psij - Psik partial derivative.
##########################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dPsijdPsik(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - Psik double partial derivative of the
    extended model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                           _n_
           d2J(w)       2  \       d2ci         /      S2            (S2f - S2)(ts + ti)ts   \ 
        -----------  =  -   >  ----------- . ti | ------------  +  ------------------------- |
        dPsij.dPsik     5  /__ dPsij.dPsik      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                           i=m
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2_index] * data.fact_ti + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dPsijdPsik(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - Psik double partial derivative of the
    extended model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                           _n_
           d2J(w)       2  \       d2ci         /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        -----------  =  -   >  ----------- . ti | ------------  +  -------------------------  +  ------------------------- |
        dPsij.dPsik     5  /__ dPsij.dPsik      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                           i=m
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2_index] * data.fact_ti + data.one_s2f * data.tf_ti_tf * data.inv_tf_denom + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended Psij - S2 partial derivative.
########################################

# {S2f, S2, ts} and {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dPsijdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - S2 double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} and {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci       /      1                 (ts + ti)ts         \ 
        ---------  =  -   >  ----- . ti | ------------  -  ------------------------- |
        dPsij.dS2     5  /__ dPsij      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                         i=m
    """

    return 0.4 * sum(data.dci[k] * data.ti * (data.fact_ti - data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended Psij - S2f partial derivative.
#########################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dPsijdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - S2f double partial derivative of the
    extended model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                          _n_
          d2J(w)       2  \    dci             (ts + ti)ts
        ----------  =  -   >  ----- . ti -------------------------
        dPsij.dS2f     5  /__ dPsij      (ts + ti)^2 + (w.ts.ti)^2
                          i=m
    """

    return 0.4 * sum(data.dci[k] * data.ti * data.ts_ti_ts * data.inv_ts_denom, axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dPsijdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - S2f double partial derivative of the
    extended model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                            _n_
          d2J(w)         2  \    dci       /       (tf + ti)tf                   (ts + ti)ts         \ 
        ----------  =  - -   >  ----- . ti | -------------------------  -  ------------------------- |
        dPsij.dS2f       5  /__ dPsij      \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                            i=m
    """

    return -0.4 * sum(data.dci[k] * data.ti * (data.tf_ti_tf * data.inv_tf_denom - data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended Psij - tf partial derivative.
########################################

# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dPsijdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                                  _n_
          d2J(w)      2           \    dci           (tf + ti)^2 - (w.tf.ti)^2
        ---------  =  - (1 - S2f)  >  ----- . ti^2 -----------------------------
        dPsij.dtf     5           /__ dPsij        ((tf + ti)^2 + (w.tf.ti)^2)^2
                                  i=m
    """

    return 0.4 * data.one_s2f * sum(data.dci[k] * data.fact_djw_dtf, axis=2)



# Extended Psij - ts partial derivative.
########################################

# {S2f, S2, ts} and {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dPsijdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is:

                                   _n_
          d2J(w)      2            \    dci           (ts + ti)^2 - (w.ts.ti)^2
        ---------  =  - (S2f - S2)  >  ----- . ti^2 -----------------------------
        dPsij.dts     5            /__ dPsij        ((ts + ti)^2 + (w.ts.ti)^2)^2
                                   i=m
    """

    return 0.4 * data.s2f_s2 * sum(data.dci[k] * data.fact_djw_dts, axis=2)



# Extended S2 - ts partial derivative.
######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_d2jw_dS2dts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2 - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
         d2J(w)       2  \               (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - -   >  ci . ti^2 -----------------------------
        dS2.dts       5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                         i=m
    """

    return -0.4 * sum(data.ci * data.fact_djw_dts, axis=2)



# Extended S2f - tf partial derivative.
#######################################

# {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_tf_S2_ts_d2jw_dS2fdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2f - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} with or without diffusion tensor
    parameters.

    The model-free Hessian is:

                          _n_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=m
    """

    return -0.4 * sum(data.ci * data.fact_djw_dtf, axis=2)



# Extended S2f - ts partial derivative.
#######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_d2jw_dS2fdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2f - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is:

                        _n_
         d2J(w)      2  \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  -   >  ci . ti^2 -----------------------------
        dS2f.dts     5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                        i=m
    """

    return 0.4 * sum(data.ci * data.fact_djw_dts, axis=2)



# Extended tf - tf partial derivative.
######################################

# {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_tf_S2_ts_d2jw_dtf2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the tf - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} with or without diffusion tensor
    parameters.

    The model-free Hessian is:

                                 _n_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=m
    """

    num = data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.tf_index] * data.tf_ti - data.w_ti_sqrd**2 * params[data.tf_index]**3

    return -0.8 * data.one_s2f * sum(data.ci * data.ti**2 * num * data.inv_tf_denom**3, axis=2)



# Extended ts - ts partial derivative.
######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_d2jw_dts2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the ts - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is:

                                  _n_
        d2J(w)       4            \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - (S2f - S2)  >  ci . ti^2 -----------------------------------------------------
        dts**2       5            /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                  i=m
    """

    num = data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.ts_index] * data.ts_ti - data.w_ti_sqrd**2 * params[data.ts_index]**3

    return -0.8 * data.s2f_s2 * sum(data.ci * data.ti**2 * num * data.inv_ts_denom**3, axis=2)



# Extended 2 Dj - Dk partial derivative.
########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dDjdDk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dk double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is:

                            _n_     /                             dti   dti                     d2ti
         d2J(w)       2     \       |     2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) -------
        -------  =  - - S2f  >  ci  | S2s                         dDj   dDk                    dDj.dDk
        dDj.dDk       5     /__     |     ------------------------------------------------------------
                            i=m     \                        (1 + (w.ti)^2)^3

                                                                                            dti   dti                                  d2ti    \ 
                                    2((ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3) --- . ---  +  ((ts + ti)^4 - (w.ts.ti)^4) -------  |
                                                                                            dDj   dDk                                 dDj.dDk  |
                +  (1 - S2s) . ts^2 ---------------------------------------------------------------------------------------------------------  |
                                                                         ((ts + ti)^2 + (w.ts.ti)^2)^3                                         /
    """

    # ti.
    fact_ti = params[data.s2s_index] * (2 * data.ti * data.frq_sqrd_list_ext * (3.0 - data.w_ti_sqrd) * data.dti[j] * data.dti[k] - (1.0 - data.w_ti_sqrd**2) * data.d2ti[j, k]) * data.fact_ti**3

    # ts.
    fact_ts = 2.0 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_index]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_index])**4 * data.ti**3) * data.dti[j] * data.dti[k]  +  (data.ts_ti**4 - data.w_ts_ti_sqrd**2) * data.d2ti[j, k]
    fact_ts = data.one_s2s * params[data.ts_index]**2 * fact_ts * data.inv_ts_denom**3

    return -0.4 * params[data.s2f_index] * sum(data.ci * (fact_ti + fact_ts), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dDjdDk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dk double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                         _n_     /                                   dti   dti                     d2ti
         d2J(w)       2  \       |           2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) -------
        -------  =  - -   >  ci  | S2f . S2s                         dDj   dDk                    dDj.dDk
        dDj.dDk       5  /__     |           ------------------------------------------------------------
                         i=m     \                              (1 + (w.ti)^2)^3

                                                                                            dti   dti                                  d2ti
                                    2((tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3) --- . ---  +  ((tf + ti)^4 - (w.tf.ti)^4) -------
                                                                                            dDj   dDk                                 dDj.dDk
                +  (1 - S2f) . tf^2 ---------------------------------------------------------------------------------------------------------
                                                                         ((tf + ti)^2 + (w.tf.ti)^2)^3

                                                                                               dti   dti                                  d2ti    \ 
                                       2((ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3) --- . ---  +  ((ts + ti)^4 - (w.ts.ti)^4) -------  |
                                                                                               dDj   dDk                                 dDj.dDk  |
                +  S2f(1 - S2s) . ts^2 ---------------------------------------------------------------------------------------------------------  |
                                                                            ((ts + ti)^2 + (w.ts.ti)^2)^3                                         /
    """

    # ti.
    fact_ti = params[data.s2f_index] * params[data.s2s_index] * (2 * data.ti * data.frq_sqrd_list_ext * (3.0 - data.w_ti_sqrd) * data.dti[j] * data.dti[k] - (1.0 - data.w_ti_sqrd**2) * data.d2ti[j, k]) * data.fact_ti**3

    # tf.
    fact_tf = 2.0 * (data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.tf_index]**3 * data.ti * data.tf_ti - (data.frq_list_ext * params[data.tf_index])**4 * data.ti**3) * data.dti[j] * data.dti[k]  +  (data.tf_ti**4 - data.w_tf_ti_sqrd**2) * data.d2ti[j, k]
    fact_tf = data.one_s2f * params[data.tf_index]**2 * fact_tf * data.inv_tf_denom**3

    # ts.
    fact_ts = 2.0 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_index]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_index])**4 * data.ti**3) * data.dti[j] * data.dti[k]  +  (data.ts_ti**4 - data.w_ts_ti_sqrd**2) * data.d2ti[j, k]
    fact_ts = data.s2f_s2 * params[data.ts_index]**2 * fact_ts * data.inv_ts_denom**3

    return -0.4 * sum(data.ci * (fact_ti + fact_tf + fact_ts), axis=2)



# Extended 2 Dj - Psij partial derivative.
##########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dDjdPsij(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Psij double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci    dti  /               1 - (w.ti)^2                             (ts + ti)^2 - (w.ts.ti)^2   \ 
        ---------  =  -   >  ----- . ---  | S2f . S2s . ----------------  +  S2f(1 - S2s) . ts^2 ----------------------------- |
        dDj.dPsij     5  /__ dPsij   dDj  \             (1 + (w.ti)^2)^2                         ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                         i=m
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dDjdPsij(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Psij double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \    dci    dti  /               1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                             (ts + ti)^2 - (w.ts.ti)^2   \ 
        ---------  =  -   >  ----- . ---  | S2f . S2s . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  S2f(1 - S2s) . ts^2 ----------------------------- |
        dDj.dPsij     5  /__ dPsij   dDj  \             (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                         ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                         i=m
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)



# Extended 2 Dj - S2f partial derivative.
#########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dDjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is:

                        _n_
         d2J(w)      2  \        dti  /         1 - (w.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  ci . ---  | S2s . ----------------  +  (1 - S2s) . ts^2 ----------------------------- |
        dDj.dS2f     5  /__      dDj  \       (1 + (w.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=m
    """

    return 0.4 * sum(data.ci * data.dti[k] * (params[data.s2s_index] * data.fact_ti_djw_dti + data.one_s2s * data.fact_ts_djw_dti), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dDjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                        _n_
         d2J(w)      2  \        dti  /         1 - (w.ti)^2              (tf + ti)^2 - (w.tf.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  ci . ---  | S2s . ----------------  -  tf^2 -----------------------------  +  (1 - S2s) . ts^2 ----------------------------- |
        dDj.dS2f     5  /__      dDj  \       (1 + (w.ti)^2)^2          ((tf + ti)^2 + (w.tf.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=m
    """

    return 0.4 * sum(data.ci * data.dti[k] * (params[data.s2s_index] * data.fact_ti_djw_dti - data.fact_tf_djw_dti + data.one_s2s * data.fact_ts_djw_dti), axis=2)



# Extended 2 Dj - S2s partial derivative.
#########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dDjdS2s(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2s double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is:

                           _n_
         d2J(w)      2     \        dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - S2f  >  ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dDj.dS2s     5     /__      dDj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                           i=m
    """

    return 0.4 * params[data.s2f_index] * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_ts_djw_dti), axis=2)



# Extended 2 Dj - tf partial derivative.
########################################

# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dDjdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                                     _n_
         d2J(w)     4                \        dti                   (tf + ti)^2 - 3(w.tf.ti)^2
        -------  =  - (1 - S2f) . tf  >  ci . --- . ti . (tf + ti) -----------------------------
        dDj.dtf     5                /__      dDj                  ((tf + ti)^2 + (w.tf.ti)^2)^3
                                     i=m
    """

    return 0.8 * data.one_s2f * params[data.tf_index] * sum(data.ci * data.dti[k] * data.ti * data.tf_ti * (data.tf_ti_sqrd - 3.0 * data.w_tf_ti_sqrd) * data.inv_tf_denom**3, axis=2)



# Extended 2 Dj - ts partial derivative.
########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dDjdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is:

                                        _n_
         d2J(w)     4                   \        dti                   (ts + ti)^2 - 3(w.ts.ti)^2
        -------  =  - S2f(1 - S2s) . ts  >  ci . --- . ti . (ts + ti) -----------------------------
        dDj.dts     5                   /__      dDj                  ((ts + ti)^2 + (w.ts.ti)^2)^3
                                        i=m
    """

    return 0.8 * data.s2f_s2 * params[data.ts_index] * sum(data.ci * data.dti[k] * data.ti * data.ts_ti * (data.ts_ti_sqrd - 3.0 * data.w_ts_ti_sqrd) * data.inv_ts_denom**3, axis=2)



# Extended 2 Psij - Psik partial derivative.
############################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dPsijdPsik(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - Psik double partial derivative of the
    extended model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                           _n_
           d2J(w)       2  \       d2ci         /  S2f . S2s        S2f(1 - S2s)(ts + ti)ts  \ 
        -----------  =  -   >  ----------- . ti | ------------  +  ------------------------- |
        dPsij.dPsik     5  /__ dPsij.dPsik      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                           i=m
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dPsijdPsik(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - Psik double partial derivative of the
    extended model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                           _n_
           d2J(w)       2  \       d2ci         /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        -----------  =  -   >  ----------- . ti | ------------  +  -------------------------  +  ------------------------- |
        dPsij.dPsik     5  /__ dPsij.dPsik      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                           i=m
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2f_index] * params[data.s2s_index] * data.fact_ti + data.one_s2f * data.tf_ti_tf * data.inv_tf_denom + data.s2f_s2 * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 Psij - S2f partial derivative.
###########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dPsijdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - S2f double partial derivative of the
    extended model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                          _n_
          d2J(w)       2  \    dci       /      S2s           (1 - S2s)(ts + ti)ts    \ 
        ----------  =  -   >  ----- . ti | ------------  +  ------------------------- |
        dPsij.dS2f     5  /__ dPsij      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                          i=m
    """

    return 0.4 * sum(data.dci[k] * data.ti * (params[data.s2s_index] * data.fact_ti + data.one_s2s * data.ts_ti_ts * data.inv_ts_denom), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dPsijdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - S2f double partial derivative of the
    extended model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                          _n_
          d2J(w)       2  \    dci       /      S2s               (tf + ti)tf               (1 - S2s)(ts + ti)ts    \ 
        ----------  =  -   >  ----- . ti | ------------  -  -------------------------  +  ------------------------- |
        dPsij.dS2f     5  /__ dPsij      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                          i=m
    """

    return 0.4 * sum(data.dci[k] * data.ti * (params[data.s2s_index] * data.fact_ti - data.tf_ti_tf * data.inv_tf_denom + data.one_s2s * data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 Psij - S2s partial derivative.
###########################################

# {S2f, S2s, ts} and {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dPsijdS2s(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - S2 double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} and {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is:

                             _n_
          d2J(w)       2     \    dci       /      1                 (ts + ti)ts         \ 
        ----------  =  - S2f  >  ----- . ti | ------------  -  ------------------------- |
        dPsij.dS2s     5     /__ dPsij      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                             i=m
    """

    return 0.4 * params[data.s2f_index] * sum(data.dci[k] * data.ti * (data.fact_ti - data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 Psij - tf partial derivative.
##########################################

# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dPsijdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is:

                                  _n_
          d2J(w)      2           \    dci           (tf + ti)^2 - (w.tf.ti)^2
        ---------  =  - (1 - S2f)  >  ----- . ti^2 -----------------------------
        dPsij.dtf     5           /__ dPsij        ((tf + ti)^2 + (w.tf.ti)^2)^2
                                  i=m
    """

    return 0.4 * data.one_s2f * sum(data.dci[k] * data.fact_djw_dtf, axis=2)



# Extended 2 Psij - ts partial derivative.
##########################################

# {S2f, S2s, ts} and {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dPsijdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Psij - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is:

                                     _n_
          d2J(w)      2              \    dci           (ts + ti)^2 - (w.ts.ti)^2
        ---------  =  - S2f(1 - S2s)  >  ----- . ti^2 -----------------------------
        dPsij.dts     5              /__ dPsij        ((ts + ti)^2 + (w.ts.ti)^2)^2
                                     i=m
    """

    return 0.4 * data.s2f_s2 * sum(data.dci[k] * data.fact_djw_dts, axis=2)



# Extended 2 S2f - S2s partial derivative.
##########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_S2s_ts_d2jw_dS2fdS2s(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2f - S2s double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is:

                         _n_
          d2J(w)      2  \           /      1                 (ts + ti).ts        \ 
        ---------  =  -   >  ci . ti | ------------  -  ------------------------- |
        dS2f.dS2s     5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                         i=m
    """

    return 0.4 * sum(data.ci * data.ti * (data.fact_ti - data.ts_ti_ts * data.inv_ts_denom), axis=2)



# Extended 2 S2f - tf partial derivative.
#########################################

# {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_tf_S2s_ts_d2jw_dS2fdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2f - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} with or without diffusion tensor
    parameters.

    The model-free Hessian is:

                          _n_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=m
    """

    return -0.4 * sum(data.ci * data.fact_djw_dtf, axis=2)



# Extended 2 S2f - ts partial derivative.
#########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_S2s_ts_d2jw_dS2fdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2f - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is:

                                 _n_
         d2J(w)      2           \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  - (1 - S2s)  >  ci . ti^2 -----------------------------
        dS2f.dts     5           /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=m
    """

    return 0.4 * data.one_s2s * sum(data.ci * data.fact_djw_dts, axis=2)



# Extended 2 S2s - ts partial derivative.
#########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_S2s_ts_d2jw_dS2sdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2s - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is:

                             _n_
         d2J(w)        2     \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  - - S2f  >  ci . ti^2 -----------------------------
        dS2s.dts       5     /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                             i=m
    """

    return -0.4 * params[data.s2f_index] * sum(data.ci * data.fact_djw_dts, axis=2)



# Extended 2 tf - tf partial derivative.
########################################

# {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_tf_S2s_ts_d2jw_dtf2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the tf - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} with or without diffusion tensor
    parameters.

    The model-free Hessian is:

                                 _n_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=m
    """

    num = data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.tf_index] * data.tf_ti - data.w_ti_sqrd**2 * params[data.tf_index]**3

    return -0.8 * data.one_s2f * sum(data.ci * data.ti**2 * num * data.inv_tf_denom**3, axis=2)



# Extended 2 ts - ts partial derivative.
########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_S2s_ts_d2jw_dts2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the ts - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is:

                                    _n_
        d2J(w)       4              \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - S2f(1 - S2s)  >  ci . ti^2 -----------------------------------------------------
        dts**2       5              /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                    i=m
    """

    num = data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.ts_index] * data.ts_ti - data.w_ti_sqrd**2 * params[data.ts_index]**3

    return -0.8 * data.s2f_s2 * sum(data.ci * data.ti**2 * num * data.inv_ts_denom**3, axis=2)
