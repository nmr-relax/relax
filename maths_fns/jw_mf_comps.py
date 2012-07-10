###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax.  If not, see <http://www.gnu.org/licenses/>.              #
#                                                                             #
###############################################################################


############################
# Spectral density values. #
############################


# Original {S2, te}.
####################

def calc_S2_te_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the original model-free formula with
    the parameters {S2, te}.

    The model-free formula is::

                    _n_
                 2  \           /      S2             (1 - S2)(te + ti)te    \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |.
                 5  /__         \ 1 + (w.ti)^2     (te + ti)^2 + (w.te.ti)^2 /
                    i=m

    Replicated calculations are::

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation),

        te_ti = te + ti,
        te_ti_te = (te + ti).te.


    Calculations which are replicated in the gradient equations are::

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation),

        one_s2 = 1 - S2,

        te_ti_sqrd = (te + ti)^2,
        w_te_ti_sqrd = (w.te.ti)^2,

                           (te + ti)te
        fact_te  =  -------------------------.
                    (te + ti)^2 + (w.te.ti)^2

    """

    # Order parameter factors.
    data.one_s2 = 1.0 - params[data.s2_i]

    # Internal correlation time, te, factors.
    data.te_ti =        params[data.te_i] + data.ti
    data.te_ti_te =     data.te_ti * params[data.te_i]
    data.te_ti_sqrd =   data.te_ti**2

    data.w_te_ti_sqrd = data.w_ti_sqrd * params[data.te_i]**2
    data.inv_te_denom = 1.0 / (data.te_ti_sqrd + data.w_te_ti_sqrd)
    data.fact_te =      data.te_ti_te * data.inv_te_denom



# Extended {S2f, S2, ts}.
#########################

def calc_S2f_S2_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {S2f, S2, ts}.

    The model-free formula is::

                    _n_
                 2  \           /      S2            (S2f - S2)(ts + ti)ts   \ 
        J(w)  =  -   >  ci . ti | ------------  +  ------------------------- |.
                 5  /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                    i=m

    Replicated calculations are::

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation),

        ts_ti = ts + ti,
        ts_ti_ts = (ts + ti).ts.


    Calculations which are replicated in the gradient equations are::

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation),

        s2f_s2 = S2f - S2,

        ts_ti_sqrd = (ts + ti)^2,
        w_ts_ti_sqrd = (w.ts.ti)^2,
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2),

                           (ts + ti)ts
        fact_ts  =  -------------------------.
                    (ts + ti)^2 + (w.ts.ti)^2

    """

    # Order parameter factors.
    data.s2f_s2 = params[data.s2f_i] - params[data.s2_i]

    # Internal correlation time, ts, factors.
    data.ts_ti =        params[data.ts_i] + data.ti
    data.ts_ti_ts =     data.ts_ti * params[data.ts_i]
    data.ts_ti_sqrd =   data.ts_ti**2

    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_i]**2
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)
    data.fact_ts =      data.ts_ti_ts * data.inv_ts_denom



# Extended 2 {S2f, S2s, ts}.
############################

