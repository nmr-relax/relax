###############################################################################
#                                                                             #
# Copyright (C) 2003-2014 Edward d'Auvergne                                   #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
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
"""The model-free analysis optimisation functions."""

# Python module imports.
from minfx.generic import generic_minimise
from minfx.grid import grid, grid_point_array
from numpy import array, dot, float64
import sys

# relax module imports.
import lib.arg_check
from lib.errors import RelaxError, RelaxInfError, RelaxMultiVectorError, RelaxNaNError
from lib.float import isNaN, isInf
from lib.periodic_table import periodic_table
from lib.text.sectioning import subsection
from multi import Memo, Result_command, Slave_command
from pipe_control import pipes
from pipe_control.interatomic import return_interatom_list
from pipe_control.mol_res_spin import return_spin, return_spin_from_index, spin_loop
from specific_analyses.model_free.parameters import assemble_param_vector, disassemble_param_vector
from target_functions.mf import Mf


def disassemble_result(param_vector=None, func=None, iter=None, fc=None, gc=None, hc=None, warning=None, spin=None, sim_index=None, model_type=None, scaling_matrix=None):
    """Disassemble the optimisation results.

    @keyword param_vector:      The model-free parameter vector.
    @type param_vector:         numpy array
    @keyword func:              The optimised chi-squared value.
    @type func:                 float
    @keyword iter:              The number of optimisation steps required to find the minimum.
    @type iter:                 int
    @keyword fc:                The function count.
    @type fc:                   int
    @keyword gc:                The gradient count.
    @type gc:                   int
    @keyword hc:                The Hessian count.
    @type hc:                   int
    @keyword warning:           Any optimisation warnings.
    @type warning:              str or None
    @keyword spin:              The spin container.
    @type spin:                 SpinContainer instance or None
    @keyword sim_index:         The Monte Carlo simulation index.
    @type sim_index:            int or None
    @keyword model_type:        The model-free model type, one of 'mf', 'local_tm', 'diff', or
                                'all'.
    @type model_type:           str
    @keyword scaling_matrix:    The diagonal, square scaling matrix.
    @type scaling_matrix:       numpy diagonal matrix
    """

    # No result.
    if param_vector == None:
        return

    # Alias the current data pipe.
    cdp = pipes.get_pipe()

    # Catch infinite chi-squared values.
    if isInf(func):
        raise RelaxInfError('chi-squared')

    # Catch chi-squared values of NaN.
    if isNaN(func):
        raise RelaxNaNError('chi-squared')

    # Scaling.
    if scaling_matrix != None:
        param_vector = dot(scaling_matrix, param_vector)

    # Check if the chi-squared value is lower.  This allows for a parallelised grid search!
    if sim_index == None:
        # Get the correct value.
        chi2 = None
        if (model_type == 'mf' or model_type == 'local_tm') and hasattr(cdp, 'chi2'):
            chi2 = spin.chi2
        if (model_type == 'diff' or model_type == 'all') and hasattr(cdp, 'chi2'):
            chi2 = cdp.chi2

        # Spin text.
        spin_text = ''
        if spin != None and hasattr(spin, '_spin_ids') and len(spin._spin_ids):
            spin_text = " for the spin '%s'" % spin._spin_ids[0]

        # No improvement.
        if chi2 != None and func >= chi2:
            print("Discarding the optimisation results%s, the optimised chi-squared value is higher than the current value (%s >= %s)." % (spin_text, func, chi2))

            # Exit!
            return

        # New minimum.
        else:
            print("Storing the optimisation results%s, the optimised chi-squared value is lower than the current value (%s < %s)." % (spin_text, func, chi2))

    # Disassemble the parameter vector.
    disassemble_param_vector(model_type, param_vector=param_vector, spin=spin, sim_index=sim_index)

    # Monte Carlo minimisation statistics.
    if sim_index != None:
        # Sequence specific minimisation statistics.
        if model_type == 'mf' or model_type == 'local_tm':

            # Chi-squared statistic.
            spin.chi2_sim[sim_index] = func

            # Iterations.
            spin.iter_sim[sim_index] = iter

            # Function evaluations.
            spin.f_count_sim[sim_index] = fc

            # Gradient evaluations.
            spin.g_count_sim[sim_index] = gc

            # Hessian evaluations.
            spin.h_count_sim[sim_index] = hc

            # Warning.
            spin.warning_sim[sim_index] = warning

        # Global minimisation statistics.
        elif model_type == 'diff' or model_type == 'all':
            # Chi-squared statistic.
            cdp.chi2_sim[sim_index] = func

            # Iterations.
            cdp.iter_sim[sim_index] = iter

            # Function evaluations.
            cdp.f_count_sim[sim_index] = fc

            # Gradient evaluations.
            cdp.g_count_sim[sim_index] = gc

            # Hessian evaluations.
            cdp.h_count_sim[sim_index] = hc

            # Warning.
            cdp.warning_sim[sim_index] = warning

    # Normal statistics.
    else:
        # Sequence specific minimisation statistics.
        if model_type == 'mf' or model_type == 'local_tm':
            # Chi-squared statistic.
            spin.chi2 = func

            # Iterations.
            spin.iter = iter

            # Function evaluations.
            spin.f_count = fc

            # Gradient evaluations.
            spin.g_count = gc

            # Hessian evaluations.
            spin.h_count = hc

            # Warning.
            spin.warning = warning

        # Global minimisation statistics.
        elif model_type == 'diff' or model_type == 'all':
            # Chi-squared statistic.
            cdp.chi2 = func

            # Iterations.
            cdp.iter = iter

            # Function evaluations.
            cdp.f_count = fc

            # Gradient evaluations.
            cdp.g_count = gc

            # Hessian evaluations.
            cdp.h_count = hc

            # Warning.
            cdp.warning = warning


