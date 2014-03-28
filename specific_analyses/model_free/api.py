###############################################################################
#                                                                             #
# Copyright (C) 2007-2014 Edward d'Auvergne                                   #
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
"""The Lipari-Szabo model-free analysis API object."""


# Python module imports.
from copy import deepcopy
from minfx.grid import grid_split
from numpy import array, dot, float64, zeros
from numpy.linalg import inv
from re import match, search

# relax module imports.
from lib.arg_check import is_num_list
from lib.physical_constants import N15_CSA, h_bar, mu0, return_gyromagnetic_ratio
from multi import Processor_box
from pipe_control import diffusion_tensor, relax_data
from pipe_control.interatomic import return_interatom_list
from pipe_control.mol_res_spin import count_spins, exists_mol_res_spin_data, return_spin, return_spin_from_index, spin_loop
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.model_free.bmrb import Bmrb
from specific_analyses.model_free.main import Model_free_main
from specific_analyses.model_free.molmol import Molmol
from specific_analyses.model_free.parameters import are_mf_params_set, assemble_param_vector, assemble_scaling_matrix, conv_factor_rex, determine_model_type, linear_constraints, units_rex
from specific_analyses.model_free.optimisation import MF_grid_command, MF_memo, MF_minimise_command, grid_search_config, minimise_data_setup, relax_data_opt_structs, reset_min_stats
from specific_analyses.model_free.pymol import Pymol
from specific_analyses.model_free.results import Results
from target_functions.mf import Mf


