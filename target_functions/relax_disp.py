###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Module docstring.
"""Target functions for relaxation dispersion."""

# Python module imports.
from copy import deepcopy
from math import pi
from numpy import add, array, asarray, complex64, dot, float64, int16, max, multiply, ones, sum, tile, zeros
from numpy.ma import masked_equal

# relax module imports.
from lib.dispersion.b14 import r2eff_B14
from lib.dispersion.cr72 import r2eff_CR72
from lib.dispersion.dpl94 import r1rho_DPL94
from lib.dispersion.it99 import r2eff_IT99
from lib.dispersion.lm63 import r2eff_LM63
from lib.dispersion.lm63_3site import r2eff_LM63_3site
from lib.dispersion.m61 import r1rho_M61
from lib.dispersion.m61b import r1rho_M61b
from lib.dispersion.mp05 import r1rho_MP05
from lib.dispersion.mmq_cr72 import r2eff_mmq_cr72
from lib.dispersion.ns_cpmg_2site_3d import r2eff_ns_cpmg_2site_3D
from lib.dispersion.ns_cpmg_2site_expanded import r2eff_ns_cpmg_2site_expanded
from lib.dispersion.ns_cpmg_2site_star import r2eff_ns_cpmg_2site_star
from lib.dispersion.ns_mmq_3site import r2eff_ns_mmq_3site_mq, r2eff_ns_mmq_3site_sq_dq_zq
from lib.dispersion.ns_mmq_2site import r2eff_ns_mmq_2site_mq, r2eff_ns_mmq_2site_sq_dq_zq
from lib.dispersion.ns_r1rho_2site import ns_r1rho_2site
from lib.dispersion.ns_r1rho_3site import ns_r1rho_3site
from lib.dispersion.ns_matrices import r180x_3d
from lib.dispersion.tp02 import r1rho_TP02
from lib.dispersion.tap03 import r1rho_TAP03
from lib.dispersion.tsmfk01 import r2eff_TSMFK01
from lib.errors import RelaxError
from lib.float import isNaN
from target_functions.chi2 import chi2, chi2_rankN
from specific_analyses.relax_disp.variables import EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_ZQ, EXP_TYPE_R1RHO, MODEL_B14, MODEL_B14_FULL, MODEL_CR72, MODEL_CR72_FULL, MODEL_DPL94, MODEL_IT99, MODEL_LIST_CPMG, MODEL_LIST_CPMG_FULL, MODEL_LIST_FULL, MODEL_LIST_MMQ, MODEL_LIST_MQ_CPMG, MODEL_LIST_R1RHO, MODEL_LIST_R1RHO_FULL, MODEL_LM63, MODEL_LM63_3SITE, MODEL_M61, MODEL_M61B, MODEL_MP05, MODEL_MMQ_CR72, MODEL_NOREX, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR, MODEL_TAP03, MODEL_TP02, MODEL_TSMFK01