def minimise_data_setup(data_store, min_algor, num_data_sets, min_options, spin=None, sim_index=None):
    """Set up all the data required for minimisation.

    @param data_store:      A data storage container.
    @type data_store:       class instance
    @param min_algor:       The minimisation algorithm to use.
    @type min_algor:        str
    @param num_data_sets:   The number of data sets.
    @type num_data_sets:    int
    @param min_options:     The minimisation options array.
    @type min_options:      list
    @keyword spin:          The spin data container.
    @type spin:             SpinContainer instance
    @keyword sim_index:     The optional MC simulation index.
    @type sim_index:        int
    @return:                An insane tuple.  The full tuple is (ri_data, ri_data_err, equations, param_types, param_values, r, csa, num_frq, frq, num_ri, remap_table, noe_r1_table, ri_types, num_params, xh_unit_vectors, diff_type, diff_params)
    @rtype:                 tuple
    """

    # Initialise the data structures for the model-free function.
    data_store.ri_data = []
    data_store.ri_data_err = []
    data_store.equations = []
    data_store.param_types = []
    data_store.param_values = None
    data_store.r = []
    data_store.csa = []
    data_store.num_frq = []
    data_store.frq = []
    data_store.num_ri = []
    data_store.remap_table = []
    data_store.noe_r1_table = []
    data_store.ri_types = []
    data_store.gx = []
    data_store.gh = []
    data_store.num_params = []
    data_store.xh_unit_vectors = []
    if data_store.model_type == 'local_tm':
        data_store.mf_params = []
    elif data_store.model_type == 'diff':
        data_store.param_values = []

    # Set up the data for the back_calc function.
    if min_algor == 'back_calc':
        # The spin data.
        data_store.ri_data = [0.0]
        data_store.ri_data_err = [0.000001]
        data_store.equations = [spin.equation]
        data_store.param_types = [spin.params]
        data_store.csa = [spin.csa]
        data_store.num_frq = [1]
        data_store.frq = [[min_options[3]]]
        data_store.num_ri = [1]
        data_store.remap_table = [[0]]
        data_store.noe_r1_table = [[None]]
        data_store.ri_types = [[min_options[2]]]
        data_store.gx = [periodic_table.gyromagnetic_ratio(spin.isotope)]

        # The interatomic data.
        interatoms = return_interatom_list(data_store.spin_id)
        for i in range(len(interatoms)):
            # No relaxation mechanism.
            if not interatoms[i].dipole_pair:
                continue

            # The surrounding spins.
            if data_store.spin_id != interatoms[i].spin_id1:
                spin_id2 = interatoms[i].spin_id1
            else:
                spin_id2 = interatoms[i].spin_id2
            spin2 = return_spin(spin_id2)

            # The data.
            data_store.r = [interatoms[i].r]
            data_store.gh = [periodic_table.gyromagnetic_ratio(spin2.isotope)]
            if data_store.model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                data_store.xh_unit_vectors = [interatoms[i].vector]
            else:
                data_store.xh_unit_vectors = [None]

        # Count the number of model-free parameters for the spin index.
        data_store.num_params = [len(spin.params)]

    # Loop over the number of data sets.
    for j in range(num_data_sets):
        # Set the spin index and get the spin, if not already set.
        if data_store.model_type == 'diff' or data_store.model_type == 'all':
            spin_index = j
            spin, data_store.spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)

        # Skip deselected spins.
        if not spin.select:
            continue

        # Skip spins where there is no data or errors.
        if not hasattr(spin, 'ri_data') or not hasattr(spin, 'ri_data_err'):
            continue

        # Make sure that the errors are strictly positive numbers.
        for ri_id in cdp.ri_ids:
            # Skip missing data.
            if not ri_id in spin.ri_data_err:
                continue

            # Alias.
            err = spin.ri_data_err[ri_id]

            # Checks.
            if err != None and err == 0.0:
                raise RelaxError("Zero error for spin '%s' for the relaxation data ID '%s', minimisation not possible." % (data_store.spin_id, ri_id))
            elif err != None and err < 0.0:
                raise RelaxError("Negative error of %s for spin '%s' for the relaxation data ID '%s', minimisation not possible." % (err, data_store.spin_id, ri_id))

        # The relaxation data optimisation structures.
        data = relax_data_opt_structs(spin, sim_index=sim_index)

        # Append the data.
        data_store.ri_data.append(data[0])
        data_store.ri_data_err.append(data[1])
        data_store.num_frq.append(data[2])
        data_store.num_ri.append(data[3])
        data_store.ri_types.append(data[4])
        data_store.frq.append(data[5])
        data_store.remap_table.append(data[6])
        data_store.noe_r1_table.append(data[7])
        if sim_index == None or data_store.model_type == 'diff':
            data_store.csa.append(spin.csa)
        else:
            data_store.csa.append(spin.csa_sim[sim_index])

        # Repackage the spin data.
        data_store.equations.append(spin.equation)
        data_store.param_types.append(spin.params)
        data_store.gx.append(periodic_table.gyromagnetic_ratio(spin.isotope))

        # Repackage the interatomic data.
        interatoms = return_interatom_list(data_store.spin_id)
        for i in range(len(interatoms)):
            # No relaxation mechanism.
            if not interatoms[i].dipole_pair:
                continue

            # The surrounding spins.
            if data_store.spin_id != interatoms[i].spin_id1:
                spin_id2 = interatoms[i].spin_id1
            else:
                spin_id2 = interatoms[i].spin_id2
            spin2 = return_spin(spin_id2)

            # The data.
            data_store.gh.append(periodic_table.gyromagnetic_ratio(spin2.isotope))
            if sim_index == None or data_store.model_type == 'diff' or not hasattr(interatoms[i], 'r_sim'):
                data_store.r.append(interatoms[i].r)
            else:
                data_store.r.append(interatoms[i].r_sim[sim_index])

            # Vectors.
            if data_store.model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                # Check that this is a single vector!
                if lib.arg_check.is_num_list(interatoms[i].vector[0], raise_error=False):
                    raise RelaxMultiVectorError(data_store.spin_id)

                # Store the vector.
                data_store.xh_unit_vectors.append(interatoms[i].vector)

            # No vector.
            else:
                data_store.xh_unit_vectors.append(None)

            # Stop - only one mechanism is current supported.
            break

        # Model-free parameter values.
        if data_store.model_type == 'local_tm':
            pass

        # Count the number of model-free parameters for the spin index.
        data_store.num_params.append(len(spin.params))

        # Repackage the parameter values for minimising just the diffusion tensor parameters.
        if data_store.model_type == 'diff':
            data_store.param_values.append(assemble_param_vector(model_type='mf'))

    # Convert to numpy arrays.
    for k in range(len(data_store.ri_data)):
        data_store.ri_data[k] = array(data_store.ri_data[k], float64)
        data_store.ri_data_err[k] = array(data_store.ri_data_err[k], float64)

    # Diffusion tensor type.
    if data_store.model_type == 'local_tm':
        data_store.diff_type = 'sphere'
    else:
        data_store.diff_type = cdp.diff_tensor.type

    # Package the diffusion tensor parameters.
    data_store.diff_params = None
    if data_store.model_type == 'mf':
        # Spherical diffusion.
        if data_store.diff_type == 'sphere':
            data_store.diff_params = [cdp.diff_tensor.tm]

        # Spheroidal diffusion.
        elif data_store.diff_type == 'spheroid':
            data_store.diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.theta, cdp.diff_tensor.phi]

        # Ellipsoidal diffusion.
        elif data_store.diff_type == 'ellipsoid':
            data_store.diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.Dr, cdp.diff_tensor.alpha, cdp.diff_tensor.beta, cdp.diff_tensor.gamma]
    elif min_algor == 'back_calc' and data_store.model_type == 'local_tm':
        # Spherical diffusion.
        data_store.diff_params = [spin.local_tm]


