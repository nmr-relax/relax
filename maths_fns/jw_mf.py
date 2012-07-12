###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Python module imports.
from numpy import sum


############################
# Spectral density values. #
############################

"""
    The spectral density equation
    =============================

    Data structure:  data.jw
    Dimension:  2D, (number of NMR frequencies, 5 spectral density frequencies)
    Type:  numpy matrix, float64
    Dependencies:  None
    Required by:  data.ri, data.dri, data.d2ri


    Formulae
    ========

    Original::

                      _k_
                 2    \                1
        J(w)  =  - S2  >  ci . ti ------------,
                 5    /__         1 + (w.ti)^2
                      i=-k


                    _k_
                 2  \           /      S2             (1 - S2)(te + ti)te    \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |,
                 5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                    i=-k


    Extended::

                    _k_
                 2  \           /      S2            (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |,
                 5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=-k


                    _k_
                 2  \           /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |,
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=-k


    Extended 2::

                       _k_
                 2     \           /      S2s           (1 - S2s)(ts + ti)ts    \ 
        J(w)  =  - S2f  >  ci . ti | ------------  +  ------------------------- |,
                 5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k


                    _k_
                 2  \           /   S2f . S2s        (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |.
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=-k
"""



# Original no params with or without diffusion parameters.
##########################################################

def calc_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with no parameters {}
    with or without diffusion tensor parameters.

    The formula is::

                    _k_
                 2  \                1
        J(w)  =  -   >  ci . ti ------------.
                 5  /__         1 + (w.ti)^2
                    i=-k
    """

    return 0.4 * sum(data.ci * data.ti * data.fact_ti, axis=2)



# Original {S2} with or without diffusion parameters.
#####################################################

def calc_S2_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with the single
    parameter {S2} with or without diffusion tensor parameters.

    The formula is::

                      _k_
                 2    \                1
        J(w)  =  - S2  >  ci . ti ------------.
                 5    /__         1 + (w.ti)^2
                      i=-k
    """

    return 0.4 * params[data.s2_i] * sum(data.ci * data.ti * data.fact_ti, axis=2)



# Original {S2, te} with or without diffusion parameters.
#########################################################

def calc_S2_te_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with the parameters
    {S2, te} with or without diffusion tensor parameters.

    The model-free formula is::

                    _k_
                 2  \           /      S2             (1 - S2)(te + ti)te    \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |.
                 5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                    i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2 * data.fact_te), axis=2)



# Extended {S2f, S2, ts} with or without diffusion parameters.
##############################################################

def calc_S2f_S2_ts_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, S2, ts} with or without diffusion tensor parameters.

    The model-free formula is::

                    _k_
                 2  \           /      S2            (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |.
                 5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2_i] * data.fact_ti + data.s2f_s2 * data.fact_ts), axis=2)



# Extended {S2f, tf, S2, ts} with or without diffusion parameters.
##################################################################

def calc_S2f_tf_S2_ts_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, tf, S2, ts} with or without diffusion tensor parameters.

    The model-free formula is::

                    _k_
                 2  \           /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |.
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended 2 {S2f, S2s, ts} with or without diffusion parameters.
#################################################################

def calc_S2f_S2s_ts_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, S2s, ts} with or without diffusion tensor parameters.

    The model-free formula is::

                       _k_
                 2     \           /      S2s           (1 - S2s)(ts + ti)ts    \ 
        J(w)  =  - S2f  >  ci . ti | ------------  +  ------------------------- |.
                 5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k
    """

    return 0.4 * params[data.s2f_i] * sum(data.ci * data.ti * (params[data.s2s_i] * data.fact_ti + data.one_s2s * data.fact_ts), axis=2)



# Extended 2 {S2f, tf, S2s, ts} with or without diffusion parameters.
#####################################################################

def calc_S2f_tf_S2s_ts_jw(data, params):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, tf, S2s, ts} with or without diffusion tensor parameters.

    The model-free formula is::

                    _k_
                 2  \           /   S2f . S2s        (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |.
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)




###############################
# Spectral density gradients. #
###############################

"""
    The spectral density gradients
    ==============================

    Data structure:  data.djw
    Dimension:  3D, (number of NMR frequencies, 5 spectral density frequencies,
        model-free parameters)
    Type:  numpy 3D matrix, float64
    Dependencies:  None
    Required by:  data.dri, data.d2ri


    Formulae
    ========

    Original::

                     _k_
        dJ(w)     2  \   /      dti  /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 ----------------  +  (1 - S2)te^2 ----------------------------- |
         dGj      5  /__ \      dGj  \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 /
                     i=-k

                              dci      /      S2             (1 - S2)(te + ti)te    \ \ 
                           +  --- . ti | ------------  +  ------------------------- | |,
                              dGj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /


                     _k_
        dJ(w)     2  \   dci      /      S2             (1 - S2)(te + ti)te    \ 
        -----  =  -   >  --- . ti | ------------  +  ------------------------- |,
         dOj      5  /__ dOj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=-k


                     _k_
        dJ(w)     2  \           /      1                 (te + ti)te         \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |,
         dS2      5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=-k


                             _k_
        dJ(w)     2          \               (te + ti)^2 - (w.te.ti)^2
        -----  =  - (1 - S2)  >  ci . ti^2 -----------------------------,
         dte      5          /__           ((te + ti)^2 + (w.te.ti)^2)^2
                             i=-k


        dJ(w)
        -----  =  0,
        dRex


        dJ(w)
        -----  =  0,
        dcsa


        dJ(w)
        -----  =  0.
         dr


    Extended::

                     _k_
        dJ(w)     2  \   /      dti  /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------  +  (S2f - S2)ts^2 ----------------------------- |
         dGj      5  /__ \      dGj  \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=-k

                              dci      /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ \ 
                           +  --- . ti | ------------  +  -------------------------  +  ------------------------- | |,
                              dGj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                     _k_
        dJ(w)     2  \   dci      /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        -----  =  -   >  --- . ti | ------------  +  -------------------------  +  ------------------------- |,
         dOj      5  /__ dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k


                     _k_
        dJ(w)     2  \           /      1                 (ts + ti).ts        \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |,
         dS2      5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k


                       _k_
        dJ(w)       2  \           /       (tf + ti).tf                  (ts + ti).ts        \ 
        -----  =  - -   >  ci . ti | -------------------------  -  ------------------------- |,
        dS2f        5  /__         \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k


                              _k_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------,
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=-k


                               _k_
        dJ(w)     2            \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - (S2f - S2)  >  ci . ti^2 -----------------------------,
         dts      5            /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                               i=-k


        dJ(w)
        -----  =  0,
        dRex


        dJ(w)
        -----  =  0,
        dcsa


        dJ(w)
        -----  =  0.
         dr


    Extended 2::

                     _k_
        dJ(w)     2  \   /      dti  /           1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2f.S2s ----------------  +  (1 - S2f)tf^2 -----------------------------  +  S2f(1 - S2s)ts^2 ----------------------------- |
         dGj      5  /__ \      dGj  \         (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=-k

                              dci      /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ \ 
                           +  --- . ti | ------------  +  -------------------------  +  ------------------------- | |,
                              dGj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                     _k_
        dJ(w)     2  \   dci      /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        -----  =  -   >  --- . ti | ------------  +  -------------------------  +  ------------------------- |,
         dOj      5  /__ dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k


                     _k_
        dJ(w)     2  \           /     S2s                (tf + ti).tf              (1 - S2s)(ts + ti).ts   \ 
        -----  =  -   >  ci . ti | ------------  -  -------------------------  +  ------------------------- |,
        dS2f      5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k


                        _k_
        dJ(w)     2     \           /      1                 (ts + ti).ts        \ 
        -----  =  - S2f  >  ci . ti | ------------  -  ------------------------- |,
        dS2s      5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=-k


                              _k_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------,
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=-k


                                 _k_
        dJ(w)     2              \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - S2f(1 - S2s)  >  ci . ti^2 -----------------------------,
         dts      5              /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=-k


        dJ(w)
        -----  =  0,
        dRex


        dJ(w)
        -----  =  0,
        dcsa


        dJ(w)
        -----  =  0.
         dr
"""



# Original Gj partial derivative.
#################################

# {} with diffusion parameters.

def calc_diff_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the original model-free
    formula with no parameters {} together with diffusion tensor parameters.

    The model-free gradient is::

                     _k_
        dJ(w)     2  \        dti    1 - (w.ti)^2
        -----  =  -   >  ci . ---  ----------------.
         dGj      5  /__      dGj  (1 + (w.ti)^2)^2
                     i=-k
    """

    return 0.4 * sum(data.ci * data.dti[j] * data.fact_ti_djw_dti, axis=2)


def calc_ellipsoid_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the original model-free
    formula with no parameters {} together with diffusion tensor parameters.

    The model-free gradient is::

                     _k_
        dJ(w)     2  \   /      dti    1 - (w.ti)^2       dci           1       \ 
        -----  =  -   >  | ci . ---  ----------------  +  --- . ti ------------ |.
         dGj      5  /__ \      dGj  (1 + (w.ti)^2)^2     dGj      1 + (w.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.dti[j] * data.fact_ti_djw_dti  +  data.dci[j] * data.ti * data.fact_ti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the original model-free
    formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free gradient is::

                       _k_
        dJ(w)     2    \        dti    1 - (w.ti)^2
        -----  =  - S2  >  ci . ---  ----------------.
         dGj      5    /__      dGj  (1 + (w.ti)^2)^2
                       i=-k
    """

    return 0.4 * params[data.s2_i] * sum(data.ci * data.dti[j] * data.fact_ti_djw_dti, axis=2)


def calc_ellipsoid_S2_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the original model-free
    formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free gradient is::

                       _k_
        dJ(w)     2    \   /      dti    1 - (w.ti)^2       dci           1       \ 
        -----  =  - S2  >  | ci . ---  ----------------  +  --- . ti ------------ |.
         dGj      5    /__ \      dGj  (1 + (w.ti)^2)^2     dGj      1 + (w.ti)^2 /
                       i=-k
    """

    return 0.4 * params[data.s2_i] * sum(data.ci * data.dti[j] * data.fact_ti_djw_dti  +  data.dci[j] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the original model-free
    formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free gradient is::

                     _k_
        dJ(w)     2  \        dti  /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 ----------------  +  (1 - S2)te^2 ----------------------------- |.
         dGj      5  /__      dGj  \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti), axis=2)


def calc_ellipsoid_S2_te_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the original model-free
    formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free gradient is::

                     _k_
        dJ(w)     2  \   /      dti  /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 ----------------  +  (1 - S2)te^2 ----------------------------- |
         dGj      5  /__ \      dGj  \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 /
                     i=-k

                              dci      /      S2             (1 - S2)(te + ti)te    \ \ 
                           +  --- . ti | ------------  +  ------------------------- | |.
                              dGj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2 * data.fact_te), axis=2)



# Original Oj partial derivative.
#################################

# {} with diffusion parameters.

def calc_diff_djw_dOj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the O partial derivative of the original model-free
    formula with no parameters {} together with diffusion tensor parameters.

    The model-free gradient is::

                    _k_
        dJ(w)     2 \   dci           1
        -----  =  -  >  --- . ti ------------.
         dOj      5 /__ dOj      1 + (w.ti)^2
                    i=-k
    """

    return 0.4 * sum(data.dci[j] * data.ti * data.fact_ti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_djw_dOj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the O partial derivative of the original model-free
    formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free gradient is::

                       _k_
        dJ(w)     2    \   dci           1
        -----  =  - S2  >  --- . ti ------------.
         dOj      5    /__ dOj      1 + (w.ti)^2
                       i=-k
    """

    return 0.4 * params[data.s2_i] * sum(data.dci[j] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_djw_dOj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the O partial derivative of the original model-free
    formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free gradient is::

                     _k_
        dJ(w)     2  \   dci      /      S2             (1 - S2)(te + ti)te    \ 
        -----  =  -   >  --- . ti | ------------  +  ------------------------- |.
         dOj      5  /__ dOj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.dci[j] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2 * data.fact_te), axis=2)



