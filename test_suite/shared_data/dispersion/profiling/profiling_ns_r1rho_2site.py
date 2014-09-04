#!/usr/bin/env python

###############################################################################
#                                                                             #
# Copyright (C) 2014 Troels E. Linnet                                         #
# Copyright (C) 2014 Edward d'Auvergne                                        #
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
import cProfile
from os import getcwd, path
from numpy import array, asarray, int32, float64, ones, pi
from math import atan2, sqrt
import pstats
import sys
import tempfile

# Python 3 support.
try:
    import __builtin__
    del __builtin__
except ImportError:
    import builtins
    builtins.xrange = builtins.range

# Add to system path, according to 
if len(sys.argv) == 1:
    path_to_base = path.join(getcwd(), '..', '..', '..', '..')
else:
    path_to_base = path.abspath(sys.argv[1])

# Reverse sys path.
sys.path.reverse()
# Add to path.
sys.path.append(path_to_base)
# Reverse sys path.
sys.path.reverse()

# relax module imports.
from compat_profiling import g1H, g15N
from target_functions.relax_disp import Dispersion
from specific_analyses.relax_disp.variables import EXP_TYPE_R1RHO, MODEL_NS_R1RHO_2SITE


# Alter setup.
def main():
    if True:
        # Nr of iterations.
        nr_iter = 10

        # Print statistics.
        verbose = True

        # Calc for single.
        s_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a single spin.
        cProfile.run('single(iter=%s)'%nr_iter, s_filename)

        # Read all stats files into a single object
        s_stats = pstats.Stats(s_filename)

        # Clean up filenames for the report
        s_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        s_stats.sort_stats('cumulative')

        # Print report for single.
        if verbose:
            s_stats.print_stats()

    if True:
        # Calc for cluster.
        c_filename = tempfile.NamedTemporaryFile(delete=False).name
        # Profile for a cluster of 100 spins.
        cProfile.run('cluster(iter=%s)'%nr_iter, c_filename)

        # Read all stats files into a single object
        c_stats = pstats.Stats(c_filename)

        # Clean up filenames for the report
        c_stats.strip_dirs()

        # Sort the statistics by the cumulative time spent in the function. cumulative, time, calls
        c_stats.sort_stats('cumulative')

        # Print report for clustered.
        if verbose:
            c_stats.print_stats()


