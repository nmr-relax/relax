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



############################
# Spectral density values. #
############################

def create_jw_struct(data, calc_jw):
    """Function to create the model-free spectral density values.

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

    data.jw = calc_jw(data)



# Original, no params or {tm}.
##############################

def calc_jw(data):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with no parameters {}
    or the single parameter {tm}.

    The formula is:

                    _n_
                 2  \           /      1       \ 
        J(w)  =  -   >  ci . ti | ------------ |
                 5  /__         \ 1 + (w.ti)^2 /
                    i=m
    """

    jw = data.ci[0] * data.ti[0] * data.fact_ti[0]

    for i in xrange(1, data.num_indecies):
        jw = jw + data.ci[i] * data.ti[i] * data.fact_ti[i]

    return 0.4 * jw



# Original {S2} or {tm, S2}.
############################

def calc_S2_jw(data):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with the single
    parameter {S2} or the parameters {tm, S2}.

    The formula is:

                      _n_
                 2    \           /      1       \ 
        J(w)  =  - S2  >  ci . ti | ------------ |
                 5    /__         \ 1 + (w.ti)^2 /
                      i=m
    """

    jw = data.ci[0] * data.ti[0] * data.fact_ti[0]

    for i in xrange(1, data.num_indecies):
        jw = jw + data.ci[i] * data.ti[i] * data.fact_ti[i]

    return 0.4 * data.params[data.s2_index] * jw



# Original {S2, te} or {tm, S2, te}.
####################################

def calc_S2_te_jw(data):
    """Spectral density function.

    Calculate the spectral density values for the original model-free formula with the parameters
    {S2, te} or the parameters {tm, S2, te}.

    The model-free formula is:

                    _n_
                 2  \           /      S2             (1 - S2)(te + ti)te    \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                    i=m
    """

    jw = data.ci[0] * data.ti[0] * (data.params[data.s2_index] * data.fact_ti[0] + data.one_s2 * data.te_ti_te[0] * data.inv_te_denom[0])

    for i in xrange(1, data.num_indecies):
        jw = jw + data.ci[i] * data.ti[i] * (data.params[data.s2_index] * data.fact_ti[i] + data.one_s2 * data.te_ti_te[i] * data.inv_te_denom[i])

    return 0.4 * jw



# Extended {S2f, S2, ts} or {tm, S2f, S2, ts}.
##############################################

def calc_S2f_S2_ts_jw(data):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, S2, ts} or the parameters {tm, S2f, S2, ts}.

    The model-free formula is:

                    _n_
                 2  \           /      S2            (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m
    """

    jw = data.ci[0] * data.ti[0] * (data.params[data.s2_index] * data.fact_ti[0] + data.s2f_s2 * data.ts_ti_ts[0] * data.inv_ts_denom[0])

    for i in xrange(1, data.num_indecies):
        jw = jw + data.ci[i] * data.ti[i] * (data.params[data.s2_index] * data.fact_ti[i] + data.s2f_s2 * data.ts_ti_ts[i] * data.inv_ts_denom[i])

    return 0.4 * jw



# Extended {S2f, tf, S2, ts} or {tm, S2f, tf, S2, ts}.
######################################################

