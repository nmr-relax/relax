###############################################################################
#                                                                             #
# Copyright (C) 2009 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for the specific methods of the Frame Order theories."""

# Python module imports.
from copy import deepcopy
from math import pi
from minfx.generic import generic_minimise
from numpy import array, float64, ones, transpose, zeros
from re import search
from warnings import warn

# relax module imports.
from float import isNaN, isInf
from generic_fns import pipes
from generic_fns.angles import wrap_angles
from generic_fns.structure.geometric import cone_edge, generate_vector_dist, generate_vector_residues, stitch_cone_to_edge
from generic_fns.structure.internal import Internal
from maths_fns import frame_order
from maths_fns.frame_order_matrix_ops import generate_vector
from maths_fns.rotation_matrix import two_vect_to_R
from relax_errors import RelaxError, RelaxInfError, RelaxNaNError, RelaxNoModelError
from relax_io import open_write_file
from relax_warnings import RelaxWarning
from specific_fns.base_class import Common_functions


class Frame_order(Common_functions):
    """Class containing the specific methods of the Frame Order theories."""

    def __minimise_setup_tensors(self, sim_index=None):
        """Set up the data structures for optimisation using alignment tensors as base data sets.

        @keyword sim_index: The simulation index.  This should be None if normal optimisation is
                            desired.
        @type sim_index:    None or int
        @return:            The assembled data structures for using alignment tensors as the base
                            data for optimisation.  These include:
                                - full_tensors, the full tensors as concatenated arrays.
                                - red_tensors, the reduced tensors as concatenated arrays.
                                - red_err, the reduced tensor errors as concatenated arrays.
        @rtype:             tuple of 3 numpy nx5D, rank-1 arrays
        """

        # Checks.
        if not hasattr(cdp, 'ref_domain'):
            raise RelaxError("The reference domain has not been set up.")
        if not hasattr(cdp.align_tensors, 'reduction'):
            raise RelaxError("The tensor reductions have not been specified.")
        for i, tensor in self.__tensor_loop():
            if not hasattr(tensor, 'domain'):
                raise RelaxError("The domain that the '%s' tensor is attached to has not been set" % tensor.name)

        # Initialise.
        n = len(cdp.align_tensors.reduction)
        full_tensors = zeros(n*5, float64)
        red_tensors  = zeros(n*5, float64)
        red_err = ones(n*5, float64) * 1e-5
        full_in_ref_frame = zeros(n, float64)

        # Loop over the full tensors.
        for i, tensor in self.__tensor_loop(red=False):
            # The full tensor.
            full_tensors[5*i + 0] = tensor.Axx
            full_tensors[5*i + 1] = tensor.Ayy
            full_tensors[5*i + 2] = tensor.Axy
            full_tensors[5*i + 3] = tensor.Axz
            full_tensors[5*i + 4] = tensor.Ayz

            # The full tensor corresponds to the frame of reference.
            if cdp.ref_domain == tensor.domain:
                full_in_ref_frame[i] = 1

        # Loop over the reduced tensors.
        for i, tensor in self.__tensor_loop(red=True):
            # The reduced tensor (simulation data).
            if sim_index != None:
                red_tensors[5*i + 0] = tensor.Axx_sim[sim_index]
                red_tensors[5*i + 1] = tensor.Ayy_sim[sim_index]
                red_tensors[5*i + 2] = tensor.Axy_sim[sim_index]
                red_tensors[5*i + 3] = tensor.Axz_sim[sim_index]
                red_tensors[5*i + 4] = tensor.Ayz_sim[sim_index]

            # The reduced tensor.
            else:
                red_tensors[5*i + 0] = tensor.Axx
                red_tensors[5*i + 1] = tensor.Ayy
                red_tensors[5*i + 2] = tensor.Axy
                red_tensors[5*i + 3] = tensor.Axz
                red_tensors[5*i + 4] = tensor.Ayz

            # The reduced tensor errors.
            if hasattr(tensor, 'Axx_err'):
                red_err[5*i + 0] = tensor.Axx_err
                red_err[5*i + 1] = tensor.Ayy_err
                red_err[5*i + 2] = tensor.Axy_err
                red_err[5*i + 3] = tensor.Axz_err
                red_err[5*i + 4] = tensor.Ayz_err

        # Return the data structures.
        return full_tensors, red_tensors, red_err, full_in_ref_frame


    def __tensor_loop(self, red=False):
        """Generator method for looping over the full or reduced tensors.

        @keyword red:   A flag which if True causes the reduced tensors to be returned, and if False
                        the full tensors are returned.
        @type red:      bool
        @return:        The tensor index and the tensor.
        @rtype:         (int, AlignTensorData instance)
        """

        # Number of tensor pairs.
        n = len(cdp.align_tensors.reduction)

        # Alias.
        data = cdp.align_tensors
        list = data.reduction

        # Full or reduced index.
        if red:
            index = 1
        else:
            index = 0

        # Loop over the reduction list.
        for i in range(n):
            yield i, data[list[i][index]]


    def __update_model(self):
        """Update the model parameters as necessary."""

        # Initialise the list of model parameters.
        if not hasattr(cdp, 'params'):
            cdp.params = []

        # Initialisation flag.
        init = False
        if not len(cdp.params):
            init = True

        # Set up the tensor rotation parameter arrays.
        if init:
            cdp.params.append('alpha')
            cdp.params.append('beta')
            cdp.params.append('gamma')

        # Initialise the tensor rotation angles.
        if not hasattr(cdp, 'alpha'):
            cdp.alpha = 0.0
        if not hasattr(cdp, 'beta'):
            cdp.beta = 0.0
        if not hasattr(cdp, 'gamma'):
            cdp.gamma = 0.0

        # Isotropic cone model.
        if cdp.model == 'iso cone':
            # Set up the parameter arrays.
            if init:
                cdp.params.append('theta_axis')
                cdp.params.append('phi_axis')
                cdp.params.append('theta_cone')

            # Initialise the cone axis angles and cone angle values.
            if not hasattr(cdp, 'theta_axis'):
                cdp.theta_axis = 0.0
            if not hasattr(cdp, 'phi_axis'):
                cdp.phi_axis = 0.0
            if not hasattr(cdp, 'theta_cone'):
                cdp.theta_cone = 0.0


    def __unpack_opt_results(self, results, sim_index=None):
        """Unpack and store the Frame Order optimisation results.

        @param results:     The results tuple returned by the minfx generic_minimise() function.
        @type results:      tuple
        @param sim_index:   The index of the simulation to optimise.  This should be None for normal
                            optimisation.
        @type sim_index:    None or int
         """

        # Disassemble the results.
        param_vector, func, iter_count, f_count, g_count, h_count, warning = results

        # Catch infinite chi-squared values.
        if isInf(func):
            raise RelaxInfError('chi-squared')

        # Catch chi-squared values of NaN.
        if isNaN(func):
            raise RelaxNaNError('chi-squared')

        # The rigid model.
        if cdp.model == 'rigid':
            # Disassemble the parameter vector.
            alpha, beta, gamma = param_vector

        # Isotropic cone model.
        elif cdp.model == 'iso cone':
            # Disassemble the parameter vector.
            alpha, beta, gamma, theta_axis, phi_axis, theta_cone = param_vector

            # Wrap the cone angle to be between 0 and pi.
            if theta_cone < 0.0:
                theta_cone = -theta_cone
            if theta_cone > pi:
                theta_cone = 2.0*pi - theta_cone

            # Monte Carlo simulation data structures.
            if sim_index != None:
                # Model parameters.
                cdp.theta_axis_sim[sim_index] = theta_axis
                cdp.phi_axis_sim[sim_index] = phi_axis
                cdp.theta_cone_sim[sim_index] = theta_cone

            # Normal data structures.
            else:
                # Model parameters.
                cdp.theta_axis = theta_axis
                cdp.phi_axis = phi_axis
                cdp.theta_cone = theta_cone

        # Wrap the Euler angles.
        alpha = wrap_angles(alpha, 0.0, 2.0*pi)
        beta  = wrap_angles(beta, 0.0, 2.0*pi)
        gamma = wrap_angles(gamma, 0.0, 2.0*pi)

        # Fold beta to be between 0 and pi.
        if beta >= pi:
            alpha = alpha - pi
            beta = 2*pi - beta
            gamma = gamma - pi

        # Wrap again.
        alpha = wrap_angles(alpha, 0.0, 2.0*pi)
        beta  = wrap_angles(beta, 0.0, 2.0*pi)
        gamma = wrap_angles(gamma, 0.0, 2.0*pi)

        # Monte Carlo simulation data structures.
        if sim_index != None:
            # Tensor rotation.
            cdp.alpha_sim[sim_index] = alpha
            cdp.beta_sim[sim_index] = beta
            cdp.gamma_sim[sim_index] = gamma

            # Optimisation stats.
            cdp.chi2_sim[sim_index] = func
            cdp.iter_sim[sim_index] = iter_count
            cdp.f_count_sim[sim_index] = f_count
            cdp.g_count_sim[sim_index] = g_count
            cdp.h_count_sim[sim_index] = h_count
            cdp.warning_sim[sim_index] = warning

        # Normal optimisation data structures.
        else:
            # Tensor rotation.
            cdp.alpha = alpha
            cdp.beta = beta
            cdp.gamma = gamma

            # Optimisation stats.
            cdp.chi2 = func
            cdp.iter = iter_count
            cdp.f_count = f_count
            cdp.g_count = g_count
            cdp.h_count = h_count
            cdp.warning = warning



    def back_calc(self):
        """Back-calculation of the reduced alignment tensor.

        @return:                    The peak intensity for the desired relaxation time.
        @rtype:                     float
        """

        # The rigid model initial parameter vector (the cone axis angles and the cone angle).
        if cdp.model == 'rigid':
            param_vector = array([cdp.alpha, cdp.beta, cdp.gamma], float64)

        # The isotropic cone model initial parameter vector (the cone axis angles and the cone angle).
        elif cdp.model == 'iso cone':
            param_vector = array([cdp.alpha, cdp.beta, cdp.gamma, cdp.theta_axis, cdp.phi_axis, cdp.theta_cone], float64)

        # Get the data structures for optimisation using the tensors as base data sets.
        full_tensors, red_tensors, red_tensor_err, full_in_ref_frame = self.__minimise_setup_tensors()

        # Set up the optimisation function.
        target = frame_order.Frame_order(model=cdp.model, full_tensors=full_tensors, red_tensors=red_tensors, red_errors=red_tensor_err, full_in_ref_frame=full_in_ref_frame)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        target.func(param_vector)

        # Return the reduced tensors.
        return target.red_tensors_bc


    def base_data_loop(self):
        """Generator method for looping nothing.

        The loop essentially consists of a single element.

        @return:    Nothing.
        @rtype:     None
        """

        yield None


    def calculate(self, verbosity=None):
        """Calculate the chi-squared value for the current parameter values."""

        # The rigid model initial parameter vector (the cone axis angles and the cone angle).
        if cdp.model == 'rigid':
            param_vector = array([cdp.alpha, cdp.beta, cdp.gamma], float64)

        # The isotropic cone model initial parameter vector (the cone axis angles and the cone angle).
        elif cdp.model == 'iso cone':
            param_vector = array([cdp.alpha, cdp.beta, cdp.gamma, cdp.theta_axis, cdp.phi_axis, cdp.theta_cone], float64)

        # Get the data structures for optimisation using the tensors as base data sets.
        full_tensors, red_tensors, red_tensor_err, full_in_ref_frame = self.__minimise_setup_tensors()

        # Set up the optimisation function.
        target = frame_order.Frame_order(model=cdp.model, full_tensors=full_tensors, red_tensors=red_tensors, red_errors=red_tensor_err, full_in_ref_frame=full_in_ref_frame)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        chi2 = target.func(param_vector)

        # Set the chi2.
        cdp.chi2 = chi2


    def cone_pdb(self, size=30.0, file=None, dir=None, inc=40, force=False):
        """Create a PDB file containing a geometric object representing the Frame Order cone models.

        @param size:        The size of the geometric object in Angstroms.
        @type size:         float
        @param inc:         The number of increments for the filling of the cone objects.
        @type inc:          int
        @param file:        The name of the PDB file to create.
        @type file:         str
        @param dir:         The name of the directory to place the PDB file into.
        @type dir:          str
        @param force:       Flag which if set to True will cause any pre-existing file to be
                            overwritten.
        @type force:        bool
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Test the model.
        if not cdp.model in ['iso cone']:
            raise RelaxError("A cone PDB representation of the '%s' model cannot be made." % cdp.model)

        # Test for the data structures.
        if not hasattr(cdp, 'theta_cone'):
            raise RelaxError("The cone angle theta_cone does not exist.")
        if not hasattr(cdp, 'theta_axis'):
            raise RelaxError("The cone polar angle theta_axis does not exist.")
        if not hasattr(cdp, 'phi_axis'):
            raise RelaxError("The cone azimuthal angle phi_axis does not exist.")
        if not hasattr(cdp, 'pivot'):
            raise RelaxError("The pivot point for the cone motion has not been set.")

        # The cone axis. 
        cone_axis = zeros(3, float64)
        generate_vector(cone_axis, cdp.theta_axis, cdp.phi_axis)
        print(("Cone axis: %s." % cone_axis))
        print(("Cone angle: %s." % cdp.theta_cone))

        # Cone axis from simulations.
        num_sim = 0
        cone_axis_sim = None
        cone_axis_sim_new = None
        if hasattr(cdp, 'sim_number'):
            num_sim = cdp.sim_number
            cone_axis_sim = zeros((num_sim, 3), float64)
        for i in range(num_sim):
            generate_vector(cone_axis_sim[i], cdp.theta_axis_sim[i], cdp.phi_axis_sim[i])

        # Create a positive and negative cone.
        for factor in [-1, 1]:
            # Negative prefix.
            prefix = ''
            if factor == -1:
                prefix = 'neg_'

            # The rotation matrix (rotation from the z-axis to the cone axis).
            R = zeros((3, 3), float64)
            two_vect_to_R(array([0, 0, 1], float64), cone_axis, R)

            # Mirroring.
            cone_axis_new = factor*cone_axis
            if cone_axis_sim != None:
                cone_axis_sim_new = factor*cone_axis_sim
            if factor == -1:
                R = -R

            # Create the structural object.
            structure = Internal()

            # Add a molecule.
            structure.add_molecule(name='iso cone')

            # Alias the single molecule from the single model.
            mol = structure.structural_data[0].mol[0]

            # Add the pivot point.
            mol.atom_add(pdb_record='HETATM', atom_num=1, atom_name='R', res_name='PIV', res_num=1, pos=cdp.pivot, element='C')

            # Generate the axis vectors.
            print("\nGenerating the axis vectors.")
            res_num = generate_vector_residues(mol=mol, vector=cone_axis_new, atom_name='Axis', res_name_vect='AXE', sim_vectors=cone_axis_sim_new, res_num=2, origin=cdp.pivot, scale=size)

            # Generate the cone outer edge.
            print("\nGenerating the cone outer edge.")
            edge_start_atom = mol.atom_num[-1]+1
            cone_edge(mol=mol, res_name='CON', res_num=3+num_sim, apex=cdp.pivot, R=R, angle=cdp.theta_cone, length=size, inc=inc)

            # Generate the cone cap, and stitch it to the cone edge.
            print("\nGenerating the cone cap.")
            cone_start_atom = mol.atom_num[-1]+1
            generate_vector_dist(mol=mol, res_name='CON', res_num=3+num_sim, centre=cdp.pivot, R=R, max_angle=cdp.theta_cone, scale=size, inc=inc)
            stitch_cone_to_edge(mol=mol, cone_start=cone_start_atom, edge_start=edge_start_atom+1, max_angle=cdp.theta_cone, inc=inc)

            # Create the PDB file.
            print("\nGenerating the PDB file.")
            pdb_file = open_write_file(prefix+file, dir, force=force)
            structure.write_pdb(pdb_file)
            pdb_file.close()


    def create_mc_data(self, index):
        """Create the Monte Carlo data by back calculating the reduced tensor data.

        @keyword index: Not used.
        @type index:    None
        @return:        The Monte Carlo simulation data.
        @rtype:         list of floats
        """

        # Back calculate the tensors.
        red_tensors_bc = self.back_calc()

        # Return the data.
        return red_tensors_bc


    def data_names(self, set='all', error_names=False, sim_names=False):
        """Function for returning a list of names of data structures.

        Description
        ===========

        The names are as follows:

            - 'params', an array of the parameter names associated with the model.
            - 'chi2', chi-squared value.
            - 'iter', iterations.
            - 'f_count', function count.
            - 'g_count', gradient count.
            - 'h_count', hessian count.
            - 'warning', minimisation warning.

        The isotropic cone specific model parameters are:

            - 'theta_axis', the cone axis polar angle (for the isotropic cone model).
            - 'phi_axis', the cone axis azimuthal angle (for the isotropic cone model).
            - 'theta_cone', the isotropic cone angle.


        @keyword set:           The set of object names to return.  This can be set to 'all' for all
                                names, to 'generic' for generic object names, 'params' for the
                                Frame Order parameter names, or to 'min' for minimisation specific
                                object names.
        @type set:              str
        @keyword error_names:   A flag which if True will add the error object names as well.
        @type error_names:      bool
        @keyword sim_names:     A flag which if True will add the Monte Carlo simulation object
                                names as well.
        @type sim_names:        bool
        @return:                The list of object names.
        @rtype:                 list of str
        """

        # Initialise.
        names = []

        # Generic.
        if set == 'all' or set == 'generic':
            names.append('params')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('alpha')
            names.append('beta')
            names.append('gamma')

            # The isotropic cone model.
            if hasattr(cdp, 'model') and cdp.model == 'iso cone':
                names.append('theta_axis')
                names.append('phi_axis')
                names.append('theta_cone')

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        # Parameter errors.
        if error_names and (set == 'all' or set == 'params'):
            names.append('alpha_err')
            names.append('beta_err')
            names.append('gamma_err')

            # The isotropic cone model.
            if hasattr(cdp, 'model') and  cdp.model == 'iso cone':
                names.append('theta_axis_err')
                names.append('phi_axis_err')
                names.append('theta_cone_err')

        # Parameter simulation values.
        if sim_names and (set == 'all' or set == 'params'):
            names.append('alpha_sim')
            names.append('beta_sim')
            names.append('gamma_sim')

            # The isotropic cone model.
            if hasattr(cdp, 'model') and  cdp.model == 'iso cone':
                names.append('theta_axis_sim')
                names.append('phi_axis_sim')
                names.append('theta_cone_sim')

        # Return the names.
        return names


    def grid_search(self, lower, upper, inc, constraints=False, verbosity=0, sim_index=None):
        """Perform a grid search.

        @param lower:       The lower bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type lower:        array of numbers
        @param upper:       The upper bounds of the grid search which must be equal to the number of
                            parameters in the model.
        @type upper:        array of numbers
        @param inc:         The increments for each dimension of the space for the grid search.  The
                            number of elements in the array must equal to the number of parameters
                            in the model.
        @type inc:          int or array of int
        @param constraints: If True, constraints are applied during the grid search (eliminating
                            parts of the grid).  If False, no constraints are used.
        @type constraints:  bool
        @param verbosity:   A flag specifying the amount of information to print.  The higher the
                            value, the greater the verbosity.
        @type verbosity:    int
        """

        # Test if the Frame Order model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('Frame Order')

        # The number of parameters.
        n = len(cdp.params)

        # If inc is an int, convert it into an array of that value.
        if isinstance(inc, int):
            inc = [inc]*n

        # Initialise the grid_ops structure.
        grid_ops = []
        """This structure is a list of lists.  The first dimension corresponds to the model
        parameter.  The second dimension has the elements: 0, the number of increments in that
        dimension; 1, the lower limit of the grid; 2, the upper limit of the grid."""

        # Set the grid search options.
        for i in xrange(n):
            # Euler angles.
            if cdp.params[i] == 'alpha':
                grid_ops.append([inc[i], 0.0, 2*pi * (1.0 - 1.0/inc[i])])
            if cdp.params[i] == 'beta':
                grid_ops.append([inc[i]/2, 0.0, pi * (1.0 - 1.0/inc[i])])
            if cdp.params[i] == 'gamma':
                grid_ops.append([inc[i], 0.0, 2*pi * (1.0 - 1.0/inc[i])])

            # The isotropic cone model.
            if cdp.model == 'iso cone':
                # Cone axis angles and cone angle.
                if cdp.params[i] == 'theta_axis':
                    grid_ops.append([inc[i], 0.0, pi * (1.0 - 1.0/inc[i])])
                if cdp.params[i] == 'phi_axis':
                    grid_ops.append([inc[i], 0.0, 2*pi * (1.0 - 1.0/inc[i])])

                # The cone angle.
                if cdp.params[i] == 'theta_cone':
                    grid_ops.append([inc[i], 0.0, pi * (1.0 - 1.0/inc[i])])

            # Lower bound (if supplied).
            if lower:
                grid_ops[i][1] = lower[i]

            # Upper bound (if supplied).
            if upper:
                grid_ops[i][1] = upper[i]

        # Minimisation.
        self.minimise(min_algor='grid', min_options=grid_ops, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None):
        """Minimisation function.

        @param min_algor:       The minimisation algorithm to use.
        @type min_algor:        str
        @param min_options:     An array of options to be used by the minimisation algorithm.
        @type min_options:      array of str
        @param func_tol:        The function tolerance which, when reached, terminates optimisation.
                                Setting this to None turns of the check.
        @type func_tol:         None or float
        @param grad_tol:        The gradient tolerance which, when reached, terminates optimisation.
                                Setting this to None turns of the check.
        @type grad_tol:         None or float
        @param max_iterations:  The maximum number of iterations for the algorithm.
        @type max_iterations:   int
        @param constraints:     If True, constraints are used during optimisation.
        @type constraints:      bool
        @param scaling:         If True, diagonal scaling is enabled during optimisation to allow
                                the problem to be better conditioned.
        @type scaling:          bool
        @param verbosity:       A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        @param sim_index:       The index of the simulation to optimise.  This should be None if
                                normal optimisation is desired.
        @type sim_index:        None or int
        """

        # Constraints not implemented yet.
        if constraints:
            # Turn the constraints off.
            constraints = False

            # Remove the method of multipliers arg.
            if not search('^[Gg]rid', min_algor):
                min_algor = min_options[0]
                min_options = min_options[1:]

            # Throw a warning.
            warn(RelaxWarning("Constraints are as of yet not implemented - turning this option off."))

        # The rigid model initial parameter vector (the cone axis angles and the cone angle).
        if cdp.model == 'rigid':
            param_vector = array([cdp.alpha, cdp.beta, cdp.gamma], float64)

        # The isotropic cone model initial parameter vector (the cone axis angles and the cone angle).
        elif cdp.model == 'iso cone':
            param_vector = array([cdp.alpha, cdp.beta, cdp.gamma, cdp.theta_axis, cdp.phi_axis, cdp.theta_cone], float64)

        # Get the data structures for optimisation using the tensors as base data sets.
        full_tensors, red_tensors, red_tensor_err, full_in_ref_frame = self.__minimise_setup_tensors(sim_index)

        # Set up the optimisation function.
        target = frame_order.Frame_order(model=cdp.model, full_tensors=full_tensors, red_tensors=red_tensors, red_errors=red_tensor_err, full_in_ref_frame=full_in_ref_frame)

        # Minimisation.
        results = generic_minimise(func=target.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=True, print_flag=verbosity)

        # Unpack the results.
        self.__unpack_opt_results(results, sim_index)


    def model_loop(self):
        """Dummy generator method.

        In this case only a single model per spin system is assumed.  Hence the yielded data is the
        spin container object.


        @return:    Information about the model which for this analysis is the spin container.
        @rtype:     SpinContainer instance
        """

        # Don't return anything, just loop once.
        yield None


    def pivot(self, pivot=None):
        """Set the pivot point for the 2 body motion.

        @param pivot:   The pivot point of the two bodies (domains, etc.) in the structural
                        coordinate system.
        @type pivot:    list of num
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Set the pivot point.
        cdp.pivot = pivot

        # Convert to floats.
        for i in range(3):
            cdp.pivot[i] = float(cdp.pivot[i])


    def ref_domain(self, ref=None):
        """Set the reference domain for the frame order, multi-domain models.

        @param ref: The reference domain.
        @type ref:  str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Test if the model is setup.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('Frame order')

        # Test if the reference domain exists.
        exists = False
        for tensor_cont in cdp.align_tensors:
            if hasattr(tensor_cont, 'domain') and tensor_cont.domain == ref:
                exists = True
        if not exists:
            raise RelaxError("The reference domain cannot be found within any of the loaded tensors.")

        # Set the reference domain.
        cdp.ref_domain = ref

        # Update the model.
        self.__update_model()


    def return_error(self, index):
        """Return the alignment tensor error structure.

        @param index:   Not used.
        @type index:    None
        @return:        The array of relaxation data error values.
        @rtype:         list of float
        """

        # Get the tensor data structures.
        full_tensors, red_tensors, red_tensor_err, full_in_ref_frame = self.__minimise_setup_tensors()

        # Return the errors.
        return red_tensor_err


    def select_model(self, model=None):
        """Select the Frame Order model.

        @param model:   The Frame Order model.  As of yet, this can only be 'iso cone'.
        @type model:    str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Test if the model is already setup.
        if hasattr(cdp, 'model'):
            raise RelaxModelError('Frame Order')

        # Test if the model name exists.
        if not model in ['rigid', 'iso cone']:
            raise RelaxError("The model name " + repr(model) + " is invalid.")

        # Set the model
        cdp.model = model

        # Initialise the list of model parameters.
        cdp.params = []

        # Update the model.
        self.__update_model()


    def set_error(self, nothing, index, error):
        """Set the parameter errors.

        @param nothing: Not used.
        @type nothing:  None
        @param index:   The index of the parameter to set the errors for.
        @type index:    int
        @param error:   The error value.
        @type error:    float
        """

        # Parameter increment counter.
        inc = 0

        # Loop over the residue specific parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                setattr(cdp, param + "_err", error)

            # Increment.
            inc = inc + 1


    def set_selected_sim(self, index, select_sim):
        """Set the simulation selection flag for the spin.

        @param index:       Not used.
        @type index:        None
        @param select_sim:  The selection flag for the simulations.
        @type select_sim:   bool
        """

        # Set the array.
        cdp.select_sim = deepcopy(select_sim)


    def sim_init_values(self):
        """Initialise the Monte Carlo parameter values."""

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Loop over all the parameter names.
        for object_name in param_names:
            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Test if the simulation object already exists.
            if hasattr(cdp, sim_object_name):
                raise RelaxError("Monte Carlo parameter values have already been set.")


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over all the data names.
        for object_name in param_names:
            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(cdp, sim_object_name, [])

            # Get the simulation object.
            sim_object = getattr(cdp, sim_object_name)

            # Loop over the simulations.
            for j in xrange(cdp.sim_number):
                # Copy and append the data.
                sim_object.append(deepcopy(getattr(cdp, object_name)))

        # Loop over all the minimisation object names.
        for object_name in min_names:
            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(cdp, sim_object_name, [])

            # Get the simulation object.
            sim_object = getattr(cdp, sim_object_name)

            # Loop over the simulations.
            for j in xrange(cdp.sim_number):
                # Copy and append the data.
                sim_object.append(deepcopy(getattr(cdp, object_name)))


    def sim_pack_data(self, index, sim_data):
        """Pack the Monte Carlo simulation data.

        @param index:       Not used.
        @type index:        None
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Transpose the data.
        sim_data = transpose(sim_data)

        # Loop over the reduced tensors.
        for i, tensor in self.__tensor_loop(red=True):
            # Set the reduced tensor simulation data.
            tensor.Axx_sim = sim_data[5*i + 0]
            tensor.Ayy_sim = sim_data[5*i + 1]
            tensor.Axy_sim = sim_data[5*i + 2]
            tensor.Axz_sim = sim_data[5*i + 3]
            tensor.Ayz_sim = sim_data[5*i + 4]


    def sim_return_param(self, nothing, index):
        """Return the array of simulation parameter values.

        @param nothing:     Not used.
        @type nothing:      None
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        """

        # Parameter increment counter.
        inc = 0

        # Loop over the parameters.
        for param in self.data_names(set='params'):
            # Return the parameter array.
            if index == inc:
                return getattr(cdp, param + "_sim")

            # Increment.
            inc = inc + 1


    def sim_return_selected(self, nothing):
        """Return the array of selected simulation flags for the spin.

        @param nothing:     Not used.
        @type nothing:      None
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Return the array.
        return cdp.select_sim
