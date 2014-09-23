###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
"""Module for the optimisation of the relaxation dispersion models."""

# Python module imports.
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import dot, float64, int32, ones, zeros
from numpy.linalg import inv
from operator import mul
from re import match, search
import sys
from warnings import warn

# relax module imports.
from dep_check import C_module_exp_fn
from lib.dispersion.two_point import calc_two_point_r2eff, calc_two_point_r2eff_err
from lib.dispersion.variables import EXP_TYPE_LIST_CPMG, MODEL_CR72, MODEL_CR72_FULL, MODEL_LIST_MMQ, MODEL_LM63, MODEL_M61, MODEL_MP05, MODEL_TAP03, MODEL_TP02
from lib.errors import RelaxError
from lib.text.sectioning import subsection
from lib.warnings import RelaxWarning
from multi import Memo, Result_command, Slave_command
from pipe_control.mol_res_spin import generate_spin_string, spin_loop
from specific_analyses.relax_disp.checks import check_disp_points, check_exp_type, check_exp_type_fixed_time
from specific_analyses.relax_disp.data import average_intensity, count_spins, find_intensity_keys, has_exponential_exp_type, has_proton_mmq_cpmg, is_r1_optimised, loop_exp, loop_exp_frq_offset_point, loop_exp_frq_offset_point_time, loop_frq, loop_offset, loop_time, pack_back_calc_r2eff, return_cpmg_frqs, return_offset_data, return_param_key_from_data, return_r1_data, return_r2eff_arrays, return_spin_lock_nu1
from specific_analyses.relax_disp.parameters import assemble_param_vector, disassemble_param_vector, linear_constraints, param_conversion, param_num, r1_setup
from target_functions.relax_disp import Dispersion

# C modules.
if C_module_exp_fn:
    from specific_analyses.relax_fit.optimisation import func_wrapper, dfunc_wrapper, d2func_wrapper
    from target_functions.relax_fit import setup, back_calc_I
    # Call the python wrapper function to help with list to numpy array conversion.
    func = func_wrapper
    dfunc = dfunc_wrapper
    d2func = d2func_wrapper


def back_calc_peak_intensities(spin=None, exp_type=None, frq=None, offset=None, point=None):
    """Back-calculation of peak intensity for the given relaxation time.

    @keyword spin:      The specific spin data container.
    @type spin:         SpinContainer instance
    @keyword exp_type:  The experiment type.
    @type exp_type:     str
    @keyword frq:       The spectrometer frequency.
    @type frq:          float
    @keyword offset:    For R1rho-type data, the spin-lock offset value in ppm.
    @type offset:       None or float
    @keyword point:     The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
    @type point:        float
    @return:            The back-calculated peak intensities for the given exponential curve.
    @rtype:             numpy rank-1 float array
    """

    # Check.
    if not has_exponential_exp_type():
        raise RelaxError("Back-calculation is not allowed for the fixed time experiment types.")

    # The key.
    param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

    # Create the initial parameter vector.
    param_vector = assemble_param_vector(spins=[spin], key=param_key)

    # The peak intensities and times.
    values = []
    errors = []
    times = []
    for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
        # The data.
        values.append(average_intensity(spin=spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time))
        errors.append(average_intensity(spin=spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, error=True))
        times.append(time)

    # The scaling matrix in a diagonalised list form.
    scaling_list = []
    for i in range(len(param_vector)):
        scaling_list.append(1.0)

    # Initialise the relaxation fit functions.
    setup(num_params=len(param_vector), num_times=len(times), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)

    # Make a single function call.  This will cause back calculation and the data will be stored in the C module.
    func(param_vector)

    # Get the data back.
    results = back_calc_I()

    # Return the correct peak height.
    return results


