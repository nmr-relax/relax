/*
Copyright (C) 2003 Edward d'Auvergne

This file is part of the program relax.

Relax is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

Relax is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with relax; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
*/


/* swig interface for jw_mf_new.c */
%module swig_jw_mf

extern double jw;
extern double c_calc_iso_s2_jw(double s2_tm, double omega_tm_sqrd);
extern double c_calc_iso_s2f_s2s_ts_jw(double s2f, double s2s_tm, double omega_tm_sqrd, double s2s, double ts_prime, double omega_ts_prime_sqrd);