def relax_data_opt_structs(spin, sim_index=None):
    """Package the relaxation data into the data structures used for optimisation.

    @param spin:        The spin container to extract the data from.
    @type spin:         SpinContainer instance
    @keyword sim_index: The optional MC simulation index.
    @type sim_index:    int
    @return:            The structures ri_data, ri_data_err, num_frq, num_ri, ri_ids, frq, remap_table, noe_r1_table.
    @rtype:             tuple
    """

    # Initialise the data.
    ri_data = []
    ri_data_err = []
    ri_labels = []
    frq = []
    remap_table = []
    noe_r1_table = []

    # Loop over the relaxation data.
    for ri_id in cdp.ri_ids:
        # Skip missing data.
        if ri_id not in spin.ri_data:
            continue

        # The Rx data.
        if sim_index == None:
            data = spin.ri_data[ri_id]
        else:
            data = spin.ri_data_sim[ri_id][sim_index]

        # The errors.
        err = spin.ri_data_err[ri_id]

        # Missing data, so don't add it.
        if data == None or err == None:
            continue

        # Append the data and error.
        ri_data.append(data)
        ri_data_err.append(err)

        # The labels.
        ri_labels.append(cdp.ri_type[ri_id])

        # The frequencies.
        if cdp.spectrometer_frq[ri_id] not in frq:
            frq.append(cdp.spectrometer_frq[ri_id])

        # The remap table.
        remap_table.append(frq.index(cdp.spectrometer_frq[ri_id]))

        # The NOE to R1 mapping table.
        noe_r1_table.append(None)

    # The number of data sets.
    num_ri = len(ri_data)

    # Fill the NOE to R1 mapping table.
    for i in range(num_ri):
        # If the data corresponds to 'NOE', try to find if the corresponding R1 data.
        if cdp.ri_type[cdp.ri_ids[i]] == 'NOE':
            for j in range(num_ri):
                if cdp.ri_type[cdp.ri_ids[j]] == 'R1' and cdp.spectrometer_frq[cdp.ri_ids[i]] == cdp.spectrometer_frq[cdp.ri_ids[j]]:
                    noe_r1_table[i] = j

    # Return the structures.
    return ri_data, ri_data_err, len(frq), num_ri, ri_labels, frq, remap_table, noe_r1_table