class Model_free(Model_free_main, Results, Bmrb, API_base, API_common):
    """Parent class containing all the model-free specific functions."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Execute the base class __init__ method.
        super(Model_free, self).__init__()

        # Place methods into the API.
        self.base_data_loop = self._base_data_loop_spin
        self.return_error = self._return_error_relax_data
        self.return_value = self._return_value_general
        self.sim_pack_data = self._sim_pack_relax_data
        self.test_grid_ops = self._test_grid_ops_general

        # Initialise the macro classes.
        self._molmol_macros = Molmol()
        self._pymol_macros = Pymol()

        # Alias the macro creation methods.
        self.pymol_macro = self._pymol_macros.create_macro
        self.molmol_macro = self._molmol_macros.create_macro

        # Set up the global parameters.
        self.PARAMS.add('tm', scope='global', default=diffusion_tensor.default_value('tm'), conv_factor=1e-9, grace_string='\\xt\\f{}\\sm', units='ns', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Diso', scope='global', default=diffusion_tensor.default_value('Diso'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dx', scope='global', default=diffusion_tensor.default_value('Dx'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dy', scope='global', default=diffusion_tensor.default_value('Dy'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dz', scope='global', default=diffusion_tensor.default_value('Dz'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dpar', scope='global', default=diffusion_tensor.default_value('Dpar'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dper', scope='global', default=diffusion_tensor.default_value('Dper'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Da', scope='global', default=diffusion_tensor.default_value('Da'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dratio', scope='global', default=diffusion_tensor.default_value('Dratio'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('Dr', scope='global', default=diffusion_tensor.default_value('Dr'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('alpha', scope='global', default=diffusion_tensor.default_value('alpha'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('beta', scope='global', default=diffusion_tensor.default_value('beta'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('gamma', scope='global', default=diffusion_tensor.default_value('gamma'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('theta', scope='global', default=diffusion_tensor.default_value('theta'), py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('phi', scope='global', default=diffusion_tensor.default_value('phi'), py_type=float, set='params', err=True, sim=True)

        # Set up the spin parameters.
        self.PARAMS.add('model', scope='spin', desc='The model', py_type=str)
        self.PARAMS.add('equation', scope='spin', desc='The model equation', py_type=str)
        self.PARAMS.add('params', scope='spin', desc='The model parameters', py_type=list)
        self.PARAMS.add('s2', scope='spin', default=0.8, desc='S2, the model-free generalised order parameter (S2 = S2f.S2s)', py_type=float, set='params', grace_string='\\qS\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.PARAMS.add('s2f', scope='spin', default=0.8, desc='S2f, the faster motion model-free generalised order parameter', py_type=float, set='params', grace_string='\\qS\\sf\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.PARAMS.add('s2s', scope='spin', default=0.8, desc='S2s, the slower motion model-free generalised order parameter', py_type=float, set='params', grace_string='\\qS\\ss\\N\\h{-0.2}\\v{0.4}\\z{0.71}2\\Q', err=True, sim=True)
        self.PARAMS.add('local_tm', scope='spin', default=10.0 * 1e-9, desc='The spin specific global correlation time (seconds)', py_type=float, set='params', grace_string='\\xt\\f{}\\sm', units='ns', err=True, sim=True)
        self.PARAMS.add('te', scope='spin', default=100.0 * 1e-12, desc='Single motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\se', units='ps', err=True, sim=True)
        self.PARAMS.add('tf', scope='spin', default=10.0 * 1e-12, desc='Faster motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\sf', units='ps', err=True, sim=True)
        self.PARAMS.add('ts', scope='spin', default=1000.0 * 1e-12, desc='Slower motion effective internal correlation time (seconds)', py_type=float, set='params', conv_factor=1e-12, grace_string='\\xt\\f{}\\ss', units='ps', err=True, sim=True)
        self.PARAMS.add('rex', scope='spin', default=0.0, desc='Chemical exchange relaxation (sigma_ex = Rex / omega**2)', py_type=float, set='params', conv_factor=conv_factor_rex, units=units_rex, grace_string='\\qR\\sex\\Q', err=True, sim=True)
        self.PARAMS.add('csa', scope='spin', default=N15_CSA, units='ppm', desc='Chemical shift anisotropy (unitless)', py_type=float, set='params', conv_factor=1e-6, grace_string='\\qCSA\\Q', err=True, sim=True)

        # Add the minimisation data.
        self.PARAMS.add_min_data(min_stats_global=True, min_stats_spin=True)

        # Add the relaxation data parameters.
        self.PARAMS.add('ri_data', scope='spin', desc=relax_data.return_data_desc('ri_data'), py_type=dict, err=False, sim=True)
        self.PARAMS.add('ri_data_err', scope='spin', desc=relax_data.return_data_desc('ri_data_err'), py_type=dict, err=False, sim=False)


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculation of the model-free chi-squared value.

        @keyword spin_id:   The spin identification string.
        @type spin_id:      str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The optional MC simulation index.
        @type sim_index:    int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Determine the model type.
        model_type = determine_model_type()

        # Test if diffusion tensor data exists.
        if model_type != 'local_tm' and not diffusion_tensor.diff_data_exists():
            raise RelaxNoTensorError('diffusion')

        # Test if the PDB file has been loaded.
        if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and not hasattr(cdp, 'structure'):
            raise RelaxNoPdbError

        # Loop over the spins.
        for spin, id in spin_loop(spin_id, return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Test if the model-free model has been setup.
            if not spin.model:
                raise RelaxNoModelError

            # Test if the nuclear isotope type has been set.
            if not hasattr(spin, 'isotope'):
                raise RelaxSpinTypeError

            # Test if the model-free parameter values exist.
            unset_param = are_mf_params_set(spin)
            if unset_param != None:
                raise RelaxNoValueError(unset_param)

            # Test if the CSA value has been set.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Test the interatomic data.
            interatoms = return_interatom_list(spin_id)
            for interatom in interatoms:
                # No relaxation mechanism.
                if not interatom.dipole_pair:
                    continue

                # Test if unit vectors exist.
                if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and not hasattr(interatom, 'vector'):
                    raise RelaxNoVectorsError

                # Test if multiple unit vectors exist.
                if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere' and hasattr(interatom, 'vector') and is_num_list(interatom.vector[0], raise_error=False):
                    raise RelaxMultiVectorError

                # The interacting spin.
                if spin_id != interatom.spin_id1:
                    spin_id2 = interatom.spin_id1
                else:
                    spin_id2 = interatom.spin_id2
                spin2 = return_spin(spin_id2)

                # Test if the nuclear isotope type has been set.
                if not hasattr(spin2, 'isotope'):
                    raise RelaxSpinTypeError

                # Test if the interatomic distance has been set.
                if not hasattr(interatom, 'r') or interatom.r == None:
                    raise RelaxNoValueError("interatomic distance", spin_id=spin_id, spin_id2=spin_id2)

            # Skip spins where there is no data or errors.
            if not hasattr(spin, 'ri_data') or not hasattr(spin, 'ri_data_err'):
                continue

            # Make sure that the errors are strictly positive numbers.
            for ri_id in cdp.ri_ids:
                # Alias.
                err = spin.ri_data_err[ri_id]

                # Checks.
                if err != None and err == 0.0:
                    raise RelaxError("Zero error for spin '%s' for the relaxation data ID '%s', minimisation not possible." % (id, ri_id))
                elif err != None and err < 0.0:
                    raise RelaxError("Negative error of %s for spin '%s' for the relaxation data ID '%s', minimisation not possible." % (err, id, ri_id))

            # Create the initial parameter vector.
            param_vector = assemble_param_vector(spin=spin, sim_index=sim_index)

            # The relaxation data optimisation structures.
            data = relax_data_opt_structs(spin, sim_index=sim_index)

            # The spin data.
            ri_data = [array(data[0])]
            ri_data_err = [array(data[1])]
            num_frq = [data[2]]
            num_ri = [data[3]]
            ri_labels = [data[4]]
            frq = [data[5]]
            remap_table = [data[6]]
            noe_r1_table = [data[7]]
            gx = [return_gyromagnetic_ratio(spin.isotope)]
            if sim_index == None:
                csa = [spin.csa]
            else:
                csa = [spin.csa_sim[sim_index]]

            # The interatomic data.
            interatoms = return_interatom_list(spin_id)
            for i in range(len(interatoms)):
                # No relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # The surrounding spins.
                if spin_id != interatoms[i].spin_id1:
                    spin_id2 = interatoms[i].spin_id1
                else:
                    spin_id2 = interatoms[i].spin_id2
                spin2 = return_spin(spin_id2)

                # The data.
                if sim_index == None:
                    r = [interatoms[i].r]
                else:
                    r = [interatoms[i].r_sim[sim_index]]

                # Vectors.
                if model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
                    xh_unit_vectors = [interatoms[i].vector]
                else:
                    xh_unit_vectors = [None]

                # Gyromagnetic ratios.
                gh = [return_gyromagnetic_ratio(spin2.isotope)]

            # Count the number of model-free parameters for the residue index.
            num_params = [len(spin.params)]

            # Repackage the parameter values as a local model (ignore if the diffusion tensor is not fixed).
            param_values = [assemble_param_vector(model_type='mf')]

            # Package the diffusion tensor parameters.
            if model_type == 'local_tm':
                diff_params = [spin.local_tm]
                diff_type = 'sphere'
            else:
                # Diff type.
                diff_type = cdp.diff_tensor.type

                # Spherical diffusion.
                if diff_type == 'sphere':
                    diff_params = [cdp.diff_tensor.tm]

                # Spheroidal diffusion.
                elif diff_type == 'spheroid':
                    diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.theta, cdp.diff_tensor.phi]

                # Ellipsoidal diffusion.
                elif diff_type == 'ellipsoid':
                    diff_params = [cdp.diff_tensor.tm, cdp.diff_tensor.Da, cdp.diff_tensor.Dr, cdp.diff_tensor.alpha, cdp.diff_tensor.beta, cdp.diff_tensor.gamma]

            # Initialise the model-free function.
            mf = Mf(init_params=param_vector, model_type='mf', diff_type=diff_type, diff_params=diff_params, num_spins=1, equations=[spin.equation], param_types=[spin.params], param_values=param_values, relax_data=ri_data, errors=ri_data_err, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=gx, gh=gh, h_bar=h_bar, mu0=mu0, num_params=num_params, vectors=xh_unit_vectors)

            # Chi-squared calculation.
            try:
                chi2 = mf.func(param_vector)
            except OverflowError:
                chi2 = 1e200

            # Global chi-squared value.
            if model_type == 'all' or model_type == 'diff':
                cdp.chi2 = cdp.chi2 + chi2
            else:
                spin.chi2 = chi2


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """The model-free grid search function.

        @keyword lower:         The lower bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search.
                                The number of elements in the array must equal to the number of
                                parameters in the model.
        @type inc:              array of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating
                                parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The index of the simulation to apply the grid search to.  If None,
                                the normal model is optimised.
        @type sim_index:        int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Model-free minimisation function.

        Three categories of models exist for which the approach to minimisation is different.  These
        are:

        Single spin optimisations:  The 'mf' and 'local_tm' model types which are the
        model-free parameters for single spins, optionally with a local tm parameter.  These
        models have no global parameters.

        Diffusion tensor optimisations:  The 'diff' diffusion tensor model type.  No spin
        specific parameters exist.

        Optimisation of everything:  The 'all' model type consisting of all model-free and all
        diffusion tensor parameters.


        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.
                                    Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.
                                    Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow
                                    the problem to be better conditioned.
        @type scaling:              bool
        @keyword verbosity:         The amount of information to print.  The higher the value, the
                                    greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if
                                    normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The lower bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is only
                                    used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the
                                    number of parameters in the model.  This optional argument is only
                                    used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search.
                                    The number of elements in the array must equal to the number of
                                    parameters in the model.  This argument is only used when doing a
                                    grid search.
        @type inc:                  array of int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the model-free model has been setup, and that the nuclear isotope types have been set.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Not setup.
            if not spin.model:
                raise RelaxNoModelError

            # Test if the nuclear isotope type has been set.
            if not hasattr(spin, 'isotope'):
                raise RelaxSpinTypeError

        # Reset the minimisation statistics.
        if sim_index == None and min_algor != 'back_calc':
            reset_min_stats()

        # Containers for the model-free data and optimisation parameters.
        data_store = Data_container()
        opt_params = Data_container()

        # Add the imported parameters.
        data_store.h_bar = h_bar
        data_store.mu0 = mu0
        opt_params.min_algor = min_algor
        opt_params.min_options = min_options
        opt_params.func_tol = func_tol
        opt_params.grad_tol = grad_tol
        opt_params.max_iterations = max_iterations

        # Add the keyword args.
        opt_params.verbosity = verbosity

        # Determine the model type.
        data_store.model_type = determine_model_type()
        if not data_store.model_type:
            return

        # Model type for the back-calculate function.
        if min_algor == 'back_calc' and data_store.model_type != 'local_tm':
            data_store.model_type = 'mf'

        # Test if diffusion tensor data exists.
        if data_store.model_type != 'local_tm' and not diffusion_tensor.diff_data_exists():
            raise RelaxNoTensorError('diffusion')

        # Tests for the PDB file and unit vectors.
        if data_store.model_type != 'local_tm' and cdp.diff_tensor.type != 'sphere':
            # Test if the structure file has been loaded.
            if not hasattr(cdp, 'structure'):
                raise RelaxNoPdbError

            # Test if unit vectors exist.
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Get the interatomic data container.
                interatoms = return_interatom_list(spin_id)

                # Unit vectors.
                for i in range(len(interatoms)):
                    # No relaxation mechanism.
                    if not interatoms[i].dipole_pair:
                        continue

                    # Check for the vectors.
                    if not hasattr(interatoms[i], 'vector'):
                        raise RelaxNoVectorsError

        # Test if the model-free parameter values are set for minimising diffusion tensor parameters by themselves.
        if data_store.model_type == 'diff':
            # Loop over the sequence.
            for spin in spin_loop():
                unset_param = are_mf_params_set(spin)
                if unset_param != None:
                    raise RelaxNoValueError(unset_param)

        # Print out.
        if verbosity >= 1:
            if data_store.model_type == 'mf':
                print("Only the model-free parameters for single spins will be used.")
            elif data_store.model_type == 'local_mf':
                print("Only a local tm value together with the model-free parameters for single spins will be used.")
            elif data_store.model_type == 'diff':
                print("Only diffusion tensor parameters will be used.")
            elif data_store.model_type == 'all':
                print("The diffusion tensor parameters together with the model-free parameters for all spins will be used.")

        # Test if the CSA and interatomic distances have been set.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # CSA value.
            if not hasattr(spin, 'csa') or spin.csa == None:
                raise RelaxNoValueError("CSA")

            # Get the interatomic data container.
            interatoms = return_interatom_list(spin_id)

            # Interatomic distances.
            count = 0
            for i in range(len(interatoms)):
                # No relaxation mechanism.
                if not interatoms[i].dipole_pair:
                    continue

                # Check for the distances.
                if not hasattr(interatoms[i], 'r') or interatoms[i].r == None:
                    raise RelaxNoValueError("interatomic distance", spin_id=interatoms[i].spin_id1, spin_id2=interatoms[i].spin_id2)

                # Count the number of interactions.
                count += 1
            
            # Too many interactions.
            if count > 1:
                raise RelaxError("The spin '%s' has %s dipolar relaxation interactions defined, but only a maximum of one is currently supported." % (spin_id, count))

        # Number of spins, minimisation instances, and data sets for each model type.
        if data_store.model_type == 'mf' or data_store.model_type == 'local_tm':
            num_instances = count_spins(skip_desel=False)
            num_data_sets = 1
            data_store.num_spins = 1
        elif data_store.model_type == 'diff' or data_store.model_type == 'all':
            num_instances = 1
            num_data_sets = count_spins(skip_desel=False)
            data_store.num_spins = count_spins()

        # Number of spins, minimisation instances, and data sets for the back-calculate function.
        if min_algor == 'back_calc':
            num_instances = 1
            num_data_sets = 0
            data_store.num_spins = 1

        # Get the Processor box singleton (it contains the Processor instance) and alias the Processor.
        processor_box = Processor_box() 
        processor = processor_box.processor

        # Loop over the minimisation instances.
        #######################################

        for i in range(num_instances):
            # Get the spin container if required.
            if data_store.model_type == 'diff' or data_store.model_type == 'all':
                spin_index = None
                spin, data_store.spin_id = None, None
            elif min_algor == 'back_calc':
                spin_index = opt_params.min_options[0]
                spin, data_store.spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)
            else:
                spin_index = i
                spin, data_store.spin_id = return_spin_from_index(global_index=spin_index, return_spin_id=True)

            # Individual spin stuff.
            if spin and (data_store.model_type == 'mf' or data_store.model_type == 'local_tm') and not min_algor == 'back_calc':
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins missing relaxation data or errors.
                if not hasattr(spin, 'ri_data') or not hasattr(spin, 'ri_data_err'):
                    continue

            # Skip spins missing the dipolar interaction.
            if spin and (data_store.model_type == 'mf' or data_store.model_type == 'local_tm'):
                interatoms = return_interatom_list(data_store.spin_id)
                if not len(interatoms):
                    continue

            # Parameter vector and diagonal scaling.
            if min_algor == 'back_calc':
                # Create the initial parameter vector.
                opt_params.param_vector = assemble_param_vector(spin=spin, model_type=data_store.model_type)

                # Diagonal scaling.
                data_store.scaling_matrix = None

            else:
                # Create the initial parameter vector.
                opt_params.param_vector = assemble_param_vector(spin=spin, sim_index=sim_index)

                # The number of parameters.
                num_params = len(opt_params.param_vector)

                # Diagonal scaling.
                data_store.scaling_matrix = assemble_scaling_matrix(num_params, model_type=data_store.model_type, spin=spin, scaling=scaling)
                if len(data_store.scaling_matrix):
                    opt_params.param_vector = dot(inv(data_store.scaling_matrix), opt_params.param_vector)

            # Configure the grid search.
            opt_params.inc, opt_params.lower, opt_params.upper = None, None, None
            if match('^[Gg]rid', min_algor):
                opt_params.inc, opt_params.lower, opt_params.upper = grid_search_config(num_params, spin=spin, lower=lower, upper=upper, inc=inc, scaling_matrix=data_store.scaling_matrix)

            # Scaling of values for the set function.
            if match('^[Ss]et', min_algor):
                opt_params.min_options = dot(inv(data_store.scaling_matrix), opt_params.min_options)

            # Linear constraints.
            if constraints:
                opt_params.A, opt_params.b = linear_constraints(num_params, model_type=data_store.model_type, spin=spin, scaling_matrix=data_store.scaling_matrix)
            else:
                opt_params.A, opt_params.b = None, None

            # Get the data for minimisation.
            minimise_data_setup(data_store, min_algor, num_data_sets, opt_params.min_options, spin=spin, sim_index=sim_index)

            # Setup the minimisation algorithm when constraints are present.
            if constraints and not match('^[Gg]rid', min_algor):
                algor = opt_params.min_options[0]
            else:
                algor = min_algor

            # Initialise the function to minimise (for back-calculation and LM minimisation).
            if min_algor == 'back_calc' or match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                self.mf = Mf(init_params=opt_params.param_vector, model_type=data_store.model_type, diff_type=data_store.diff_type, diff_params=data_store.diff_params, scaling_matrix=data_store.scaling_matrix, num_spins=data_store.num_spins, equations=data_store.equations, param_types=data_store.param_types, param_values=data_store.param_values, relax_data=data_store.ri_data, errors=data_store.ri_data_err, bond_length=data_store.r, csa=data_store.csa, num_frq=data_store.num_frq, frq=data_store.frq, num_ri=data_store.num_ri, remap_table=data_store.remap_table, noe_r1_table=data_store.noe_r1_table, ri_labels=data_store.ri_types, gx=data_store.gx, gh=data_store.gh, h_bar=data_store.h_bar, mu0=data_store.mu0, num_params=data_store.num_params, vectors=data_store.xh_unit_vectors)

            # Levenberg-Marquardt minimisation.
            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                # Total number of ri.
                number_ri = 0
                for k in range(len(ri_data_err)):
                    number_ri = number_ri + len(ri_data_err[k])

                # Reconstruct the error data structure.
                lm_error = zeros(number_ri, float64)
                index = 0
                for k in range(len(ri_data_err)):
                    lm_error[index:index+len(ri_data_err[k])] = ri_data_err[k]
                    index = index + len(ri_data_err[k])

                opt_params.min_options = opt_params.min_options + (self.mf.lm_dri, lm_error)

            # Back-calculation.
            if min_algor == 'back_calc':
                return self.mf.calc_ri()

            # Parallelised grid search for the diffusion parameter space.
            if match('^[Gg]rid', min_algor) and data_store.model_type == 'diff':
                # Print out.
                print("Parallelised diffusion tensor grid search.")

                # Loop over each grid subdivision.
                for subdivision in grid_split(divisions=processor.processor_size(), lower=opt_params.lower, upper=opt_params.upper, inc=opt_params.inc):
                    # Set the points.
                    opt_params.subdivision = subdivision

                    # Grid search initialisation.
                    command = MF_grid_command()

                    # Pass in the data and optimisation parameters.
                    command.store_data(deepcopy(data_store), deepcopy(opt_params))

                    # Set up the model-free memo and add it to the processor queue.
                    memo = MF_memo(model_free=self, model_type=data_store.model_type, spin=spin, sim_index=sim_index, scaling=scaling, scaling_matrix=data_store.scaling_matrix)
                    processor.add_to_queue(command, memo)

                # Execute the queued elements.
                processor.run_queue()

                # Exit this method.
                return

            # Normal grid search (command initialisation).
            if search('^[Gg]rid', min_algor):
                command = MF_grid_command()

            # Minimisation of all other model types (command initialisation).
            else:
                command = MF_minimise_command()

            # Pass in the data and optimisation parameters.
            command.store_data(deepcopy(data_store), deepcopy(opt_params))

            # Set up the model-free memo and add it to the processor queue.
            memo = MF_memo(model_free=self, model_type=data_store.model_type, spin=spin, sim_index=sim_index, scaling=scaling, scaling_matrix=data_store.scaling_matrix)
            processor.add_to_queue(command, memo)

        # Execute the queued elements.
        processor.run_queue()



class Data_container:
    """Empty class to be used for data storage."""