class Dispersion:
    def __init__(self, model=None, num_params=None, num_spins=None, num_frq=None, exp_types=None, values=None, errors=None, missing=None, frqs=None, frqs_H=None, cpmg_frqs=None, spin_lock_nu1=None, chemical_shifts=None, offset=None, tilt_angles=None, r1=None, relax_times=None, scaling_matrix=None, recalc_tau=True):
        """Relaxation dispersion target functions for optimisation.

        Models
        ======

        The following analytic models are currently supported:

            - 'No Rex':  The model for no chemical exchange relaxation.
            - 'LM63':  The Luz and Meiboom (1963) 2-site fast exchange model.
            - 'LM63 3-site':  The Luz and Meiboom (1963) 3-site fast exchange model.
            - 'CR72':  The reduced Carver and Richards (1972) 2-site model for all time scales with R20A = R20B.
            - 'CR72 full':  The full Carver and Richards (1972) 2-site model for all time scales.
            - 'IT99':  The Ishima and Torchia (1999) 2-site model for all time scales with skewed populations (pA >> pB).
            - 'TSMFK01':  The Tollinger et al. (2001) 2-site very-slow exchange model, range of microsecond to second time scale.
            - 'B14':  The Baldwin (2014) 2-site exact solution model for all time scales with R20A = R20B..
            - 'B14 full':  The Baldwin (2014) 2-site exact solution model for all time scales.
            - 'M61':  The Meiboom (1961) 2-site fast exchange model for R1rho-type experiments.
            - 'DPL94':  The Davis, Perlman and London (1994) 2-site fast exchange model for R1rho-type experiments.
            - 'M61 skew':  The Meiboom (1961) on-resonance 2-site model with skewed populations (pA >> pB) for R1rho-type experiments.
            - 'TP02':  The Trott and Palmer (2002) 2-site exchange model for R1rho-type experiments.
            - 'TAP03':  The Trott, Abergel and Palmer (2003) 2-site exchange model for R1rho-type experiments.
            - 'MP05':  The Miloushev and Palmer (2005) off-resonance 2-site exchange model for R1rho-type experiments.

        The following numerical models are currently supported:

            - 'NS CPMG 2-site 3D':  The reduced numerical solution for the 2-site Bloch-McConnell equations for CPMG data using 3D magnetisation vectors with R20A = R20B.
            - 'NS CPMG 2-site 3D full':  The full numerical solution for the 2-site Bloch-McConnell equations for CPMG data using 3D magnetisation vectors.
            - 'NS CPMG 2-site star':  The reduced numerical solution for the 2-site Bloch-McConnell equations for CPMG data using complex conjugate matrices with R20A = R20B.
            - 'NS CPMG 2-site star full':  The full numerical solution for the 2-site Bloch-McConnell equations for CPMG data using complex conjugate matrices.
            - 'NS CPMG 2-site expanded':  The numerical solution for the 2-site Bloch-McConnell equations for CPMG data expanded using Maple by Nikolai Skrynnikov.
            - 'NS MMQ 2-site':  The numerical solution for the 2-site Bloch-McConnell equations for combined proton-heteronuclear SQ, ZD, DQ, and MQ CPMG data with R20A = R20B.
            - 'NS MMQ 3-site linear':  The numerical solution for the 3-site Bloch-McConnell equations linearised with kAC = kCA = 0 for combined proton-heteronuclear SQ, ZD, DQ, and MQ CPMG data with R20A = R20B = R20C.
            - 'NS MMQ 3-site':  The numerical solution for the 3-site Bloch-McConnell equations for combined proton-heteronuclear SQ, ZD, DQ, and MQ CPMG data with R20A = R20B = R20C.
            - 'NS R1rho 2-site':  The numerical solution for the 2-site Bloch-McConnell equations for R1rho data with R20A = R20B.
            - 'NS R1rho 3-site linear':  The numerical solution for the 3-site Bloch-McConnell equations linearised with kAC = kCA = 0 for R1rho data with R20A = R20B = R20C.
            - 'NS R1rho 3-site':  The numerical solution for the 3-site Bloch-McConnell equations for R1rho data with R20A = R20B = R20C.


        Indices
        =======

        The data structures used in this target function class consist of many different index types.  These are:

            - Ei:  The index for each experiment type.
            - Si:  The index for each spin of the spin cluster.
            - Mi:  The index for each magnetic field strength.
            - Oi:  The index for each spin-lock offset.  In the case of CPMG-type data, this index is always zero.
            - Di:  The index for each dispersion point (either the spin-lock field strength or the nu_CPMG frequency).


        @keyword model:             The relaxation dispersion model to fit.
        @type model:                str
        @keyword num_param:         The number of parameters in the model.
        @type num_param:            int
        @keyword num_spins:         The number of spins in the cluster.
        @type num_spins:            int
        @keyword num_frq:           The number of spectrometer field strengths.
        @type num_frq:              int
        @keyword exp_types:         The list of experiment types.  The dimensions are {Ei}.
        @type exp_types:            list of str
        @keyword values:            The R2eff/R1rho values.  The dimensions are {Ei, Si, Mi, Oi, Di}.
        @type values:               rank-4 list of numpy rank-1 float arrays
        @keyword errors:            The R2eff/R1rho errors.  The dimensions are {Ei, Si, Mi, Oi, Di}.
        @type errors:               rank-4 list of numpy rank-1 float arrays
        @keyword missing:           The data structure indicating missing R2eff/R1rho data.  The dimensions are {Ei, Si, Mi, Oi, Di}.
        @type missing:              rank-4 list of numpy rank-1 int arrays
        @keyword frqs:              The spin Larmor frequencies (in MHz*2pi to speed up the ppm to rad/s conversion).  The dimensions are {Ei, Si, Mi}.
        @type frqs:                 rank-3 list of floats
        @keyword frqs_H:            The proton spin Larmor frequencies for the MMQ-type models (in MHz*2pi to speed up the ppm to rad/s conversion).  The dimensions are {Ei, Si, Mi}.
        @type frqs_H:               rank-3 list of floats
        @keyword cpmg_frqs:         The CPMG frequencies in Hertz.  This will be ignored for R1rho experiments.  The dimensions are {Ei, Mi}.
        @type cpmg_frqs:            rank-2 list of floats
        @keyword spin_lock_nu1:     The spin-lock field strengths in Hertz.  This will be ignored for CPMG experiments.  The dimensions are {Ei, Mi}.
        @type spin_lock_nu1:        rank-2 list of floats
        @keyword chemical_shifts:   The chemical shifts in rad/s.  This is only used for off-resonance R1rho models.  The ppm values are not used to save computation time, therefore they must be converted to rad/s by the calling code.  The dimensions are {Ei, Si, Mi}.
        @type chemical_shifts:      rank-3 list of floats
        @keyword offset:            The structure of spin-lock or hard pulse offsets in rad/s.  This is only currently used for off-resonance R1rho models.  The dimensions are {Ei, Si, Mi, Oi}.
        @type offset:               rank-4 list of floats
        @keyword tilt_angles:       The spin-lock rotating frame tilt angle.  This is only used for off-resonance R1rho models.  The dimensions are {Ei, Si, Mi, Oi, Di}.
        @type tilt_angles:          rank-5 list of floats
        @keyword r1:                The R1 relaxation rates.  This is only used for off-resonance R1rho models.  The dimensions are {Ei, Si, Mi}.
        @type r1:                   rank-3 list of floats
        @keyword relax_times:       The experiment specific fixed time period for relaxation (in seconds).  The dimensions are {Ei, Mi}.
        @type relax_times:          rank-2 list of floats
        @keyword scaling_matrix:    The square and diagonal scaling matrix.
        @type scaling_matrix:       numpy rank-2 float array
        @keyword recalc_tau:        A flag which if True will cause tau_CPMG to be recalculated to remove user input truncation.
        @type recalc_tau:           bool
        """

        # Check the args.
        if model not in MODEL_LIST_FULL:
            raise RelaxError("The model '%s' is unknown." % model)
        if values == None:
            raise RelaxError("No values have been supplied to the target function.")
        if errors == None:
            raise RelaxError("No errors have been supplied to the target function.")
        if missing == None:
            raise RelaxError("No missing data information has been supplied to the target function.")
        if model in [MODEL_DPL94, MODEL_TP02, MODEL_TAP03, MODEL_MP05]:
            if chemical_shifts == None:
                raise RelaxError("Chemical shifts must be supplied for the '%s' R1rho off-resonance dispersion model." % model)
            if r1 == None:
                raise RelaxError("R1 relaxation rates must be supplied for the '%s' R1rho off-resonance dispersion model." % model)

        # Store the arguments.
        self.model = model
        self.num_params = num_params
        self.num_spins = num_spins
        self.num_frq = num_frq
        self.exp_types = exp_types
        self.scaling_matrix = scaling_matrix

        ### Initialise higher order numpy structures.
        # Define the shape of all the numpy arrays.
        # The total numbers of experiments, number of spins, number of magnetic field strength, maximum number of offsets, maximum number of dispersion point.
        self.NE = len(self.exp_types)
        self.NS = self.num_spins
        self.NM = self.num_frq

        # The number of offsets points can vary. We need to find the maximum elements in the numpy array list.
        max_NO = 1
        for ei in range(self.NE):
            for si in range(self.NS):
                for mi in range(self.NM):
                    nr_NO = len(offset[ei][si][mi])
                    if nr_NO > max_NO:
                        max_NO = nr_NO

        # Set the maximum number of offsets.
        self.NO = max_NO

        # The number of dispersion points can vary. We need to find the maximum elements in the numpy array list.
        max_ND = 1
        for ei in range(self.NE):
            for si in range(self.NS):
                for mi in range(self.NM):
                    for oi in range(self.NO):
                        if cpmg_frqs != None and len(cpmg_frqs[ei][mi][oi]):
                            nr_ND = len(cpmg_frqs[ei][mi][oi])
                            if nr_ND > max_ND:
                                max_ND = nr_ND
                        elif spin_lock_nu1 != None and len(spin_lock_nu1[ei][mi][oi]):
                            nr_ND = len(spin_lock_nu1[ei][mi][oi])
                            if nr_ND > max_ND:
                                max_ND = nr_ND

        # Set the maximum number of dispersion points.
        self.NO = max_NO
        self.ND = max_ND

        # Set the shape of the multi dimensional numpy array,
        self.numpy_array_shape = [self.NE, self.NS, self.NM, self.NO, self.ND]

        # Create zero and one numpy structure.
        numpy_array_zeros = zeros(self.numpy_array_shape, float64)
        numpy_array_ones = ones(self.numpy_array_shape, float64)

        # Create special numpy structures.
        self.no_nd_ones = ones([self.NO, self.ND], float64)
        self.nm_no_nd_ones = ones([self.NM, self.NO, self.ND], float64)
        # Structure of r20a and r20b. The full and outer dimensions structures.
        self.r20_struct = deepcopy(numpy_array_zeros)
        self.r20a_struct = deepcopy(numpy_array_zeros)
        self.r20b_struct = deepcopy(numpy_array_zeros)
        # Structure of dw. The full and the outer dimensions structures.
        self.dw_struct = deepcopy(numpy_array_zeros)
        self.dwH_struct = deepcopy(numpy_array_zeros)
        self.phi_ex_struct = deepcopy(numpy_array_zeros)

        # Structure of values, errors and missing.
        self.values = deepcopy(numpy_array_zeros)
        self.errors = deepcopy(numpy_array_ones)
        self.missing = deepcopy(numpy_array_zeros)
        self.disp_struct = deepcopy(numpy_array_zeros)

        # Create the data structures to fill in.
        self.cpmg_frqs = deepcopy(numpy_array_ones)
        self.frqs = deepcopy(numpy_array_zeros)
        self.frqs_squared = deepcopy(numpy_array_zeros)
        self.frqs_H = deepcopy(numpy_array_zeros)
        self.relax_times = deepcopy(numpy_array_zeros)
        self.inv_relax_times = deepcopy(numpy_array_zeros)
        self.tau_cpmg = deepcopy(numpy_array_zeros)
        self.power = deepcopy(numpy_array_zeros)
        self.r1 = deepcopy(numpy_array_zeros)
        self.spin_lock_omega1 = deepcopy(numpy_array_zeros)
        self.spin_lock_omega1_squared = deepcopy(numpy_array_zeros)
        self.offset = deepcopy(numpy_array_zeros)
        self.chemical_shifts = deepcopy(numpy_array_zeros)
        self.tilt_angles = deepcopy(numpy_array_zeros)
        self.num_offsets = zeros([self.NE, self.NS, self.NM], int16)
        self.num_disp_points = zeros([self.NE, self.NS, self.NM, self.NO], int16)

        # Set flag to tell if there is missing data points.
        self.has_missing = False

        # Fill in data.
        for ei in range(self.NE):
            for si in range(self.NS):
                for mi in range(self.NM):
                    # Fill the frequency.
                    frq = frqs[ei][si][mi]
                    self.frqs[ei][si][mi][:] = frq
                    self.frqs_squared[ei][si][mi][:] = frq**2
                    frq_H = frqs_H[ei][si][mi]
                    self.frqs_H[ei][si][mi][:] = frq_H

                    # Fill the relaxation time.
                    relax_time = relax_times[ei][mi]
                    self.relax_times[ei][si][mi][:] = relax_time

                    # Fill r1.
                    r1_l = r1[si][mi]
                    self.r1[ei][si][mi][:] = r1_l

                    # Fill chemical shift.
                    chemical_shift = chemical_shifts[ei][si][mi]
                    self.chemical_shifts[ei][si][mi][:] = chemical_shift

                    # The inverted relaxation delay.
                    if model in [MODEL_B14, MODEL_B14_FULL, MODEL_MMQ_CR72, MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_EXPANDED, MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_MMQ_2SITE, MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR, MODEL_NS_R1RHO_2SITE, MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]:
                        self.inv_relax_times[ei][si][mi][:] = 1.0 / relax_time

                    # The number of offset data points.
                    if len(offset[ei][si][mi]):
                        self.num_offsets[ei][si][mi] = len(self.offset[ei][si][mi])
                    else:
                        self.num_offsets[ei][si][mi] = 0

                    # Loop over offsets.
                    for oi in range(self.NO):
                        if cpmg_frqs != None and len(cpmg_frqs[ei][mi][oi]):
                            cpmg_frqs_list = cpmg_frqs[ei][mi][oi]
                            num_disp_points = len(cpmg_frqs_list)
                            self.cpmg_frqs[ei][si][mi][oi][:num_disp_points] = cpmg_frqs_list

                            for di in range(num_disp_points):
                                cpmg_frq = cpmg_frqs[ei][mi][oi][di]
                                # Missing data for an entire field strength.
                                if isNaN(relax_time):
                                    power = 0
                                # Normal value.
                                else:
                                    power = int(round(cpmg_frq * relax_time))
                                self.power[ei][si][mi][oi][di] = power

                                # Recalculate the tau_cpmg times to avoid any user induced truncation in the input files.
                                if recalc_tau:
                                    tau_cpmg = 0.25 * relax_time / power
                                else:
                                    tau_cpmg = 0.25 / frq
                                self.tau_cpmg[ei][si][mi][oi][di] = tau_cpmg

                        elif spin_lock_nu1 != None and len(spin_lock_nu1[ei][mi][oi]):
                            num_disp_points = len( spin_lock_nu1[ei][mi][oi] )
                        else:
                            num_disp_points = 0

                        self.num_disp_points[ei][si][mi][oi] = num_disp_points

                        # Get the values and errors.
                        self.values[ei][si][mi][oi][:num_disp_points] = values[ei][si][mi][oi]
                        self.errors[ei][si][mi][oi][:num_disp_points] = errors[ei][si][mi][oi]
                        self.disp_struct[ei][si][mi][oi][:num_disp_points] = ones(num_disp_points)

                        # Loop over dispersion points.
                        for di in range(num_disp_points):
                            if missing[ei][si][mi][oi][di]:
                                self.has_missing = True
                                self.missing[ei][si][mi][oi][di] = 1.0

                            # For R1rho data.
                            if model in MODEL_LIST_R1RHO_FULL and model != MODEL_NOREX:
                                self.disp_struct[ei][si][mi][oi][di] = 1.0
                                # Get the tilt angles.
                                self.tilt_angles[ei][si][mi][oi][di] = tilt_angles[ei][si][mi][oi][di]
                                self.offset[ei][si][mi][oi] = offset[ei][si][mi][oi]
                                ## Convert the spin-lock data to rad.s^-1.
                                self.spin_lock_omega1[ei][si][mi][oi][di] = 2.0 * pi * spin_lock_nu1[ei][mi][oi][di]
                                self.spin_lock_omega1_squared[ei][si][mi][oi][di] = self.spin_lock_omega1[ei][si][mi][oi][di] ** 2

        # Create the structure for holding the back-calculated R2eff values (matching the dimensions of the values structure).
        self.back_calc = deepcopy(self.values)

        # Find the mask to replace back_calc values with measured values, if there is missing data points.
        # This is to make sure, that the chi2 values is not affected by missing values.
        self.mask_replace_blank = masked_equal(self.missing, 1.0)

        # Check the experiment types, simplifying the data structures as needed.
        self.experiment_type_setup()

        # Scaling initialisation.
        self.scaling_flag = False
        if self.scaling_matrix != None:
            self.scaling_flag = True

        # Initialise the post spin parameter indices.
        self.end_index = []

        # The spin and frequency dependent R2 parameters.
        self.end_index.append(self.num_exp * self.num_spins * self.num_frq)
        if model in [MODEL_B14_FULL, MODEL_CR72_FULL, MODEL_NS_CPMG_2SITE_3D_FULL, MODEL_NS_CPMG_2SITE_STAR_FULL]:
            self.end_index.append(2 * self.num_exp * self.num_spins * self.num_frq)

        # The spin and dependent parameters (phi_ex, dw, padw2).
        self.end_index.append(self.end_index[-1] + self.num_spins)
        if model in [MODEL_IT99, MODEL_LM63_3SITE, MODEL_MMQ_CR72, MODEL_NS_MMQ_2SITE]:
            self.end_index.append(self.end_index[-1] + self.num_spins)
        elif model in [MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]:
            self.end_index.append(self.end_index[-1] + self.num_spins)
            self.end_index.append(self.end_index[-1] + self.num_spins)
        elif model in [MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]:
            self.end_index.append(self.end_index[-1] + self.num_spins)
            self.end_index.append(self.end_index[-1] + self.num_spins)
            self.end_index.append(self.end_index[-1] + self.num_spins)

        # Set up the matrices for the numerical solutions.
        if model in [MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL]:
            # The matrix that contains only the R2 relaxation terms ("Redfield relaxation", i.e. non-exchange broadening).
            self.Rr = zeros((2, 2), complex64)

            # The matrix that contains the exchange terms between the two states A and B.
            self.Rex = zeros((2, 2), complex64)

            # The matrix that contains the chemical shift evolution.  It works here only with X magnetization, and the complex notation allows to evolve in the transverse plane (x, y).
            self.RCS = zeros((2, 2), complex64)

            # The matrix that contains all the contributions to the evolution, i.e. relaxation, exchange and chemical shift evolution.
            self.R = zeros((2, 2), complex64)

        # Pi-pulse propagators.
        if model in [MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL]:
            self.r180x = r180x_3d()

        # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
        if model in [MODEL_NS_CPMG_2SITE_STAR, MODEL_NS_CPMG_2SITE_STAR_FULL, MODEL_NS_MMQ_2SITE]:
            self.M0 = zeros(2, float64)
        if model in [MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]:
            self.M0 = zeros(3, float64)
        if model in [MODEL_NS_CPMG_2SITE_3D, MODEL_NS_CPMG_2SITE_3D_FULL]:
            self.M0 = zeros(7, float64)
            self.M0[0] = 0.5
        if model in [MODEL_NS_R1RHO_2SITE]:
            self.M0 = zeros(6, float64)
        if model in [MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]:
            self.M0 = zeros(9, float64)

        # Special storage matrices for the multi-quantum CPMG N-site numerical models.
        if model == MODEL_NS_MMQ_2SITE:
            self.m1 = zeros((2, 2), complex64)
            self.m2 = zeros((2, 2), complex64)
        elif model in [MODEL_NS_MMQ_3SITE, MODEL_NS_MMQ_3SITE_LINEAR]:
            self.m1 = zeros((3, 3), complex64)
            self.m2 = zeros((3, 3), complex64)
        elif model == MODEL_NS_R1RHO_2SITE:
            self.matrix = zeros((6, 6), float64)
        elif model in [MODEL_NS_R1RHO_3SITE, MODEL_NS_R1RHO_3SITE_LINEAR]:
            self.matrix = zeros((9, 9), float64)

        # Set up the model.
        if model == MODEL_NOREX:
            self.func = self.func_NOREX
        if model == MODEL_LM63:
            self.func = self.func_LM63
        if model == MODEL_LM63_3SITE:
            self.func = self.func_LM63_3site
        if model == MODEL_CR72_FULL:
            self.func = self.func_CR72_full
        if model == MODEL_CR72:
            self.func = self.func_CR72
        if model == MODEL_IT99:
            self.func = self.func_IT99
        if model == MODEL_TSMFK01:
            self.func = self.func_TSMFK01
        if model == MODEL_B14:
            self.func = self.func_B14
        if model == MODEL_B14_FULL:
            self.func = self.func_B14_full
        if model == MODEL_NS_CPMG_2SITE_3D_FULL:
            self.func = self.func_ns_cpmg_2site_3D_full
        if model == MODEL_NS_CPMG_2SITE_3D:
            self.func = self.func_ns_cpmg_2site_3D
        if model == MODEL_NS_CPMG_2SITE_EXPANDED:
            self.func = self.func_ns_cpmg_2site_expanded
        if model == MODEL_NS_CPMG_2SITE_STAR_FULL:
            self.func = self.func_ns_cpmg_2site_star_full
        if model == MODEL_NS_CPMG_2SITE_STAR:
            self.func = self.func_ns_cpmg_2site_star
        if model == MODEL_M61:
            self.func = self.func_M61
        if model == MODEL_M61B:
            self.func = self.func_M61b
        if model == MODEL_DPL94:
            self.func = self.func_DPL94
        if model == MODEL_TP02:
            self.func = self.func_TP02
        if model == MODEL_TAP03:
            self.func = self.func_TAP03
        if model == MODEL_MP05:
            self.func = self.func_MP05
        if model == MODEL_NS_R1RHO_2SITE:
            self.func = self.func_ns_r1rho_2site
        if model == MODEL_NS_R1RHO_3SITE:
            self.func = self.func_ns_r1rho_3site
        if model == MODEL_NS_R1RHO_3SITE_LINEAR:
            self.func = self.func_ns_r1rho_3site_linear
        if model == MODEL_MMQ_CR72:
            self.func = self.func_mmq_CR72
        if model == MODEL_NS_MMQ_2SITE:
            self.func = self.func_ns_mmq_2site
        if model == MODEL_NS_MMQ_3SITE:
            self.func = self.func_ns_mmq_3site
        if model == MODEL_NS_MMQ_3SITE_LINEAR:
            self.func = self.func_ns_mmq_3site_linear


    def calc_B14_chi2(self, R20A=None, R20B=None, dw=None, pA=None, kex=None):
        """Calculate the chi-squared value of the Baldwin (2014) 2-site exact solution model for all time scales.


        @keyword R20A:  The R2 value for state A in the absence of exchange.
        @type R20A:     list of float
        @keyword R20B:  The R2 value for state B in the absence of exchange.
        @type R20B:     list of float
        @keyword dw:    The chemical shift differences in ppm for each spin.
        @type dw:       list of float
        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20A and R20B to per experiment, spin and frequency.
        self.r20a_struct[:] = multiply.outer( R20A.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )
        self.r20b_struct[:] = multiply.outer( R20B.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r2eff_B14(r20a=self.r20a_struct, r20b=self.r20b_struct, pA=pA, dw=self.dw_struct, dw_orig=dw, kex=kex, ncyc=self.power, inv_tcpmg=self.inv_relax_times, tcp=self.tau_cpmg, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def calc_CR72_chi2(self, R20A=None, R20B=None, dw=None, pA=None, kex=None):
        """Calculate the chi-squared value of the Carver and Richards (1972) 2-site exchange model on all time scales.

        @keyword R20A:  The R2 value for state A in the absence of exchange.
        @type R20A:     list of float
        @keyword R20B:  The R2 value for state B in the absence of exchange.
        @type R20B:     list of float
        @keyword dw:    The chemical shift differences in ppm for each spin.
        @type dw:       list of float
        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20A and R20B to per experiment, spin and frequency.
        self.r20a_struct[:] = multiply.outer( R20A.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )
        self.r20b_struct[:] = multiply.outer( R20B.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        ## Back calculate the R2eff values.
        r2eff_CR72(r20a=self.r20a_struct, r20a_orig=R20A, r20b=self.r20b_struct, r20b_orig=R20B, pA=pA, dw=self.dw_struct, dw_orig=dw, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        ## Calculate the chi-squared statistic.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def calc_ns_cpmg_2site_3D_chi2(self, R20A=None, R20B=None, dw=None, pA=None, kex=None):
        """Calculate the chi-squared value of the 'NS CPMG 2-site' models.

        @keyword R20A:  The R2 value for state A in the absence of exchange.
        @type R20A:     list of float
        @keyword R20B:  The R2 value for state B in the absence of exchange.
        @type R20B:     list of float
        @keyword dw:    The chemical shift differences in ppm for each spin.
        @type dw:       list of float
        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20A and R20B to per experiment, spin and frequency.
        self.r20a_struct[:] = multiply.outer( R20A.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )
        self.r20b_struct[:] = multiply.outer( R20B.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r2eff_ns_cpmg_2site_3D(r180x=self.r180x, M0=self.M0, r20a=self.r20a_struct, r20b=self.r20b_struct, pA=pA, dw=self.dw_struct, dw_orig=dw, kex=kex, inv_tcpmg=self.inv_relax_times, tcp=self.tau_cpmg, back_calc=self.back_calc, num_points=self.num_disp_points, power=self.power)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        ## Calculate the chi-squared statistic.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def calc_ns_cpmg_2site_star_chi2(self, R20A=None, R20B=None, dw=None, pA=None, kex=None):
        """Calculate the chi-squared value of the 'NS CPMG 2-site star' models.

        @keyword R20A:  The R2 value for state A in the absence of exchange.
        @type R20A:     list of float
        @keyword R20B:  The R2 value for state B in the absence of exchange.
        @type R20B:     list of float
        @keyword dw:    The chemical shift differences in ppm for each spin.
        @type dw:       list of float
        @keyword pA:    The population of state A.
        @type pA:       float
        @keyword kex:   The rate of exchange.
        @type kex:      float
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20A and R20B to per experiment, spin and frequency.
        self.r20a_struct[:] = multiply.outer( R20A.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )
        self.r20b_struct[:] = multiply.outer( R20B.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r2eff_ns_cpmg_2site_star(Rr=self.Rr, Rex=self.Rex, RCS=self.RCS, R=self.R, M0=self.M0, r20a=self.r20a_struct, r20b=self.r20b_struct, pA=pA, dw=self.dw_struct, dw_orig=dw, kex=kex, inv_tcpmg=self.inv_relax_times, tcp=self.tau_cpmg, back_calc=self.back_calc, num_points=self.num_disp_points, power=self.power)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        ## Calculate the chi-squared statistic.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def calc_ns_mmq_3site_chi2(self, R20A=None, R20B=None, R20C=None, dw_AB=None, dw_BC=None, dwH_AB=None, dwH_BC=None, pA=None, pB=None, kex_AB=None, kex_BC=None, kex_AC=None):
        """Calculate the chi-squared value for the 'NS MMQ 3-site' models.

        @keyword R20A:      The R2 value for state A in the absence of exchange.
        @type R20A:         list of float
        @keyword R20B:      The R2 value for state B in the absence of exchange.
        @type R20B:         list of float
        @keyword R20C:      The R2 value for state C in the absence of exchange.
        @type R20C:         list of float
        @keyword dw_AB:     The chemical exchange difference between states A and B in rad/s.
        @type dw_AB:        float
        @keyword dw_BC:     The chemical exchange difference between states B and C in rad/s.
        @type dw_BC:        float
        @keyword dwH_AB:    The proton chemical exchange difference between states A and B in rad/s.
        @type dwH_AB:       float
        @keyword dwH_BC:    The proton chemical exchange difference between states B and C in rad/s.
        @type dwH_BC:       float
        @keyword pA:        The population of state A.
        @type pA:           float
        @keyword kex_AB:    The rate of exchange between states A and B.
        @type kex_AB:       float
        @keyword kex_BC:    The rate of exchange between states B and C.
        @type kex_BC:       float
        @keyword kex_AC:    The rate of exchange between states A and C.
        @type kex_AC:       float
        @return:            The chi-squared value.
        @rtype:             float
        """

        # Once off parameter conversions.
        pC = 1.0 - pA - pB
        pA_pB = pA + pB
        pA_pC = pA + pC
        pB_pC = pB + pC
        k_BA = pA * kex_AB / pA_pB
        k_AB = pB * kex_AB / pA_pB
        k_CB = pB * kex_BC / pB_pC
        k_BC = pC * kex_BC / pB_pC
        k_CA = pA * kex_AC / pA_pC
        k_AC = pC * kex_AC / pA_pC
        dw_AC = dw_AB + dw_BC
        dwH_AC = dwH_AB + dwH_BC

        # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
        self.M0[0] = pA
        self.M0[1] = pB
        self.M0[2] = pC

        # Initialise.
        chi2_sum = 0.0

        # Loop over the experiment types.
        for ei in range(self.num_exp):
            # Loop over the spins.
            for si in range(self.num_spins):
                # Loop over the spectrometer frequencies.
                for mi in range(self.num_frq):
                    # The R20 index.
                    r20_index = mi + ei*self.num_frq + si*self.num_frq*self.num_exp

                    # Convert dw from ppm to rad/s.
                    dw_AB_frq = dw_AB[si] * self.frqs[ei][si][mi][0][0]
                    dw_AC_frq = dw_AC[si] * self.frqs[ei][si][mi][0][0]
                    dwH_AB_frq = dwH_AB[si] * self.frqs_H[ei][si][mi][0][0]
                    dwH_AC_frq = dwH_AC[si] * self.frqs_H[ei][si][mi][0][0]

                    # Alias the dw frequency combinations.
                    aliased_dwH_AB = 0.0
                    aliased_dwH_AC = 0.0
                    if self.exp_types[ei] == EXP_TYPE_CPMG_SQ:
                        aliased_dw_AB = dw_AB_frq
                        aliased_dw_AC = dw_AC_frq
                    elif self.exp_types[ei] == EXP_TYPE_CPMG_PROTON_SQ:
                        aliased_dw_AB = dwH_AB_frq
                        aliased_dw_AC = dwH_AC_frq
                    elif self.exp_types[ei] == EXP_TYPE_CPMG_DQ:
                        aliased_dw_AB = dw_AB_frq + dwH_AB_frq
                        aliased_dw_AC = dw_AC_frq + dwH_AC_frq
                    elif self.exp_types[ei] == EXP_TYPE_CPMG_ZQ:
                        aliased_dw_AB = dw_AB_frq - dwH_AB_frq
                        aliased_dw_AC = dw_AC_frq - dwH_AC_frq
                    elif self.exp_types[ei] == EXP_TYPE_CPMG_MQ:
                        aliased_dw_AB = dw_AB_frq
                        aliased_dw_AC = dw_AC_frq
                        aliased_dwH_AB = dwH_AB_frq
                        aliased_dwH_AC = dwH_AC_frq
                    elif self.exp_types[ei] == EXP_TYPE_CPMG_PROTON_MQ:
                        aliased_dw_AB = dwH_AB_frq
                        aliased_dw_AC = dwH_AC_frq
                        aliased_dwH_AB = dw_AB_frq
                        aliased_dwH_AC = dw_AC_frq

                    # Back calculate the R2eff values for each experiment type.
                    self.r2eff_ns_mmq[ei](M0=self.M0, m1=self.m1, m2=self.m2, R20A=R20A[r20_index], R20B=R20B[r20_index], R20C=R20C[r20_index], pA=pA, pB=pB, pC=pC, dw_AB=aliased_dw_AB, dw_AC=aliased_dw_AC, dwH_AB=aliased_dwH_AB, dwH_AC=aliased_dwH_AC, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA, inv_tcpmg=self.inv_relax_times[ei][si][mi][0], tcp=self.tau_cpmg[ei][si][mi][0], back_calc=self.back_calc[ei][si][mi][0], num_points=self.num_disp_points[ei][si][mi][0], power=self.power[ei][si][mi][0])

                    # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                    for di in range(self.num_disp_points[ei][si][mi][0]):
                        if self.missing[ei][si][mi][0][di]:
                            self.back_calc[ei][si][mi][0][di] = self.values[ei][si][mi][0][di]

                    # Calculate and return the chi-squared value.
                    chi2_sum += chi2(self.values[ei][si][mi][0], self.back_calc[ei][si][mi][0], self.errors[ei][si][mi][0])

        # Return the total chi-squared value.
        return chi2_sum


    def calc_ns_r1rho_3site_chi2(self, r1rho_prime=None, dw_AB=None, dw_BC=None, pA=None, pB=None, kex_AB=None, kex_BC=None, kex_AC=None):
        """Calculate the chi-squared value for the 'NS MMQ 3-site' models.

        @keyword r1rho_prime:   The R1rho value for all states in the absence of exchange.
        @type r1rho_prime:      list of float
        @keyword dw_AB:         The chemical exchange difference between states A and B in rad/s.
        @type dw_AB:            float
        @keyword dw_BC:         The chemical exchange difference between states B and C in rad/s.
        @type dw_BC:            float
        @keyword pA:            The population of state A.
        @type pA:               float
        @keyword kex_AB:        The rate of exchange between states A and B.
        @type kex_AB:           float
        @keyword kex_BC:        The rate of exchange between states B and C.
        @type kex_BC:           float
        @keyword kex_AC:        The rate of exchange between states A and C.
        @type kex_AC:           float
        @return:                The chi-squared value.
        @rtype:                 float
        """

        # Once off parameter conversions.
        pC = 1.0 - pA - pB
        pA_pB = pA + pB
        pA_pC = pA + pC
        pB_pC = pB + pC
        k_BA = pA * kex_AB / pA_pB
        k_AB = pB * kex_AB / pA_pB
        k_CB = pB * kex_BC / pB_pC
        k_BC = pC * kex_BC / pB_pC
        k_CA = pA * kex_AC / pA_pC
        k_AC = pC * kex_AC / pA_pC
        dw_AC = dw_AB + dw_BC

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for si in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for mi in range(self.num_frq):
                # The R20 index.
                r20_index = mi + si*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_AB_frq = dw_AB[si] * self.frqs[0][si][mi][0][0]
                dw_AC_frq = dw_AC[si] * self.frqs[0][si][mi][0][0]

                # Loop over the offsets.
                for oi in range(self.num_offsets[0][si][mi]):
                    # Back calculate the R2eff values for each experiment type.
                    ns_r1rho_3site(M0=self.M0, matrix=self.matrix, r1rho_prime=r1rho_prime[r20_index], omega=self.chemical_shifts[0][si][mi][oi][0], offset=self.offset[0][si][mi][oi][0], r1=self.r1[0][si][mi][oi][0], pA=pA, pB=pB, pC=pC, dw_AB=dw_AB_frq, dw_AC=dw_AC_frq, k_AB=k_AB, k_BA=k_BA, k_BC=k_BC, k_CB=k_CB, k_AC=k_AC, k_CA=k_CA, spin_lock_fields=self.spin_lock_omega1[0][si][mi][oi], relax_time=self.relax_times[0][si][mi][oi], inv_relax_time=self.inv_relax_times[0][si][mi][oi], back_calc=self.back_calc[0][si][mi][oi], num_points=self.num_disp_points[0][si][mi][oi])

                    # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                    for di in range(self.num_disp_points[0][si][mi][oi]):
                        if self.missing[0][si][mi][oi][di]:
                            self.back_calc[0][si][mi][oi][di] = self.values[0][si][mi][oi][di]

                    # Calculate and return the chi-squared value.
                    chi2_sum += chi2(self.values[0][si][mi][oi], self.back_calc[0][si][mi][oi], self.errors[0][si][mi][oi])

        # Return the total chi-squared value.
        return chi2_sum


    def experiment_type_setup(self):
        """Check the experiment types and simplify data structures.

        For the single experiment type models, the first dimension of the values, errors, and missing data structures will be removed to simplify the target functions.
        """

        # The number of experiments.
        self.num_exp = len(self.exp_types)

        # The MMQ combined data type models.
        if self.model in MODEL_LIST_MMQ:
            # Alias the r2eff functions.
            self.r2eff_ns_mmq = []

            # Loop over the experiment types.
            for ei in range(self.num_exp):
                # SQ, DQ and ZQ data types.
                if self.exp_types[ei] in [EXP_TYPE_CPMG_SQ, EXP_TYPE_CPMG_PROTON_SQ, EXP_TYPE_CPMG_DQ, EXP_TYPE_CPMG_ZQ]:
                    if self.model == MODEL_NS_MMQ_2SITE:
                        self.r2eff_ns_mmq.append(r2eff_ns_mmq_2site_sq_dq_zq)
                    else:
                        self.r2eff_ns_mmq.append(r2eff_ns_mmq_3site_sq_dq_zq)

                # MQ data types.
                elif self.exp_types[ei] in [EXP_TYPE_CPMG_MQ, EXP_TYPE_CPMG_PROTON_MQ]:
                    if self.model == MODEL_NS_MMQ_2SITE:
                        self.r2eff_ns_mmq.append(r2eff_ns_mmq_2site_mq)
                    else:
                        self.r2eff_ns_mmq.append(r2eff_ns_mmq_3site_mq)

        # The single data type models.
        else:
            # Check that the data is correct.
            if self.model != MODEL_NOREX and self.model in MODEL_LIST_CPMG and self.exp_types[0] != EXP_TYPE_CPMG_SQ:
                raise RelaxError("The '%s' CPMG model is not compatible with the '%s' experiment type." % (self.model, self.exp_types[0]))
            if self.model != MODEL_NOREX and self.model in MODEL_LIST_R1RHO and self.exp_types[0] != EXP_TYPE_R1RHO:
                raise RelaxError("The '%s' R1rho model is not compatible with the '%s' experiment type." % (self.model, self.exp_types[0]))
            if self.model != MODEL_NOREX and self.model in MODEL_LIST_MQ_CPMG and self.exp_types[0] != EXP_TYPE_CPMG_MQ:
                raise RelaxError("The '%s' CPMG model is not compatible with the '%s' experiment type." % (self.model, self.exp_types[0]))


    def func_B14(self, params):
        """Target function for the Baldwin (2014) 2-site exact solution model for all time scales, whereby the simplification R20A = R20B is assumed.

        This assumes that pA > pB, and hence this must be implemented as a constraint.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Calculate and return the chi-squared value.
        return self.calc_B14_chi2(R20A=R20, R20B=R20, dw=dw, pA=pA, kex=kex)


    def func_B14_full(self, params):
        """Target function for the Baldwin (2014) 2-site exact solution model for all time scales.

        This assumes that pA > pB, and hence this must be implemented as a constraint.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[1]].reshape(self.num_spins*2, self.num_frq)
        R20A = R20[::2].flatten()
        R20B = R20[1::2].flatten()
        dw = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Calculate and return the chi-squared value.
        return self.calc_B14_chi2(R20A=R20A, R20B=R20B, dw=dw, pA=pA, kex=kex)


    def func_CR72(self, params):
        """Target function for the reduced Carver and Richards (1972) 2-site exchange model on all time scales.

        This assumes that pA > pB, and hence this must be implemented as a constraint.  For this model, the simplification R20A = R20B is assumed.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Calculate and return the chi-squared value.
        return self.calc_CR72_chi2(R20A=R20, R20B=R20, dw=dw, pA=pA, kex=kex)


    def func_CR72_full(self, params):
        """Target function for the full Carver and Richards (1972) 2-site exchange model on all time scales.

        This assumes that pA > pB, and hence this must be implemented as a constraint.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[1]].reshape(self.num_spins*2, self.num_frq)
        R20A = R20[::2].flatten()
        R20B = R20[1::2].flatten()
        dw = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Calculate and return the chi-squared value.
        return self.calc_CR72_chi2(R20A=R20A, R20B=R20B, dw=dw, pA=pA, kex=kex)


    def func_DPL94(self, params):
        """Target function for the Davis, Perlman and London (1994) fast 2-site off-resonance exchange model for R1rho-type experiments.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Convert phi_ex from ppm^2 to (rad/s)^2. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( phi_ex.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs_squared, out=self.phi_ex_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r1rho_DPL94(r1rho_prime=self.r20_struct, phi_ex=self.phi_ex_struct, kex=kex, theta=self.tilt_angles, R1=self.r1, spin_lock_fields2=self.spin_lock_omega1_squared, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_IT99(self, params):
        """Target function for the Ishima and Torchia (1999) 2-site model for all timescales with pA >> pB.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        tex = params[self.end_index[1]+1]

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r2eff_IT99(r20=self.r20_struct, pA=pA, dw=self.dw_struct, dw_orig=dw, tex=tex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_LM63_3site(self, params):
        """Target function for the Luz and Meiboom (1963) fast 3-site exchange model.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex_B = params[self.end_index[0]:self.end_index[1]]
        phi_ex_C = params[self.end_index[1]:self.end_index[2]]
        kB = params[self.end_index[2]]
        kC = params[self.end_index[2]+1]

        # Once off parameter conversions.
        rex_B = phi_ex_B / kB
        rex_C = phi_ex_C / kC
        quart_kB = kB / 4.0
        quart_kC = kC / 4.0

        # Initialise.
        chi2_sum = 0.0

        # Loop over the spins.
        for si in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for mi in range(self.num_frq):
                # The R20 index.
                r20_index = mi + si*self.num_frq

                # Convert phi_ex (or rex) from ppm^2 to (rad/s)^2.
                rex_B_scaled = rex_B[si] * self.frqs_squared[0][si][mi][0][0]
                rex_C_scaled = rex_C[si] * self.frqs_squared[0][si][mi][0][0]

                # Back calculate the R2eff values.
                r2eff_LM63_3site(r20=R20[r20_index], rex_B=rex_B_scaled, rex_C=rex_C_scaled, quart_kB=quart_kB, quart_kC=quart_kC, cpmg_frqs=self.cpmg_frqs[0][si][mi][0], back_calc=self.back_calc[0][si][mi][0], num_points=self.num_disp_points[0][si][mi][0])

                # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                for di in range(self.num_disp_points[0][si][mi][0]):
                    if self.missing[0][si][mi][0][di]:
                        self.back_calc[0][si][mi][0][di] = self.values[0][si][mi][0][di]

                # Calculate and return the chi-squared value.
                chi2_sum += chi2(self.values[0][si][mi][0], self.back_calc[0][si][mi][0], self.errors[0][si][mi][0])

        # Return the total chi-squared value.
        return chi2_sum


    def func_LM63(self, params):
        """Target function for the Luz and Meiboom (1963) fast 2-site exchange model.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Convert phi_ex from ppm^2 to (rad/s)^2. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( phi_ex.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs_squared, out=self.phi_ex_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r2eff_LM63(r20=self.r20_struct, phi_ex=self.phi_ex_struct, kex=kex, cpmg_frqs=self.cpmg_frqs, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_M61(self, params):
        """Target function for the Meiboom (1961) fast 2-site exchange model for R1rho-type experiments.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        phi_ex = params[self.end_index[0]:self.end_index[1]]
        kex = params[self.end_index[1]]

        # Convert phi_ex from ppm^2 to (rad/s)^2. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( phi_ex.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs_squared, out=self.phi_ex_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r1rho_M61(r1rho_prime=self.r20_struct, phi_ex=self.phi_ex_struct, kex=kex, spin_lock_fields2=self.spin_lock_omega1_squared, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_M61b(self, params):
        """Target function for the Meiboom (1961) R1rho on-resonance 2-site model for skewed populations (pA >> pB).

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R1rho values.
        r1rho_M61b(r1rho_prime=self.r20_struct, pA=pA, dw=self.dw_struct, kex=kex, spin_lock_fields2=self.spin_lock_omega1_squared, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_MP05(self, params):
        """Target function for the Miloushev and Palmer (2005) R1rho off-resonance 2-site model.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R1rho values.
        r1rho_MP05(r1rho_prime=self.r20_struct, omega=self.chemical_shifts, offset=self.offset, pA=pA, dw=self.dw_struct, kex=kex, R1=self.r1, spin_lock_fields=self.spin_lock_omega1, spin_lock_fields2=self.spin_lock_omega1_squared, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_mmq_CR72(self, params):
        """Target function for the CR72 model extended for MQ CPMG data.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        dwH = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Once off parameter conversions.
        pB = 1.0 - pA
        k_BA = pA * kex
        k_AB = pB * kex

        # Convert dw and dwH from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )
        multiply( multiply.outer( dwH.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs_H, out=self.dwH_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Initialise.
        chi2_sum = 0.0

        # Loop over the experiment types.
        for ei in range(self.num_exp):

            r20 = self.r20_struct[ei]
            dw_frq = self.dw_struct[ei]
            dwH_frq = self.dwH_struct[ei]

            # Alias the dw frequency combinations.
            aliased_dwH = 0.0
            if self.exp_types[ei] == EXP_TYPE_CPMG_SQ:
                aliased_dw = dw_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_PROTON_SQ:
                aliased_dw = dwH_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_DQ:
                aliased_dw = dw_frq + dwH_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_ZQ:
                aliased_dw = dw_frq - dwH_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_MQ:
                aliased_dw = dw_frq
                aliased_dwH = dwH_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_PROTON_MQ:
                aliased_dw = dwH_frq
                aliased_dwH = dw_frq

            # Back calculate the R2eff values.
            r2eff_mmq_cr72(r20=r20, pA=pA, pB=pB, dw=aliased_dw, dwH=aliased_dwH, kex=kex, k_AB=k_AB, k_BA=k_BA, cpmg_frqs=self.cpmg_frqs[ei], inv_tcpmg=self.inv_relax_times[ei], tcp=self.tau_cpmg[ei], back_calc=self.back_calc[ei])

            # Clean the data for all values, which is left over at the end of arrays.
            self.back_calc[ei] = self.back_calc[ei]*self.disp_struct[ei]

            # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
            if self.has_missing:
                # Replace with values.
                mask_replace_blank_ei = masked_equal(self.missing[ei], 1.0)
                self.back_calc[ei][mask_replace_blank_ei.mask] = self.values[ei][mask_replace_blank_ei.mask]

            # Calculate and return the chi-squared value.
            chi2_sum += chi2_rankN(self.values[ei], self.back_calc[ei], self.errors[ei])

        # Return the total chi-squared value.
        return chi2_sum


    def func_NOREX(self, params):
        """Target function for no exchange.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params

        # Reshape R20 to per experiment, spin and frequency.
        self.back_calc[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_ns_cpmg_2site_3D(self, params):
        """Target function for the reduced numerical solution for the 2-site Bloch-McConnell equations.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Calculate and return the chi-squared value.
        return self.calc_ns_cpmg_2site_3D_chi2(R20A=R20, R20B=R20, dw=dw, pA=pA, kex=kex)


    def func_ns_cpmg_2site_3D_full(self, params):
        """Target function for the full numerical solution for the 2-site Bloch-McConnell equations.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[1]].reshape(self.num_spins*2, self.num_frq)
        R20A = R20[::2].flatten()
        R20B = R20[1::2].flatten()
        dw = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Calculate and return the chi-squared value.
        return self.calc_ns_cpmg_2site_3D_chi2(R20A=R20A, R20B=R20B, dw=dw, pA=pA, kex=kex)


    def func_ns_cpmg_2site_expanded(self, params):
        """Target function for the numerical solution for the 2-site Bloch-McConnell equations using the expanded notation.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20A and R20B to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r2eff_ns_cpmg_2site_expanded(r20=self.r20_struct, pA=pA, dw=self.dw_struct, dw_orig=dw, kex=kex, relax_time=self.relax_times, inv_relax_time=self.inv_relax_times, tcp=self.tau_cpmg, back_calc=self.back_calc, num_cpmg=self.power)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        ## Calculate the chi-squared statistic.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_ns_cpmg_2site_star(self, params):
        """Target function for the reduced numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices.

        This is the model whereby the simplification R20A = R20B is assumed.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Calculate and return the chi-squared value.
        return self.calc_ns_cpmg_2site_star_chi2(R20A=R20, R20B=R20, dw=dw, pA=pA, kex=kex)


    def func_ns_cpmg_2site_star_full(self, params):
        """Target function for the full numerical solution for the 2-site Bloch-McConnell equations using complex conjugate matrices.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[1]].reshape(self.num_spins*2, self.num_frq)
        R20A = R20[::2].flatten()
        R20B = R20[1::2].flatten()
        dw = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Calculate and return the chi-squared value.
        return self.calc_ns_cpmg_2site_star_chi2(R20A=R20A, R20B=R20B, dw=dw, pA=pA, kex=kex)


    def func_ns_mmq_2site(self, params):
        """Target function for the combined SQ, ZQ, DQ and MQ CPMG numeric solution.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        dwH = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex = params[self.end_index[2]+1]

        # Once off parameter conversions.
        pB = 1.0 - pA
        k_BA = pA * kex
        k_AB = pB * kex

        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )
        multiply( multiply.outer( dwH.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs_H, out=self.dwH_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # This is a vector that contains the initial magnetizations corresponding to the A and B state transverse magnetizations.
        self.M0[0] = pA
        self.M0[1] = pB

        # Initialise.
        chi2_sum = 0.0

        # Loop over the experiment types.
        for ei in range(self.num_exp):

            r20 = self.r20_struct[ei]
            dw_frq = self.dw_struct[ei]
            dwH_frq = self.dwH_struct[ei]

            # Alias the dw frequency combinations.
            aliased_dwH = 0.0
            if self.exp_types[ei] == EXP_TYPE_CPMG_SQ:
                aliased_dw = dw_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_PROTON_SQ:
                aliased_dw = dwH_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_DQ:
                aliased_dw = dw_frq + dwH_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_ZQ:
                aliased_dw = dw_frq - dwH_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_MQ:
                aliased_dw = dw_frq
                aliased_dwH = dwH_frq
            elif self.exp_types[ei] == EXP_TYPE_CPMG_PROTON_MQ:
                aliased_dw = dwH_frq
                aliased_dwH = dw_frq

            # Back calculate the R2eff values for each experiment type.
            self.r2eff_ns_mmq[ei](M0=self.M0, m1=self.m1, m2=self.m2, R20A=r20, R20B=r20, pA=pA, pB=pB, dw=aliased_dw, dwH=aliased_dwH, k_AB=k_AB, k_BA=k_BA, inv_tcpmg=self.inv_relax_times[ei], tcp=self.tau_cpmg[ei], back_calc=self.back_calc[ei], num_points=self.num_disp_points[ei], power=self.power[ei])

            # Clean the data for all values, which is left over at the end of arrays.
            self.back_calc[ei] = self.back_calc[ei]*self.disp_struct[ei]

            # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
            if self.has_missing:
                # Replace with values.
                mask_replace_blank_ei = masked_equal(self.missing[ei], 1.0)
                self.back_calc[ei][mask_replace_blank_ei.mask] = self.values[ei][mask_replace_blank_ei.mask]

            # Calculate and return the chi-squared value.
            chi2_sum += chi2_rankN(self.values[ei], self.back_calc[ei], self.errors[ei])

        # Return the total chi-squared value.
        return chi2_sum


    def func_ns_mmq_3site(self, params):
        """Target function for the combined SQ, ZQ, DQ and MQ 3-site MMQ CPMG numeric solution.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw_AB = params[self.end_index[0]:self.end_index[1]]
        dw_BC = params[self.end_index[1]:self.end_index[2]]
        dwH_AB = params[self.end_index[2]:self.end_index[3]]
        dwH_BC = params[self.end_index[3]:self.end_index[4]]
        pA = params[self.end_index[4]]
        kex_AB = params[self.end_index[4]+1]
        pB = params[self.end_index[4]+2]
        kex_BC = params[self.end_index[4]+3]
        kex_AC = params[self.end_index[4]+4]

        # Calculate and return the chi-squared value.
        return self.calc_ns_mmq_3site_chi2(R20A=R20, R20B=R20, R20C=R20, dw_AB=dw_AB, dw_BC=dw_BC, dwH_AB=dwH_AB, dwH_BC=dwH_BC, pA=pA, pB=pB, kex_AB=kex_AB, kex_BC=kex_BC, kex_AC=kex_AC)


    def func_ns_mmq_3site_linear(self, params):
        """Target function for the combined SQ, ZQ, DQ and MQ 3-site linearised MMQ CPMG numeric solution.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw_AB = params[self.end_index[0]:self.end_index[1]]
        dw_BC = params[self.end_index[1]:self.end_index[2]]
        dwH_AB = params[self.end_index[2]:self.end_index[3]]
        dwH_BC = params[self.end_index[3]:self.end_index[4]]
        pA = params[self.end_index[4]]
        kex_AB = params[self.end_index[4]+1]
        pB = params[self.end_index[4]+2]
        kex_BC = params[self.end_index[4]+3]

        # Calculate and return the chi-squared value.
        return self.calc_ns_mmq_3site_chi2(R20A=R20, R20B=R20, R20C=R20, dw_AB=dw_AB, dw_BC=dw_BC, dwH_AB=dwH_AB, dwH_BC=dwH_BC, pA=pA, pB=pB, kex_AB=kex_AB, kex_BC=kex_BC, kex_AC=0.0)


    def func_ns_r1rho_2site(self, params):
        """Target function for the reduced numerical solution for the 2-site Bloch-McConnell equations for R1rho data.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        r1rho_prime = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Once off parameter conversions.
        pB = 1.0 - pA
        k_BA = pA * kex
        k_AB = pB * kex

        # Chi-squared initialisation.
        chi2_sum = 0.0

        # Loop over the spins.
        for si in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for mi in range(self.num_frq):
                # The R20 index.
                r20_index = mi + si*self.num_frq

                # Convert dw from ppm to rad/s.
                dw_frq = dw[si] * self.frqs[0][si][mi][0][0]

                # Loop over the offsets.
                for oi in range(self.num_offsets[0][si][mi]):
                    # Back calculate the R2eff values.
                    ns_r1rho_2site(M0=self.M0, matrix=self.matrix, r1rho_prime=r1rho_prime[r20_index], omega=self.chemical_shifts[0][si][mi][oi][0], offset=self.offset[0][si][mi][oi][0], r1=self.r1[0][si][mi][oi][0], pA=pA, pB=pB, dw=dw_frq, k_AB=k_AB, k_BA=k_BA, spin_lock_fields=self.spin_lock_omega1[0][si][mi][oi], relax_time=self.relax_times[0][si][mi][oi], inv_relax_time=self.inv_relax_times[0][si][mi][oi], back_calc=self.back_calc[0][si][mi][oi], num_points=self.num_disp_points[0][si][mi][oi])

                    # For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
                    for di in range(self.num_disp_points[0][si][mi][oi]):
                        if self.missing[0][si][mi][oi][di]:
                            self.back_calc[0][si][mi][oi][di] = self.values[0][si][mi][oi][di]

                    # Calculate and return the chi-squared value.
                    chi2_sum += chi2(self.values[0][si][mi][oi], self.back_calc[0][si][mi][oi], self.errors[0][si][mi][oi])

        # Return the total chi-squared value.
        return chi2_sum


    def func_ns_r1rho_3site(self, params):
        """Target function for the R1rho 3-site numeric solution.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        r1rho_prime = params[:self.end_index[0]]
        dw_AB = params[self.end_index[0]:self.end_index[1]]
        dw_BC = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex_AB = params[self.end_index[2]+1]
        pB = params[self.end_index[2]+2]
        kex_BC = params[self.end_index[2]+3]
        kex_AC = params[self.end_index[2]+4]

        # Calculate and return the chi-squared value.
        return self.calc_ns_r1rho_3site_chi2(r1rho_prime=r1rho_prime, dw_AB=dw_AB, dw_BC=dw_BC, pA=pA, pB=pB, kex_AB=kex_AB, kex_BC=kex_BC, kex_AC=kex_AC)


    def func_ns_r1rho_3site_linear(self, params):
        """Target function for the R1rho 3-site numeric solution linearised with kAC = kCA = 0.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        r1rho_prime = params[:self.end_index[0]]
        dw_AB = params[self.end_index[0]:self.end_index[1]]
        dw_BC = params[self.end_index[1]:self.end_index[2]]
        pA = params[self.end_index[2]]
        kex_AB = params[self.end_index[2]+1]
        pB = params[self.end_index[2]+2]
        kex_BC = params[self.end_index[2]+3]

        # Calculate and return the chi-squared value.
        return self.calc_ns_r1rho_3site_chi2(r1rho_prime=r1rho_prime, dw_AB=dw_AB, dw_BC=dw_BC, pA=pA, pB=pB, kex_AB=kex_AB, kex_BC=kex_BC, kex_AC=0.0)


    def func_TAP03(self, params):
        """Target function for the Trott, Abergel and Palmer (2003) R1rho off-resonance 2-site model.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R1rho values.
        r1rho_TAP03(r1rho_prime=self.r20_struct, omega=self.chemical_shifts, offset=self.offset, pA=pA, dw=self.dw_struct, kex=kex, R1=self.r1, spin_lock_fields=self.spin_lock_omega1, spin_lock_fields2=self.spin_lock_omega1_squared, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_TP02(self, params):
        """Target function for the Trott and Palmer (2002) R1rho off-resonance 2-site model.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20 = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        pA = params[self.end_index[1]]
        kex = params[self.end_index[1]+1]

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20 to per experiment, spin and frequency.
        self.r20_struct[:] = multiply.outer( R20.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R1rho values.
        r1rho_TP02(r1rho_prime=self.r20_struct, omega=self.chemical_shifts, offset=self.offset, pA=pA, dw=self.dw_struct, kex=kex, R1=self.r1, spin_lock_fields=self.spin_lock_omega1, spin_lock_fields2=self.spin_lock_omega1_squared, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)


    def func_TSMFK01(self, params):
        """Target function for the the Tollinger et al. (2001) 2-site very-slow exchange model, range of microsecond to second time scale.

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 float array
        @return:        The chi-squared value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Unpack the parameter values.
        R20A = params[:self.end_index[0]]
        dw = params[self.end_index[0]:self.end_index[1]]
        k_AB = params[self.end_index[1]]

        # Convert dw from ppm to rad/s. Use the out argument, to pass directly to structure.
        multiply( multiply.outer( dw.reshape(1, self.NS), self.nm_no_nd_ones ), self.frqs, out=self.dw_struct )

        # Reshape R20A and R20B to per experiment, spin and frequency.
        self.r20a_struct[:] = multiply.outer( R20A.reshape(self.NE, self.NS, self.NM), self.no_nd_ones )

        # Back calculate the R2eff values.
        r2eff_TSMFK01(r20a=self.r20a_struct, dw=self.dw_struct, dw_orig=dw, k_AB=k_AB, tcp=self.tau_cpmg, back_calc=self.back_calc)

        # Clean the data for all values, which is left over at the end of arrays.
        self.back_calc = self.back_calc*self.disp_struct

        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        if self.has_missing:
            # Replace with values.
            self.back_calc[self.mask_replace_blank.mask] = self.values[self.mask_replace_blank.mask]

        # Return the total chi-squared value.
        return chi2_rankN(self.values, self.back_calc, self.errors)