def back_calc_r2eff(spin=None, spin_id=None, cpmg_frqs=None, spin_lock_offset=None, spin_lock_nu1=None, relax_times_new=None, store_chi2=False):
    """Back-calculation of R2eff/R1rho values for the given spin.

    @keyword spin:              The specific spin data container.
    @type spin:                 SpinContainer instance
    @keyword spin_id:           The spin ID string for the spin container.
    @type spin_id:              str
    @keyword cpmg_frqs:         The CPMG frequencies to use instead of the user loaded values - to enable interpolation.
    @type cpmg_frqs:            list of lists of numpy rank-1 float arrays
    @keyword spin_lock_offset:  The spin-lock offsets to use instead of the user loaded values - to enable interpolation.
    @type spin_lock_offset:     list of lists of numpy rank-1 float arrays
    @keyword spin_lock_nu1:     The spin-lock field strengths to use instead of the user loaded values - to enable interpolation.
    @type spin_lock_nu1:        list of lists of numpy rank-1 float arrays
    @keyword relax_times_new:   The interpolated experiment specific fixed time period for relaxation (in seconds).  The dimensions are {Ei, Mi, Oi, Di, Ti}.
    @type relax_times_new:      rank-4 list of floats
    @keyword store_chi2:        A flag which if True will cause the spin specific chi-squared value to be stored in the spin container.
    @type store_chi2:           bool
    @return:                    The back-calculated R2eff/R1rho value for the given spin.
    @rtype:                     numpy rank-1 float array
    """

    # Skip protons for MMQ data.
    if spin.model in MODEL_LIST_MMQ and spin.isotope == '1H':
        return

    # Create the initial parameter vector.
    param_vector = assemble_param_vector(spins=[spin])

    # Number of spectrometer fields.
    fields = [None]
    field_count = 1
    if hasattr(cdp, 'spectrometer_frq_count'):
        fields = cdp.spectrometer_frq_list
        field_count = cdp.spectrometer_frq_count

    # Initialise the data structures for the target function.
    values, errors, missing, frqs, frqs_H, exp_types, relax_times = return_r2eff_arrays(spins=[spin], spin_ids=[spin_id], fields=fields, field_count=field_count)

    # The offset and R1 data.
    r1_setup()
    offsets, spin_lock_fields_inter, chemical_shifts, tilt_angles, Delta_omega, w_eff = return_offset_data(spins=[spin], spin_ids=[spin_id], field_count=field_count, spin_lock_offset=spin_lock_offset, fields=spin_lock_nu1)
    r1 = return_r1_data(spins=[spin], spin_ids=[spin_id], field_count=field_count)
    r1_fit = is_r1_optimised(spin.model)

    # The relaxation times.
    if relax_times_new != None:
        relax_times = relax_times_new

    # The dispersion data.
    recalc_tau = True
    if cpmg_frqs == None and spin_lock_nu1 == None and spin_lock_offset == None:
        cpmg_frqs = return_cpmg_frqs(ref_flag=False)
        spin_lock_nu1 = return_spin_lock_nu1(ref_flag=False)

    # Reset the cpmg_frqs if interpolating R1rho models.
    elif cpmg_frqs == None and spin_lock_offset != None:
        cpmg_frqs = None
        spin_lock_nu1 = spin_lock_fields_inter

        recalc_tau = False
        values = []
        errors = []
        missing = []
        for exp_type, ei in loop_exp(return_indices=True):
            values.append([])
            errors.append([])
            missing.append([])
            for si in range(1):
                values[ei].append([])
                errors[ei].append([])
                missing[ei].append([])
                for frq, mi in loop_frq(return_indices=True):
                    values[ei][si].append([])
                    errors[ei][si].append([])
                    missing[ei][si].append([])
                    for oi, offset in enumerate(offsets[ei][si][mi]):
                        num = len(spin_lock_nu1[ei][mi][oi])

                        values[ei][si][mi].append(zeros(num, float64))
                        errors[ei][si][mi].append(ones(num, float64))
                        missing[ei][si][mi].append(zeros(num, int32))

    # Reconstruct the structures for interpolation.
    else:
        recalc_tau = False
        values = []
        errors = []
        missing = []
        for exp_type, ei in loop_exp(return_indices=True):
            values.append([])
            errors.append([])
            missing.append([])
            for si in range(1):
                values[ei].append([])
                errors[ei].append([])
                missing[ei].append([])
                for frq, mi in loop_frq(return_indices=True):
                    values[ei][si].append([])
                    errors[ei][si].append([])
                    missing[ei][si].append([])
                    for offset, oi in loop_offset(exp_type=exp_type, frq=frq, return_indices=True):
                        if exp_type in EXP_TYPE_LIST_CPMG:
                            num = len(cpmg_frqs[ei][mi][oi])
                        else:
                            num = len(spin_lock_nu1[ei][mi][oi])
                        values[ei][si][mi].append(zeros(num, float64))
                        errors[ei][si][mi].append(ones(num, float64))
                        missing[ei][si][mi].append(zeros(num, int32))

    # Initialise the relaxation dispersion fit functions.
    model = Dispersion(model=spin.model, num_params=param_num(spins=[spin]), num_spins=1, num_frq=field_count, exp_types=exp_types, values=values, errors=errors, missing=missing, frqs=frqs, frqs_H=frqs_H, cpmg_frqs=cpmg_frqs, spin_lock_nu1=spin_lock_nu1, chemical_shifts=chemical_shifts, offset=offsets, tilt_angles=tilt_angles, r1=r1, relax_times=relax_times, recalc_tau=recalc_tau, r1_fit=r1_fit)

    # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
    chi2 = model.func(param_vector)

    # Store the chi-squared value.
    if store_chi2:
        spin.chi2 = chi2

    # Return the structure.
    return model.get_back_calc()