def calc_S2f_tf_S2_ts_jw(data):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, tf, S2, ts} or the parameters {tm, S2f, tf, S2, ts}.

    The model-free formula is:

                    _n_
                 2  \           /      S2            (1 - S2f)(tf + ti)tf          (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m
    """

    jw = data.ci[0] * data.ti[0] * (data.params[data.s2_index] * data.fact_ti[0] + data.one_s2f * data.tf_ti_tf[0] * data.inv_tf_denom[0] + data.s2f_s2 * data.ts_ti_ts[0] * data.inv_ts_denom[0])

    for i in xrange(1, data.num_indecies):
        jw = jw + data.ci[i] * data.ti[i] * (data.params[data.s2_index] * data.fact_ti[i] + data.one_s2f * data.tf_ti_tf[i] * data.inv_tf_denom[i] + data.s2f_s2 * data.ts_ti_ts[i] * data.inv_ts_denom[i])

    return 0.4 * jw



# Extended 2 {S2f, S2s, ts} or {tm, S2f, S2s, ts}.
##################################################

def calc_S2f_S2s_ts_jw(data):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, S2s, ts} or the parameters {tm, S2f, S2s, ts}.

    The model-free formula is:

                       _n_
                 2     \           /      S2s           (1 - S2s)(ts + ti)ts    \ 
        J(w)  =  - S2f  >  ci . ti | ------------  +  ------------------------- |
                 5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=m
    """

    jw = data.ci[0] * data.ti[0] * (data.params[data.s2s_index] * data.fact_ti[0] + data.one_s2s * data.ts_ti_ts[0] * data.inv_ts_denom[0])

    for i in xrange(1, data.num_indecies):
        jw = jw + data.ci[i] * data.ti[i] * (data.params[data.s2s_index] * data.fact_ti[i] + data.one_s2s * data.ts_ti_ts[i] * data.inv_ts_denom[i])

    return 0.4 * data.params[data.s2f_index] * jw



# Extended 2 {S2f, tf, S2s, ts} or {tm, S2f, tf, S2s, ts}.
##########################################################

def calc_S2f_tf_S2s_ts_jw(data):
    """Spectral density function.

    Calculate the spectral density values for the extended model-free formula with the parameters
    {S2f, tf, S2s, ts} or the parameters {tm, S2f, tf, S2s, ts}.

    The model-free formula is:

                    _n_
                 2  \           /   S2f . S2s        (1 - S2f)(tf + ti)tf         S2f(1 - S2s)(ts + ti)ts  \ 
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------  +  ------------------------- |
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m
    """

    jw = data.ci[0] * data.ti[0] * (data.params[data.s2f_index] * data.params[data.s2s_index] * data.fact_ti[0] + data.one_s2f * data.tf_ti_tf[0] * data.inv_tf_denom[0] + data.s2f_s2 * data.ts_ti_ts[0] * data.inv_ts_denom[0])

    for i in xrange(1, data.num_indecies):
        jw = jw + data.ci[i] * data.ti[i] * (data.params[data.s2f_index] * data.params[data.s2s_index] * data.fact_ti[i] + data.one_s2f * data.tf_ti_tf[i] * data.inv_tf_denom[i] + data.s2f_s2 * data.ts_ti_ts[i] * data.inv_ts_denom[i])

    return 0.4 * jw




###############################
# Spectral density gradients. #
###############################

def create_djw_struct(data, calc_djw):
    """Function to create model-free spectral density gradients.

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
        dJ(w)     2  \        dti  /        1 - (w.ti)^2                         (te + ti)^2 - (w.te.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 . ----------------  +  (1 - S2) . te^2 ----------------------------- |
         dDj      5  /__      dDj  \      (1 + (w.ti)^2)^2                     ((te + ti)^2 + (w.te.ti)^2)^2 /
                     i=m


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
        dJ(w)     2  \        dti  /        1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  (S2f - S2) . ts^2 ----------------------------- |
         dDj      5  /__      dDj  \      (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m


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

        dJ(w)     2    /     S2s                (tf + ti).tf              (1 - S2s)(ts + ti).ts   \ 
        -----  =  - ti | ------------  -  -------------------------  +  ------------------------- |
        dS2f      5    \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /


        dJ(w)     2        /      1                 (ts + ti).ts        \ 
        -----  =  - ti.S2f | ------------  -  ------------------------- |
        dS2s      5        \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /


        dJ(w)     2                    (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - ti^2 . (1 - S2f) -----------------------------
         dtf      5                  ((tf + ti)^2 + (w.tf.ti)^2)^2


        dJ(w)     2                       (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - ti^2 . S2f(1 - S2s) -----------------------------
         dts      5                     ((ts + ti)^2 + (w.ts.ti)^2)^2


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

    for j in xrange(data.total_num_params):
        if calc_djw[j]:
            data.djw[:, :, j] = calc_djw[j](data)



# Original Dj partial derivative.
#################################

# {tm}

def calc_tm_djw_dDj(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the tm partial derivative of the original model-free
    formula with the single parameter {tm}.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \        dti  /   1 - (w.ti)^2   \ 
        -----  =  -   >  ci . ---  | ---------------- |
         dDj      5  /__      dDj  \ (1 + (w.ti)^2)^2 /
                     i=m
    """

    djw = data.ci[0] * data.dti[0] * data.fact_ti_djw_dti[0]

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.dti[i] * data.fact_ti_djw_dti[i]

    return 0.4 * djw


# {tm, S2}

def calc_tm_S2_djw_dDj(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the tm partial derivative of the original model-free
    formula with the parameters {tm, S2}.

    The model-free gradient is:

                       _n_
        dJ(w)     2    \        dti  /   1 - (w.ti)^2   \ 
        -----  =  - S2  >  ci . ---  | ---------------- |
         dDj      5    /__      dDj  \ (1 + (w.ti)^2)^2 /
                       i=m
    """

    djw = data.ci[0] * data.dti[0] * data.fact_ti_djw_dti[0]

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.dti[i] * data.fact_ti_djw_dti[i]

    return 0.4 * data.params[data.s2_index] * djw


# {tm, S2, te}

def calc_tm_S2_te_djw_dDj(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the tm partial derivative of the original model-free
    formula with the parameters {tm, S2, te}.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \        dti  /        1 - (w.ti)^2                         (te + ti)^2 - (w.te.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 . ----------------  +  (1 - S2) . te^2 ----------------------------- |
         dDj      5  /__      dDj  \      (1 + (w.ti)^2)^2                     ((te + ti)^2 + (w.te.ti)^2)^2 /
                     i=m
    """

    djw = data.ci[0] * data.dti[0] * (data.params[data.s2_index] * data.fact_ti_djw_dti[0] + data.one_s2 * data.fact_te_djw_dti[0])

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.dti[i] * (data.params[data.s2_index] * data.fact_ti_djw_dti[i] + data.one_s2 * data.fact_te_djw_dti[i])

    return 0.4 * djw



# Original Psij partial derivative.
###################################

# Please code me!!!



# Original S2 partial derivative.
#################################

# {S2} or {tm, S2}

def calc_S2_djw_dS2(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the original model-free
    formula with the single parameter {S2} or the parameters {tm, S2}.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \           /      1       \ 
        -----  =  -   >  ci . ti | ------------ |
         dS2      5  /__         \ 1 + (w.ti)^2 /
                     i=m
    """

    djw = data.ci[0] * data.ti[0] * data.fact_ti[0]

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.ti[i] * data.fact_ti[i]

    return 0.4 * djw


# {S2, te} or {tm, S2, te}

def calc_S2_te_djw_dS2(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the original model-free
    formula with the parameters {S2, te} or the parameters {tm, S2, te}.

    The model-free gradient is:

                     _n_
        dJ(w)     2  \           /      1                 (te + ti)te         \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |
         dS2      5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                     i=m
    """

    djw = data.ci[0] * data.ti[0] * (data.fact_ti[0] - data.te_ti_te[0] * data.inv_te_denom[0])

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.ti[i] * (data.fact_ti[i] - data.te_ti_te[i] * data.inv_te_denom[i])

    return 0.4 * djw



# Original te partial derivative.
#################################

# {S2, te} or {tm, S2, te}

def calc_S2_te_djw_dte(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the te partial derivative of the original model-free
    formula with the parameters {S2, te} or the parameters {tm, S2, te}.

    The model-free gradient is:

                             _n_
        dJ(w)     2          \                 (te + ti)^2 - (w.te.ti)^2
        -----  =  - (1 - S2)  >  ci . ti^2 . -----------------------------
         dte      5          /__             ((te + ti)^2 + (w.te.ti)^2)^2
                             i=m
    """

    djw = data.ci[0] * data.fact_djw_dte[0]

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.fact_djw_dte[i]

    return 0.4 * data.one_s2 * djw



# Extended Dj partial derivative.
#################################

# {tm, S2f, S2, ts}

def calc_tm_S2f_S2_ts_djw_dDj(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the tm partial derivative of the extended model-free
    formula with the parameters {tm, S2f, S2, ts}.

    The formula is:

                     _n_
        dJ(w)     2  \        dti  /        1 - (w.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 . ----------------  +  (S2f - S2) . ts^2 ----------------------------- |
         dDj      5  /__      dDj  \      (1 + (w.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m
    """

    djw = data.ci[0] * data.dti[0] * (data.params[data.s2_index] * data.fact_ti_djw_dti[0] + data.s2f_s2 * data.fact_ts_djw_dti[0])

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.dti[i] * (data.params[data.s2_index] * data.fact_ti_djw_dti[i] + data.s2f_s2 * data.fact_ts_djw_dti[i])

    return 0.4 * djw


# {tm, S2f, tf, S2, ts}

def calc_tm_S2f_tf_S2_ts_djw_dDj(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {tm, S2f, tf, S2, ts}.

    The formula is:

                     _n_
        dJ(w)     2  \        dti  /        1 - (w.ti)^2                          (tf + ti)^2 - (w.tf.ti)^2                           (ts + ti)^2 - (w.ts.ti)^2   \ 
        -----  =  -   >  ci . ---  | S2 . ----------------  +  (1 - S2f) . tf^2 -----------------------------  +  (S2f - S2) . ts^2 ----------------------------- |
         dDj      5  /__      dDj  \      (1 + (w.ti)^2)^2                      ((tf + ti)^2 + (w.tf.ti)^2)^2                       ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                     i=m
    """

    djw = data.ci[0] * data.dti[0] * (data.params[data.s2_index] * data.fact_ti_djw_dti[0] + data.one_s2f * data.fact_tf_djw_dti[0] + data.s2f_s2 * data.fact_ts_djw_dti[0])

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.dti[i] * (data.params[data.s2_index] * data.fact_ti_djw_dti[i] + data.one_s2f * data.fact_tf_djw_dti[i] + data.s2f_s2 * data.fact_ts_djw_dti[i])

    return 0.4 * djw



# Extended Psij partial derivative.
###################################

# Please code me!!!


# Extended S2 partial derivative.
#################################

# {S2f, S2, ts}, {tm, S2f, S2, ts}, {S2f, tf, S2, ts}, or {tm, S2f, tf, S2, ts}

def calc_S2f_S2_ts_djw_dS2(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2 partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} or the parameters {tm, S2f, S2, ts} or
    {S2f, tf, S2, ts} or {tm, S2f, tf, S2, ts}.

    The formula is:

                     _n_
        dJ(w)     2  \           /      1                 (ts + ti).ts        \ 
        -----  =  -   >  ci . ti | ------------  -  ------------------------- |
         dS2      5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    djw = data.ci[0] * data.ti[0] * (data.fact_ti[0] - data.ts_ti_ts[0] * data.inv_ts_denom[0])

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.ti[i] * (data.fact_ti[i] - data.ts_ti_ts[i] * data.inv_ts_denom[i])

    return 0.4 * djw



# Extended S2f partial derivative.
##################################

# {S2f, S2, ts} or {tm, S2f, S2, ts}

def calc_S2f_S2_ts_djw_dS2f(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} or the parameters {tm, S2f, S2, ts}.

    The formula is:

                     _n_
        dJ(w)     2  \           /       (ts + ti).ts        \ 
        -----  =  -   >  ci . ti | ------------------------- |
        dS2f      5  /__         \ (ts + ti)^2 + (w.ts.ti)^2 /
                     i=m
    """

    djw = data.ci[0] * data.ti[0] * data.ts_ti_ts[0] * data.inv_ts_denom[0]

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.ti[i] * data.ts_ti_ts[i] * data.inv_ts_denom[i]

    return 0.4 * djw


# {S2f, tf, S2, ts} or {tm, S2f, tf, S2, ts}

def calc_S2f_tf_S2_ts_djw_dS2f(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the S2f partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} or the parameters {tm, S2f, tf, S2, ts}.

    The formula is:

                       _n_
        dJ(w)       2  \           /       (tf + ti).tf                  (ts + ti).ts        \ 
        -----  =  - -   >  ci . ti | -------------------------  -  ------------------------- |
        dS2f        5  /__         \ (tf + ti)^2 + (w.tf.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=m
    """

    djw = data.ci[0] * data.ti[0] * (data.tf_ti_tf[0] * data.inv_tf_denom[0] - data.ts_ti_ts[0] * data.inv_ts_denom[0])

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.ti[i] * (data.tf_ti_tf[i] * data.inv_tf_denom[i] - data.ts_ti_ts[i] * data.inv_ts_denom[i])

    return -0.4 * djw



# Extended tf partial derivative.
#################################

# {S2f, tf, S2, ts} or {tm, S2f, tf, S2, ts}

def calc_S2f_tf_S2_ts_djw_dtf(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the tf partial derivative of the extended model-free
    formula with the parameters {S2f, tf, S2, ts} or the parameters {tm, S2f, tf, S2, ts}.

    The formula is:

                              _n_
        dJ(w)     2           \               (tf + ti)^2 - (w.tf.ti)^2
        -----  =  - (1 - S2f)  >  ci . ti^2 -----------------------------
         dtf      5           /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                              i=m
    """

    djw = data.ci[0] * data.fact_djw_dtf[0]

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.fact_djw_dtf[i]

    return 0.4 * data.one_s2f * djw



# Extended ts partial derivative.
#################################

# {S2f, S2, ts}, {tm, S2f, S2, ts}, {S2f, tf, S2, ts}, or {tm, S2f, tf, S2, ts}

def calc_S2f_S2_ts_djw_dts(data):
    """Spectral density gradient.

    Calculate the spectral desity values for the ts partial derivative of the extended model-free
    formula with the parameters {S2f, S2, ts} or the parameters {tm, S2f, S2, ts} or
    {S2f, tf, S2, ts} or {tm, S2f, tf, S2, ts}.

    The formula is:

                               _n_
        dJ(w)     2            \               (ts + ti)^2 - (w.ts.ti)^2
        -----  =  - (S2f - S2)  >  ci . ti^2 -----------------------------
         dts      5            /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                               i=m
    """

    djw = data.ci[0] * data.fact_djw_dts[0]

    for i in xrange(1, data.num_indecies):
        djw = djw + data.ci[i] * data.fact_djw_dts[i]

    return 0.4 * data.s2f_s2 * djw



# Extended 2 {S2f, S2s, ts}.
############################

def calc_S2f_S2s_ts_djw_dS2f(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity values for the S2f partial derivative of the extended
    model-free formula with the parameters S2f, S2s, and ts.

    The formula is:

        dJ(w)     2    /     S2s            (1 - S2s)(ts + tm).ts   \ 
        -----  =  - tm | ------------  +  ------------------------- |
        dS2f      5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    raise RelaxError, "Not coded yet."
    return data.two_fifths_tm * (data.params[data.s2s_index] * data.fact_tm + data.one_s2s * data.ts_tm_ts * data.inv_ts_denom)


def calc_S2f_S2s_ts_djw_dS2s(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity values for the S2s partial derivative of the extended
    model-free formula with the parameters S2f, S2s, and ts.

    The formula is:

        dJ(w)     2        /      1                 (ts + tm).ts        \ 
        -----  =  - tm.S2f | ------------  -  ------------------------- |
        dS2s      5        \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    raise RelaxError, "Not coded yet."
    return data.fact_djw_ds2s * data.params[data.s2f_index]


def calc_S2f_S2s_ts_djw_dts(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity values for the ts partial derivative of the extended
    model-free formula with the parameters S2f, S2s, and ts.

    The formula is:

        dJ(w)     2                       (ts + tm)^2 - (w.ts.tm)^2
        -----  =  - tm^2 . S2f(1 - S2s) -----------------------------
         dts      5                     ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    raise RelaxError, "Not coded yet."
    return data.fact_djw_dts * data.s2f_s2



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_S2f_tf_S2s_ts_djw_dS2f(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity values for the S2f partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2s, and ts.

    The formula is:

        dJ(w)     2    /     S2s                (tf + tm).tf              (1 - S2s)(ts + tm).ts   \ 
        -----  =  - tm | ------------  -  -------------------------  +  ------------------------- |
        dS2f      5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    raise RelaxError, "Not coded yet."
    return data.two_fifths_tm * (data.params[data.s2s_index] * data.fact_tm - data.tf_tm_tf * data.inv_tf_denom + data.one_s2s * data.ts_tm_ts * data.inv_ts_denom)


def calc_S2f_tf_S2s_ts_djw_dS2s(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity values for the S2s partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2s, and ts.

    The formula is:

        dJ(w)     2        /      1                 (ts + tm).ts        \ 
        -----  =  - tm.S2f | ------------  -  ------------------------- |
        dS2s      5        \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    raise RelaxError, "Not coded yet."
    return data.fact_djw_ds2s * data.params[data.s2f_index]


def calc_S2f_tf_S2s_ts_djw_dtf(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity values for the tf partial derivative of the extended
    model-free formula with the parameters S2f, tf, S2s, and ts.

    The formula is:

        dJ(w)     2                    (tf + tm)^2 - (w.tf.tm)^2
        -----  =  - tm^2 . (1 - S2f) -----------------------------
         dtf      5                  ((tf + tm)^2 + (w.tf.tm)^2)^2
    """

    raise RelaxError, "Not coded yet."
    return data.fact_djw_dtf * data.one_s2f


def calc_S2f_tf_S2s_ts_djw_dts(data):
    """Spectral density gradient.

    Calculate the isotropic spectral desity values for the ts partial derivative of the extended
    model-free formula with the parameters S2f, S2s, and ts.

    The formula is:

        dJ(w)     2                       (ts + tm)^2 - (w.ts.tm)^2
        -----  =  - tm^2 . S2f(1 - S2s) -----------------------------
         dts      5                     ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    raise RelaxError, "Not coded yet."
    return data.fact_djw_dts * data.s2f_s2




##############################
# Spectral density Hessians. #
##############################

def create_d2jw_struct(data, calc_d2jw):
    """Function to create model-free spectral density Hessians.

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

         d2J(w)
        -------  =  0
        dS2f**2


          d2J(w)      2    /      1                 (ts + tm).ts        \ 
        ---------  =  - tm | ------------  -  ------------------------- |
        dS2f.dS2s     5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


         d2J(w)        2        (tf + tm)^2 - (w.tf.tm)^2
        --------  =  - - tm^2 -----------------------------
        dS2f.dtf       5      ((tf + tm)^2 + (w.tf.tm)^2)^2


         d2J(w)      2                    (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 . (1 - S2s) -----------------------------
        dS2f.dts     5                  ((ts + tm)^2 + (w.ts.tm)^2)^2


         d2J(w)              d2J(w)
        -------  =  0   ,   --------  =  0
        dS2s**2             dS2s.dtf


         d2J(w)        2              (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - - tm^2 . S2f -----------------------------
        dS2s.dts       5            ((ts + tm)^2 + (w.ts.tm)^2)^2


        d2J(w)       4                  (tf + tm)^3 + 3.tm^3.tf.w^2.(tf + tm) - (w.tm)^4.tf^3
        ------  =  - - tm^2 . (1 - S2f) -----------------------------------------------------
        dtf**2       5                              ((tf + tm)^2 + (w.tf.tm)^2)^3


         d2J(w)
        -------  =  0
        dtf.dts


        d2J(w)       4                     (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . S2f(1 - S2s) -----------------------------------------------------
        dts**2       5                                 ((ts + tm)^2 + (w.ts.tm)^2)^3


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

    for j in xrange(data.total_num_params):
        for k in xrange(j + 1):
            if calc_d2jw[j][k]:
                data.d2jw[:, :, j, k] = calc_d2jw[j][k](data)
                # Make the Hessian symmetric.
                if j != k:
                    data.d2jw[:, :, k, j] = data.d2jw[:, :, j, k]



# Original Dj - Dk partial derivative.
######################################

# {tm}

def calc_tm_d2jw_dDj2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dj double partial derivative of the original
    model-free formula with the single parameter {tm}.

    The model-free Hessian is:

                         _n_     /                         dti   dti                     d2ti   \ 
         d2J(w)       2  \       | 2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) ------- |
        -------  =  - -   >  ci  |                         dDj   dDk                    dDj.dDk |
        dDj.dDk       5  /__     | ------------------------------------------------------------ |
                         i=m     \                    (1 + (w.ti)^2)^3                          /
    """

    d2jw = data.ci[0] * (2 * data.ti[0] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[0]) * data.dti[0] * data.dti[0] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[0]) * data.fact_ti[0]**3

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * (2 * data.ti[i] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[i]) * data.dti[i] * data.dti[i] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[i]) * data.fact_ti[i]**3

    return -0.4 * d2jw


# {tm, S2}

def calc_tm_S2_d2jw_dDj2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dj double partial derivative of the original
    model-free formula with the parameters {tm, S2}.

    The model-free Hessian is:

                           _n_     /                         dti   dti                     d2ti   \ 
         d2J(w)       2    \       | 2.ti.w^2.(3 - (w.ti)^2) --- . ---  -  (1 - (w.ti)^4) ------- |
        -------  =  - - S2  >  ci  |                         dDj   dDk                    dDj.dDk |
        dDj.dDk       5    /__     | ------------------------------------------------------------ |
                           i=m     \                    (1 + (w.ti)^2)^3                          /
    """

    d2jw = data.ci[0] * (2 * data.ti[0] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[0]) * data.dti[0] * data.dti[0] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[0]) * data.fact_ti[0]**3

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * (2 * data.ti[i] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[i]) * data.dti[i] * data.dti[i] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[i]) * data.fact_ti[i]**3

    return -0.4 * data.params[data.s2_index] * d2jw


# {tm, S2, te}

def calc_tm_S2_te_d2jw_dtDj(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dj double partial derivative of the original
    model-free formula with the parameters {tm, S2, te}.

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
    fact_ti = data.params[data.s2_index] * (2 * data.ti[0] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[0]) * data.dti[0] * data.dti[0] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[0]) * data.fact_ti[0]**3

    # te.
    fact_te = 2.0 * (data.te_ti[0]**3 + 3.0 * data.frq_sqrd_list * data.params[data.te_index]**3 * data.params[data.ti_index] * data.te_ti[0] - (data.frq_list * data.params[data.te_index])**4 * data.params[data.ti_index]**3) * data.dti[0] * data.dti[0]  +  (data.te_ti[0]**4 - data.w_te_ti_sqrd[0]**2) * data.d2ti[0]
    fact_te = data.one_s2 * data.params[data.te_index]**2 * fact_te * data.inv_te_denom[0]**3

    d2jw = data.ci[0] + (fact_ti + fact_te)

    for i in xrange(1, data.num_indecies):
        # ti.
        fact_ti = data.params[data.s2_index] * (2 * data.ti[i] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[i]) * data.dti[i] * data.dti[i] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[i]) * data.fact_ti[i]**3

        # te.
        fact_te = 2.0 * (data.te_ti[i]**3 + 3.0 * data.frq_sqrd_list * data.params[data.te_index]**3 * data.params[data.ti_index] * data.te_ti[i] - (data.frq_list * data.params[data.te_index])**4 * data.params[data.ti_index]**3) * data.dti[i] * data.dti[i]  +  (data.te_ti[i]**4 - data.w_te_ti_sqrd[i]**2) * data.d2ti[i]
        fact_te = data.one_s2 * data.params[data.te_index]**2 * fact_te * data.inv_te_denom[i]**3

        d2jw = d2jw + data.ci[i] + (fact_ti + fact_te)

    return -0.4 * d2jw



# Original Dj - Psij partial derivative.
########################################

# Please code me!!!



# Original Dj - S2 partial derivative.
######################################

# {tm, S2}

def calc_tm_S2_d2jw_dDjdS2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2 double partial derivative of the original
    model-free formula with the parameters {tm, S2}.

    The model-free Hessian is:

                       _n_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2   \ 
        -------  =  -   >  ci . ---  | ---------------- |
        dDj.dS2     5  /__      dDj  \ (1 + (w.ti)^2)^2 /
                       i=m
    """

    d2jw = data.ci[0] * data.dti[0] * data.fact_ti_djw_dti[0]

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.dti[i] * data.fact_ti_djw_dti[i]

    return 0.4 * d2jw


# {tm, S2, te}

def calc_tm_S2_te_d2jw_dDjdS2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the tm - S2 double partial derivative of the original
    model-free formula with the parameters {tm, S2, te}.

    The model-free Hessian is:

                       _n_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2              (te + ti)^2 - (w.te.ti)^2   \ 
        -------  =  -   >  ci . ---  | ----------------  -  te^2 ----------------------------- |
        dDj.dS2     5  /__      dDj  \ (1 + (w.ti)^2)^2          ((te + ti)^2 + (w.te.ti)^2)^2 /
                       i=m
    """

    d2jw = data.ci[0] * data.dti[0] * (data.fact_ti_djw_dti[0] - data.fact_te_djw_dti[0])

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.dti[i] * (data.fact_ti_djw_dti[i] - data.fact_te_djw_dti[i])

    return 0.4 * d2jw



# Original Dj - te partial derivative.
#######################################

# {tm, S2, te}

def calc_tm_S2_te_d2jw_dDjdte(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the tm - te double partial derivative of the
    original model-free formula with the parameters tm, S2, and te.

    The model-free Hessian is:

                                    _n_
         d2J(w)     4               \        dti                   (te + ti)^2 - 3(w.te.ti)^2
        -------  =  - (1 - S2) . te  >  ci . --- . ti . (te + ti) -----------------------------
        dDj.dte     5               /__      dDj                  ((te + ti)^2 + (w.te.ti)^2)^3
                                    i=m
    """

    d2jw = data.ci[0] * data.dti[0] * data.params[data.ti_index] * data.te_ti[0] * (data.te_ti_sqrd[0] - 3.0 * data.w_te_ti_sqrd[0]) * data.inv_te_denom[0]**3

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.dti[i] * data.params[data.ti_index] * data.te_ti[i] * (data.te_ti_sqrd[i] - 3.0 * data.w_te_ti_sqrd[i]) * data.inv_te_denom[i]**3

    return 0.8 * data.one_s2 * data.params[data.te_index] * d2jw



# Original Psij - ? partial derivative.
#######################################

# Please code me!



# Original S2 - te partial derivative.
######################################

# {S2, te} and {tm, S2, te}

def calc_S2_te_d2jw_dS2dte(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2 - te double partial derivative of the original
    model-free formula with the parameters {S2, te} or the parameters {tm, S2, te}.

    The model-free Hessian is:

                        _n_
         d2J(w)       2 \               (te + ti)^2 - (w.te.ti)^2
        -------  =  - -  >  ci . ti^2 -----------------------------
        dS2.dte       5 /__           ((te + ti)^2 + (w.te.ti)^2)^2
                        i=m
    """

    d2jw = data.ci[0] * data.fact_djw_dte[0]

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.fact_djw_dte[i]

    return -0.4 * d2jw



# Original te - te partial derivative.
######################################

# {S2, te}

def calc_S2_te_d2jw_dte2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the te - te double partial derivative of the original
    model-free formula with the parameters {S2, te}.

    The model-free Hessian is:

                                _n_
        d2J(w)       4          \             (te + ti)^3 + 3.w^2.ti^3.te.(te + ti) - (w.ti)^4.te^3
        ------  =  - - (1 - S2)  >  ci . ti^2 -----------------------------------------------------
        dte**2       5          /__                        ((te + ti)^2 + (w.te.ti)^2)^3
                                i=m
    """

    num = data.te_ti[0]**3 + 3.0 * data.diff_params[0]**3 * data.params[data.te_index] * data.frq_sqrd_list * data.te_ti[0] - data.w_ti_sqrd[0]**2 * data.params[data.te_index]**3
    d2jw = data.ci[0] * data.diff_params[0]**2 * num * data.inv_te_denom[0]**3

    for i in xrange(1, data.num_indecies):
        num = data.te_ti[i]**3 + 3.0 * data.diff_params[i]**3 * data.params[data.te_index] * data.frq_sqrd_list * data.te_ti[i] - data.w_ti_sqrd[i]**2 * data.params[data.te_index]**3
        d2jw = d2jw + data.ci[i] * data.diff_params[i]**2 * num * data.inv_te_denom[i]**3

    return -0.8 * data.one_s2 * d2jw


# {tm, S2, te}

def calc_tm_S2_te_d2jw_dte2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the te - te double partial derivative of the original
    model-free formula with the parameters {tm, S2, te}.

    The model-free Hessian is:

                                _n_
        d2J(w)       4          \             (te + ti)^3 + 3.w^2.ti^3.te.(te + ti) - (w.ti)^4.te^3
        ------  =  - - (1 - S2)  >  ci . ti^2 -----------------------------------------------------
        dte**2       5          /__                        ((te + ti)^2 + (w.te.ti)^2)^3
                                i=m
    """

    num = data.te_ti[0]**3 + 3.0 * data.params[data.tm_index]**3 * data.params[data.te_index] * data.frq_sqrd_list * data.te_ti[0] - data.w_ti_sqrd[0]**2 * data.params[data.te_index]**3
    d2jw = data.ci[0] * data.diff_params[0]**2 * num * data.inv_te_denom[0]**3

    for i in xrange(1, data.num_indecies):
        num = data.te_ti[i]**3 + 3.0 * data.params[data.tm_index]**3 * data.params[data.te_index] * data.frq_sqrd_list * data.te_ti[i] - data.w_ti_sqrd[i]**2 * data.params[data.te_index]**3
        d2jw = d2jw + data.ci[i] * data.diff_params[i]**2 * num * data.inv_te_denom[i]**3

    return -0.8 * data.one_s2 * d2jw



# Extended Dj - Dk partial derivative.
######################################

# {tm, S2f, S2, ts}

def calc_tm_S2f_S2_ts_d2jw_dDj2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dj double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, S2, ts}.

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
    fact_ti = data.params[data.s2_index] * (2 * data.ti[0] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[0]) * data.dti[0] * data.dti[0] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[0]) * data.fact_ti[0]**3

    # ts.
    fact_ts = 2.0 * (data.ts_ti[0]**3 + 3.0 * data.frq_sqrd_list * data.params[data.ts_index]**3 * data.params[data.ti_index] * data.ts_ti[0] - (data.frq_list * data.params[data.ts_index])**4 * data.params[data.ti_index]**3) * data.dti[0] * data.dti[0]  +  (data.ts_ti[0]**4 - data.w_ts_ti_sqrd[0]**2) * data.d2ti[0]
    fact_ts = data.s2f_s2 * data.params[data.ts_index]**2 * fact_ts * data.inv_ts_denom[0]**3

    d2jw = data.ci[0] * (fact_ti + fact_ts)

    for i in xrange(1, data.num_indecies):
        # ti.
        fact_ti = data.params[data.s2_index] * (2 * data.ti[i] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[i]) * data.dti[i] * data.dti[i] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[i]) * data.fact_ti[i]**3

        # ts.
        fact_ts = 2.0 * (data.ts_ti[i]**3 + 3.0 * data.frq_sqrd_list * data.params[data.ts_index]**3 * data.params[data.ti_index] * data.ts_ti[i] - (data.frq_list * data.params[data.ts_index])**4 * data.params[data.ti_index]**3) * data.dti[i] * data.dti[i]  +  (data.ts_ti[i]**4 - data.w_ts_ti_sqrd[i]**2) * data.d2ti[i]
        fact_ts = data.s2f_s2 * data.params[data.ts_index]**2 * fact_ts * data.inv_ts_denom[i]**3

        d2jw = d2jw + data.ci[i] * (fact_ti + fact_ts)

    return -0.4 * d2jw


# {tm, S2f, tf, S2, ts}

def calc_tm_S2f_tf_S2_ts_d2jw_dDj2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - Dj double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, tf, S2, ts}.

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
    fact_ti = data.params[data.s2_index] * (2 * data.ti[0] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[0]) * data.dti[0] * data.dti[0] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[0]) * data.fact_ti[0]**3

    # tf.
    fact_tf = 2.0 * (data.tf_ti[0]**3 + 3.0 * data.frq_sqrd_list * data.params[data.tf_index]**3 * data.params[data.ti_index] * data.tf_ti[0] - (data.frq_list * data.params[data.tf_index])**4 * data.params[data.ti_index]**3) * data.dti[0] * data.dti[0]  +  (data.tf_ti[0]**4 - data.w_tf_ti_sqrd[0]**2) * data.d2ti[0]
    fact_tf = data.one_s2f * data.params[data.tf_index]**2 * fact_tf * data.inv_tf_denom[0]**3

    # ts.
    fact_ts = 2.0 * (data.ts_ti[0]**3 + 3.0 * data.frq_sqrd_list * data.params[data.ts_index]**3 * data.params[data.ti_index] * data.ts_ti[0] - (data.frq_list * data.params[data.ts_index])**4 * data.params[data.ti_index]**3) * data.dti[0] * data.dti[0]  +  (data.ts_ti[0]**4 - data.w_ts_ti_sqrd[0]**2) * data.d2ti[0]
    fact_ts = data.s2f_s2 * data.params[data.ts_index]**2 * fact_ts * data.inv_ts_denom[0]**3

    d2jw = data.ci[0] * (fact_ti + fact_tf + fact_ts)

    for i in xrange(1, data.num_indecies):
        # ti.
        fact_ti = data.params[data.s2_index] * (2 * data.ti[i] * data.frq_sqrd_list * (3.0 - data.w_ti_sqrd[i]) * data.dti[i] * data.dti[i] - (1.0 - data.frq_sqrd_list**2) * data.d2ti[i]) * data.fact_ti[i]**3

        # tf.
        fact_tf = 2.0 * (data.tf_ti[i]**3 + 3.0 * data.frq_sqrd_list * data.params[data.tf_index]**3 * data.params[data.ti_index] * data.tf_ti[i] - (data.frq_list * data.params[data.tf_index])**4 * data.params[data.ti_index]**3) * data.dti[i] * data.dti[i]  +  (data.tf_ti[i]**4 - data.w_tf_ti_sqrd[i]**2) * data.d2ti[i]
        fact_tf = data.one_s2f * data.params[data.tf_index]**2 * fact_tf * data.inv_tf_denom[i]**3

        # ts.
        fact_ts = 2.0 * (data.ts_ti[i]**3 + 3.0 * data.frq_sqrd_list * data.params[data.ts_index]**3 * data.params[data.ti_index] * data.ts_ti[i] - (data.frq_list * data.params[data.ts_index])**4 * data.params[data.ti_index]**3) * data.dti[i] * data.dti[i]  +  (data.ts_ti[i]**4 - data.w_ts_ti_sqrd[i]**2) * data.d2ti[i]
        fact_ts = data.s2f_s2 * data.params[data.ts_index]**2 * fact_ts * data.inv_ts_denom[i]**3

        d2jw = d2jw + data.ci[i] * (fact_ti + fact_tf + fact_ts)

    return -0.4 * d2jw



# Extended Dj - Psij partial derivative.
########################################

# Please code me!!!



# Extended Dj - S2 partial derivative.
######################################

# {tm, S2f, S2, ts} or {tm, S2f, tf, S2, ts}

def calc_tm_S2f_S2_ts_d2jw_dDjdS2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2 double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, S2, ts} or the parameters 
    {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                       _n_
         d2J(w)     2  \        dti  /   1 - (w.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        -------  =  -   >  ci . ---  | ----------------  -  ts^2 ----------------------------- |
        dDj.dS2     5  /__      dDj  \ (1 + (w.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                       i=m
    """

    d2jw = data.ci[0] * data.dti[0] * (data.fact_ti_djw_dti[0] - data.fact_ts_djw_dti[0])

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.dti[i] * (data.fact_ti_djw_dti[i] - data.fact_ts_djw_dti[i])

    return 0.4 * d2jw



# Extended Dj - S2f partial derivative.
#######################################

# {tm, S2f, S2, ts}

def calc_tm_S2f_S2_ts_d2jw_dDjdS2f(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2f double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, S2, ts}.

    The model-free Hessian is:

                        _n_
         d2J(w)      2  \        dti  /        (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  -   >  ci . ---  | ts^2 ----------------------------- |
        dDj.dS2f     5  /__      dDj  \      ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                        i=m
    """

    d2jw = data.ci[0] * data.dti[0] * data.fact_ts_djw_dti[0]

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.dti[i] * data.fact_ts_djw_dti[i]

    return 0.4 * d2jw


# {tm, S2f, tf, S2, ts}

def calc_tm_S2f_tf_S2_ts_d2jw_dDjdS2f(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - S2f double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                          _n_
         d2J(w)        2  \        dti  /        (tf + ti)^2 - (w.tf.ti)^2              (ts + ti)^2 - (w.ts.ti)^2   \ 
        --------  =  - -   >  ci . ---  | tf^2 -----------------------------  -  ts^2 ----------------------------- |
        dDj.dS2f       5  /__      dDj  \      ((tf + ti)^2 + (w.tf.ti)^2)^2          ((ts + ti)^2 + (w.ts.ti)^2)^2 /
                          i=m
    """

    d2jw = data.ci[0] * data.dti[0] * (data.fact_tf_djw_dti[0] - data.fact_ts_djw_dti[0])

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.dti[i] * (data.fact_tf_djw_dti[i] - data.fact_ts_djw_dti[i])

    return -0.4 * d2jw



# Extended Dj - tf partial derivative.
######################################

# {tm, S2f, tf, S2, ts}

def calc_tm_S2f_tf_S2_ts_d2jw_dDjdtf(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the Dj - tf double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                                     _n_
         d2J(w)     4                \        dti                   (tf + ti)^2 - 3(w.tf.ti)^2
        -------  =  - (1 - S2f) . tf  >  ci . --- . ti . (tf + ti) -----------------------------
        dDj.dtf     5                /__      dDj                  ((tf + ti)^2 + (w.tf.ti)^2)^3
                                     i=m
    """

    d2jw = data.ci[0] * data.dti[0]* data.params[data.ti_index] * data.tf_ti[0] * (data.tf_ti_sqrd[0] - 3.0 * data.w_tf_ti_sqrd[0]) * data.inv_tf_denom[0]**3

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.dti[i]* data.params[data.ti_index] * data.tf_ti[i] * (data.tf_ti_sqrd[i] - 3.0 * data.w_tf_ti_sqrd[i]) * data.inv_tf_denom[i]**3

    return 0.8 * data.one_s2f * data.params[data.tf_index] * d2jw



# Extended Dj - ts partial derivative.
######################################

# {tm, S2f, S2, ts} or {tm, S2f, tf, S2, ts}

def calc_tm_S2f_S2_ts_d2jw_dDjdts(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the tm - ts double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, S2, ts} or the parameters
    {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                                      _n_
         d2J(w)     4                 \        dti                   (ts + ti)^2 - 3(w.ts.ti)^2
        -------  =  - (S2f - S2) . ts  >  ci . --- . ti . (ts + ti) -----------------------------
        dDj.dts     5                 /__      dDj                  ((ts + ti)^2 + (w.ts.ti)^2)^3
                                      i=m
    """

    d2jw = data.ci[0] * data.dti[0]* data.params[data.ti_index] * data.ts_ti[0] * (data.ts_ti_sqrd[0] - 3.0 * data.w_ts_ti_sqrd[0]) * data.inv_ts_denom[0]**3

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.dti[i]* data.params[data.ti_index] * data.ts_ti[i] * (data.ts_ti_sqrd[i] - 3.0 * data.w_ts_ti_sqrd[i]) * data.inv_ts_denom[i]**3

    return 0.8 * data.s2f_s2 * data.params[data.ts_index] * d2jw



# Extended Psij - ? partial derivative.
#######################################

# Please code me!!!



# Extended S2 - ts partial derivative.
######################################

# {S2f, S2, ts}, {S2f, tf, S2, ts}, {tm, S2f, S2, ts}, or {tm, S2f, tf, S2, ts}

def calc_S2f_S2_ts_d2jw_dS2dts(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2 - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts}, {S2f, tf, S2, ts}, {tm, S2f, S2, ts}, or
    {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                         _n_
         d2J(w)       2  \               (ts + ti)^2 - (w.ts.ti)^2
        -------  =  - -   >  ci . ti^2 -----------------------------
        dS2.dts       5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                         i=m
    """

    d2jw = data.ci[0] * data.fact_djw_dts[0]

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.fact_djw_dts[i]

    return -0.4 * d2jw



# Extended S2f - tf partial derivative.
#######################################

# {S2f, tf, S2, ts} or {tm, S2f, tf, S2, ts}

def calc_S2f_tf_S2_ts_d2jw_dS2fdtf(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2f - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts} or the parameters
    {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                          _n_
         d2J(w)        2  \               (tf + ti)^2 - (w.tf.ti)^2
        --------  =  - -   >  ci . ti^2 -----------------------------
        dS2f.dtf       5  /__           ((tf + ti)^2 + (w.tf.ti)^2)^2
                          i=m
    """

    d2jw = data.ci[0] * data.fact_djw_dtf[0]

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.fact_djw_dtf[i]

    return -0.4 * d2jw



# Extended S2f - ts partial derivative.
#######################################

# {S2f, S2, ts}, {S2f, tf, S2, ts}, {tm, S2f, S2, ts}, or {tm, S2f, tf, S2, ts}

def calc_S2f_S2_ts_d2jw_dS2fdts(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the S2f - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts}, {S2f, tf, S2, ts}, {tm, S2f, S2, ts}, or
    {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                        _n_
         d2J(w)      2  \               (ts + ti)^2 - (w.ts.ti)^2
        --------  =  -   >  ci . ti^2 -----------------------------
        dS2f.dts     5  /__           ((ts + ti)^2 + (w.ts.ti)^2)^2
                        i=m
    """

    d2jw = data.ci[0] * data.fact_djw_dts[0]

    for i in xrange(1, data.num_indecies):
        d2jw = d2jw + data.ci[i] * data.fact_djw_dts[i]

    return 0.4 * d2jw



# Extended tf - tf partial derivative.
#######################################

# {S2f, tf, S2, ts}

def calc_S2f_tf_S2_ts_d2jw_dtf2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the tf - tf double partial derivative of the extended
    model-free formula with the parameters {S2f, tf, S2, ts}.

    The model-free Hessian is:

                                 _n_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=m
    """

    num = data.tf_ti[0]**3 + 3.0 * data.diff_params[0]**3 * data.params[data.tf_index] * data.frq_sqrd_list * data.tf_ti[0] - data.w_ti_sqrd[0]**2 * data.params[data.tf_index]**3
    d2jw = data.ci[0] * data.diff_params[0]**2 * num * data.inv_tf_denom[0]**3

    for i in xrange(1, data.num_indecies):
        num = data.tf_ti[i]**3 + 3.0 * data.diff_params[i]**3 * data.params[data.tf_index] * data.frq_sqrd_list * data.tf_ti[i] - data.w_ti_sqrd[i]**2 * data.params[data.tf_index]**3
        d2jw = d2jw + data.ci[i] * data.diff_params[i]**2 * num * data.inv_tf_denom[i]**3

    return -0.8 * data.one_s2f * d2jw


# {tm, S2f, tf, S2, ts}

def calc_tm_S2f_tf_S2_ts_d2jw_dtf2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the tf - tf double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                                 _n_
        d2J(w)       4           \             (tf + ti)^3 + 3.w^2.ti^3.tf.(tf + ti) - (w.ti)^4.tf^3
        ------  =  - - (1 - S2f)  >  ci . ti^2 -----------------------------------------------------
        dtf**2       5           /__                        ((tf + ti)^2 + (w.tf.ti)^2)^3
                                 i=m
    """

    num = data.tf_ti[0]**3 + 3.0 * data.params[data.tm_index]**3 * data.params[data.tf_index] * data.frq_sqrd_list * data.tf_ti[0] - data.w_ti_sqrd[0]**2 * data.params[data.tf_index]**3
    d2jw = data.ci[0] * data.diff_params[0]**2 * num * data.inv_tf_denom[0]**3

    for i in xrange(1, data.num_indecies):
        num = data.tf_ti[i]**3 + 3.0 * data.params[data.tm_index]**3 * data.params[data.tf_index] * data.frq_sqrd_list * data.tf_ti[i] - data.w_ti_sqrd[i]**2 * data.params[data.tf_index]**3
        d2jw = d2jw + data.ci[i] * data.diff_params[i]**2 * num * data.inv_tf_denom[i]**3

    return -0.8 * data.one_s2f * d2jw



# Extended ts - ts partial derivative.
#######################################

# {S2f, S2, ts} or {S2f, tf, S2, ts}

def calc_S2f_S2_ts_d2jw_dts2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the ts - ts double partial derivative of the extended
    model-free formula with the parameters {S2f, S2, ts} or the parameters {S2f, tf, S2, ts}.

    The model-free Hessian is:

                                  _n_
        d2J(w)       4            \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - (S2f - S2)  >  ci . ti^2 -----------------------------------------------------
        dts**2       5            /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                  i=m
    """

    num = data.ts_ti[0]**3 + 3.0 * data.diff_params[0]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_ti[0] - data.w_ti_sqrd[0]**2 * data.params[data.ts_index]**3
    d2jw = data.ci[0] * data.diff_params[0]**2 * num * data.inv_ts_denom[0]**3

    for i in xrange(1, data.num_indecies):
        num = data.ts_ti[i]**3 + 3.0 * data.diff_params[i]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_ti[i] - data.w_ti_sqrd[i]**2 * data.params[data.ts_index]**3
        d2jw = d2jw + data.ci[i] * data.diff_params[i]**2 * num * data.inv_ts_denom[i]**3

    return -0.8 * data.s2f_s2 * d2jw


# {tm, S2f, S2, ts} or {tm, S2f, tf, S2, ts}

def calc_tm_S2f_S2_ts_d2jw_dts2(data):
    """Spectral density Hessian.

    Calculate the spectral desity values for the ts - ts double partial derivative of the extended
    model-free formula with the parameters {tm, S2f, S2, ts} or the parameters
    {tm, S2f, tf, S2, ts}.

    The model-free Hessian is:

                                  _n_
        d2J(w)       4            \             (ts + ti)^3 + 3.w^2.ti^3.ts.(ts + ti) - (w.ti)^4.ts^3
        ------  =  - - (S2f - S2)  >  ci . ti^2 -----------------------------------------------------
        dts**2       5            /__                        ((ts + ti)^2 + (w.ts.ti)^2)^3
                                  i=m
    """

    num = data.ts_ti[0]**3 + 3.0 * data.params[data.ti_index]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_ti[0] - data.w_ti_sqrd[0]**2 * data.params[data.ts_index]**3
    d2jw = data.ci[0] * data.diff_params[0]**2 * num * data.inv_ts_denom[0]**3

    for i in xrange(1, data.num_indecies):
        num = data.ts_ti[i]**3 + 3.0 * data.params[data.ti_index]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_ti[i] - data.w_ti_sqrd[i]**2 * data.params[data.ts_index]**3
        d2jw = d2jw + data.ci[i] * data.diff_params[i]**2 * num * data.inv_ts_denom[i]**3

    return -0.8 * data.s2f_s2 * d2jw



# Extended 2 {S2f, S2s, ts}.
############################

def calc_S2f_S2s_ts_d2jw_dS2fdS2s(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the S2f/S2s double partial derivative of the
    extended model-free formula with the parameters S2f, S2s, and ts.

    The model-free Hessian is:

          d2J(w)      2    /      1                 (ts + tm).ts        \ 
        ---------  =  - tm | ------------  -  ------------------------- |
        dS2f.dS2s     5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.fact_djw_ds2s


def calc_S2f_S2s_ts_d2jw_dS2fdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the S2f/ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2s, and ts.

    The model-free Hessian is:

         d2J(w)      2                    (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 . (1 - S2s) -----------------------------
        dS2f.dts     5                  ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts * data.one_s2s


def calc_S2f_S2s_ts_d2jw_dS2sdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the S2s/ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2s, and ts.

    The model-free Hessian is:

         d2J(w)        2              (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - - tm^2 . S2f -----------------------------
        dS2s.dts       5            ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return -data.fact_djw_dts * data.params[data.s2f_index]


def calc_S2f_S2s_ts_d2jw_dts2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the ts/ts double partial derivative of the
    extended model-free formula with the parameters S2f, S2s, and ts.

    The model-free Hessian is:

        d2J(w)       4                     (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . S2f(1 - S2s) -----------------------------------------------------
        dts**2       5                                 ((ts + tm)^2 + (w.ts.tm)^2)^3
    """

    num = data.ts_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_tm - data.w_tm_sqrd**2 * data.params[data.ts_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.s2f_s2 * num * data.inv_ts_denom**3



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_S2f_tf_S2s_ts_d2jw_dS2fdtf(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the S2f/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

         d2J(w)        2        (tf + tm)^2 - (w.tf.tm)^2
        --------  =  - - tm^2 -----------------------------
        dS2f.dtf       5      ((tf + tm)^2 + (w.tf.tm)^2)^2
    """

    return -data.fact_djw_dtf



def calc_S2f_tf_S2s_ts_d2jw_dS2fdS2s(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the S2f/S2s double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

          d2J(w)      2    /      1                 (ts + tm).ts        \ 
        ---------  =  - tm | ------------  -  ------------------------- |
        dS2f.dS2s     5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    return data.fact_djw_ds2s

def calc_S2f_tf_S2s_ts_d2jw_dS2fdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the S2f/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

         d2J(w)      2                    (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - tm^2 . (1 - S2s) -----------------------------
        dS2f.dts     5                  ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return data.fact_djw_dts * data.one_s2s


def calc_S2f_tf_S2s_ts_d2jw_dS2sdts(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the S2s/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

         d2J(w)        2              (ts + tm)^2 - (w.ts.tm)^2
        --------  =  - - tm^2 . S2f -----------------------------
        dS2s.dts       5            ((ts + tm)^2 + (w.ts.tm)^2)^2
    """

    return -data.fact_djw_dts * data.params[data.s2f_index]


def calc_S2f_tf_S2s_ts_d2jw_dtf2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the ts/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

        d2J(w)       4                  (tf + tm)^3 + 3.tm^3.tf.w^2.(tf + tm) - (w.tm)^4.tf^3
        ------  =  - - tm^2 . (1 - S2f) -----------------------------------------------------
        dtf**2       5                              ((tf + tm)^2 + (w.tf.tm)^2)^3
    """

    num = data.tf_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.tf_index] * data.frq_sqrd_list * data.tf_tm - data.w_tm_sqrd**2 * data.params[data.tf_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.one_s2f * num * data.inv_tf_denom**3


def calc_S2f_tf_S2s_ts_d2jw_dts2(data):
    """Spectral density Hessian.

    Calculate the isotropic spectral desity values for the ts/ts double partial derivative of the
    extended model-free formula with the parameters S2f, tf, S2s, and ts.

    The model-free Hessian is:

        d2J(w)       4                     (ts + tm)^3 + 3.tm^3.ts.w^2.(ts + tm) - (w.tm)^4.ts^3
        ------  =  - - tm^2 . S2f(1 - S2s) -----------------------------------------------------
        dts**2       5                                 ((ts + tm)^2 + (w.ts.tm)^2)^3
    """

    num = data.ts_tm**3 + 3.0 * data.diff_params[0]**3 * data.params[data.ts_index] * data.frq_sqrd_list * data.ts_tm - data.w_tm_sqrd**2 * data.params[data.ts_index]**3
    return -2.0*data.two_fifths_tm_sqrd * data.s2f_s2 * num * data.inv_ts_denom**3