# Original S2 partial derivative.
#################################

# {S2} with or without diffusion parameters.

def calc_S2_djw_dS2(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the original model-free
    formula with the single parameter {S2} with or without diffusion tensor parameters.

    The model-free gradient is::

                     _k_
        dJ(w)     2  \                1
        -----  =  -   >  ci . ti ------------.
         dS2      5  /__         1 + (w.ti)^2
                     i=-k
    """

    return 0.4 * sum(data.ci * data.ti * data.fact_ti, axis=2)


# {S2, te} with or without diffusion parameters.

def calc_S2_te_djw_dS2(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the original model-free
    formula with the parameters {S2, te} with or without diffusion tensor parameters.

    The model-free gradient is::

                     _k_
        dJ(w)     2  \           /      1                 (te + ti)te         \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |.
         dS2      5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (data.fact_ti - data.fact_te), axis=2)



# Original te partial derivative.
#################################

# {S2, te} with or without diffusion parameters.

def calc_S2_te_djw_dte(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the te partial derivative of the original model-free
    formula with the parameters {S2, te} with or without diffusion tensor parameters.

    The model-free gradient is::

                             _k_
        dJ(w)     2          \               (te + ti)^2 - (w.te.ti)^2
        -----  =  - (1 - S2)  >  ci . ti^2 -----------------------------.
         dte      5          /__           ((te + ti)^2 + (w.te.ti)^2)^2
                             i=-k
    """

    return 0.4 * data.one_s2 * sum(data.ci * data.fact_djw_dte, axis=2)



# Extended Gj partial derivative.
#################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \        dti  /      1 - (w.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 ----------------  +  (S2f - S2)ts^2 ----------------------------- |.
         dGj      5  /__      dGj  \    (1 + (w.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_S2_ts_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \   /      dti  /      1 - (w.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 ----------------  +  (S2f - S2)ts^2 ----------------------------- |
         dGj      5  /__ \      dGj  \    (1 + (w.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=-k

                              dci      /      S2            (S2f - S2)(ts + ti)ts   \ \ 
                           +  --- . ti | ------------  +  ------------------------- | |.
                              dGj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2_i] * data.fact_ti + data.s2f_s2 * data.fact_ts), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \        dti  /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------  +  (S2f - S2)ts^2 ----------------------------- |.
         dGj      5  /__      dGj  \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_tf_S2_ts_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \   /      dti  /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------  +  (S2f - S2)ts^2 ----------------------------- |
         dGj      5  /__ \      dGj  \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=-k

                              dci      /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ \ 
                           +  --- . ti | ------------  +  -------------------------  +  ------------------------- | |.
                              dGj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended Oj partial derivative.
#################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_djw_dOj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the O partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \   dci      /      S2            (S2f - S2)(ts + ti)ts   \ 
        -----  =  -   >  --- . ti | ------------  +  ------------------------- |.
         dOj      5  /__ dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.dci[j] * data.ti * (params[data.s2_i] * data.fact_ti + data.s2f_s2 * data.fact_ts), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_djw_dOj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the O partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \   dci      /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        -----  =  -   >  --- . ti | ------------  +  -------------------------  +  ------------------------- |.
         dOj      5  /__ dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.dci[j] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended S2 partial derivative.
#################################

# {S2f, S2, ts} and {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_djw_dS2(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} with or without diffusion tensor
    parameters.

    The formula is::

                     _k_
        dJ(w)     2  \           /      1                 (ts + ti).ts        \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |.
         dS2      5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (data.fact_ti - data.fact_ts), axis=2)



# Extended S2f partial derivative.
##################################

# {S2f, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_djw_dS2f(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} with or without diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \                 (ts + ti).ts
        -----  =  -   >  ci . ti -------------------------.
        dS2f      5  /__         (ts + ti)^2 + (w.ts.ti)^2
                     i=-k
    """

    return 0.4 * sum(data.ci * data.ti * data.fact_ts, axis=2)


# {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_tf_S2_ts_djw_dS2f(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} with or without diffusion tensor parameters.

    The formula is::

                       _k_
        dJ(w)       2  \           /       (tf + ti).tf                  (ts + ti).ts        \ 
        -----  =  - -   >  ci . ti | -------------------------  -  ------------------------- |.
        dS2f        5  /__         \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k
    """

    return -0.4 * sum(data.ci * data.ti * (data.fact_tf - data.fact_ts), axis=2)



# Extended tf partial derivative.
#################################

# {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_tf_S2_ts_djw_dtf(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the tf partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} with or without diffusion tensor parameters.

    The formula is::

                              _k_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------.
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=-k
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

    The formula is::

                               _k_
        dJ(w)     2            \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - (S2f - S2)  >  ci . ti^2 -----------------------------.
         dts      5            /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                               i=-k
    """

    return 0.4 * data.s2f_s2 * sum(data.ci * data.fact_djw_dts, axis=2)



# Extended 2 Gj partial derivative.
###################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The formula is::

                        _k_
        dJ(w)     2     \        dti  /       1 - (w.ti)^2                       (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  - S2f  >  ci . ---  | S2s ----------------  +  (1 - S2s)ts^2 ----------------------------- |.
         dGj      5     /__      dGj  \     (1 + (w.ti)^2)^2                   ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=-k
    """

    return 0.4 * params[data.s2f_i] * sum(data.ci * data.dti[j] * (params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2s * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_S2s_ts_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The formula is::

                        _k_
        dJ(w)     2     \   /      dti  /       1 - (w.ti)^2                       (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  - S2f  >  | ci . ---  | S2s ----------------  +  (1 - S2s)ts^2 ----------------------------- |
         dGj      5     /__ \      dGj  \     (1 + (w.ti)^2)^2                   ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=-k

                                 dci      /     S2s             (1 - S2s)(ts + ti)ts   \ \ 
                              +  --- . ti | ------------  +  ------------------------- | |.
                                 dGj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * params[data.s2f_i] * sum(data.ci * data.dti[j] * (params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2s * data.fact_ts_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2s_i] * data.fact_ti + data.one_s2s * data.fact_ts), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \        dti  /           1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2f.S2s ----------------  +  (1 - S2f)tf^2 -----------------------------  +  S2f(1 - S2s)ts^2 ----------------------------- |
         dGj      5  /__      dGj  \         (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_tf_S2s_ts_djw_dGj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the Gj partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \   /      dti  /           1 - (w.ti)^2                        (tf + ti)^2 - (w.tf.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  | ci . ---  | S2f.S2s ----------------  +  (1 - S2f).tf^2 -----------------------------  +  S2f(1 - S2s).ts^2 ----------------------------- |
         dGj      5  /__ \      dGj  \         (1 + (w.ti)^2)^2                    ((tf + ti)^2 + (w.tf.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=-k

                              dci      /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ \ 
                           +  --- . ti | ------------  +  -------------------------  +  ------------------------- | |.
                              dGj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[j] * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.dci[j] * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended 2 Oj partial derivative.
###################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_djw_dOj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the O partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The formula is::

                        _k_
        dJ(w)     2     \   dci      /     S2s             (1 - S2s)(ts + ti)ts   \ 
        -----  =  - S2f  >  --- . ti | ------------  +  ------------------------- |.
         dOj      5     /__ dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=-k
    """

    return 0.4 * params[data.s2f_i] * sum(data.dci[j] * data.ti * (params[data.s2s_i] * data.fact_ti + data.one_s2s * data.fact_ts), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_djw_dOj(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the O partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \   dci      /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        -----  =  -   >  --- . ti | ------------  +  -------------------------  +  ------------------------- |.
         dOj      5  /__ dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.dci[j] * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended 2 S2f partial derivative.
###################################

# {S2f, S2s, ts} with or without diffusion parameters..

def calc_S2f_S2s_ts_djw_dS2f(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} with or without diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \           /     S2s            (1 - S2s)(ts + ti).ts   \ 
        -----  =  -   >  ci . ti | ------------  +  ------------------------- |.
        dS2f      5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2s_i] * data.fact_ti + data.one_s2s * data.fact_ts), axis=2)


# {S2f, tf, S2s, ts} with or without diffusion parameters..

def calc_S2f_tf_S2s_ts_djw_dS2f(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} with or without diffusion tensor parameters.

    The formula is::

                     _k_
        dJ(w)     2  \           /     S2s                (tf + ti).tf              (1 - S2s)(ts + ti).ts   \ 
        -----  =  -   >  ci . ti | ------------  -  -------------------------  +  ------------------------- |.
        dS2f      5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (params[data.s2s_i] * data.fact_ti - data.fact_tf + data.one_s2s * data.fact_ts), axis=2)



# Extended 2 S2s partial derivative.
####################################

# {S2f, S2s, ts} and {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_tf_S2s_ts_djw_dS2s(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2s partial derivative of the extended model-free
    formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without diffusion
    tensor parameters.

    The formula is::

                        _k_
        dJ(w)     2     \           /      1                 (ts + ti).ts        \ 
        -----  =  - S2f  >  ci . ti | ------------  -  ------------------------- |.
        dS2s      5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=-k
    """

    return 0.4 * params[data.s2f_i] * sum(data.ci * data.ti * (data.fact_ti - data.fact_ts), axis=2)



# Extended 2 tf partial derivative.
###################################

# {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_tf_S2s_ts_djw_dtf(data, params, j):
    """Spectral density gradient.

    Calculate the spectral desity values for the tf partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2s, ts} with or without diffusion tensor parameters.

    The formula is::

                              _k_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------.
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=-k
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

    The formula is::

                                 _k_
        dJ(w)     2              \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - S2f(1 - S2s)  >  ci . ti^2 -----------------------------.
         dts      5              /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=-k
    """

    return 0.4 * data.s2f_s2 * sum(data.ci * data.fact_djw_dts, axis=2)




##############################
# Spectral density Hessians. #
##############################

"""
    The spectral density Hessians
    =============================

    Data structure:  data.d2jw
    Dimension:  4D, (number of NMR frequencies, 5 spectral density frequencies, model-free
        parameters, model-free parameters)
    Type:  numpy 4D matrix, float64
    Dependencies:  None
    Required by:  data.d2ri


    Formulae
    ========

    Original:  Model-free parameter - Model-free parameter::

                       _k_
         d2J(w)     2  \   /      dti   dti  /             3 - (w.ti)^2                    (te + ti)^3 + 3.w^2.te^3.ti(te + ti) - (w.te)^4.ti^3 \ 
        -------  =  -   >  | -2ci --- . ---  | S2.w^2.ti ----------------  +  (1 - S2)te^2 ---------------------------------------------------- |
        dGj.dGk     5  /__ \      dGj   dGk  \           (1 + (w.ti)^2)^3                            ((te + ti)^2 + (w.te.ti)^2)^3              /
                       i=-k

                                / dti   dci     dti   dci         d2ti   \ /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ 
                             +  | --- . ---  +  --- . ---  +  ci ------- | | S2 ----------------  +  (1 - S2)te^2 ----------------------------- |
                                \ dGj   dGk     dGk   dGj        dGj.dGk / \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 /


                                 d2ci      /      S2             (1 - S2)(te + ti)te    \ \ 
                             +  ------- ti | ------------  +  ------------------------- | |,
                                dGj.dGk    \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /


                       _k_
         d2J(w)     2  \   / dci   dti  /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  | --- . ---  | S2 ----------------  +  (1 - S2)te^2 ----------------------------- |
        dGj.dOj     5  /__ \ dOj   dGj  \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=-k

                                   d2ci      /      S2             (1 - S2)(te + ti)te    \ \ 
                               +  ------- ti | ------------  +  ------------------------- | |,
                                  dGj.dOj    \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /


                       _k_
         d2J(w)     2  \   /      dti  /   1 - (w.ti)^2              (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  | ci . ---  | ----------------  -  te^2 ----------------------------- |
        dGj.dS2     5  /__ \      dGj  \ (1 + (w.ti)^2)^2          ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=-k

                                dci      /      1                 (te + ti)te         \ \ 
                             +  --- . ti | ------------  -  ------------------------- | |,
                                dGj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /


                              _k_
         d2J(w)     2         \   /       dti                        (te + ti)^2 - 3(w.te.ti)^2       dci          (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  - (1 - S2) >  | 2ci . --- . te . ti . (te + ti) -----------------------------  +  --- . ti^2 ----------------------------- |,
        dGj.dte     5         /__ \       dGj                       ((te + ti)^2 + (w.te.ti)^2)^3     dGj        ((te + ti)^2 + (w.te.ti)^2)^2 /
                              i=-k


                       _k_
         d2J(w)     2  \    d2ci        /      S2             (1 - S2)(te + ti)te    \ 
        -------  =  -   >  ------- . ti | ------------  +  ------------------------- |,
        dOj.dOk     5  /__ dOj.dOk      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                       i=-k


                       _k_
         d2J(w)     2  \   dci      /      1                 (te + ti)te         \ 
        -------  =  -   >  --- . ti | ------------  -  ------------------------- |,
        dOj.dS2     5  /__ dOj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                       i=-k


                               _k_
         d2J(w)     2          \   dci          (te + ti)^2 - (w.te.ti)^2
        -------  =  - (1 - S2)  >  --- . ti^2 -----------------------------,
        dOj.dte     5          /__ dOj        ((te + ti)^2 + (w.te.ti)^2)^2
                               i=-k


        d2J(w)
        ------  =  0,
        dS2**2


                        _k_
         d2J(w)       2 \               (te + ti)^2 - (w.te.ti)^2
        -------  =  - -  >  ci . ti^2 -----------------------------,
        dS2.dte       5 /__           ((te + ti)^2 + (w.te.ti)^2)^2
                        i=-k


                                _k_
        d2J(w)       4          \             (te + ti)^3 + 3.w^2.ti^3.te.(te + ti) - (w.ti)^4.te^3
        ------  =  - - (1 - S2)  >  ci . ti^2 -----------------------------------------------------.
        dte**2       5          /__                        ((te + ti)^2 + (w.te.ti)^2)^3
                                i=-k


    Original:  Other parameters::

         d2J(w)               d2J(w)              d2J(w)
        --------  =  0,      --------  =  0,      ------  =  0,
        dS2.dRex             dS2.dcsa             dS2.dr


         d2J(w)              d2J(w)               d2J(w)
        --------  =  0,     --------  =  0,       ------  =  0,
        dte.dRex            dte.dcsa              dte.dr


         d2J(w)              d2J(w)                d2J(w)
        -------  =  0,     ---------  =  0,       -------  =  0,
        dRex**2            dRex.dcsa              dRex.dr


         d2J(w)             d2J(w)
        -------  =  0,     -------  =  0,
        dcsa**2            dcsa.dr


        d2J(w)
        ------  =  0.
        dr**2


    Extended:  Model-free parameter - Model-free parameter::

                       _k_
         d2J(w)     2  \   /      dti   dti  /             3 - (w.ti)^2                     (tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3
        -------  =  -   >  | -2ci --- . ---  | S2.w^2.ti ----------------  +  (1 - S2f)tf^2 ----------------------------------------------------
        dGj.dGk     5  /__ \      dGj   dGk  \           (1 + (w.ti)^2)^3                             ((tf + ti)^2 + (w.tf.ti)^2)^3
                       i=-k

                                                                 (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
                                               +  (S2f - S2)ts^2 ---------------------------------------------------- |
                                                                           ((ts + ti)^2 + (w.ts.ti)^2)^3              /


                                / dti   dci     dti   dci         d2ti   \ /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2
                             +  | --- . ---  +  --- . ---  +  ci ------- | | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------
                                \ dGj   dGk     dGk   dGj        dGj.dGk / \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2


                                                                                                 (ts + ti)^2 - (w.ts.ti)^2   \ 
                                                                             +  (S2f - S2)ts^2 ----------------------------- |
                                                                                               ((ts + ti)^2 + (w.ts.ti)^2)^2 /


                                 d2ci        /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ \ 
                             +  ------- . ti | ------------  +  -------------------------  +  ------------------------- | |,
                                dGj.dGk      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                       _k_
         d2J(w)     2  \   / dci   dti  /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  | --- . ---  | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------  +  (S2f - S2)ts^2 ----------------------------- |
        dGj.dOj     5  /__ \ dOj   dGj  \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k

                                   d2ci        /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ \ 
                               +  ------- . ti | ------------  +  -------------------------  +  ------------------------- | |,
                                  dGj.dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                       _k_
         d2J(w)     2  \   /      dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  | ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dGj.dS2     5  /__ \      dGj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k

                                dci      /      1                 (ts + ti)ts         \ \ 
                             +  --- . ti | ------------  -  ------------------------- | |,
                                dGj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                          _k_
         d2J(w)        2  \   /      dti  /        (tf + ti)^2 - (w.tf.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - -   >  | ci . ---  | tf^2 -----------------------------  -  ts^2 ----------------------------- |
        dGj.dS2f       5  /__ \      dGj  \      ((tf + ti)^2 + (w.tf.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                          i=-k

                                   dci      /       (tf + ti)tf                   (ts + ti)ts         \ \ 
                                +  --- . ti | -------------------------  -  ------------------------- | |,
                                   dGj      \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                                _k_
         d2J(w)     2           \   /       dti                        (tf + ti)^2 - 3(w.tf.ti)^2       dci          (tf + ti)^2 - (w.tf.ti)^2   \ 
        -------  =  - (1 - S2f)  >  | 2ci . --- . tf . ti . (tf + ti) -----------------------------  +  --- . ti^2 ----------------------------- |,
        dGj.dtf     5           /__ \       dGj                       ((tf + ti)^2 + (w.tf.ti)^2)^3     dGj        ((tf + ti)^2 + (w.tf.ti)^2)^2 /
                                i=-k


                                 _k_
         d2J(w)     2            \   /       dti                        (ts + ti)^2 - 3(w.ts.ti)^2       dci          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  - (S2f - S2)  >  | 2ci . --- . ts . ti . (ts + ti) -----------------------------  +  --- . ti^2 ----------------------------- |,
        dGj.dts     5            /__ \       dGj                       ((ts + ti)^2 + (w.ts.ti)^2)^3     dGj        ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                                 i=-k


                       _k_
         d2J(w)     2  \    d2ci        /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        -------  =  -   >  ------- . ti | ------------  +  -------------------------  +  ------------------------- |,
        dOj.dOk     5  /__ dOj.dOk      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k


                       _k_
         d2J(w)     2  \   dci      /      1                 (ts + ti)ts         \ 
        -------  =  -   >  --- . ti | ------------  -  ------------------------- |,
        dOj.dS2     5  /__ dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k


                          _k_
         d2J(w)        2  \   dci      /       (tf + ti)tf                   (ts + ti)ts         \ 
        --------  =  - -   >  --- . ti | -------------------------  -  ------------------------- |,
        dOj.dS2f       5  /__ dOj      \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                          i=-k


                                _k_
         d2J(w)     2           \   dci          (tf + ti)^2 - (w.tf.ti)^2
        -------  =  - (1 - S2f)  >  --- . ti^2 -----------------------------,
        dOj.dtf     5           /__ dOj        ((tf + ti)^2 + (w.tf.ti)^2)^2
                                i=-k


                                 _k_
         d2J(w)     2            \   dci          (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - (S2f - S2)  >  --- . ti^2 -----------------------------,
        dOj.dts     5            /__ dOj        ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=-k


        d2J(w)              d2J(w)               d2J(w)
        ------  =  0,      --------  =  0,      -------  =  0,
        dS2**2             dS2.dS2f             dS2.dtf


                         _k_
         d2J(w)       2  \               (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - -   >  ci . ti^2 -----------------------------,
        dS2.dts       5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                         i=-k


         d2J(w)
        -------  =  0,
        dS2f**2


                          _k_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------,
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=-k


                        _k_
         d2J(w)      2  \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  -   >  ci . ti^2 -----------------------------,
        dS2f.dts     5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                        i=-k


                                 _k_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------,
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=-k


         d2J(w)
        -------  =  0,
        dtf.dts


                                  _k_
        d2J(w)       4            \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - (S2f - S2)  >  ci . ti^2 -----------------------------------------------------,
        dts**2       5            /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                  i=-k


    Extended:  Other parameters::

          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0,      ---------  =  0,      -------  =  0,
        dS2f.dRex             dS2f.dcsa             dS2f.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0,      --------  =  0,      ------  =  0,
        dS2.dRex             dS2.dcsa             dS2.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0,      --------  =  0,      ------  =  0,
        dtf.dRex             dtf.dcsa             dtf.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0,      --------  =  0,      ------  =  0,
        dts.dRex             dts.dcsa             dts.dr


         d2J(w)               d2J(w)               d2J(w)
        -------  =  0,      ---------  =  0,      -------  =  0,
        dRex**2             dRex.dcsa             dRex.dr


         d2J(w)              d2J(w)
        -------  =  0,      -------  =  0,
        dcsa**2             dcsa.dr


        d2J(w)
        ------  =  0.
        dr**2


    Extended 2:  Model-free parameter - Model-free parameter::

                       _k_
         d2J(w)     2  \   /      dti   dti  /                  3 - (w.ti)^2                     (tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3
        -------  =  -   >  | -2ci --- . ---  | S2f.S2s.w^2.ti ----------------  +  (1 - S2f)tf^2 ----------------------------------------------------
        dGj.dGk     5  /__ \      dGj   dGk  \                (1 + (w.ti)^2)^3                             ((tf + ti)^2 + (w.tf.ti)^2)^3
                       i=-k

                                                                   (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
                                               +  S2f(1 - S2s)ts^2 ---------------------------------------------------- |
                                                                             ((ts + ti)^2 + (w.ts.ti)^2)^3              /


                                / dti   dci     dti   dci         d2ti   \ /           1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2
                             +  | --- . ---  +  --- . ---  +  ci ------- | | S2f.S2s ----------------  +  (1 - S2f)tf^2 -----------------------------
                                \ dGj   dGk     dGk   dGj        dGj.dGk / \         (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2


                                                                                                   (ts + ti)^2 - (w.ts.ti)^2   \ 
                                                                             +  S2f(1 - S2s)ts^2 ----------------------------- |
                                                                                                 ((ts + ti)^2 + (w.ts.ti)^2)^2 /


                                 d2ci        /   S2f.S2s          (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ \ 
                             +  ------- . ti | ------------  +  -------------------------  +  ------------------------- | |,
                                dGj.dGk      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                       _k_
         d2J(w)     2  \   / dci   dti  /           1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  | --- . ---  | S2f.S2s ----------------  +  (1 - S2f)tf^2 -----------------------------  +  S2f(1 - S2s)ts^2 ----------------------------- |
        dGj.dOj     5  /__ \ dOj   dGj  \         (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k

                                   d2ci        /   S2f.S2s          (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ \ 
                               +  ------- . ti | ------------  +  -------------------------  +  ------------------------- | |,
                                  dGj.dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                        _k_
         d2J(w)      2  \   /      dti  /       1 - (w.ti)^2              (tf + ti)^2 - (w.tf.ti)^2                       (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  | ci . ---  | S2s ----------------  -  tf^2 -----------------------------  +  (1 - S2s)ts^2 ----------------------------- |
        dGj.dS2f     5  /__ \      dGj  \     (1 + (w.ti)^2)^2          ((tf + ti)^2 + (w.tf.ti)^2)^2                   ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=-k

                                 dci      /     S2s                (tf + ti)tf               (1 - S2s)(ts + ti)ts    \ \ 
                              +  --- . ti | ------------  -  -------------------------  +  ------------------------- | |,
                                 dGj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                           _k_
         d2J(w)      2     \   /      dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - S2f  >  | ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dGj.dS2s     5     /__ \      dGj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                           i=-k

                                    dci      /      1                 (ts + ti)ts         \ \ 
                                 +  --- . ti | ------------  -  ------------------------- | |,
                                    dGj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /


                                _k_
         d2J(w)     2           \   /       dti                        (tf + ti)^2 - 3(w.tf.ti)^2       dci          (tf + ti)^2 - (w.tf.ti)^2   \ 
        -------  =  - (1 - S2f)  >  | 2ci . --- . tf . ti . (tf + ti) -----------------------------  +  --- . ti^2 ----------------------------- |,
        dGj.dtf     5           /__ \       dGj                       ((tf + ti)^2 + (w.tf.ti)^2)^3     dGj        ((tf + ti)^2 + (w.tf.ti)^2)^2 /
                                i=-k


                                   _k_
         d2J(w)     2              \   /       dti                        (ts + ti)^2 - 3(w.ts.ti)^2       dci          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  - S2f(1 - S2s)  >  | 2ci . --- . ts . ti . (ts + ti) -----------------------------  +  --- . ti^2 ----------------------------- |,
        dGj.dts     5              /__ \       dGj                       ((ts + ti)^2 + (w.ts.ti)^2)^3     dGj        ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                                   i=-k


                       _k_
         d2J(w)     2  \    d2ci        /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        -------  =  -   >  ------- . ti | ------------  +  -------------------------  +  ------------------------- |,
        dOj.dOk     5  /__ dOj.dOk      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k


                        _k_
         d2J(w)      2  \   dci      /     S2s                (tf + ti)tf               (1 - S2s)(ts + ti)ts    \ 
        --------  =  -   >  --- . ti | ------------  -  -------------------------  +  ------------------------- |,
        dOj.dS2f     5  /__ dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=-k


                           _k_
         d2J(w)      2     \   dci      /      1                 (ts + ti)ts         \ 
        --------  =  - S2f  >  --- . ti | ------------  -  ------------------------- |,
        dOj.dS2s     5     /__ dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                           i=-k


                                _k_
         d2J(w)     2           \   dci          (tf + ti)^2 - (w.tf.ti)^2
        -------  =  - (1 - S2f)  >  --- . ti^2 -----------------------------,
        dOj.dtf     5           /__ dOj        ((tf + ti)^2 + (w.tf.ti)^2)^2
                                i=-k


                                   _k_
         d2J(w)     2              \   dci          (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - S2f(1 - S2s)  >  --- . ti^2 -----------------------------,
        dOj.dts     5              /__ dOj        ((ts + ti)^2 + (w.ts.ti)^2)^2
                                   i=-k


         d2J(w)
        -------  =  0,
        dS2f**2


                         _k_
          d2J(w)      2  \           /      1                 (ts + ti).ts        \ 
        ---------  =  -   >  ci . ti | ------------  -  ------------------------- |,
        dS2f.dS2s     5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                         i=-k


                          _k_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------,
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=-k


                                 _k_
         d2J(w)      2           \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  - (1 - S2s)  >  ci . ti^2 -----------------------------,
        dS2f.dts     5           /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=-k


         d2J(w)              d2J(w)
        -------  =  0,      --------  =  0,
        dS2s**2             dS2s.dtf


                             _k_
         d2J(w)        2     \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  - - S2f  >  ci . ti^2 -----------------------------,
        dS2s.dts       5     /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                             i=-k


                                 _k_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------,
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=-k


         d2J(w)
        -------  =  0,
        dtf.dts


                                    _k_
        d2J(w)       4              \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - S2f(1 - S2s)  >  ci . ti^2 -----------------------------------------------------.
        dts**2       5              /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                    i=-k



    Extended 2:  Other parameters::

          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0,      ---------  =  0,      -------  =  0,
        dS2f.dRex             dS2f.dcsa             dS2f.dr


          d2J(w)                d2J(w)               d2J(w)
        ---------  =  0,      ---------  =  0,      -------  =  0,
        dS2s.dRex             dS2s.dcsa             dS2s.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0,      --------  =  0,      ------  =  0,
        dtf.dRex             dtf.dcsa             dtf.dr


         d2J(w)               d2J(w)              d2J(w)
        --------  =  0,      --------  =  0,      ------  =  0,
        dts.dRex             dts.dcsa             dts.dr


         d2J(w)               d2J(w)               d2J(w)
        -------  =  0,      ---------  =  0,      -------  =  0,
        dRex**2             dRex.dcsa             dRex.dr


         d2J(w)              d2J(w)
        -------  =  0,      -------  =  0,
        dcsa**2             dcsa.dr


        d2J(w)
        ------  =  0.
        dr**2
"""


# Original Gj - Gk partial derivative.
######################################

# {} with diffusion parameters.

def calc_diff_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the original
    model-free formula with no parameters {} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \      /    dti   dti           3 - (w.ti)^2        d2ti     1 - (w.ti)^2   \ 
        -------  =  -   >  ci | -2 --- . ---  w^2.ti ----------------  +  ------- ---------------- |.
        dGj.dGk     5  /__    \    dGj   dGk         (1 + (w.ti)^2)^3     dGj.dGk (1 + (w.ti)^2)^2 /
                       i=-k
    """

    return 0.4 * sum(data.ci * (-2.0 * data.dti[j] * data.dti[k] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.d2ti[j, k] * data.fact_ti_djw_dti), axis=2)


def calc_ellipsoid_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the original
    model-free formula with no parameters {} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti   dti           3 - (w.ti)^2       / dti   dci     dti   dci         d2ti   \   1 - (w.ti)^2        d2ci           1       \ 
        -------  =  -   >  | -2ci --- . ---  w^2.ti ----------------  +  | --- . ---  +  --- . ---  +  ci ------- | ----------------  +  ------- ti ------------ |.
        dGj.dGk     5  /__ \      dGj   dGk         (1 + (w.ti)^2)^3     \ dGj   dGk     dGk   dGj        dGj.dGk / (1 + (w.ti)^2)^2     dGj.dGk    1 + (w.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(-2.0 * data.ci * data.dti[j] * data.dti[k] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  (data.dti[j] * data.dci[k] + data.dti[k] * data.dci[j] + data.ci * data.d2ti[j, k]) * data.fact_ti_djw_dti  +  data.d2ci[j, k] * data.ti * data.fact_ti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is::

                         _k_
         d2J(w)     2    \      /    dti   dti           3 - (w.ti)^2        d2ti     1 - (w.ti)^2   \ 
        -------  =  - S2  >  ci | -2 --- . ---  w^2.ti ----------------  +  ------- ---------------- |.
        dGj.dGk     5    /__    \    dGj   dGk         (1 + (w.ti)^2)^3     dGj.dGk (1 + (w.ti)^2)^2 /
                         i=-k
    """

    return 0.4 * params[data.s2_i] * sum(data.ci * (-2.0 * data.dti[j] * data.dti[k] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.d2ti[j, k] * data.fact_ti_djw_dti), axis=2)


def calc_ellipsoid_S2_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is::

                         _k_
         d2J(w)     2    \   /      dti   dti           3 - (w.ti)^2       / dti   dci     dti   dci         d2ti   \   1 - (w.ti)^2        d2ci           1       \ 
        -------  =  - S2  >  | -2ci --- . ---  w^2.ti ----------------  +  | --- . ---  +  --- . ---  +  ci ------- | ----------------  +  ------- ti ------------ |.
        dGj.dGk     5    /__ \      dGj   dGk         (1 + (w.ti)^2)^3     \ dGj   dGk     dGk   dGj        dGj.dGk / (1 + (w.ti)^2)^2     dGj.dGk    1 + (w.ti)^2 /
                         i=-k
    """

    return 0.4 * params[data.s2_i] * sum(-2.0 * data.ci * data.dti[j] * data.dti[k] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  (data.dti[j] * data.dci[k] + data.dti[k] * data.dci[j] + data.ci * data.d2ti[j, k]) * data.fact_ti_djw_dti  +  data.d2ci[j, k] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \      /    dti   dti  /             3 - (w.ti)^2                    (te + ti)^3 + 3.w^2.te^3.ti(te + ti) - (w.te)^4.ti^3 \ 
        -------  =  -   >  ci | -2 --- . ---  | S2.w^2.ti ----------------  +  (1 - S2)te^2 ---------------------------------------------------- |
        dGj.dGk     5  /__    \    dGj   dGk  \           (1 + (w.ti)^2)^3                            ((te + ti)^2 + (w.te.ti)^2)^3              /
                       i=-k

                                 d2ti   /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ \ 
                             +  ------- | S2 ----------------  +  (1 - S2)te^2 ----------------------------- | |.
                                dGj.dGk \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 / /
    """

    # First component.
    a = -2.0 * data.dti[j] * data.dti[k] * (params[data.s2_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.one_s2 * params[data.te_i]**2 * (data.te_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.te_i]**3 * data.ti * data.te_ti - (data.frq_list_ext * params[data.te_i])**4 * data.ti**3) * data.inv_te_denom**3)

    # Second component.
    b = data.d2ti[j, k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti)

    return 0.4 * sum(data.ci * (a + b), axis=2)


def calc_ellipsoid_S2_te_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti   dti  /             3 - (w.ti)^2                    (te + ti)^3 + 3.w^2.te^3.ti(te + ti) - (w.te)^4.ti^3 \ 
        -------  =  -   >  | -2ci --- . ---  | S2.w^2.ti ----------------  +  (1 - S2)te^2 ---------------------------------------------------- |
        dGj.dGk     5  /__ \      dGj   dGk  \           (1 + (w.ti)^2)^3                            ((te + ti)^2 + (w.te.ti)^2)^3              /
                       i=-k

                                / dti   dci     dti   dci         d2ti   \ /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ 
                             +  | --- . ---  +  --- . ---  +  ci ------- | | S2 ----------------  +  (1 - S2)te^2 ----------------------------- |
                                \ dGj   dGk     dGk   dGj        dGj.dGk / \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 /


                                 d2ci      /      S2             (1 - S2)(te + ti)te    \ \ 
                             +  ------- ti | ------------  +  ------------------------- | |.
                                dGj.dGk    \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /
    """

    # First component.
    a = -2.0 * data.ci * data.dti[j] * data.dti[k] * (params[data.s2_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.one_s2 * params[data.te_i]**2 * (data.te_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.te_i]**3 * data.ti * data.te_ti - (data.frq_list_ext * params[data.te_i])**4 * data.ti**3) * data.inv_te_denom**3)

    # Second component.
    b = (data.dti[j] * data.dci[k] + data.dti[k] * data.dci[j] + data.ci * data.d2ti[j, k]) * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti)

    # Third component.
    c = data.d2ci[j, k] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2 * data.fact_te)

    return 0.4 * sum(a + b + c, axis=2)



# Original Gj - Oj partial derivative.
######################################


# {} with diffusion parameters.

def calc_diff_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the original
    model-free formula with no parameters {} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci   dti     1 - (w.ti)^2
        -------  =  -   >  --- . --- . ----------------.
        dGj.dOj     5  /__ dOj   dGj   (1 + (w.ti)^2)^2
                       i=-k
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * data.fact_ti_djw_dti, axis=2)


def calc_ellipsoid_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the original
    model-free formula with no parameters {} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   / dci   dti     1 - (w.ti)^2        d2ci           1       \ 
        -------  =  -   >  | --- . --- . ----------------  +  ------- ti ------------ |.
        dGj.dOj     5  /__ \ dOj   dGj   (1 + (w.ti)^2)^2     dGj.dOj    1 + (w.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * data.fact_ti_djw_dti  +  data.d2ci[k, j] * data.ti * data.fact_ti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is::

                         _k_
         d2J(w)     2    \   dci   dti     1 - (w.ti)^2
        -------  =  - S2  >  --- . --- . ----------------.
        dGj.dOj     5    /__ dOj   dGj   (1 + (w.ti)^2)^2
                         i=-k
    """

    return 0.4 * params[data.s2_i] * sum(data.dci[j] * data.dti[k] * data.fact_ti_djw_dti, axis=2)


def calc_ellipsoid_S2_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is::

                         _k_
         d2J(w)     2    \   / dci   dti     1 - (w.ti)^2        d2ci           1       \ 
        -------  =  - S2  >  | --- . --- . ----------------  +  ------- ti ------------ |.
        dGj.dOj     5    /__ \ dOj   dGj   (1 + (w.ti)^2)^2     dGj.dOj    1 + (w.ti)^2 /
                         i=-k
    """

    return 0.4 * params[data.s2_i] * sum(data.dci[j] * data.dti[k] * data.fact_ti_djw_dti  +  data.d2ci[k, j] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci   dti  /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  --- . ---  | S2 ----------------  +  (1 - S2)te^2 ----------------------------- |.
        dGj.dOj     5  /__ dOj   dGj  \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=-k
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti), axis=2)


def calc_ellipsoid_S2_te_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   / dci   dti  /      1 - (w.ti)^2                      (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  | --- . ---  | S2 ----------------  +  (1 - S2)te^2 ----------------------------- |
        dGj.dOj     5  /__ \ dOj   dGj  \    (1 + (w.ti)^2)^2                  ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=-k

                                   d2ci      /      S2             (1 - S2)(te + ti)te    \ \ 
                               +  ------- ti | ------------  +  ------------------------- | |.
                                  dGj.dOj    \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2 * data.fact_te_djw_dti)  +  data.d2ci[k, j] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2 * data.fact_te), axis=2)



# Original Gj - S2 partial derivative.
######################################

# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dGjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2 double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \        dti    1 - (w.ti)^2
        -------  =  -   >  ci . ---  ----------------.
        dGj.dS2     5  /__      dGj  (1 + (w.ti)^2)^2
                       i=-k
    """

    return 0.4 * sum(data.ci * data.dti[k] * data.fact_ti_djw_dti, axis=2)


def calc_ellipsoid_S2_d2jw_dGjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2 double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti    1 - (w.ti)^2       dci           1       \ 
        -------  =  -   >  | ci . ---  ----------------  +  --- . ti ------------ |.
        dGj.dS2     5  /__ \      dGj  (1 + (w.ti)^2)^2     dGj      1 + (w.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.ci * data.dti[k] * data.fact_ti_djw_dti  +  data.dci[k] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dGjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2 double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2              (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  ci . ---  | ----------------  -  te^2 ----------------------------- |.
        dGj.dS2     5  /__      dGj  \ (1 + (w.ti)^2)^2          ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=-k
    """

    return 0.4 * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_te_djw_dti), axis=2)


def calc_ellipsoid_S2_te_d2jw_dGjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2 double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti  /   1 - (w.ti)^2              (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  | ci . ---  | ----------------  -  te^2 ----------------------------- |
        dGj.dS2     5  /__ \      dGj  \ (1 + (w.ti)^2)^2          ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=-k

                                dci      /      1                 (te + ti)te         \ \ 
                             +  --- . ti | ------------  -  ------------------------- | |.
                                dGj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_te_djw_dti)  +  data.dci[k] * data.ti * (data.fact_ti - data.fact_te), axis=2)



# Original Gj - te partial derivative.
#######################################

# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dGjdte(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - te double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                                    _k_
         d2J(w)     4               \        dti                   (te + ti)^2 - 3(w.te.ti)^2
        -------  =  - (1 - S2) . te  >  ci . --- . ti . (te + ti) -----------------------------.
        dGj.dte     5               /__      dGj                  ((te + ti)^2 + (w.te.ti)^2)^3
                                    i=-k
    """

    return 0.8 * data.one_s2 * params[data.te_i] * sum(data.ci * data.dti[k] * data.ti * data.te_ti * (data.te_ti_sqrd - 3.0 * data.w_te_ti_sqrd) * data.inv_te_denom**3, axis=2)


def calc_ellipsoid_S2_te_d2jw_dGjdte(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - te double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                              _k_
         d2J(w)     2         \   /       dti                        (te + ti)^2 - 3(w.te.ti)^2       dci          (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  - (1 - S2) >  | 2ci . --- . te . ti . (te + ti) -----------------------------  +  --- . ti^2 ----------------------------- |.
        dGj.dte     5         /__ \       dGj                       ((te + ti)^2 + (w.te.ti)^2)^3     dGj        ((te + ti)^2 + (w.te.ti)^2)^2 /
                              i=-k
    """

    return 0.4 * data.one_s2 * sum(2.0 * data.ci * data.dti[k] * params[data.te_i] * data.ti * data.te_ti * (data.te_ti_sqrd - 3.0 * data.w_te_ti_sqrd) * data.inv_te_denom**3  +  data.dci[k] * data.fact_djw_dte, axis=2)



# Original Oj - Ok partial derivative.
######################################

# {} with diffusion parameters.

def calc_diff_d2jw_dOjdOk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - Ok double partial derivative of the
    original model-free formula with no parameters {} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \    d2ci          ti
        -------  =  -   >  ------- . ------------.
        dOj.dOk     5  /__ dOj.dOk   1 + (w.ti)^2
                       i=-k
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * data.fact_ti, axis=2)


# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dOjdOk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - Ok double partial derivative of the
    original model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is::

                         _k_
         d2J(w)     2    \    d2ci          ti
        -------  =  - S2  >  ------- . ------------.
        dOj.dOk     5    /__ dOj.dOk   1 + (w.ti)^2
                         i=-k
    """

    return 0.4 * params[data.s2_i] * sum(data.d2ci[j, k] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dOjdOk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - Ok double partial derivative of the
    original model-free formula with the parameters {S2, te} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \    d2ci        /      S2             (1 - S2)(te + ti)te    \ 
        -------  =  -   >  ------- . ti | ------------  +  ------------------------- |.
        dOj.dOk     5  /__ dOj.dOk      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2 * data.fact_te), axis=2)



# Original Oj - S2 partial derivative.
######################################

# {S2} with diffusion parameters.

def calc_diff_S2_d2jw_dOjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - S2 double partial derivative of the original
    model-free formula with the parameter {S2} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci            1
        -------  =  -   >  --- . ti ------------.
        dOj.dS2     5  /__ dOj      1 + (w.ti)^2
                       i=-k
    """

    return 0.4 * sum(data.dci[k] * data.ti * data.fact_ti, axis=2)


# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dOjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - S2 double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci      /      1                 (te + ti)te         \ 
        -------  =  -   >  --- . ti | ------------  -  ------------------------- |.
        dOj.dS2     5  /__ dOj      \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.dci[k] * data.ti * (data.fact_ti - data.fact_te), axis=2)



# Original Oj - te partial derivative.
######################################

# {S2, te} with diffusion parameters.

def calc_diff_S2_te_d2jw_dOjdte(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - te double partial derivative of the original
    model-free formula with the parameters {S2, te} together with diffusion tensor parameters.

    The model-free Hessian is::

                               _k_
         d2J(w)     2          \   dci          (te + ti)^2 - (w.te.ti)^2
        -------  =  - (1 - S2)  >  --- . ti^2 -----------------------------.
        dOj.dte     5          /__ dOj        ((te + ti)^2 + (w.te.ti)^2)^2
                               i=-k
    """

    return 0.4 * data.one_s2 * sum(data.dci[k] * data.fact_djw_dte, axis=2)



# Original S2 - te partial derivative.
######################################

# {S2, te} with or without diffusion parameters.

def calc_S2_te_d2jw_dS2dte(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2 - te double partial derivative of the original
    model-free formula with the parameters {S2, te} with or without diffusion tensor parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)       2 \               (te + ti)^2 - (w.te.ti)^2
        -------  =  - -  >  ci . ti^2 -----------------------------.
        dS2.dte       5 /__           ((te + ti)^2 + (w.te.ti)^2)^2
                        i=-k
    """

    return -0.4 * sum(data.ci * data.fact_djw_dte, axis=2)



# Original te - te partial derivative.
######################################

# {S2, te} with or without diffusion parameters.

def calc_S2_te_d2jw_dte2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the te - te double partial derivative of the original
    model-free formula with the parameters {S2, te} with or without diffusion tensor parameters.

    The model-free Hessian is::

                                _k_
        d2J(w)       4          \             (te + ti)^3 + 3.w^2.ti^3.te.(te + ti) - (w.ti)^4.te^3
        ------  =  - - (1 - S2)  >  ci . ti^2 -----------------------------------------------------.
        dte**2       5          /__                        ((te + ti)^2 + (w.te.ti)^2)^3
                                i=-k
    """

    return -0.8 * data.one_s2 * sum(data.ci * data.ti**2 * (data.te_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.te_i] * data.te_ti - data.w_ti_sqrd**2 * params[data.te_i]**3) * data.inv_te_denom**3, axis=2)



# Extended Gj - Gk partial derivative.
######################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \      /    dti   dti  /             3 - (w.ti)^2                      (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
        -------  =  -   >  ci | -2 --- . ---  | S2.w^2.ti ----------------  +  (S2f - S2)ts^2 ---------------------------------------------------- |
        dGj.dGk     5  /__    \    dGj   dGk  \           (1 + (w.ti)^2)^3                              ((ts + ti)^2 + (w.ts.ti)^2)^3              /
                       i=-k

                                 d2ti   /      1 - (w.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ \ 
                             +  ------- | S2 ----------------  +  (S2f - S2)ts^2 ----------------------------- | |.
                                dGj.dGk \    (1 + (w.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 / /
    """

    # First component.
    a = -2.0 * data.dti[j] * data.dti[k] * (params[data.s2_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.s2f_s2 * params[data.ts_i]**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_i]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_i])**4 * data.ti**3) * data.inv_ts_denom**3)

    # Second component.
    b = data.d2ti[j, k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)

    return 0.4 * sum(data.ci * (a + b), axis=2)


def calc_ellipsoid_S2f_S2_ts_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti   dti  /             3 - (w.ti)^2                      (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
        -------  =  -   >  | -2ci --- . ---  | S2.w^2.ti ----------------  +  (S2f - S2)ts^2 ---------------------------------------------------- |
        dGj.dGk     5  /__ \      dGj   dGk  \           (1 + (w.ti)^2)^3                              ((ts + ti)^2 + (w.ts.ti)^2)^3              /
                       i=-k

                                / dti   dci     dti   dci         d2ti   \ /      1 - (w.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
                             +  | --- . ---  +  --- . ---  +  ci ------- | | S2 ----------------  +  (S2f - S2)ts^2 ----------------------------- |
                                \ dGj   dGk     dGk   dGj        dGj.dGk / \    (1 + (w.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /


                                 d2ci        /      S2            (S2f - S2)(ts + ti)ts   \ \ 
                             +  ------- . ti | ------------  +  ------------------------- | |.
                                dGj.dGk      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    # First component.
    a = -2.0 * data.ci * data.dti[j] * data.dti[k] * (params[data.s2_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.s2f_s2 * params[data.ts_i]**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_i]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_i])**4 * data.ti**3) * data.inv_ts_denom**3)

    # Second component.
    b = (data.dti[j] * data.dci[k] + data.dti[k] * data.dci[j] + data.ci * data.d2ti[j, k]) * (params[data.s2_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)

    # Third component.
    c = data.d2ci[j, k] * data.ti * (params[data.s2_i] * data.fact_ti + data.s2f_s2 * data.fact_ts)

    return 0.4 * sum(a + b + c, axis=2)



# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \      /    dti   dti  /             3 - (w.ti)^2                     (tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3
        -------  =  -   >  ci | -2 --- . ---  | S2.w^2.ti ----------------  +  (1 - S2f)tf^2 ----------------------------------------------------
        dGj.dGk     5  /__    \    dGj   dGk  \           (1 + (w.ti)^2)^3                             ((tf + ti)^2 + (w.tf.ti)^2)^3
                       i=-k

                                                                 (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
                                               +  (S2f - S2)ts^2 ---------------------------------------------------- |
                                                                           ((ts + ti)^2 + (w.ts.ti)^2)^3              /


                                 d2ti   /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ \ 
                             +  ------- | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------  +  (S2f - S2)ts^2 ----------------------------- | |.
                                dGj.dGk \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 / /
    """

    # First component.
    a = -2.0 * data.dti[j] * data.dti[k] * (params[data.s2_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.one_s2f * params[data.tf_i]**2 * (data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.tf_i]**3 * data.ti * data.tf_ti - (data.frq_list_ext * params[data.tf_i])**4 * data.ti**3) * data.inv_tf_denom**3  +  data.s2f_s2 * params[data.ts_i]**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_i]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_i])**4 * data.ti**3) * data.inv_ts_denom**3)

    # Second component.
    b = data.d2ti[j, k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)

    return 0.4 * sum(data.ci * (a + b), axis=2)


def calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti   dti  /             3 - (w.ti)^2                     (tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3
        -------  =  -   >  | -2ci --- . ---  | S2.w^2.ti ----------------  +  (1 - S2f)tf^2 ----------------------------------------------------
        dGj.dGk     5  /__ \      dGj   dGk  \           (1 + (w.ti)^2)^3                             ((tf + ti)^2 + (w.tf.ti)^2)^3
                       i=-k

                                                                 (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
                                               +  (S2f - S2)ts^2 ---------------------------------------------------- |
                                                                           ((ts + ti)^2 + (w.ts.ti)^2)^3              /


                                / dti   dci     dti   dci         d2ti   \ /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2
                             +  | --- . ---  +  --- . ---  +  ci ------- | | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------
                                \ dGj   dGk     dGk   dGj        dGj.dGk / \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2


                                                                                                 (ts + ti)^2 - (w.ts.ti)^2   \ 
                                                                             +  (S2f - S2)ts^2 ----------------------------- |
                                                                                               ((ts + ti)^2 + (w.ts.ti)^2)^2 /


                                 d2ci        /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ \ 
                             +  ------- . ti | ------------  +  -------------------------  +  ------------------------- | |.
                                dGj.dGk      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    # First component.
    a = -2.0 * data.ci * data.dti[j] * data.dti[k] * (params[data.s2_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.one_s2f * params[data.tf_i]**2 * (data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.tf_i]**3 * data.ti * data.tf_ti - (data.frq_list_ext * params[data.tf_i])**4 * data.ti**3) * data.inv_tf_denom**3  +  data.s2f_s2 * params[data.ts_i]**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_i]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_i])**4 * data.ti**3) * data.inv_ts_denom**3)

    # Second component.
    b = (data.dti[j] * data.dci[k] + data.dti[k] * data.dci[j] + data.ci * data.d2ti[j, k]) * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)

    # Third component.
    c = data.d2ci[j, k] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts)

    return 0.4 * sum(a + b + c, axis=2)



# Extended Gj - Oj partial derivative.
######################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci   dti  /      1 - (w.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  --- . ---  | S2 ----------------  +  (S2f - S2)ts^2 ----------------------------- |.
        dGj.dOj     5  /__ dOj   dGj  \    (1 + (w.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_S2_ts_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   / dci   dti  /      1 - (w.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  | --- . ---  | S2 ----------------  +  (S2f - S2)ts^2 ----------------------------- |
        dGj.dOj     5  /__ \ dOj   dGj  \    (1 + (w.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k

                                   d2ci        /      S2            (S2f - S2)(ts + ti)ts   \ \ 
                               +  ------- . ti | ------------  +  ------------------------- | |.
                                  dGj.dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.d2ci[k, j] * data.ti * (params[data.s2_i] * data.fact_ti + data.s2f_s2 * data.fact_ts), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci   dti  /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  --- . ---  | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------  +  (S2f - S2)ts^2 ----------------------------- |.
        dGj.dOj     5  /__ dOj   dGj  \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   / dci   dti  /      1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                        (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  | --- . ---  | S2 ----------------  +  (1 - S2f)tf^2 -----------------------------  +  (S2f - S2)ts^2 ----------------------------- |
        dGj.dOj     5  /__ \ dOj   dGj  \    (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                    ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k

                                   d2ci        /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ \ 
                               +  ------- . ti | ------------  +  -------------------------  +  ------------------------- | |.
                                  dGj.dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.d2ci[k, j] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended Gj - S2 partial derivative.
######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dGjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2 double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  ci . ---  | ----------------  -  ts^2 ----------------------------- |.
        dGj.dS2     5  /__      dGj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k
    """

    return 0.4 * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2 double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  | ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dGj.dS2     5  /__ \      dGj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k

                                dci      /      1                 (ts + ti)ts         \ \ 
                             +  --- . ti | ------------  -  ------------------------- | |.
                                dGj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_ts_djw_dti)  +  data.dci[k] * data.ti * (data.fact_ti - data.fact_ts), axis=2)



# Extended Gj - S2f partial derivative.
#######################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dGjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \        dti         (ts + ti)^2 - (w.ts.ti)^2
        --------  =  -   >  ci . ---  ts^2 -----------------------------.
        dGj.dS2f     5  /__      dGj       ((ts + ti)^2 + (w.ts.ti)^2)^2
                        i=-k
    """

    return 0.4 * sum(data.ci * data.dti[k] * data.fact_ts_djw_dti, axis=2)


def calc_ellipsoid_S2f_S2_ts_d2jw_dGjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \   /      dti         (ts + ti)^2 - (w.ts.ti)^2       dci            (ts + ti)ts         \ 
        --------  =  -   >  | ci . ---  ts^2 -----------------------------  +  --- . ti ------------------------- |.
        dGj.dS2f     5  /__ \      dGj       ((ts + ti)^2 + (w.ts.ti)^2)^2     dGj      (ts + ti)^2 + (w.ts.ti)^2 /
                        i=-k
    """

    return 0.4 * sum(data.ci * data.dti[k] * data.fact_ts_djw_dti  +  data.dci[k] * data.ti * data.fact_ts, axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dGjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                          _k_
         d2J(w)        2  \        dti  /        (tf + ti)^2 - (w.tf.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - -   >  ci . ---  | tf^2 -----------------------------  -  ts^2 ----------------------------- |.
        dGj.dS2f       5  /__      dGj  \      ((tf + ti)^2 + (w.tf.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                          i=-k
    """

    return -0.4 * sum(data.ci * data.dti[k] * (data.fact_tf_djw_dti - data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                          _k_
         d2J(w)        2  \   /      dti  /        (tf + ti)^2 - (w.tf.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - -   >  | ci . ---  | tf^2 -----------------------------  -  ts^2 ----------------------------- |
        dGj.dS2f       5  /__ \      dGj  \      ((tf + ti)^2 + (w.tf.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                          i=-k

                                   dci      /       (tf + ti)tf                   (ts + ti)ts         \ \ 
                                +  --- . ti | -------------------------  -  ------------------------- | |.
                                   dGj      \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return -0.4 * sum(data.ci * data.dti[k] * (data.fact_tf_djw_dti - data.fact_ts_djw_dti)  +  data.dci[k] * data.ti * (data.fact_tf - data.fact_ts), axis=2)



# Extended Gj - tf partial derivative.
######################################

# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dGjdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                                     _k_
         d2J(w)     4                \        dti                   (tf + ti)^2 - 3(w.tf.ti)^2
        -------  =  - (1 - S2f) . tf  >  ci . --- . ti . (tf + ti) -----------------------------.
        dGj.dtf     5                /__      dGj                  ((tf + ti)^2 + (w.tf.ti)^2)^3
                                     i=-k
    """

    return 0.8 * data.one_s2f * params[data.tf_i] * sum(data.ci * data.dti[k] * data.ti * data.tf_ti * (data.tf_ti_sqrd - 3.0 * data.w_tf_ti_sqrd) * data.inv_tf_denom**3, axis=2)


def calc_ellipsoid_S2f_tf_S2_ts_d2jw_dGjdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                                _k_
         d2J(w)     2           \   /       dti                        (tf + ti)^2 - 3(w.tf.ti)^2       dci          (tf + ti)^2 - (w.tf.ti)^2   \ 
        -------  =  - (1 - S2f)  >  | 2ci . --- . tf . ti . (tf + ti) -----------------------------  +  --- . ti^2 ----------------------------- |.
        dGj.dtf     5           /__ \       dGj                       ((tf + ti)^2 + (w.tf.ti)^2)^3     dGj        ((tf + ti)^2 + (w.tf.ti)^2)^2 /
                                i=-k
    """

    return 0.4 * data.one_s2f * sum(2.0 * data.ci * data.dti[k] * params[data.tf_i] * data.ti * data.tf_ti * (data.tf_ti_sqrd - 3.0 * data.w_tf_ti_sqrd) * data.inv_tf_denom**3  +  data.dci[k] * data.fact_djw_dtf, axis=2)



# Extended Gj - ts partial derivative.
######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dGjdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                                      _k_
         d2J(w)     4                 \        dti                   (ts + ti)^2 - 3(w.ts.ti)^2
        -------  =  - (S2f - S2) . ts  >  ci . --- . ti . (ts + ti) -----------------------------.
        dGj.dts     5                 /__      dGj                  ((ts + ti)^2 + (w.ts.ti)^2)^3
                                      i=-k
    """

    return 0.8 * data.s2f_s2 * params[data.ts_i] * sum(data.ci * data.dti[k] * data.ti * data.ts_ti * (data.ts_ti_sqrd - 3.0 * data.w_ts_ti_sqrd) * data.inv_ts_denom**3, axis=2)


def calc_ellipsoid_S2f_S2_ts_d2jw_dGjdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                                 _k_
         d2J(w)     2            \   /       dti                        (ts + ti)^2 - 3(w.ts.ti)^2       dci          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  - (S2f - S2)  >  | 2ci . --- . ts . ti . (ts + ti) -----------------------------  +  --- . ti^2 ----------------------------- |.
        dGj.dts     5            /__ \       dGj                       ((ts + ti)^2 + (w.ts.ti)^2)^3     dGj        ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                                 i=-k
    """

    return 0.4 * data.s2f_s2 * sum(2.0 * data.ci * data.dti[k] * params[data.ts_i] * data.ti * data.ts_ti * (data.ts_ti_sqrd - 3.0 * data.w_ts_ti_sqrd) * data.inv_ts_denom**3  +  data.dci[k] * data.fact_djw_dts, axis=2)



# Extended Oj - Ok partial derivative.
######################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dOjdOk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - Ok double partial derivative of the
    extended model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \    d2ci        /      S2            (S2f - S2)(ts + ti)ts   \ 
        -------  =  -   >  ------- . ti | ------------  +  ------------------------- |.
        dOj.dOk     5  /__ dOj.dOk      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2_i] * data.fact_ti + data.s2f_s2 * data.fact_ts), axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dOjdOk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - Ok double partial derivative of the
    extended model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \    d2ci        /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        -------  =  -   >  ------- . ti | ------------  +  -------------------------  +  ------------------------- |.
        dOj.dOk     5  /__ dOj.dOk      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended Oj - S2 partial derivative.
######################################

# {S2f, S2, ts} and {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dOjdS2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - S2 double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} and {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci      /      1                 (ts + ti)ts         \ 
        -------  =  -   >  --- . ti | ------------  -  ------------------------- |.
        dOj.dS2     5  /__ dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.dci[k] * data.ti * (data.fact_ti - data.fact_ts), axis=2)



# Extended Oj - S2f partial derivative.
#######################################

# {S2f, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dOjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - S2f double partial derivative of the
    extended model-free formula with the parameters {S2f, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \   dci             (ts + ti)ts
        --------  =  -   >  --- . ti -------------------------.
        dOj.dS2f     5  /__ dOj      (ts + ti)^2 + (w.ts.ti)^2
                        i=-k
    """

    return 0.4 * sum(data.dci[k] * data.ti * data.fact_ts, axis=2)


# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dOjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - S2f double partial derivative of the
    extended model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                          _k_
         d2J(w)        2  \   dci      /       (tf + ti)tf                   (ts + ti)ts         \ 
        --------  =  - -   >  --- . ti | -------------------------  -  ------------------------- |.
        dOj.dS2f       5  /__ dOj      \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                          i=-k
    """

    return -0.4 * sum(data.dci[k] * data.ti * (data.fact_tf - data.fact_ts), axis=2)



# Extended Oj - tf partial derivative.
######################################

# {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2_ts_d2jw_dOjdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                                _k_
         d2J(w)     2           \   dci          (tf + ti)^2 - (w.tf.ti)^2
        -------  =  - (1 - S2f)  >  --- . ti^2 -----------------------------.
        dOj.dtf     5           /__ dOj        ((tf + ti)^2 + (w.tf.ti)^2)^2
                                i=-k
    """

    return 0.4 * data.one_s2f * sum(data.dci[k] * data.fact_djw_dtf, axis=2)



# Extended Oj - ts partial derivative.
######################################

# {S2f, S2, ts} and {S2f, tf, S2, ts} with diffusion parameters.

def calc_diff_S2f_S2_ts_d2jw_dOjdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                                 _k_
         d2J(w)     2            \   dci          (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - (S2f - S2)  >  --- . ti^2 -----------------------------.
        dOj.dts     5            /__ dOj        ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=-k
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

    The model-free Hessian is::

                         _k_
         d2J(w)       2  \               (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - -   >  ci . ti^2 -----------------------------.
        dS2.dts       5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                         i=-k
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

    The model-free Hessian is::

                          _k_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------.
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=-k
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

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  -   >  ci . ti^2 -----------------------------.
        dS2f.dts     5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                        i=-k
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

    The model-free Hessian is::

                                 _k_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------.
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=-k
    """

    return -0.8 * data.one_s2f * sum(data.ci * data.ti**2 * (data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.tf_i] * data.tf_ti - data.w_ti_sqrd**2 * params[data.tf_i]**3) * data.inv_tf_denom**3, axis=2)



# Extended ts - ts partial derivative.
######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts} with or without diffusion parameters.

def calc_S2f_S2_ts_d2jw_dts2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the ts - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or {S2f, tf, S2, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is::

                                  _k_
        d2J(w)       4            \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - (S2f - S2)  >  ci . ti^2 -----------------------------------------------------.
        dts**2       5            /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                  i=-k
    """

    return -0.8 * data.s2f_s2 * sum(data.ci * data.ti**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.ts_i] * data.ts_ti - data.w_ti_sqrd**2 * params[data.ts_i]**3) * data.inv_ts_denom**3, axis=2)



# Extended 2 Gj - Gk partial derivative.
########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \      /    dti   dti  /                  3 - (w.ti)^2                        (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
        -------  =  -   >  ci | -2 --- . ---  | S2f.S2s.w^2.ti ----------------  +  S2f(1 - S2s)ts^2 ---------------------------------------------------- |
        dGj.dGk     5  /__    \    dGj   dGk  \                (1 + (w.ti)^2)^3                                ((ts + ti)^2 + (w.ts.ti)^2)^3              /
                       i=-k

                                 d2ti   /           1 - (w.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ \ 
                             +  ------- | S2f.S2s ----------------  +  S2f(1 - S2s)ts^2 ----------------------------- | |.
                                dGj.dGk \         (1 + (w.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 / /
    """

    # First component.
    a = -2.0 * data.dti[j] * data.dti[k] * (params[data.s2f_i] * params[data.s2s_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.s2f_s2 * params[data.ts_i]**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_i]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_i])**4 * data.ti**3) * data.inv_ts_denom**3)

    # Second component.
    b = data.d2ti[j, k] * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)

    return 0.4 * sum(data.ci * (a + b), axis=2)


def calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti   dti  /                  3 - (w.ti)^2                        (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
        -------  =  -   >  | -2ci --- . ---  | S2f.S2s.w^2.ti ----------------  +  S2f(1 - S2s)ts^2 ---------------------------------------------------- |
        dGj.dGk     5  /__ \      dGj   dGk  \                (1 + (w.ti)^2)^3                                ((ts + ti)^2 + (w.ts.ti)^2)^3              /
                       i=-k

                                / dti   dci     dti   dci         d2ti   \ /           1 - (w.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
                             +  | --- . ---  +  --- . ---  +  ci ------- | | S2f.S2s ----------------  +  S2f(1 - S2s)ts^2 ----------------------------- |
                                \ dGj   dGk     dGk   dGj        dGj.dGk / \         (1 + (w.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /


                                 d2ci        /   S2f.S2s         S2f(1 - S2s)(ts + ti)ts  \ \ 
                             +  ------- . ti | ------------  +  ------------------------- | |.
                                dGj.dGk      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    # First component.
    a = -2.0 * data.ci * data.dti[j] * data.dti[k] * (params[data.s2f_i] * params[data.s2s_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.s2f_s2 * params[data.ts_i]**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_i]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_i])**4 * data.ti**3) * data.inv_ts_denom**3)

    # Second component.
    b = (data.dti[j] * data.dci[k] + data.dti[k] * data.dci[j] + data.ci * data.d2ti[j, k]) * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)

    # Third component.
    c = data.d2ci[j, k] * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.s2f_s2 * data.fact_ts)

    return 0.4 * sum(a + b + c, axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \      /    dti   dti  /                  3 - (w.ti)^2                     (tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3
        -------  =  -   >  ci | -2 --- . ---  | S2f.S2s.w^2.ti ----------------  +  (1 - S2f)tf^2 ----------------------------------------------------
        dGj.dGk     5  /__    \    dGj   dGk  \                (1 + (w.ti)^2)^3                             ((tf + ti)^2 + (w.tf.ti)^2)^3
                       i=-k

                                                                   (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
                                               +  S2f(1 - S2s)ts^2 ---------------------------------------------------- |
                                                                             ((ts + ti)^2 + (w.ts.ti)^2)^3              /


                        d2ti   /           1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
                    +  ------- | S2f.S2s ----------------  +  (1 - S2f)tf^2 -----------------------------  +  S2f(1 - S2s)ts^2 ----------------------------- |.
                       dGj.dGk \         (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
    """

    # First component.
    a = -2.0 * data.dti[j] * data.dti[k] * (params[data.s2f_i] * params[data.s2s_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.one_s2f * params[data.tf_i]**2 * (data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.tf_i]**3 * data.ti * data.tf_ti - (data.frq_list_ext * params[data.tf_i])**4 * data.ti**3) * data.inv_tf_denom**3  +  data.s2f_s2 * params[data.ts_i]**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_i]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_i])**4 * data.ti**3) * data.inv_ts_denom**3)

    # Second component.
    b = data.d2ti[j, k] * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)

    return 0.4 * sum(data.ci * (a + b), axis=2)


def calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdGk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Gk double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   /      dti   dti  /                  3 - (w.ti)^2                     (tf + ti)^3 + 3.w^2.tf^3.ti(tf + ti) - (w.tf)^4.ti^3
        -------  =  -   >  | -2ci --- . ---  | S2f.S2s.w^2.ti ----------------  +  (1 - S2f)tf^2 ----------------------------------------------------
        dGj.dGk     5  /__ \      dGj   dGk  \                (1 + (w.ti)^2)^3                             ((tf + ti)^2 + (w.tf.ti)^2)^3
                       i=-k

                                                                   (ts + ti)^3 + 3.w^2.ts^3.ti(ts + ti) - (w.ts)^4.ti^3 \ 
                                               +  S2f(1 - S2s)ts^2 ---------------------------------------------------- |
                                                                             ((ts + ti)^2 + (w.ts.ti)^2)^3              /


                                / dti   dci     dti   dci         d2ti   \ /           1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2
                             +  | --- . ---  +  --- . ---  +  ci ------- | | S2f.S2s ----------------  +  (1 - S2f)tf^2 -----------------------------
                                \ dGj   dGk     dGk   dGj        dGj.dGk / \         (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2


                                                                                                   (ts + ti)^2 - (w.ts.ti)^2   \ 
                                                                             +  S2f(1 - S2s)ts^2 ----------------------------- |
                                                                                                 ((ts + ti)^2 + (w.ts.ti)^2)^2 /


                                 d2ci        /   S2f.S2s          (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ \ 
                             +  ------- . ti | ------------  +  -------------------------  +  ------------------------- | |.
                                dGj.dGk      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    # First component.
    a = -2.0 * data.ci * data.dti[j] * data.dti[k] * (params[data.s2f_i] * params[data.s2s_i] * data.frq_sqrd_list_ext * data.ti * (3.0 - data.w_ti_sqrd) * data.fact_ti**3  +  data.one_s2f * params[data.tf_i]**2 * (data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.tf_i]**3 * data.ti * data.tf_ti - (data.frq_list_ext * params[data.tf_i])**4 * data.ti**3) * data.inv_tf_denom**3  +  data.s2f_s2 * params[data.ts_i]**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * params[data.ts_i]**3 * data.ti * data.ts_ti - (data.frq_list_ext * params[data.ts_i])**4 * data.ti**3) * data.inv_ts_denom**3)

    # Second component.
    b = (data.dti[j] * data.dci[k] + data.dti[k] * data.dci[j] + data.ci * data.d2ti[j, k]) * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)

    # Third component.
    c = data.d2ci[j, k] * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts)

    return 0.4 * sum(a + b + c, axis=2)



# Extended 2 Gj - Oj partial derivative.
########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci   dti  /           1 - (w.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  --- . ---  | S2f.S2s ----------------  +  S2f(1 - S2s)ts^2 ----------------------------- |.
        dGj.dOj     5  /__ dOj   dGj  \         (1 + (w.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   / dci   dti  /           1 - (w.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  | --- . ---  | S2f.S2s ----------------  +  S2f(1 - S2s)ts^2 ----------------------------- |
        dGj.dOj     5  /__ \ dOj   dGj  \         (1 + (w.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k

                                   d2ci        /   S2f.S2s         S2f(1 - S2s)(ts + ti)ts  \ \ 
                               +  ------- . ti | ------------  +  ------------------------- | |.
                                  dGj.dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.d2ci[k, j] * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.s2f_s2 * data.fact_ts), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   dci   dti  /           1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  --- . ---  | S2f.S2s ----------------  +  (1 - S2f)tf^2 -----------------------------  +  S2f(1 - S2s)ts^2 ----------------------------- |.
        dGj.dOj     5  /__ dOj   dGj  \         (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdOj(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - Oj double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \   / dci   dti  /           1 - (w.ti)^2                       (tf + ti)^2 - (w.tf.ti)^2                          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  | --- . ---  | S2f.S2s ----------------  +  (1 - S2f)tf^2 -----------------------------  +  S2f(1 - S2s)ts^2 ----------------------------- |
        dGj.dOj     5  /__ \ dOj   dGj  \         (1 + (w.ti)^2)^2                   ((tf + ti)^2 + (w.tf.ti)^2)^2                      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=-k

                                   d2ci        /   S2f.S2s          (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ \ 
                               +  ------- . ti | ------------  +  -------------------------  +  ------------------------- | |.
                                  dGj.dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.dci[j] * data.dti[k] * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2f * data.fact_tf_djw_dti + data.s2f_s2 * data.fact_ts_djw_dti)  +  data.d2ci[k, j] * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended 2 Gj - S2f partial derivative.
#########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dGjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \        dti  /       1 - (w.ti)^2                       (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  ci . ---  | S2s ----------------  +  (1 - S2s)ts^2 ----------------------------- |.
        dGj.dS2f     5  /__      dGj  \     (1 + (w.ti)^2)^2                   ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=-k
    """

    return 0.4 * sum(data.ci * data.dti[k] * (params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2s * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \   /      dti  /       1 - (w.ti)^2                       (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  | ci . ---  | S2s ----------------  +  (1 - S2s)ts^2 ----------------------------- |
        dGj.dS2f     5  /__ \      dGj  \     (1 + (w.ti)^2)^2                   ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=-k

                                dci      /     S2s            (1 - S2s)(ts + ti)ts    \ \ 
                             +  --- . ti | ------------  +  ------------------------- | |.
                                dGj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[k] * (params[data.s2s_i] * data.fact_ti_djw_dti + data.one_s2s * data.fact_ts_djw_dti)  +  data.dci[k] * data.ti * (params[data.s2s_i] * data.fact_ti + data.one_s2s * data.fact_ts), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dGjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \        dti  /       1 - (w.ti)^2              (tf + ti)^2 - (w.tf.ti)^2                       (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  ci . ---  | S2s ----------------  -  tf^2 -----------------------------  +  (1 - S2s)ts^2 ----------------------------- |.
        dGj.dS2f     5  /__      dGj  \     (1 + (w.ti)^2)^2          ((tf + ti)^2 + (w.tf.ti)^2)^2                   ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=-k
    """

    return 0.4 * sum(data.ci * data.dti[k] * (params[data.s2s_i] * data.fact_ti_djw_dti - data.fact_tf_djw_dti + data.one_s2s * data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2f double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \   /      dti  /       1 - (w.ti)^2              (tf + ti)^2 - (w.tf.ti)^2                       (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  | ci . ---  | S2s ----------------  -  tf^2 -----------------------------  +  (1 - S2s)ts^2 ----------------------------- |
        dGj.dS2f     5  /__ \      dGj  \     (1 + (w.ti)^2)^2          ((tf + ti)^2 + (w.tf.ti)^2)^2                   ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=-k

                                 dci      /     S2s                (tf + ti)tf               (1 - S2s)(ts + ti)ts    \ \ 
                              +  --- . ti | ------------  -  -------------------------  +  ------------------------- | |.
                                 dGj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * sum(data.ci * data.dti[k] * (params[data.s2s_i] * data.fact_ti_djw_dti - data.fact_tf_djw_dti + data.one_s2s * data.fact_ts_djw_dti)  +  data.dci[k] * data.ti * (params[data.s2s_i] * data.fact_ti - data.tf_ti_tf * data.inv_ts_denom + data.one_s2s * data.fact_ts), axis=2)



# Extended 2 Gj - S2s partial derivative.
#########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dGjdS2s(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2s double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                           _k_
         d2J(w)      2     \        dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - S2f  >  ci . ---  | ----------------  -  ts^2 ----------------------------- |.
        dGj.dS2s     5     /__      dGj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                           i=-k
    """

    return 0.4 * params[data.s2f_i] * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_ts_djw_dti), axis=2)


def calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdS2s(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - S2s double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                           _k_
         d2J(w)      2     \   /      dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - S2f  >  | ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dGj.dS2s     5     /__ \      dGj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                           i=-k

                                dci      /      1                 (ts + ti)ts         \ \ 
                             +  --- . ti | ------------  -  ------------------------- | |.
                                dGj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 / /
    """

    return 0.4 * params[data.s2f_i] * sum(data.ci * data.dti[k] * (data.fact_ti_djw_dti - data.fact_ts_djw_dti)  +  data.dci[k] * data.ti * (data.fact_ti - data.fact_ts), axis=2)



# Extended 2 Gj - tf partial derivative.
########################################

# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dGjdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                                     _k_
         d2J(w)     4                \        dti                   (tf + ti)^2 - 3(w.tf.ti)^2
        -------  =  - (1 - S2f) . tf  >  ci . --- . ti . (tf + ti) -----------------------------.
        dGj.dtf     5                /__      dGj                  ((tf + ti)^2 + (w.tf.ti)^2)^3
                                     i=-k
    """

    return 0.8 * data.one_s2f * params[data.tf_i] * sum(data.ci * data.dti[k] * data.ti * data.tf_ti * (data.tf_ti_sqrd - 3.0 * data.w_tf_ti_sqrd) * data.inv_tf_denom**3, axis=2)


def calc_ellipsoid_S2f_tf_S2s_ts_d2jw_dGjdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                                _k_
         d2J(w)     2           \   /       dti                        (tf + ti)^2 - 3(w.tf.ti)^2       dci          (tf + ti)^2 - (w.tf.ti)^2   \ 
        -------  =  - (1 - S2f)  >  | 2ci . --- . tf . ti . (tf + ti) -----------------------------  +  --- . ti^2 ----------------------------- |.
        dGj.dtf     5           /__ \       dGj                       ((tf + ti)^2 + (w.tf.ti)^2)^3     dGj        ((tf + ti)^2 + (w.tf.ti)^2)^2 /
                                i=-k
    """

    return 0.4 * data.one_s2f * sum(2.0 * data.ci * data.dti[k] * params[data.tf_i] * data.ti * data.tf_ti * (data.tf_ti_sqrd - 3.0 * data.w_tf_ti_sqrd) * data.inv_tf_denom**3  +  data.dci[k] * data.fact_djw_dtf, axis=2)



# Extended 2 Gj - ts partial derivative.
########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dGjdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                                        _k_
         d2J(w)     4                   \        dti                   (ts + ti)^2 - 3(w.ts.ti)^2
        -------  =  - S2f(1 - S2s) . ts  >  ci . --- . ti . (ts + ti) -----------------------------.
        dGj.dts     5                   /__      dGj                  ((ts + ti)^2 + (w.ts.ti)^2)^3
                                        i=-k
    """

    return 0.8 * data.s2f_s2 * params[data.ts_i] * sum(data.ci * data.dti[k] * data.ti * data.ts_ti * (data.ts_ti_sqrd - 3.0 * data.w_ts_ti_sqrd) * data.inv_ts_denom**3, axis=2)


def calc_ellipsoid_S2f_S2s_ts_d2jw_dGjdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Gj - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                                   _k_
         d2J(w)     2              \   /       dti                        (ts + ti)^2 - 3(w.ts.ti)^2       dci          (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  - S2f(1 - S2s)  >  | 2ci . --- . ts . ti . (ts + ti) -----------------------------  +  --- . ti^2 ----------------------------- |.
        dGj.dts     5              /__ \       dGj                       ((ts + ti)^2 + (w.ts.ti)^2)^3     dGj        ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                                   i=-k
    """

    return 0.4 * data.s2f_s2 * sum(2.0 * data.ci * data.dti[k] * params[data.ts_i] * data.ti * data.ts_ti * (data.ts_ti_sqrd - 3.0 * data.w_ts_ti_sqrd) * data.inv_ts_denom**3  +  data.dci[k] * data.fact_djw_dts, axis=2)



# Extended 2 Oj - Ok partial derivative.
########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dOjdOk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - Ok double partial derivative of the
    extended model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \    d2ci        /  S2f . S2s        S2f(1 - S2s)(ts + ti)ts  \ 
        -------  =  -   >  ------- . ti | ------------  +  ------------------------- |.
        dOj.dOk     5  /__ dOj.dOk      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.s2f_s2 * data.fact_ts), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dOjdOk(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - Ok double partial derivative of the
    extended model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                       _k_
         d2J(w)     2  \    d2ci        /  S2f . S2s         (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        -------  =  -   >  ------- . ti | ------------  +  -------------------------  +  ------------------------- |.
        dOj.dOk     5  /__ dOj.dOk      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=-k
    """

    return 0.4 * sum(data.d2ci[j, k] * data.ti * (params[data.s2f_i] * params[data.s2s_i] * data.fact_ti + data.one_s2f * data.fact_tf + data.s2f_s2 * data.fact_ts), axis=2)



# Extended 2 Oj - S2f partial derivative.
#########################################

# {S2f, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dOjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - S2f double partial derivative of the
    extended model-free formula with the parameters {S2f, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \   dci      /      S2s           (1 - S2s)(ts + ti)ts    \ 
        --------  =  -   >  --- . ti | ------------  +  ------------------------- |.
        dOj.dS2f     5  /__ dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=-k
    """

    return 0.4 * sum(data.dci[k] * data.ti * (params[data.s2s_i] * data.fact_ti + data.one_s2s * data.fact_ts), axis=2)


# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dOjdS2f(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - S2f double partial derivative of the
    extended model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                        _k_
         d2J(w)      2  \   dci      /      S2s               (tf + ti)tf               (1 - S2s)(ts + ti)ts    \ 
        --------  =  -   >  --- . ti | ------------  -  -------------------------  +  ------------------------- |.
        dOj.dS2f     5  /__ dOj      \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                        i=-k
    """

    return 0.4 * sum(data.dci[k] * data.ti * (params[data.s2s_i] * data.fact_ti - data.fact_tf + data.one_s2s * data.fact_ts), axis=2)



# Extended 2 Oj - S2s partial derivative.
#########################################

# {S2f, S2s, ts} and {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dOjdS2s(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - S2 double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} and {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                           _k_
         d2J(w)      2     \   dci      /      1                 (ts + ti)ts         \ 
        --------  =  - S2f  >  --- . ti | ------------  -  ------------------------- |.
        dOj.dS2s     5     /__ dOj      \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                           i=-k
    """

    return 0.4 * params[data.s2f_i] * sum(data.dci[k] * data.ti * (data.fact_ti - data.fact_ts), axis=2)



# Extended 2 Oj - tf partial derivative.
########################################

# {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_tf_S2s_ts_d2jw_dOjdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} together with diffusion tensor
    parameters.

    The model-free Hessian is::

                                _k_
         d2J(w)     2           \   dci          (tf + ti)^2 - (w.tf.ti)^2
        -------  =  - (1 - S2f)  >  --- . ti^2 -----------------------------.
        dOj.dtf     5           /__ dOj        ((tf + ti)^2 + (w.tf.ti)^2)^2
                                i=-k
    """

    return 0.4 * data.one_s2f * sum(data.dci[k] * data.fact_djw_dtf, axis=2)



# Extended 2 Oj - ts partial derivative.
########################################

# {S2f, S2s, ts} and {S2f, tf, S2s, ts} with diffusion parameters.

def calc_diff_S2f_S2s_ts_d2jw_dOjdts(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Oj - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} together with
    diffusion tensor parameters.

    The model-free Hessian is::

                                   _k_
         d2J(w)     2              \   dci          (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - S2f(1 - S2s)  >  --- . ti^2 -----------------------------.
        dOj.dts     5              /__ dOj        ((ts + ti)^2 + (w.ts.ti)^2)^2
                                   i=-k
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

    The model-free Hessian is::

                         _k_
          d2J(w)      2  \           /      1                 (ts + ti).ts        \ 
        ---------  =  -   >  ci . ti | ------------  -  ------------------------- |.
        dS2f.dS2s     5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                         i=-k
    """

    return 0.4 * sum(data.ci * data.ti * (data.fact_ti - data.fact_ts), axis=2)



# Extended 2 S2f - tf partial derivative.
#########################################

# {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_tf_S2s_ts_d2jw_dS2fdtf(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2f - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} with or without diffusion tensor
    parameters.

    The model-free Hessian is::

                          _k_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------.
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=-k
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

    The model-free Hessian is::

                                 _k_
         d2J(w)      2           \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  - (1 - S2s)  >  ci . ti^2 -----------------------------.
        dS2f.dts     5           /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                                 i=-k
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

    The model-free Hessian is::

                             _k_
         d2J(w)        2     \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  - - S2f  >  ci . ti^2 -----------------------------.
        dS2s.dts       5     /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                             i=-k
    """

    return -0.4 * params[data.s2f_i] * sum(data.ci * data.fact_djw_dts, axis=2)



# Extended 2 tf - tf partial derivative.
########################################

# {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_tf_S2s_ts_d2jw_dtf2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the tf - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2s, ts} with or without diffusion tensor
    parameters.

    The model-free Hessian is::

                                 _k_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------.
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=-k
    """

    return -0.8 * data.one_s2f * sum(data.ci * data.ti**2 * (data.tf_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.tf_i] * data.tf_ti - data.w_ti_sqrd**2 * params[data.tf_i]**3) * data.inv_tf_denom**3, axis=2)



# Extended 2 ts - ts partial derivative.
########################################

# {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without diffusion parameters.

def calc_S2f_S2s_ts_d2jw_dts2(data, params, j, k):
    """Spectral density Hessian.

    Calculate the spectral desity values for the ts - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2s, ts} or {S2f, tf, S2s, ts} with or without
    diffusion tensor parameters.

    The model-free Hessian is::

                                    _k_
        d2J(w)       4              \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - S2f(1 - S2s)  >  ci . ti^2 -----------------------------------------------------.
        dts**2       5              /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                    i=-k
    """

    return -0.8 * data.s2f_s2 * sum(data.ci * data.ti**2 * (data.ts_ti**3 + 3.0 * data.frq_sqrd_list_ext * data.ti**3 * params[data.ts_i] * data.ts_ti - data.w_ti_sqrd**2 * params[data.ts_i]**3) * data.inv_ts_denom**3, axis=2)