def calc_S2f_S2s_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {S2f, S2s, ts}.

    The model-free formula is::

                       _n_
                 2     \           /      S2s           (1 - S2s)(ts + ti)ts    \ 
        J(w)  =  - S2f  >  ci . ti | ------------  +  ------------------------- |.
                 5     /__         \ 1 + (w.ti)^2     (ts + ti)^2 + (w.ts.ti)^2 /
                       i=m

    Replicated calculations are::

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation),

        ts_ti = ts + ti,
        ts_ti_ts = (ts + ti).ts.


    Calculations which are replicated in the gradient equations are::

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation),

        one_s2s = 1 - S2s,

        ts_ti_sqrd = (ts + ti)^2,
        w_ts_ti_sqrd = (w.ts.ti)^2,
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2),

                           (ts + ti)ts
        fact_ts  =  -------------------------.
                    (ts + ti)^2 + (w.ts.ti)^2

    """

    # Order parameter factors.
    data.one_s2s = 1.0 - params[data.s2s_i]
    data.s2f_s2 = data.one_s2s * params[data.s2f_i]

    # Internal correlation time, ts, factors.
    data.ts_ti =        params[data.ts_i] + data.ti
    data.ts_ti_ts =     data.ts_ti * params[data.ts_i]
    data.ts_ti_sqrd =   data.ts_ti**2

    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_i]**2
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)
    data.fact_ts =      data.ts_ti_ts * data.inv_ts_denom



# Extended {S2f, tf, S2, ts}.
#############################

def calc_S2f_tf_S2_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {S2f, tf, S2, ts}.

    The model-free formula is::

                    _n_
                 2  \           /      S2            (1 - S2f)(tf + ti)tf
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2
                    i=m

                                                     (S2f - S2)(ts + ti)ts   \ 
                                                +  ------------------------- |.
                                                   (ts + ti)^2 + (w.ts.ti)^2 /

    Replicated calculations are::

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation),

        tf_ti = tf + ti,
        ts_ti = ts + ti,
        tf_ti_tf = (tf + ti).tf,
        ts_ti_ts = (ts + ti).ts.


    Calculations which are replicated in the gradient equations are::

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation),

        one_s2f = 1 - S2f,
        s2f_s2 = S2f - S2,

        tf_ti_sqrd = (tf + ti)^2,
        ts_ti_sqrd = (ts + ti)^2,
        w_tf_ti_sqrd = (w.tf.ti)^2,
        w_ts_ti_sqrd = (w.ts.ti)^2,
        inv_tf_denom = 1 / ((tf + ti)^2 + (w.tf.ti)^2),
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2),

                           (tf + ti)tf
        fact_tf  =  -------------------------,
                    (tf + ti)^2 + (w.tf.ti)^2


                           (ts + ti)ts
        fact_ts  =  -------------------------.
                    (ts + ti)^2 + (w.ts.ti)^2

    """

    # Order parameter factors.
    data.one_s2f = 1.0 - params[data.s2f_i]
    data.s2f_s2 = params[data.s2f_i] - params[data.s2_i]

    # Internal correlation time, tf, factors.
    data.tf_ti =        params[data.tf_i] + data.ti
    data.tf_ti_tf =     data.tf_ti * params[data.tf_i]
    data.tf_ti_sqrd =   data.tf_ti**2

    data.w_tf_ti_sqrd = data.w_ti_sqrd * params[data.tf_i]**2
    data.inv_tf_denom = 1.0 / (data.tf_ti_sqrd + data.w_tf_ti_sqrd)
    data.fact_tf =      data.tf_ti_tf * data.inv_tf_denom

    # Internal correlation time, ts, factors.
    data.ts_ti =        params[data.ts_i] + data.ti
    data.ts_ti_ts =     data.ts_ti * params[data.ts_i]
    data.ts_ti_sqrd =   data.ts_ti**2

    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_i]**2
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)
    data.fact_ts =      data.ts_ti_ts * data.inv_ts_denom



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_S2f_tf_S2s_ts_jw_comps(data, params):
    """Spectral density component function.

    Calculate the components of the spectral density value for the extended model-free formula with
    the parameters {S2f, tf, S2s, ts}.

    The model-free formula is::

                    _n_
                 2  \           /   S2f . S2s        (1 - S2f)(tf + ti)tf
        J(w)  =  -   >  ci . ti | ------------  +  -------------------------
                 5  /__         \ 1 + (w.ti)^2     (tf + ti)^2 + (w.tf.ti)^2
                    i=m

                                                    S2f(1 - S2s)(ts + ti)ts  \ 
                                                +  ------------------------- |.
                                                   (ts + ti)^2 + (w.ts.ti)^2 /

    Replicated calculations are::

        w_ti_sqrd = (w.ti)^2        (pre-calculated during initialisation),

        tf_ti = tf + ti,
        ts_ti = ts + ti,
        tf_ti_tf = (tf + ti).tf,
        ts_ti_ts = (ts + ti).ts.


    Calculations which are replicated in the gradient equations are::

        fact_ti = 1 / (1 + (w.ti)^2)    (pre-calculated during initialisation),

        one_s2s = 1 - S2s,
        one_s2f = 1 - S2f,
        s2f_s2 = S2f(1 - S2s) = S2f - S2,

        tf_ti_sqrd = (tf + ti)^2,
        ts_ti_sqrd = (ts + ti)^2,
        w_tf_ti_sqrd = (w.tf.ti)^2,
        w_ts_ti_sqrd = (w.ts.ti)^2,
        inv_tf_denom = 1 / ((tf + ti)^2 + (w.tf.ti)^2),
        inv_ts_denom = 1 / ((ts + ti)^2 + (w.ts.ti)^2),

                           (tf + ti)tf
        fact_tf  =  -------------------------,
                    (tf + ti)^2 + (w.tf.ti)^2


                           (ts + ti)ts
        fact_ts  =  -------------------------.
                    (ts + ti)^2 + (w.ts.ti)^2

    """

    # Order parameter factors.
    data.one_s2s = 1.0 - params[data.s2s_i]
    data.one_s2f = 1.0 - params[data.s2f_i]
    data.s2f_s2 = params[data.s2f_i] * data.one_s2s

    # Internal correlation time, tf, factors.
    data.tf_ti =        params[data.tf_i] + data.ti
    data.tf_ti_tf =     data.tf_ti * params[data.tf_i]
    data.tf_ti_sqrd =   data.tf_ti**2

    data.w_tf_ti_sqrd = data.w_ti_sqrd * params[data.tf_i]**2
    data.inv_tf_denom = 1.0 / (data.tf_ti_sqrd + data.w_tf_ti_sqrd)
    data.fact_tf =      data.tf_ti_tf * data.inv_tf_denom

    # Internal correlation time, ts, factors.
    data.ts_ti =        params[data.ts_i] + data.ti
    data.ts_ti_ts =     data.ts_ti * params[data.ts_i]
    data.ts_ti_sqrd =   data.ts_ti**2

    data.w_ts_ti_sqrd = data.w_ti_sqrd * params[data.ts_i]**2
    data.inv_ts_denom = 1.0 / (data.ts_ti_sqrd + data.w_ts_ti_sqrd)
    data.fact_ts =      data.ts_ti_ts * data.inv_ts_denom




