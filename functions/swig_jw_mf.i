/* swig interface for jw_mf_new.c */
%module jw_mf_new

extern double jw;
extern double c_calc_iso_s2_jw(double s2_tm, double omega_tm_sqrd);
extern double c_calc_iso_s2f_s2s_ts_jw(double s2f, double s2s_tm, double omega_tm_sqrd, double s2s, double ts_prime, double omega_ts_prime_sqrd);