class Profile(Dispersion):
    """
    Class Profile inherits the Dispersion container class object.
    """

    def __init__(self, num_spins=1, model=None, r2=None, r2a=None, r2b=None, phi_ex=None, dw=None, pA=None, kex=None, spins_params=None):
        """
        Special method __init__() is called first (acts as Constructor).
        It brings in data from outside the class like the variable num_spins.
        (in this case num_spins is also set to a default value of 1)
        The first parameter of any method/function in the class is always self,
        the name self is used by convention.  Assigning num_spins to self.num_spins allows it
        to be passed to all methods within the class.  Think of self as a carrier,
        or if you want impress folks call it target instance object.

        @keyword num_spins:     Number of spins in the cluster.
        @type num_spins:        integer
        @keyword model:         The dispersion model to instantiate the Dispersion class with.
        @type model:            string
        @keyword r2:            The transversal relaxation rate.
        @type r2:               float
        @keyword r2a:           The transversal relaxation rate for state A in the absence of exchange.
        @type r2a:              float
        @keyword r2b:           The transversal relaxation rate for state B in the absence of exchange.
        @type r2b:              float
        @keyword phi_ex:        The phi_ex = pA.pB.dw**2 value (ppm^2)
        @type phi_ex:           float
        @keyword dw:            The chemical exchange difference between states A and B in ppm.
        @type dw:               float
        @keyword pA:            The population of state A.
        @type pA:               float
        @keyword kex:           The rate of exchange.
        @type kex:              float
        @keyword spins_params:  List of parameter strings used in dispersion model.
        @type spins_params:     array of strings
        """

        # Define parameters
        self.model = model
        self.num_spins = num_spins
        #self.fields = array([800. * 1E6])
        #self.fields = array([600. * 1E6, 800. * 1E6])
        self.fields = array([600. * 1E6, 800. * 1E6, 900. * 1E6])
        self.exp_type = [EXP_TYPE_R1RHO]

        # Required data structures.
        self.relax_times = self.fields / (100 * 100. *1E6 )
        self.value = []
        self.error = []
        self.points = []

        # Set The spin-lock field strength, nu1, in Hz
        self.spin_lock_fields = [431.0, 651.2, 800.5, 984.0, 1341.11]

        for i in range(len(self.fields)):
            points = self.spin_lock_fields

            self.points.append(list(points))
            self.value.append([2.0]*len(self.spin_lock_fields))
            self.error.append([1.0]*len(self.spin_lock_fields))

        # Spin lock offsets in ppm.
        self.spin_lock_offsets = range(10)

        # Chemical shift in ppm.
        self.chemical_shift = 1.0

        # Assemble param vector.
        self.params = self.assemble_param_vector(r2=r2, r2a=r2a, r2b=r2b, phi_ex=phi_ex, dw=dw, pA=pA, kex=kex, spins_params=spins_params)

        # Make nested list arrays of data. And return them.
        values, errors, cpmg_frqs, missing, frqs, exp_types, relax_times, offsets, spin_lock_nu1 = self.return_r2eff_arrays()

        # The offset and R1 data.
        chemical_shifts, offsets, tilt_angles, Delta_omega, w_eff = self.return_offset_data()

        r1 = ones([self.num_spins, self.fields.shape[0]])

        # Init the Dispersion Class.
        self.model = Dispersion(model=self.model, num_params=None, num_spins=self.num_spins, num_frq=len(self.fields), exp_types=exp_types, values=values, errors=errors, missing=missing, frqs=frqs, frqs_H=None, cpmg_frqs=cpmg_frqs, spin_lock_nu1=spin_lock_nu1, chemical_shifts=chemical_shifts, offset=offsets, tilt_angles=tilt_angles, r1=r1, relax_times=relax_times, scaling_matrix=None)


    def return_offset_data(self):
        """Return numpy arrays of the chemical shifts, offsets and tilt angles.

        @keyword field_count:   The number of spectrometer field strengths.  This may not be equal to the length of the fields list as the user may not have set the field strength.
        @type field_count:      int
        @keyword fields:        The spin-lock field strengths to use instead of the user loaded values - to enable interpolation.  The dimensions are {Ei, Mi}.
        @type fields:           rank-2 list of floats
        """

        # spins=[spin], spin_ids=[spin_id], field_count=field_count, fields=spin_lock_nu1


        # Initialise the data structures for the target function.
        shifts = []
        offsets = []
        theta = []
        Domega = []
        w_e = []
        for ei in range(len(self.exp_type)):
            shifts.append([])
            offsets.append([])
            theta.append([])
            Domega.append([])
            w_e.append([])
            for si in range(self.num_spins):
                shifts[ei].append([])
                offsets[ei].append([])
                theta[ei].append([])
                Domega[ei].append([])
                w_e[ei].append([])
                for mi in range(len(self.fields)):
                    shifts[ei][si].append(None)
                    offsets[ei][si].append([])
                    theta[ei][si].append([])
                    Domega[ei][si].append([])
                    w_e[ei][si].append([])
                    for oi in range(len(self.spin_lock_offsets)):
                        offsets[ei][si][mi].append(None)
                        theta[ei][si][mi].append([])
                        Domega[ei][si][mi].append([])
                        w_e[ei][si][mi].append([])

        # Assemble the data.
        si = 0
        for spin_index in range(self.num_spins):

            for ei in range(len(self.exp_type)):
                exp_type = self.exp_type[ei]
                # Add the experiment type.

                for mi in range(len(self.fields)):
                    # Get the frq.
                    frq = self.fields[mi]

                    for oi in range(len(self.spin_lock_offsets)):
                        # The spin-lock data.

                        # Convert the shift from ppm to rad/s and store it.
                        shifts[ei][si][mi] = self.chemical_shift * 2.0 * pi * frq / g1H * g15N * 1e-6

                        # Set The spin-lock offset, omega_rf, in ppm.
                        offset = self.spin_lock_offsets[oi]

                        # Store the offset in rad/s.  Only once and using the first key.
                        offsets[ei][si][mi][oi] = offset * 2.0 * pi * frq / g1H * g15N * 1e-6

                        # Loop over the dispersion points.
                        for di in range(len(self.spin_lock_fields)):
                            # Alias the point.
                            point = self.spin_lock_fields[di]

                            # Skip reference spectra.
                            if point == None:
                                continue

                            # Calculate the tilt angle.
                            omega1 = point * 2.0 * pi
                            Delta_omega = shifts[ei][si][mi] - offsets[ei][si][mi][oi]
                            Domega[ei][si][mi][oi].append(Delta_omega)
                            if Delta_omega == 0.0:
                                theta[ei][si][mi][oi].append(pi / 2.0)
                            # Calculate the theta angle describing the tilted rotating frame relative to the laboratory.
                            # theta = atan(omega1 / Delta_omega).
                            # If Delta_omega is negative, there follow the symmetry of atan, that atan(-x) = - atan(x).
                            # Then it should be: theta = pi + atan(-x) = pi - atan(x) = pi - abs(atan( +/- x)).
                            # This is taken care of with the atan2(y, x) function, which return atan(y / x), in radians, and the result is between -pi and pi.
                            else:
                                theta[ei][si][mi][oi].append(atan2(omega1, Delta_omega))

                            # Calculate effective field in rotating frame
                            w_eff = sqrt( Delta_omega*Delta_omega + omega1*omega1 )
                            w_e[ei][si][mi][oi].append(w_eff)

            # Increment the spin index.
            si += 1

        # Return the structures.
        return shifts, offsets, theta, Domega, w_e


    def return_r2eff_arrays(self):
        """Return numpy arrays of the R2eff/R1rho values and errors.

        @return:    The numpy array structures of the R2eff/R1rho values, errors, missing data, and corresponding Larmor frequencies.  For each structure, the first dimension corresponds to the experiment types, the second the spins of a spin block, the third to the spectrometer field strength, and the fourth is the dispersion points.  For the Larmor frequency structure, the fourth dimension is omitted.  For R1rho-type data, an offset dimension is inserted between the spectrometer field strength and the dispersion points.
        @rtype:         lists of numpy float arrays, lists of numpy float arrays, lists of numpy float arrays, numpy rank-2 int array
        """

        # Unpack the parameter values.

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
                    for oi in range(len(self.spin_lock_offsets)):
                        values[ei][si][mi].append([])
                        errors[ei][si][mi].append([])
                        missing[ei][si][mi].append([])
                        offsets[ei][si][mi].append([])
            for mi in range(len(self.fields)):
                relax_times[ei].append(None)

        spin_lock_nu1 = []
        for ei in range(len(self.exp_type)):
            spin_lock_nu1.append([])
            for mi in range(len(self.fields)):
                spin_lock_nu1[ei].append([])
                for oi in range(len(self.spin_lock_offsets)):
                    #cpmg_frqs[ei][mi].append(self.points)
                    spin_lock_nu1[ei][mi].append([])

        # Pack the R2eff/R1rho data.
        si = 0
        for spin_index in range(self.num_spins):

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

                    for oi in range(len(self.spin_lock_offsets)):
                        # Get the spin_lock_nu1 frq.
                        spin_lock_nu1[ei][mi][oi] = self.points[mi]

                        back_calc = array([0.0]*len(spin_lock_nu1[ei][mi][oi]))

                        for di in range(len(self.spin_lock_fields)):

                            missing[ei][si][mi][oi].append(0)

                            # Values
                            #values[ei][si][mi][oi].append(self.value[mi][di])
                            values[ei][si][mi][oi].append(back_calc[di])
                            # The errors.
                            errors[ei][si][mi][oi].append(self.error[mi][di])
                            #print self.value[mi][di], self.error[mi][di]

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
                    for oi in range(len(self.spin_lock_offsets)):
                        spin_lock_nu1[ei][mi][oi] = array(spin_lock_nu1[ei][mi][oi], float64)
                        values[ei][si][mi][oi] = array(values[ei][si][mi][oi], float64)
                        errors[ei][si][mi][oi] = array(errors[ei][si][mi][oi], float64)
                        missing[ei][si][mi][oi] = array(missing[ei][si][mi][oi], int32)

        # Return the structures.
        return values, errors, None, missing, frqs, exp_types, relax_times, offsets, asarray(spin_lock_nu1)


    def assemble_param_vector(self, r2=None, r2a=None, r2b=None, phi_ex=None, dw=None, pA=None, kex=None, spins_params=None):
        """Assemble the dispersion relaxation dispersion curve fitting parameter vector.

        @keyword r2:            The transversal relaxation rate.
        @type r2:               float
        @keyword r2a:           The transversal relaxation rate for state A in the absence of exchange.
        @type r2a:              float
        @keyword r2b:           The transversal relaxation rate for state B in the absence of exchange.
        @type r2b:              float
        @keyword phi_ex:        The phi_ex = pA.pB.dw**2 value (ppm^2)
        @type phi_ex:           float
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
            elif param_name == 'phi_ex':
                value = phi_ex + spin_index
            elif param_name == 'dw':
                value = dw + spin_index
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

            # Yield the data.
            if 'phi_ex' in spins_params:
                yield 'phi_ex', spin_index, 0
            if 'phi_ex_B' in spins_params:
                yield 'phi_ex_B', spin_index, 0
            if 'phi_ex_C' in spins_params:
                yield 'phi_ex_C', spin_index, 0
            if 'padw2' in spins_params:
                yield 'padw2', pspin_index, 0
            if 'dw' in spins_params:
                yield 'dw', spin_index, 0

        # All other parameters (one per spin cluster).
        for param in spins_params:
            if not param in ['r2', 'r2a', 'r2b', 'phi_ex', 'phi_ex_B', 'phi_ex_C', 'padw2', 'dw', 'dw_AB', 'dw_BC', 'dw_AB', 'dwH', 'dwH_AB', 'dwH_BC', 'dwH_AB']:
                if param == 'pA':
                    yield 'pA', 0, 0
                elif param == 'kex':
                    yield 'kex', 0, 0


    def calc(self, params):
        """Calculate chi2 values.

        @keyword params:  List of parameter strings used in dispersion model.
        @type params:     array of strings
        @return:          Chi2 value.
        @rtype:           float
        """

        # Return chi2 value.
        chi2 = self.model.func_ns_r1rho_2site(params)
        return chi2


def single(num_spins=1, model=MODEL_NS_R1RHO_2SITE, iter=None):
    """Calculate for a single spin.

    @keyword num_spins:     Number of spins in the cluster.
    @type num_spins:        integer
    @keyword model:         The dispersion model to instantiate the Dispersion class with.
    @type model:            string
    @keyword iter:          The number of iterations to perform the function call.
    @type iter:             int
    @return:                Chi2 value.
    @rtype:                 float
    """

    # Instantiate class
    C1 = Profile(num_spins=num_spins, model=model, r2=5.0, dw=1.0, pA=0.9, kex=5000.0, spins_params=['r2', 'dw', 'pA', 'kex'])

    # Loop 100 times for each spin in the clustered analysis (to make the timing numbers equivalent).
    for spin_index in xrange(100):
        # Repeat the function call, to simulate minimisation.
        for i in xrange(iter):
            chi2 = C1.calc(C1.params)
    print("chi2 single:", chi2)


def cluster(num_spins=100, model=MODEL_NS_R1RHO_2SITE, iter=None):
    """Calculate for a number of clustered spins.

    @keyword num_spins:     Number of spins in the cluster.
    @type num_spins:        integer
    @keyword model:         The dispersion model to instantiate the Dispersion class with.
    @type model:            string
    @keyword iter:          The number of iterations to perform the function call.
    @type iter:             int
    @return:                Chi2 value.
    @rtype:                 float
    """

    # Instantiate class
    C1 = Profile(num_spins=num_spins, model=model, r2=5.0, dw=1.0, pA=0.9, kex=5000.0, spins_params=['r2', 'dw', 'pA', 'kex'])

    # Repeat the function call, to simulate minimisation.
    for i in xrange(iter):
        chi2 = C1.calc(C1.params)
    print("chi2 cluster:", chi2)


# Execute main function.
if __name__ == "__main__":
    main()