###############################
# Spectral density gradients. #
###############################


# Original {} and {S2} with diffusion parameters.
#################################################

def calc_diff_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the original model-free formula
    with no parameters {} or the parameter {S2} together with diffusion tensor parameters.

    Replicated calculations are::

                              1 - (w.ti)^2
        fact_ti_djw_dti  =  ----------------.
                            (1 + (w.ti)^2)^2
    """

    data.fact_ti_djw_dti = (1.0 - data.w_ti_sqrd) * data.fact_ti**2



# Original {S2, te}.
####################

def calc_S2_te_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the original model-free formula
    with the parameters {S2, te}.

    Replicated calculations are::

                                (te + ti)^2 - (w.te.ti)^2
        fact_djw_dte  =  ti^2 -----------------------------.
                              ((te + ti)^2 + (w.te.ti)^2)^2
    """

    data.fact_djw_dte = data.ti**2 * (data.te_ti_sqrd - data.w_te_ti_sqrd) * data.inv_te_denom**2



# Original {S2, te} with diffusion parameters.
##############################################

def calc_diff_S2_te_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the original model-free formula
    with the parameters {S2, te} together with diffusion tensor parameters.

    Replicated calculations are::

                              1 - (w.ti)^2
        fact_ti_djw_dti  =  ----------------,
                            (1 + (w.ti)^2)^2


                       (te + ti)^2 - (w.te.ti)^2
        fact_djw  =  -----------------------------,
                     ((te + ti)^2 + (w.te.ti)^2)^2


                                   (te + ti)^2 - (w.te.ti)^2
        fact_te_djw_dti  =  te^2 -----------------------------,
                                 ((te + ti)^2 + (w.te.ti)^2)^2


                                (te + ti)^2 - (w.te.ti)^2
        fact_djw_dte  =  ti^2 -----------------------------.
                              ((te + ti)^2 + (w.te.ti)^2)^2
    """

    fact_djw = (data.te_ti_sqrd - data.w_te_ti_sqrd) * data.inv_te_denom**2
    data.fact_ti_djw_dti = (1.0 - data.w_ti_sqrd) * data.fact_ti**2
    data.fact_te_djw_dti = params[data.te_i]**2 * fact_djw
    data.fact_djw_dte = data.ti**2 * fact_djw



# Extended {S2f, S2, ts}.
#########################

def calc_S2f_S2_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters {S2f, S2, ts}.

    Replicated calculations are::


                                (ts + ti)^2 - (w.ts.ti)^2
        fact_djw_dts  =  ti^2 -----------------------------.
                              ((ts + ti)^2 + (w.ts.ti)^2)^2
    """

    data.fact_djw_dts = data.ti**2 * (data.ts_ti_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom**2



# Extended {S2f, S2, ts} with diffusion parameters.
###################################################

def calc_diff_S2f_S2_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters {S2f, S2, ts} together with diffusion tensor parameters.

    Replicated calculations are::

                              1 - (w.ti)^2
        fact_ti_djw_dti  =  ----------------,
                            (1 + (w.ti)^2)^2


                       (ts + ti)^2 - (w.ts.ti)^2
        fact_djw  =  -----------------------------,
                     ((ts + ti)^2 + (w.ts.ti)^2)^2


                                   (ts + ti)^2 - (w.ts.ti)^2
        fact_ts_djw_dti  =  ts^2 -----------------------------,
                                 ((ts + ti)^2 + (w.ts.ti)^2)^2


                                (ts + ti)^2 - (w.ts.ti)^2
        fact_djw_dts  =  ti^2 -----------------------------.
                              ((ts + ti)^2 + (w.ts.ti)^2)^2
    """


    fact_djw = (data.ts_ti_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom**2
    data.fact_ti_djw_dti = (1.0 - data.w_ti_sqrd) * data.fact_ti**2
    data.fact_ts_djw_dti = params[data.ts_i]**2 * fact_djw
    data.fact_djw_dts = data.ti**2 * fact_djw



# Extended {S2f, tf, S2, ts}.
#############################

def calc_S2f_tf_S2_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters {S2f, tf, S2, ts}.

    Replicated calculations are::

                                (tf + ti)^2 - (w.tf.ti)^2
        fact_djw_dtf  =  ti^2 -----------------------------,
                              ((tf + ti)^2 + (w.tf.ti)^2)^2


                                (ts + ti)^2 - (w.ts.ti)^2
        fact_djw_dts  =  ti^2 -----------------------------.
                              ((ts + ti)^2 + (w.ts.ti)^2)^2
    """

    data.fact_djw_dtf = data.ti**2 * (data.tf_ti_sqrd - data.w_tf_ti_sqrd) * data.inv_tf_denom**2
    data.fact_djw_dts = data.ti**2 * (data.ts_ti_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom**2



# Extended {S2f, tf, S2, ts} with diffusion parameters.
#######################################################

def calc_diff_S2f_tf_S2_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters {S2f, tf, S2, ts} together with diffusion tensor parameters.

    Replicated calculations are::

                              1 - (w.ti)^2
        fact_ti_djw_dti  =  ----------------,
                            (1 + (w.ti)^2)^2


                          (tf + ti)^2 - (w.tf.ti)^2
        fact_tf_djw  =  -----------------------------,
                        ((tf + ti)^2 + (w.tf.ti)^2)^2


                          (ts + ti)^2 - (w.ts.ti)^2
        fact_ts_djw  =  -----------------------------,
                        ((ts + ti)^2 + (w.ts.ti)^2)^2


                                   (tf + ti)^2 - (w.tf.ti)^2
        fact_tf_djw_dti  =  tf^2 -----------------------------,
                                 ((tf + ti)^2 + (w.tf.ti)^2)^2


                                   (ts + ti)^2 - (w.ts.ti)^2
        fact_ts_djw_dti  =  ts^2 -----------------------------,
                                 ((ts + ti)^2 + (w.ts.ti)^2)^2


                                (tf + ti)^2 - (w.tf.ti)^2
        fact_djw_dtf  =  ti^2 -----------------------------,
                              ((tf + ti)^2 + (w.tf.ti)^2)^2


                                (ts + ti)^2 - (w.ts.ti)^2
        fact_djw_dts  =  ti^2 -----------------------------.
                              ((ts + ti)^2 + (w.ts.ti)^2)^2
    """

    # ti.
    data.fact_ti_djw_dti = (1.0 - data.w_ti_sqrd) * data.fact_ti**2

    # tf.
    fact_tf_djw = (data.tf_ti_sqrd - data.w_tf_ti_sqrd) * data.inv_tf_denom**2
    data.fact_tf_djw_dti = params[data.tf_i]**2 * fact_tf_djw
    data.fact_djw_dtf = data.ti**2 * fact_tf_djw

    # ts.
    fact_ts_djw = (data.ts_ti_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom**2
    data.fact_ts_djw_dti = params[data.ts_i]**2 * fact_ts_djw
    data.fact_djw_dts = data.ti**2 * fact_ts_djw



# Extended 2 {S2f, S2s, ts}.
############################

def calc_S2f_S2s_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters {S2f, S2s, ts}.

    Replicated calculations are::

                                (ts + ti)^2 - (w.ts.ti)^2
        fact_djw_dts  =  ti^2 -----------------------------.
                              ((ts + ti)^2 + (w.ts.ti)^2)^2
    """

    data.fact_djw_dts = data.ti**2 * (data.ts_ti_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom**2



# Extended 2 {S2f, S2s, ts} with diffusion parameters.
######################################################

def calc_diff_S2f_S2s_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters {S2f, S2s, ts} together with diffusion tensor parameters.

    Replicated calculations are::

                              1 - (w.ti)^2
        fact_ti_djw_dti  =  ----------------,
                            (1 + (w.ti)^2)^2


                       (ts + ti)^2 - (w.ts.ti)^2
        fact_djw  =  -----------------------------,
                     ((ts + ti)^2 + (w.ts.ti)^2)^2


                                   (ts + ti)^2 - (w.ts.ti)^2
        fact_ts_djw_dti  =  ts^2 -----------------------------,
                                 ((ts + ti)^2 + (w.ts.ti)^2)^2


                                (ts + ti)^2 - (w.ts.ti)^2
        fact_djw_dts  =  ti^2 -----------------------------.
                              ((ts + ti)^2 + (w.ts.ti)^2)^2
    """

    fact_djw = (data.ts_ti_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom**2
    data.fact_ti_djw_dti = (1.0 - data.w_ti_sqrd) * data.fact_ti**2
    data.fact_ts_djw_dti = params[data.ts_i]**2 * fact_djw
    data.fact_djw_dts = data.ti**2 * fact_djw



# Extended 2 {S2f, tf, S2s, ts}.
################################

def calc_S2f_tf_S2s_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters {S2f, tf, S2s, ts}.

    Replicated calculations are::

                                (tf + ti)^2 - (w.tf.ti)^2
        fact_djw_dtf  =  ti^2 -----------------------------,
                              ((tf + ti)^2 + (w.tf.ti)^2)^2


                                (ts + ti)^2 - (w.ts.ti)^2
        fact_djw_dts  =  ti^2 -----------------------------.
                              ((ts + ti)^2 + (w.ts.ti)^2)^2
    """

    data.fact_djw_dtf = data.ti**2 * (data.tf_ti_sqrd - data.w_tf_ti_sqrd) * data.inv_tf_denom**2
    data.fact_djw_dts = data.ti**2 * (data.ts_ti_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom**2



# Extended 2 {S2f, tf, S2s, ts} with diffusion parameters.
##########################################################

def calc_diff_S2f_tf_S2s_ts_djw_comps(data, params):
    """Spectral density gradient component function.

    Calculate the components of the spectral density gradient for the extended model-free formula
    with the parameters {S2f, tf, S2, ts} together with diffusion tensor parameters.

    Replicated calculations are::

                              1 - (w.ti)^2
        fact_ti_djw_dti  =  ----------------,
                            (1 + (w.ti)^2)^2


                          (tf + ti)^2 - (w.tf.ti)^2
        fact_tf_djw  =  -----------------------------,
                        ((tf + ti)^2 + (w.tf.ti)^2)^2


                          (ts + ti)^2 - (w.ts.ti)^2
        fact_ts_djw  =  -----------------------------,
                        ((ts + ti)^2 + (w.ts.ti)^2)^2


                                   (tf + ti)^2 - (w.tf.ti)^2
        fact_tf_djw_dti  =  tf^2 -----------------------------,
                                 ((tf + ti)^2 + (w.tf.ti)^2)^2


                                   (ts + ti)^2 - (w.ts.ti)^2
        fact_ts_djw_dti  =  ts^2 -----------------------------,
                                 ((ts + ti)^2 + (w.ts.ti)^2)^2


                                (tf + ti)^2 - (w.tf.ti)^2
        fact_djw_dtf  =  ti^2 -----------------------------,
                              ((tf + ti)^2 + (w.tf.ti)^2)^2


                                (ts + ti)^2 - (w.ts.ti)^2
        fact_djw_dts  =  ti^2 -----------------------------.
                              ((ts + ti)^2 + (w.ts.ti)^2)^2
    """

    # ti.
    data.fact_ti_djw_dti = (1.0 - data.w_ti_sqrd) * data.fact_ti**2

    # tf.
    fact_tf_djw = (data.tf_ti_sqrd - data.w_tf_ti_sqrd) * data.inv_tf_denom**2
    data.fact_tf_djw_dti = params[data.tf_i]**2 * fact_tf_djw
    data.fact_djw_dtf = data.ti**2 * fact_tf_djw

    # ts.
    fact_ts_djw = (data.ts_ti_sqrd - data.w_ts_ti_sqrd) * data.inv_ts_denom**2
    data.fact_ts_djw_dti = params[data.ts_i]**2 * fact_ts_djw
    data.fact_djw_dts = data.ti**2 * fact_ts_djw