class MF_memo(Memo):
    """The model-free memo class.

    Not quite a momento so a memo.
    """

    def __init__(self, model_free=None, model_type=None, spin=None, sim_index=None, scaling_matrix=None):
        """Initialise the model-free memo class.

        This memo stores the model-free class instance so that the disassemble_result() method can be called to store the optimisation results.  The other args are those required by this method but not generated through optimisation.

        @keyword model_free:        The model-free class instance.
        @type model_free:           specific_analyses.model_free.Model_free instance
        @keyword spin:              The spin data container.  If this argument is supplied, then the spin_id argument will be ignored.
        @type spin:                 SpinContainer instance
        @keyword sim_index:         The optional MC simulation index.
        @type sim_index:            int
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        """

        # Execute the base class __init__() method.
        super(MF_memo, self).__init__()

        # Store the arguments.
        self.model_free = model_free
        self.model_type = model_type
        self.spin = spin
        self.sim_index = sim_index
        self.scaling_matrix = scaling_matrix



class MF_minimise_command(Slave_command):
    """Command class for standard model-free minimisation."""

    def __init__(self):
        """Initialise the base class."""

        # Execute the base class __init__() method.
        super(MF_minimise_command, self).__init__()


    def optimise(self):
        """Model-free optimisation.

        @return:    The optimisation results consisting of the parameter vector, function value, iteration count, function count, gradient count, Hessian count, and warnings.
        @rtype:     tuple of numpy array, float, int, int, int, int, str
        """

        # Minimisation.
        results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.opt_params.param_vector, min_algor=self.opt_params.min_algor, min_options=self.opt_params.min_options, func_tol=self.opt_params.func_tol, grad_tol=self.opt_params.grad_tol, maxiter=self.opt_params.max_iterations, A=self.opt_params.A, b=self.opt_params.b, full_output=True, print_flag=self.opt_params.verbosity)

        # Return the minfx results unmodified.
        return results


    def run(self, processor, completed):
        """Setup and perform the model-free optimisation."""

        # Initialise the function to minimise.
        self.mf = Mf(init_params=self.opt_params.param_vector, model_type=self.data.model_type, diff_type=self.data.diff_type, diff_params=self.data.diff_params, scaling_matrix=self.data.scaling_matrix, num_spins=self.data.num_spins, equations=self.data.equations, param_types=self.data.param_types, param_values=self.data.param_values, relax_data=self.data.ri_data, errors=self.data.ri_data_err, bond_length=self.data.r, csa=self.data.csa, num_frq=self.data.num_frq, frq=self.data.frq, num_ri=self.data.num_ri, remap_table=self.data.remap_table, noe_r1_table=self.data.noe_r1_table, ri_labels=self.data.ri_types, gx=self.data.gx, gh=self.data.gh, h_bar=self.data.h_bar, mu0=self.data.mu0, num_params=self.data.num_params, vectors=self.data.xh_unit_vectors)

        # Printout.
        if self.opt_params.verbosity >= 1 and (self.data.model_type == 'mf' or self.data.model_type == 'local_tm'):
            subsection(file=sys.stdout, text="Optimisation:  Spin '%s'" % self.data.spin_id, prespace=2, postspace=0)

        # Preform optimisation.
        results = self.optimise()

        # Disassemble the results list.
        param_vector, func, iter, fc, gc, hc, warning = results

        processor.return_object(MF_result_command(processor, self.memo_id, param_vector, func, iter, fc, gc, hc, warning, completed=False))


    def store_data(self, data, opt_params):
        """Store all the data required for model-free optimisation.

        @param data:        The data used to initialise the model-free target function class.
        @type data:         class instance
        @param opt_params:  The parameters and data required for optimisation using minfx.
        @type opt_params:   class instance
        """

        # Store the data.
        self.data = data
        self.opt_params = opt_params



