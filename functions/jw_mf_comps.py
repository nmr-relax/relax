from Numeric import Float64, zeros


# Spectral density value components.
####################################

def calc_iso_s2_te_jw_comps(data):
    """Spectral density component function.
    
    Calculate the components of the isotropic spectral density value for the original model-free
    formula with the parameters S2 and te.

    The model-free formula is:

                 2 /   S2 . tm        (1 - S2) . te' \ 
        J(w)  =  - | ------------  +  -------------- |
                 5 \ 1 + (w.tm)^2     1 + (w.te')^2  /


    Simplified:

                 2    /      S2             (1 - S2)(te + tm)te    \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (te + tm)^2 + (w.te.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd =    (w.tm)^2        (pre-calculated during initialisation)

        te_tm =        te + tm
        te_tm_te =    (te + tm).te


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm =    2/5 * tm        (pre-calculated during initialisation)
        fact_tm =    1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        one_s2 =    1 - S2

        te_tm_sqrd =    (te + tm)^2
        w_te_tm_sqrd =    (w.te.tm)^2
        te_denom =     (te + tm)^2 + (w.te.tm)^2
        te_num =    (te + tm)te
    """

    data.one_s2 = 1.0 - data.params[data.s2_index]

    data.te_tm = data.params[data.te_index] + data.diff_params[0]
    data.te_tm_te = data.te_tm * data.params[data.te_index]
    data.te_tm_sqrd = data.te_tm ** 2
    data.w_te_tm_sqrd = data.w_tm_sqrd * data.params[data.te_index] ** 2
    data.te_denom = data.te_tm_sqrd + data.w_te_tm_sqrd
    data.te_num = data.te_tm * data.params[data.te_index]


def calc_iso_s2f_s2s_ts_jw_comps(data):
    """Spectral density component function.

    Calculate the components of the isotropic spectral density value for the extended model-free
    formula with the parameters S2f, S2s, and ts.

    The formula is:

                 2 /    S2 . tm        (S2f - S2) . ts' \ 
        J(w)  =  - | -------------  +  ---------------- |
                 5 \ 1 + (w.tm)**2      1 + (w.ts')**2  /


    Simplified:

                 2    /   S2f . S2s       S2f(1 - S2s)(ts + tm)ts  \ 
        J(w)  =  - tm | ------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd =    (w.tm)^2        (pre-calculated during initialisation)

        ts_tm =        ts + tm
        ts_tm_ts =    (ts + tm).ts


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm =    2/5 * tm        (pre-calculated during initialisation)
        fact_tm =    1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        one_s2s =    1 - S2s
        s2f_s2 =    S2f(1 - S2s) = S2f - S2

        ts_tm_sqrd =    (ts + tm)^2
        w_ts_tm_sqrd =    (w.ts.tm)^2
        ts_denom =     (ts + tm)^2 + (w.ts.tm)^2
        ts_num =    (ts + tm)ts
    """

    data.one_s2s = 1.0 - data.params[data.s2s_index]
    data.s2f_s2 = data.params[data.s2f_index] * data.one_s2s

    data.ts_tm = data.params[data.ts_index] + data.diff_params[0]
    data.ts_tm_ts = data.ts_tm * data.params[data.ts_index]
    data.ts_tm_sqrd = data.ts_tm ** 2
    data.w_ts_tm_sqrd = data.w_tm_sqrd * data.params[data.ts_index] ** 2
    data.ts_denom = data.ts_tm_sqrd + data.w_ts_tm_sqrd
    data.ts_num = data.ts_tm * data.params[data.ts_index]


