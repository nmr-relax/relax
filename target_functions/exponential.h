/*
 * Copyright (C) 2006 Gary S Thompson (see https://gna.org/users for contact
 *                                     details)
 * Copyright (C) 2014 Edward d'Auvergne
 *
 * This file is part of the program relax (http://www.nmr-relax.com).
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "dimensions.h"

#ifndef RELAX_EXPONENTIAL 
#define RELAX_EXPONENTIAL

void exponential(double I0, double R, double relax_times[MAX_DATA], double back_calc[MAX_DATA], int num_times);
void exponential_dI0(double I0, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);
void exponential_dR(double I0, double R, int param_index, double relax_times[MAX_DATA], double back_calc_grad[MAX_PARAMS][MAX_DATA], int num_times);

#endif