class MF_grid_command(MF_minimise_command):
    """Command class for the model-free grid search."""

    def __init__(self):
        """Initialise all the data."""

        # Execute the base class __init__() method.
        super(MF_grid_command, self).__init__()


    def optimise(self):
        """Model-free grid search.

        @return:    The optimisation results consisting of the parameter vector, function value, iteration count, function count, gradient count, Hessian count, and warnings.
        @rtype:     tuple of numpy array, float, int, int, int, int, str
        """

        # Normal grid search.
        if not hasattr(self.opt_params, 'subdivision'):
            results = grid(func=self.mf.func, args=(), num_incs=self.opt_params.inc, lower=self.opt_params.lower, upper=self.opt_params.upper, A=self.opt_params.A, b=self.opt_params.b, verbosity=self.opt_params.verbosity)

        # Subdivided grid.
        else:
            results = grid_point_array(func=self.mf.func, args=(), points=self.opt_params.subdivision, verbosity=self.opt_params.verbosity)

        # Unpack the results.
        param_vector, func, iter, warning = results
        fc = iter
        gc = 0.0
        hc = 0.0

        # Return everything.
        return param_vector, func, iter, fc, gc, hc, warning



class MF_result_command(Result_command):
    """Class for processing the model-free results."""

    def __init__(self, processor, memo_id, param_vector, func, iter, fc, gc, hc, warning, completed):
        """Set up the class, placing the minimisation results here."""

        # Execute the base class __init__() method.
        super(MF_result_command, self).__init__(processor=processor, completed=completed)

        # Store the arguments.
        self.memo_id = memo_id
        self.param_vector = param_vector
        self.func = func
        self.iter = iter
        self.fc = fc
        self.gc = gc
        self.hc = hc
        self.warning = warning


    def run(self, processor, memo):
        """Disassemble the model-free optimisation results.

        @param processor:   Unused!
        @type processor:    None
        @param memo:        The model-free memo.
        @type memo:         memo
        """

        # Disassemble the results.
        disassemble_result(param_vector=self.param_vector, func=self.func, iter=self.iter, fc=self.fc, gc=self.gc, hc=self.hc, warning=self.warning, spin=memo.spin, sim_index=memo.sim_index, model_type=memo.model_type, scaling_matrix=memo.scaling_matrix)