def calc_iso_s2f_tf_s2s_ts_jw_comps(data):
    """Spectral density component function.
    
    Calculate the components of the isotropic spectral density value for the extended model-free
    formula with the parameters S2f, tf, S2s, and ts.

    The formula is:

                 2 /    S2 . tm        (1 - S2f) . tf'     (S2f - S2) . ts' \ 
        J(w)  =  - | -------------  +  ---------------  +  ---------------- |
                 5 \ 1 + (w.tm)**2     1 + (w.tf')**2       1 + (w.ts')**2  /


    Simplified:

                 2    /   S2f . S2s        (1 - S2f)(tf + tm)tf         S2f(1 - S2s)(ts + tm)ts  \ 
        J(w)  =  - tm | ------------  +  -------------------------  +  ------------------------- |
                 5    \ 1 + (w.tm)^2     (tf + tm)^2 + (w.tf.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /


    Replicated calculations are:

        w_tm_sqrd =    (w.tm)^2        (pre-calculated during initialisation)

        tf_tm =        tf + tm
        ts_tm =        ts + tm
        tf_tm_tf =    (tf + tm).tf
        ts_tm_ts =    (ts + tm).ts


    Calculations which are replicated in the gradient equations are:

        two_fifths_tm =    2/5 * tm        (pre-calculated during initialisation)
        fact_tm =    1 / (1 + (w.tm)^2)    (pre-calculated during initialisation)

        one_s2s =    1 - S2s
        one_s2f =    1 - S2f
        s2f_s2 =    S2f(1 - S2s) = S2f - S2

        tf_tm_sqrd =    (tf + tm)^2
        ts_tm_sqrd =    (ts + tm)^2
        w_tf_tm_sqrd =    (w.tf.tm)^2
        w_ts_tm_sqrd =    (w.ts.tm)^2
        tf_denom =     (tf + tm)^2 + (w.tf.tm)^2
        ts_denom =     (ts + tm)^2 + (w.ts.tm)^2
        tf_num =    (tf + tm)tf
        ts_num =    (ts + tm)ts
    """

    data.one_s2s = 1.0 - data.params[data.s2s_index]
    data.one_s2f = 1.0 - data.params[data.s2f_index]
    data.s2f_s2 = data.params[data.s2f_index] * data.one_s2s

    data.tf_tm = data.params[data.tf_index] + data.diff_params[0]
    data.ts_tm = data.params[data.ts_index] + data.diff_params[0]
    data.tf_tm_tf = data.tf_tm * data.params[data.tf_index]
    data.ts_tm_ts = data.ts_tm * data.params[data.ts_index]
    data.tf_tm_sqrd = data.tf_tm ** 2
    data.ts_tm_sqrd = data.ts_tm ** 2
    data.w_tf_tm_sqrd = data.w_tm_sqrd * data.params[data.tf_index] ** 2
    data.w_ts_tm_sqrd = data.w_tm_sqrd * data.params[data.ts_index] ** 2
    data.tf_denom = data.tf_tm_sqrd + data.w_tf_tm_sqrd
    data.ts_denom = data.ts_tm_sqrd + data.w_ts_tm_sqrd
    data.tf_num = data.tf_tm * data.params[data.tf_index]
    data.ts_num = data.ts_tm * data.params[data.ts_index]



# Spectral density gradient components.
#######################################

def calc_iso_s2_te_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the original model-free
    formula with the parameters S2 and te.

    Replicated calculations are:

        two_fifths_tm_sqrd =    2/5 * tm^2        (pre-calculated during initialisation)

                              2        (te + tm)^2 - (w.te.tm)^2
        fact_djw_dte =        - tm^2 -----------------------------
                              5      ((te + tm)^2 + (w.te.tm)^2)^2
    """

    data.fact_djw_dte = data.two_fifths_tm_sqrd * (data.te_tm_sqrd - data.w_te_tm_sqrd) / (data.te_denom ** 2)



def calc_iso_s2f_s2s_ts_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the extended model-free
    formula with the parameters S2f, S2s, and ts.

    Replicated calculations are:

        two_fifths_tm_sqrd =    2/5 * tm^2        (pre-calculated during initialisation)


                              2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts =        - tm^2 -----------------------------
                              5      ((ts + tm)^2 + (w.ts.tm)^2)^2


                               2    /      1                 (ts + tm).ts        \ 
        fact_djw_ds2s =        - tm | ------------  -  ------------------------- |
                               5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_tm_sqrd) / (data.ts_denom ** 2)
    data.fact_djw_ds2s = data.two_fifths_tm * (data.fact_tm - data.ts_tm_ts / data.ts_denom)


def calc_iso_s2f_tf_s2s_ts_djw_comps(data):
    """Spectral density gradient component function.

    Calculate the components of the isotropic spectral density gradient for the extended model-free
    formula with the parameters S2f, tf, S2s, and ts.

    Replicated calculations are:

        two_fifths_tm_sqrd =    2/5 * tm^2        (pre-calculated during initialisation)


                              2        (tf + tm)^2 - (w.tf.tm)^2
        fact_djw_dtf =        - tm^2 -----------------------------
                              5      ((tf + tm)^2 + (w.tf.tm)^2)^2


                              2        (ts + tm)^2 - (w.ts.tm)^2
        fact_djw_dts =        - tm^2 -----------------------------
                              5      ((ts + tm)^2 + (w.ts.tm)^2)^2


                               2    /      1                 (ts + tm).ts        \ 
        fact_djw_ds2s =        - tm | ------------  -  ------------------------- |
                               5    \ 1 + (w.tm)^2     (ts + tm)^2 + (w.ts.tm)^2 /
    """

    data.fact_djw_dtf = data.two_fifths_tm_sqrd * (data.tf_tm_sqrd - data.w_tf_tm_sqrd) / (data.tf_denom ** 2)
    data.fact_djw_dts = data.two_fifths_tm_sqrd * (data.ts_tm_sqrd - data.w_ts_tm_sqrd) / (data.ts_denom ** 2)
    data.fact_djw_ds2s = data.two_fifths_tm * (data.fact_tm - data.ts_tm_ts / data.ts_denom)
