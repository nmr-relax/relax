###############################################################################
#                                                                             #
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

# Python module imports.
from copy import deepcopy
from numpy import array, arange, asarray, int32, float64, max, ones, pi, zeros
from unittest import TestCase

# relax module imports.
from lib.dispersion.cr72 import r2eff_CR72

"""The 1H gyromagnetic ratio."""
g1H = 26.7522212 * 1e7

"""The 15N gyromagnetic ratio."""
g15N = -2.7126 * 1e7


class Test_cr72_full_cluster_one_field(TestCase):
    """Unit tests for the lib.dispersion.cr72 relax module."""

    def setUp(self):
        """Set up for all unit tests."""

        # Default parameter values.
        self.r2 = None
        self.r2a = 5.0
        self.r2b = 10.0
        self.dw = 3.0
        self.pA = 0.9
        self.kex = 1000.0
        self.spins_params = ['r2a', 'r2b', 'dw', 'pA', 'kex']

        # Define parameters
        self.model = "CR72 full"
        self.num_spins = 2
        self.fields = array([800. * 1E6])
        #self.fields = array([600. * 1E6, 800. * 1E6])
        #self.fields = array([600. * 1E6, 800. * 1E6, 900. * 1E6])
        self.exp_type = ['SQ CPMG']
        self.offset = [0]

        # Required data structures.
        self.relax_times = self.fields / (100 * 100. *1E6 )
        self.ncycs = []
        self.points = []
        self.value = []
        self.error = []
        self.num_disp_points = []

        for i in range(len(self.fields)):
            ncyc = arange(2, 1000. * self.relax_times[i], 4)
            #ncyc = arange(2, 42, 2)
            self.ncycs.append(ncyc)
            #print("sfrq: ", self.fields[i], "number of cpmg frq", len(ncyc), ncyc)

            cpmg_point = ncyc / self.relax_times[i]

            nr_cpmg_points = len(cpmg_point)
            self.num_disp_points.append(nr_cpmg_points)

            self.points.append(list(cpmg_point))
            self.value.append([2.0]*len(cpmg_point))
            self.error.append([1.0]*len(cpmg_point))


    def calc_r2eff(self):
        """Calculate and check the R2eff values."""

        # Assemble param vector.
        self.params = self.assemble_param_vector(r2=self.r2, r2a=self.r2a, r2b=self.r2b, dw=self.dw, pA=self.pA, kex=self.kex, spins_params=self.spins_params)

        # Make nested list arrays of data. And return them.
        values, errors, cpmg_frqs, missing, frqs, exp_types, relax_times, offsets = self.return_r2eff_arrays()

        # Unpack the parameter values.
        # Initialise the post spin parameter indices.
        end_index = []
        # The spin and frequency dependent R2 parameters.
        end_index.append(len(self.exp_type) * self.num_spins * len(self.fields))
        if self.model in ["CR72 full"]:
            end_index.append(2 * len(self.exp_type) * self.num_spins * len(self.fields))
        # The spin and dependent parameters (phi_ex, dw, padw2).
        end_index.append(end_index[-1] + self.num_spins)

        # Unpack the parameter values.
        R20 = self.params[:end_index[1]].reshape(self.num_spins*2, len(self.fields))
        R20A = R20[::2].flatten()
        R20B = R20[1::2].flatten()
        dw = self.params[end_index[1]:end_index[2]]
        pA = self.params[end_index[2]]
        kex = self.params[end_index[2]+1]

        # Copy value structure
        self.back_calc = deepcopy(values)

        # Setup special numpy array structures, for higher dimensional computation.
        # Get the shape of back_calc structure.
        back_calc_shape = list( asarray(self.back_calc).shape )[:4]

        # Find which frequency has the maximum number of disp points.
        # To let the numpy array operate well together, the broadcast size has to be equal for all shapes.
        self.max_num_disp_points = max(self.num_disp_points)

        # Create numpy arrays to pass to the lib function.
        # All numpy arrays have to have same shape to allow to multiply together.
        # The dimensions should be [ei][si][mi][oi][di]. [Experiment][spins][spec. frq][offset][disp points].
        # The number of disp point can change per spectrometer, so we make the maximum size.
        self.R20A_a = ones(back_calc_shape + [self.max_num_disp_points])
        self.R20B_a = ones(back_calc_shape + [self.max_num_disp_points])
        self.dw_frq_a = ones(back_calc_shape + [self.max_num_disp_points])
        self.cpmg_frqs_a = ones(back_calc_shape + [self.max_num_disp_points])
        self.num_disp_points_a = ones(back_calc_shape + [self.max_num_disp_points])
        self.back_calc_a = ones(back_calc_shape + [self.max_num_disp_points])

        # Loop over the spins.
        for si in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for mi in range(len(self.fields)):
                # Extract number of dispersion points.
                num_disp_points = self.num_disp_points[mi]

                # Extract cpmg_frqs and num_disp_points from lists.
                self.cpmg_frqs_a[0][si][mi][0][:num_disp_points] = cpmg_frqs[0][mi][0]
                self.num_disp_points_a[0][si][mi][0][:num_disp_points] = self.num_disp_points[mi]

        # Now calculate.

        # Loop over the spins.
        for si in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for mi in range(len(self.fields)):
                # Extract number of dispersion points.
                num_disp_points = len(cpmg_frqs[0][mi][0])

                # The R20 index.
                r20_index = mi + si*len(self.fields)

                # Store r20a and r20b values per disp point.
                self.R20A_a[0][si][mi][0] = array( [R20A[r20_index]] * self.max_num_disp_points, float64)
                self.R20B_a[0][si][mi][0] = array( [R20B[r20_index]] * self.max_num_disp_points, float64)

                # Convert dw from ppm to rad/s.
                dw_frq = dw[si] * frqs[0][si][mi]

                # Store dw_frq per disp point.
                self.dw_frq_a[0][si][mi][0] = array( [dw_frq] * self.max_num_disp_points, float64)

        ## Back calculate the R2eff values.
        r2eff_CR72(r20a_orig=self.R20A_a, r20b_orig=self.R20B_a, dw_orig=self.dw_frq_a, r20a=self.R20A_a, r20b=self.R20B_a, pA=pA, dw=self.dw_frq_a, kex=kex, cpmg_frqs=self.cpmg_frqs_a, back_calc=self.back_calc_a)

        # Now return the values back to the structure of self.back_calc object.
        ## For all missing data points, set the back-calculated value to the measured values so that it has no effect on the chi-squared value.
        # Loop over the spins.
        for si in range(self.num_spins):
            # Loop over the spectrometer frequencies.
            for mi in range(len(self.fields)):
                # Extract number of dispersion points.
                num_disp_points = self.num_disp_points[mi]

                # Extract the value
                self.back_calc[0][si][mi][0][:] = self.back_calc_a[0][si][mi][0][:num_disp_points]

                # Check values.
                for di in range(num_disp_points):
                    self.assertAlmostEqual(self.back_calc[0][si][mi][0][di], self.R20A_a[0][si][mi][0][di])


    def return_r2eff_arrays(self):
        """Return numpy arrays of the R2eff/R1rho values and errors.

        @return:    The numpy array structures of the R2eff/R1rho values, errors, missing data, and corresponding Larmor frequencies.  For each structure, the first dimension corresponds to the experiment types, the second the spins of a spin block, the third to the spectrometer field strength, and the fourth is the dispersion points.  For the Larmor frequency structure, the fourth dimension is omitted.  For R1rho-type data, an offset dimension is inserted between the spectrometer field strength and the dispersion points.
        @rtype:     lists of numpy float arrays, lists of numpy float arrays, lists of numpy float arrays, numpy rank-2 int array
        """

        # Initialise the data structures for the target function.
        exp_types = []
        values = []
        errors = []
        missing = []
        frqs = []
        frqs_H = []
        relax_times = []
        offsets = []
        for ei in range(len(self.exp_type)):
            values.append([])
            errors.append([])
            missing.append([])
            frqs.append([])
            frqs_H.append([])
            relax_times.append([])
            offsets.append([])
            for si in range(self.num_spins):
                values[ei].append([])
                errors[ei].append([])
                missing[ei].append([])
                frqs[ei].append([])
                frqs_H[ei].append([])
                offsets[ei].append([])
                for mi in range(len(self.fields)):
                    values[ei][si].append([])
                    errors[ei][si].append([])
                    missing[ei][si].append([])
                    frqs[ei][si].append(0.0)
                    frqs_H[ei][si].append(0.0)
                    offsets[ei][si].append([])
                    for oi in range(len(self.offset)):
                        values[ei][si][mi].append([])
                        errors[ei][si][mi].append([])
                        missing[ei][si][mi].append([])
                        offsets[ei][si][mi].append([])
            for mi in range(len(self.fields)):
                relax_times[ei].append(None)

        cpmg_frqs = []
        for ei in range(len(self.exp_type)):
            cpmg_frqs.append([])
            for mi in range(len(self.fields)):
                cpmg_frqs[ei].append([])
                for oi in range(len(self.offset)):
                    #cpmg_frqs[ei][mi].append(self.points)
                    cpmg_frqs[ei][mi].append([])


        # Pack the R2eff/R1rho data.
        si = 0
        for spin_index in range(self.num_spins):
            data_flag = True

            for ei in range(len(self.exp_type)):
                exp_type = self.exp_type[ei]
                # Add the experiment type.
                if exp_type not in exp_types:
                    exp_types.append(exp_type)

                for mi in range(len(self.fields)):
                    # Get the frq.
                    frq = self.fields[mi]

                    # The Larmor frequency for this spin (and that of an attached proton for the MMQ models) and field strength (in MHz*2pi to speed up the ppm to rad/s conversion).
                    frqs[ei][si][mi] = 2.0 * pi * frq / g1H * g15N * 1e-6

                    # Get the cpmg frq.
                    cpmg_frqs[ei][mi][oi] = self.points[mi]

                    for oi in range(len(self.offset)):
                        for di in range(len(self.points[mi])):

                            missing[ei][si][mi][oi].append(0)

                            # Values
                            values[ei][si][mi][oi].append(self.value[mi][di])
                            # The errors.
                            errors[ei][si][mi][oi].append(self.error[mi][di])

                            # The relaxation times.
                            # Found.
                            relax_time = self.relax_times[mi]

                            # Store the time.
                            relax_times[ei][mi] = relax_time

            # Increment the spin index.
            si += 1

        # Convert to numpy arrays.
        relax_times = array(relax_times, float64)
        for ei in range(len(self.exp_type)):
            for si in range(self.num_spins):
                for mi in range(len(self.fields)):
                    for oi in range(len(self.offset)):
                        values[ei][si][mi][oi] = array(values[ei][si][mi][oi], float64)
                        errors[ei][si][mi][oi] = array(errors[ei][si][mi][oi], float64)
                        missing[ei][si][mi][oi] = array(missing[ei][si][mi][oi], int32)

        # Return the structures.
        return values, errors, cpmg_frqs, missing, frqs, exp_types, relax_times, offsets


    def assemble_param_vector(self, r2=None, r2a=None, r2b=None, dw=None, pA=None, kex=None, spins_params=None):
        """Assemble the dispersion relaxation dispersion curve fitting parameter vector.

        @keyword r2:            The transversal relaxation rate.
        @type r2:               float
        @keyword r2a:           The transversal relaxation rate for state A in the absence of exchange.
        @type r2a:              float
        @keyword r2b:           The transversal relaxation rate for state B in the absence of exchange.
        @type r2b:              float
        @keyword dw:            The chemical exchange difference between states A and B in ppm.
        @type dw:               float
        @keyword pA:            The population of state A.
        @type pA:               float
        @keyword kex:           The rate of exchange.
        @type kex:              float
        @keyword spins_params:  List of parameter strings used in dispersion model.
        @type spins_params:     array of strings
        @return:                An array of the parameter values of the dispersion relaxation model.
        @rtype:                 numpy float array
        """

        # Initialise.
        param_vector = []

        # Loop over the parameters of the cluster.
        for param_name, spin_index, mi in self.loop_parameters(spins_params=spins_params):
            if param_name == 'r2':
                value = r2
                value = value + mi + spin_index*0.1
            elif param_name == 'r2a':
                value = r2a
                value = value + mi+ spin_index*0.1
            elif param_name == 'r2b':
                value = r2b
                value = value + mi + spin_index*0.1
            elif param_name == 'dw':
                value = dw
            elif param_name == 'pA':
                value = pA
            elif param_name == 'kex':
                value = kex

            # Add to the vector.
            param_vector.append(value)

        # Return a numpy array.
        return array(param_vector, float64)


    def loop_parameters(self, spins_params=None):
        """Generator function for looping of the parameters of the cluster.

        @keyword spins_params:  List of parameter strings used in dispersion model.
        @type spins_params:     array of strings
        @return:                The parameter name.
        @rtype:                 str
        """

        # Loop over the parameters of the cluster.
        # First the R2 parameters (one per spin per field strength).
        for spin_index in range(self.num_spins):

            # The R2 parameter.
            if 'r2' in spins_params:
                for ei in range(len(self.exp_type)):
                    for mi in range(len(self.fields)):
                        yield 'r2', spin_index, mi

            # The R2A parameter.
            if 'r2a' in spins_params:
                for ei in range(len(self.exp_type)):
                    for mi in range(len(self.fields)):
                        yield 'r2a', spin_index, mi


            # The R2B parameter.
            if 'r2b' in spins_params:
                for ei in range(len(self.exp_type)):
                    for mi in range(len(self.fields)):
                        yield 'r2b', spin_index, mi


        # Then the chemical shift difference parameters 'phi_ex', 'phi_ex_B', 'phi_ex_C', 'padw2', 'dw', 'dw_AB', 'dw_BC', 'dw_AB' (one per spin).
        for spin_index in range(self.num_spins):

            if 'dw' in spins_params:
                yield 'dw', spin_index, 0

        # All other parameters (one per spin cluster).
        for param in spins_params:
            if not param in ['r2', 'r2a', 'r2b', 'phi_ex', 'phi_ex_B', 'phi_ex_C', 'padw2', 'dw', 'dw_AB', 'dw_BC', 'dw_AB', 'dwH', 'dwH_AB', 'dwH_BC', 'dwH_AB']:
                if param == 'pA':
                    yield 'pA', 0, 0
                elif param == 'kex':
                    yield 'kex', 0, 0


    def test_cr72_full_cluster_one_field_no_rex1(self):
        """Test the r2eff_cr72() function for no exchange when dw = 0.0."""

        # Parameter reset.
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_cr72_full_cluster_one_field_no_rex2(self):
        """Test the r2eff_cr72() function for no exchange when pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_cr72_full_cluster_one_field_no_rex3(self):
        """Test the r2eff_cr72() function for no exchange when kex = 0.0."""

        # Parameter reset.
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_cr72_full_cluster_one_field_no_rex4(self):
        """Test the r2eff_cr72() function for no exchange when dw = 0.0 and pA = 1.0."""

        # Parameter reset.
        self.pA = 1.0
        self.dw = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_cr72_full_cluster_one_field_no_rex5(self):
        """Test the r2eff_cr72() function for no exchange when dw = 0.0 and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_cr72_full_cluster_one_field_no_rex6(self):
        """Test the r2eff_cr72() function for no exchange when pA = 1.0 and kex = 0.0."""

        # Parameter reset.
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_cr72_full_cluster_one_field_no_rex7(self):
        """Test the r2eff_cr72() function for no exchange when dw = 0.0, pA = 1.0, and kex = 0.0."""

        # Parameter reset.
        self.dw = 0.0
        self.pA = 1.0
        self.kex = 0.0

        # Calculate and check the R2eff values.
        self.calc_r2eff()


    def test_cr72_full_cluster_one_field_no_rex8(self):
        """Test the r2eff_cr72() function for no exchange when kex = 1e7."""

        # Parameter reset.
        self.kex = 1e7

        # Calculate and check the R2eff values.
        self.calc_r2eff()