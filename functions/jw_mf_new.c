
/* Calculate the isotropic spectral density value for the original model-free formula with the single parameter S2.

The formula is:

	         2 /    S2 . tm    \ 
	J(w)  =  - | ------------- |
	         5 \ 1 + (w.tm)**2 /
*/
double c_calc_iso_s2_jw(double, double);

double jw;

double c_calc_iso_s2_jw(double s2_tm, double omega_tm_sqrd) {
	return  0.4 * (s2_tm / (1.0 + omega_tm_sqrd));
}

double c_calc_iso_s2f_s2s_ts_jw(double s2f, double s2s_tm, double omega_tm_sqrd, double s2s, double ts_prime, double omega_ts_prime_sqrd) {
	return 0.4 * s2f * (s2s_tm / (1.0 + omega_tm_sqrd) + (1.0 - s2s) * ts_prime / (1.0 + omega_ts_prime_sqrd));
}