def calculate_r2eff():
    """Calculate the R2eff values for fixed relaxation time period data."""

    # Data checks.
    check_exp_type()
    check_disp_points()
    check_exp_type_fixed_time()

    # Printouts.
    print("Calculating the R2eff/R1rho values for fixed relaxation time period data.")

    # Loop over the spins.
    for spin, mol_name, resi, resn, spin_id in spin_loop(full_info=True, return_id=True, skip_desel=True):
        # Spin ID printout.
        print("Spin '%s'." % spin_id)

        # Skip spins which have no data.
        if not hasattr(spin, 'peak_intensity'):
            continue

        # Initialise the data structures.
        if not hasattr(spin, 'r2eff'):
            spin.r2eff = {}
        if not hasattr(spin, 'r2eff_err'):
            spin.r2eff_err = {}

        # Loop over all the data.
        for exp_type, frq, offset, point, time in loop_exp_frq_offset_point_time():
            # The three keys.
            ref_keys = find_intensity_keys(exp_type=exp_type, frq=frq, offset=offset, point=None, time=time)
            int_keys = find_intensity_keys(exp_type=exp_type, frq=frq, offset=offset, point=point, time=time)
            param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # Check for missing data.
            missing = False
            for i in range(len(ref_keys)):
                if ref_keys[i] not in spin.peak_intensity:
                    missing = True
            for i in range(len(int_keys)):
                if int_keys[i] not in spin.peak_intensity:
                    missing = True
            if missing:
                continue

            # Average the reference intensity data and errors.
            ref_intensity = average_intensity(spin=spin, exp_type=exp_type, frq=frq, offset=offset, point=None, time=time)
            ref_intensity_err = average_intensity(spin=spin, exp_type=exp_type, frq=frq, offset=offset, point=None, time=time, error=True)

            # Average the intensity data and errors.
            intensity = average_intensity(spin=spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time)
            intensity_err = average_intensity(spin=spin, exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, error=True)

            # Check for math domain errors or log for values less than 0.0.
            if ref_intensity == 0.0:
                skip_data = True
            elif float(intensity) / ref_intensity <= 0.0:
                skip_data = True
            else:
                skip_data = False

            if skip_data:
                spin_string = generate_spin_string(spin=spin, mol_name=mol_name, res_num=resi, res_name=resn)
                msg = "Math log(I / I_ref) domain error for spin '%s' in R2eff value calculation for fixed relaxation time period data.  I=%3.3f, I_ref=%3.3f.  The point is skipped." % (spin_string, intensity, ref_intensity)
                warn(RelaxWarning("%s" % msg))
                point_info = "This happened for '%s' at %3.1f MHz, for offset=%3.1f ppm and dispersion point %3.1f Hz and time %1.2f s.\n" % (exp_type, frq/1E6, offset, point, time)
                print(point_info)
            else:
                # Calculate the R2eff value.
                spin.r2eff[param_key] = calc_two_point_r2eff(relax_time=time, I_ref=ref_intensity, I=intensity)

                # Calculate the R2eff error.
                spin.r2eff_err[param_key] = calc_two_point_r2eff_err(relax_time=time, I_ref=ref_intensity, I=intensity, I_ref_err=ref_intensity_err, I_err=intensity_err)


def minimise_r2eff(spins=None, spin_ids=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling_matrix=None, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
    """Optimise the R2eff model by fitting the 2-parameter exponential curves.

    This mimics the R1 and R2 relax_fit analysis.


    @keyword spins:             The list of spins for the cluster.
    @type spins:                list of SpinContainer instances
    @keyword spin_ids:          The list of spin IDs for the cluster.
    @type spin_ids:             list of str
    @keyword min_algor:         The minimisation algorithm to use.
    @type min_algor:            str
    @keyword min_options:       An array of options to be used by the minimisation algorithm.
    @type min_options:          array of str
    @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
    @type func_tol:             None or float
    @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
    @type grad_tol:             None or float
    @keyword max_iterations:    The maximum number of iterations for the algorithm.
    @type max_iterations:       int
    @keyword constraints:       If True, constraints are used during optimisation.
    @type constraints:          bool
    @keyword scaling_matrix:    The diagonal and square scaling matrix.
    @type scaling_matrix:       numpy rank-2, float64 array or None
    @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:            int
    @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
    @type sim_index:            None or int
    @keyword lower:             The model specific lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
    @type lower:                list of numbers
    @keyword upper:             The model specific upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
    @type upper:                list of numbers
    @keyword inc:               The model specific increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
    @type inc:                  list of int
    """

    # Check that the C modules have been compiled.
    if not C_module_exp_fn:
        raise RelaxError("Relaxation curve fitting is not available.  Try compiling the C modules on your platform.")

    # Loop over the spins.
    for si in range(len(spins)):
        # Skip deselected spins.
        if not spins[si].select:
            continue

        # Loop over each spectrometer frequency and dispersion point.
        for exp_type, frq, offset, point in loop_exp_frq_offset_point():
            # The parameter key.
            param_key = return_param_key_from_data(exp_type=exp_type, frq=frq, offset=offset, point=point)

            # The initial parameter vector.
            param_vector = assemble_param_vector(spins=[spins[si]], key=param_key, sim_index=sim_index)

            # Diagonal scaling.
            if scaling_matrix != None:
                param_vector = dot(inv(scaling_matrix), param_vector)

            # Linear constraints.
            A, b = None, None
            if constraints:
                A, b = linear_constraints(spins=[spins[si]], scaling_matrix=scaling_matrix)

            # Print out.
            if verbosity >= 1:
                # Individual spin section.
                top = 2
                if verbosity >= 2:
                    top += 2
                text = "Fitting to spin %s, frequency %s and dispersion point %s" % (spin_ids[si], frq, point)
                subsection(file=sys.stdout, text=text, prespace=top)

                # Grid search printout.
                if match('^[Gg]rid', min_algor):
                    result = 1
                    for x in inc:
                        result = mul(result, x)
                    print("Unconstrained grid search size: %s (constraints may decrease this size).\n" % result)

            # The peak intensities, errors and times.
            values = []
            errors = []
            times = []
            for time in loop_time(exp_type=exp_type, frq=frq, offset=offset, point=point):
                values.append(average_intensity(spin=spins[si], exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, sim_index=sim_index))
                errors.append(average_intensity(spin=spins[si], exp_type=exp_type, frq=frq, offset=offset, point=point, time=time, error=True))
                times.append(time)

            # Raise errors if number of time points is less than 2.
            if len(times) < 3:
                subsection(file=sys.stdout, text="Exponential curve fitting error for point:", prespace=2)
                point_info = "%s at %3.1f MHz, for offset=%3.3f ppm and dispersion point %-5.1f, with %i time points." % (exp_type, frq/1E6, offset, point, len(times))
                print(point_info)
                raise RelaxError("The data setup points to exponential curve fitting, but only %i time points was found, where 3 time points is minimum.  If calculating R2eff values for fixed relaxation time period data, check that a reference intensity has been specified for each offset value."%(len(times)))

            # The scaling matrix in a diagonalised list form.
            scaling_list = []
            if scaling_matrix == None:
                for i in range(len(param_vector)):
                    scaling_list.append(1.0)
            else:
                for i in range(len(scaling_matrix)):
                    scaling_list.append(scaling_matrix[i, i])

            # Initialise the function to minimise.
            setup(num_params=len(param_vector), num_times=len(times), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)

            # Grid search.
            if search('^[Gg]rid', min_algor):
                results = grid(func=func, args=(), num_incs=inc, lower=lower, upper=upper, A=A, b=b, verbosity=verbosity)

                # Unpack the results.
                param_vector, chi2, iter_count, warning = results
                f_count = iter_count
                g_count = 0.0
                h_count = 0.0

            # Minimisation.
            else:
                results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=True, print_flag=verbosity)

                # Unpack the results.
                if results == None:
                    return
                param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

            # Scaling.
            if scaling_matrix != None:
                param_vector = dot(scaling_matrix, param_vector)

            # Disassemble the parameter vector.
            disassemble_param_vector(param_vector=param_vector, spins=[spins[si]], key=param_key, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                # Chi-squared statistic.
                spins[si].chi2_sim[sim_index] = chi2

                # Iterations.
                spins[si].iter_sim[sim_index] = iter_count

                # Function evaluations.
                spins[si].f_count_sim[sim_index] = f_count

                # Gradient evaluations.
                spins[si].g_count_sim[sim_index] = g_count

                # Hessian evaluations.
                spins[si].h_count_sim[sim_index] = h_count

                # Warning.
                spins[si].warning_sim[sim_index] = warning

            # Normal statistics.
            else:
                # Chi-squared statistic.
                spins[si].chi2 = chi2

                # Iterations.
                spins[si].iter = iter_count

                # Function evaluations.
                spins[si].f_count = f_count

                # Gradient evaluations.
                spins[si].g_count = g_count

                # Hessian evaluations.
                spins[si].h_count = h_count

                # Warning.
                spins[si].warning = warning



class Disp_memo(Memo):
    """The relaxation dispersion memo class."""

    def __init__(self, spins=None, spin_ids=None, sim_index=None, scaling_matrix=None, verbosity=None):
        """Initialise the relaxation dispersion memo class.

        This is used for handling the optimisation results returned from a slave processor.  It runs on the master processor and is used to store data which is passed to the slave processor and then passed back to the master via the results command.


        @keyword spins:             The list of spin data container for the cluster.  If this argument is supplied, then the spin_id argument will be ignored.
        @type spins:                list of SpinContainer instances
        @keyword spin_ids:          The spin ID strings for the cluster.
        @type spin_ids:             list of str
        @keyword sim_index:         The optional MC simulation index.
        @type sim_index:            int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @keyword verbosity:         The verbosity level.  This is used by the result command returned to the master for printouts.
        @type verbosity:            int
        """

        # Execute the base class __init__() method.
        super(Disp_memo, self).__init__()

        # Store the arguments.
        self.spins = spins
        self.spin_ids = spin_ids
        self.sim_index = sim_index
        self.scaling_matrix = scaling_matrix
        self.verbosity = verbosity



class Disp_minimise_command(Slave_command):
    """Command class for relaxation dispersion optimisation on the slave processor."""

    def __init__(self, spins=None, spin_ids=None, sim_index=None, scaling_matrix=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, verbosity=0, lower=None, upper=None, inc=None, fields=None, param_names=None):
        """Initialise the base class, storing all the master data to be sent to the slave processor.

        This method is run on the master processor whereas the run() method is run on the slave processor.


        @keyword spins:             The list of spin data container for the cluster.  If this argument is supplied, then the spin_id argument will be ignored.
        @type spins:                list of SpinContainer instances
        @keyword spin_ids:          The list of spin ID strings corresponding to the spins argument.
        @type spin_ids:             list of str
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword lower:             The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        @keyword fields:            The list of unique of spectrometer field strengths.
        @type fields:               int
        @keyword param_names:       The list of parameter names to use in printouts.
        @type param_names:          str
        """

        # Execute the base class __init__() method.
        super(Disp_minimise_command, self).__init__()

        # Store the arguments needed by the run() method.
        self.spins = spins
        self.spin_ids = spin_ids
        self.sim_index = sim_index
        self.scaling_matrix = scaling_matrix
        self.verbosity = verbosity
        self.min_algor = min_algor
        self.min_options = min_options
        self.func_tol = func_tol
        self.grad_tol = grad_tol
        self.max_iterations = max_iterations
        self.lower = lower
        self.upper = upper
        self.inc = inc
        self.fields = fields
        self.param_names = param_names

        # Create the initial parameter vector.
        self.param_vector = assemble_param_vector(spins=self.spins)
        if len(scaling_matrix):
            self.param_vector = dot(inv(scaling_matrix), self.param_vector)

        # Linear constraints.
        self.A, self.b = None, None
        if constraints:
            self.A, self.b = linear_constraints(spins=spins, scaling_matrix=scaling_matrix)

        # Test if the spectrometer frequencies have been set.
        if spins[0].model in [MODEL_LM63, MODEL_CR72, MODEL_CR72_FULL, MODEL_M61, MODEL_TP02, MODEL_TAP03, MODEL_MP05] and not hasattr(cdp, 'spectrometer_frq'):
            raise RelaxError("The spectrometer frequency information has not been specified.")

        # The R2eff/R1rho data.
        self.values, self.errors, self.missing, self.frqs, self.frqs_H, self.exp_types, self.relax_times = return_r2eff_arrays(spins=spins, spin_ids=spin_ids, fields=fields, field_count=len(fields), sim_index=sim_index)

        # The offset and R1 data.
        r1_setup()
        self.offsets, spin_lock_fields_inter, self.chemical_shifts, self.tilt_angles, self.Delta_omega, self.w_eff = return_offset_data(spins=spins, spin_ids=spin_ids, field_count=len(fields))
        self.r1 = return_r1_data(spins=spins, spin_ids=spin_ids, field_count=len(fields), sim_index=sim_index)
        self.r1_fit = is_r1_optimised(spins[0].model)

        # Parameter number.
        self.param_num = param_num(spins=spins)

        # The dispersion data.
        self.dispersion_points = cdp.dispersion_points
        self.cpmg_frqs = return_cpmg_frqs(ref_flag=False)
        self.spin_lock_nu1 = return_spin_lock_nu1(ref_flag=False)


    def run(self, processor, completed):
        """Set up and perform the optimisation."""

        # Print out.
        if self.verbosity >= 1:
            # Individual spin block section.
            top = 2
            if self.verbosity >= 2:
                top += 2
            subsection(file=sys.stdout, text="Fitting to the spin block %s"%self.spin_ids, prespace=top)

            # Grid search printout.
            if search('^[Gg]rid', self.min_algor):
                result = 1
                for x in self.inc:
                    result = mul(result, x)
                print("Unconstrained grid search size: %s (constraints may decrease this size).\n" % result)

        # Initialise the function to minimise.
        model = Dispersion(model=self.spins[0].model, num_params=self.param_num, num_spins=count_spins(self.spins), num_frq=len(self.fields), exp_types=self.exp_types, values=self.values, errors=self.errors, missing=self.missing, frqs=self.frqs, frqs_H=self.frqs_H, cpmg_frqs=self.cpmg_frqs, spin_lock_nu1=self.spin_lock_nu1, chemical_shifts=self.chemical_shifts, offset=self.offsets, tilt_angles=self.tilt_angles, r1=self.r1, relax_times=self.relax_times, scaling_matrix=self.scaling_matrix, r1_fit=self.r1_fit)

        # Grid search.
        if search('^[Gg]rid', self.min_algor):
            results = grid(func=model.func, args=(), num_incs=self.inc, lower=self.lower, upper=self.upper, A=self.A, b=self.b, verbosity=self.verbosity)

            # Unpack the results.
            param_vector, chi2, iter_count, warning = results
            f_count = iter_count
            g_count = 0.0
            h_count = 0.0

        # Minimisation.
        else:
            results = generic_minimise(func=model.func, args=(), x0=self.param_vector, min_algor=self.min_algor, min_options=self.min_options, func_tol=self.func_tol, grad_tol=self.grad_tol, maxiter=self.max_iterations, A=self.A, b=self.b, full_output=True, print_flag=self.verbosity)

            # Unpack the results.
            if results == None:
                return
            param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

        # Optimisation printout.
        if self.verbosity:
            print("\nOptimised parameter values:")
            for i in range(len(param_vector)):
                print("%-20s %25.15f" % (self.param_names[i], param_vector[i]*self.scaling_matrix[i, i]))

        # Create the result command object to send back to the master.
        processor.return_object(Disp_result_command(processor=processor, memo_id=self.memo_id, param_vector=param_vector, chi2=chi2, iter_count=iter_count, f_count=f_count, g_count=g_count, h_count=h_count, warning=warning, missing=self.missing, back_calc=model.get_back_calc(), completed=False))



class Disp_result_command(Result_command):
    """Class for processing the dispersion optimisation results.

    This object will be sent from the slave back to the master to have its run() method executed.
    """

    def __init__(self, processor=None, memo_id=None, param_vector=None, chi2=None, iter_count=None, f_count=None, g_count=None, h_count=None, warning=None, missing=None, back_calc=None, completed=True):
        """Set up this class object on the slave, placing the minimisation results here.

        @keyword processor:     The processor object.
        @type processor:        multi.processor.Processor instance
        @keyword memo_id:       The memo identification string.
        @type memo_id:          str
        @keyword param_vector:  The optimised parameter vector.
        @type param_vector:     numpy rank-1 array
        @keyword chi2:          The final target function value.
        @type chi2:             float
        @keyword iter_count:    The number of optimisation iterations.
        @type iter_count:       int
        @keyword f_count:       The total function call count.
        @type f_count:          int
        @keyword g_count:       The total gradient call count.
        @type g_count:          int
        @keyword h_count:       The total Hessian call count.
        @type h_count:          int
        @keyword warning:       Any optimisation warnings.
        @type warning:          str or None
        @keyword missing:       The data structure indicating which R2eff/R1rho' base data is missing.
        @type missing:          numpy rank-3 array
        @keyword back_calc:     The back-calculated R2eff/R1rho' data structure from the target function class.  This is will be transfered to the master to be stored in the r2eff_bc data structure.
        @type back_calc:        numpy rank-3 array
        @keyword completed:     A flag which if True signals that the optimisation successfully completed.
        @type completed:        bool
        """

        # Execute the base class __init__() method.
        super(Disp_result_command, self).__init__(processor=processor, completed=completed)

        # Store the arguments (to be sent back to the master).
        self.memo_id = memo_id
        self.param_vector = param_vector
        self.chi2 = chi2
        self.iter_count = iter_count
        self.f_count = f_count
        self.g_count = g_count
        self.h_count = h_count
        self.warning = warning
        self.missing = missing
        self.back_calc = back_calc
        self.completed = completed


    def run(self, processor=None, memo=None):
        """Disassemble the model-free optimisation results (on the master).

        @param processor:   Unused!
        @type processor:    None
        @param memo:        The dispersion memo.  This holds a lot of the data and objects needed for processing the results from the slave.
        @type memo:         memo
        """

        # Printout.
        if memo.sim_index != None:
            print("Simulation %s, cluster %s" % (memo.sim_index+1, memo.spin_ids))

        # Scaling.
        if memo.scaling_matrix != None:
            param_vector = dot(memo.scaling_matrix, self.param_vector)

        # Disassemble the parameter vector.
        disassemble_param_vector(param_vector=param_vector, spins=memo.spins, sim_index=memo.sim_index)
        param_conversion(spins=memo.spins, sim_index=memo.sim_index)

        # Monte Carlo minimisation statistics.
        if memo.sim_index != None:
            for spin in memo.spins:
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Chi-squared statistic.
                spin.chi2_sim[memo.sim_index] = self.chi2

                # Iterations.
                spin.iter_sim[memo.sim_index] = self.iter_count

                # Function evaluations.
                spin.f_count_sim[memo.sim_index] = self.f_count

                # Gradient evaluations.
                spin.g_count_sim[memo.sim_index] = self.g_count

                # Hessian evaluations.
                spin.h_count_sim[memo.sim_index] = self.h_count

                # Warning.
                spin.warning_sim[memo.sim_index] = self.warning

        # Normal statistics.
        else:
            for spin in memo.spins:
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Chi-squared statistic.
                spin.chi2 = self.chi2

                # Iterations.
                spin.iter = self.iter_count

                # Function evaluations.
                spin.f_count = self.f_count

                # Gradient evaluations.
                spin.g_count = self.g_count

                # Hessian evaluations.
                spin.h_count = self.h_count

                # Warning.
                spin.warning = self.warning

        # Store the back-calculated values.
        if memo.sim_index == None:
            # 1H MMQ flag.
            proton_mmq_flag = has_proton_mmq_cpmg()

            # Loop over each spin, packing the data.
            si = 0
            for spin_index in range(len(memo.spins)):
                # Skip deselected spins.
                if not memo.spins[spin_index].select:
                    continue

                # Pack the data.
                pack_back_calc_r2eff(spin=memo.spins[spin_index], spin_id=memo.spin_ids[spin_index], si=si, back_calc=self.back_calc, proton_mmq_flag=proton_mmq_flag)

                # Increment the spin index.
                si += 1
