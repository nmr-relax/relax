###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Edward d'Auvergne                                   #
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
from math import cos, pi
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import arccos, array, float64, ones, transpose, zeros
from re import search
from warnings import warn

# relax module imports.
from api_base import API_base
from api_common import API_common
from float import isNaN, isInf
from generic_fns import pipes
from generic_fns.angles import wrap_angles
from generic_fns.structure.cones import Iso_cone
from generic_fns.structure.geometric import cone_edge, generate_vector_dist, generate_vector_residues, stitch_cone_to_edge
from generic_fns.structure.internal import Internal
from maths_fns import frame_order, order_parameters
from maths_fns.frame_order_matrix_ops import generate_vector
from maths_fns.rotation_matrix import two_vect_to_R
from relax_errors import RelaxError, RelaxInfError, RelaxNaNError, RelaxNoModelError
from relax_io import open_write_file
from relax_warnings import RelaxWarning, RelaxDeselectWarning


class Frame_order(API_base, API_common):
    """Class containing the specific methods of the Frame Order theories."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Place methods into the API.
        self.overfit_deselect = self._overfit_deselect_dummy
        self.return_conversion_factor = self._return_no_conversion_factor
        self.set_param_values = self._set_param_values_global


    def _assemble_param_vector(self):
        """Assemble and return the parameter vector.

        @return:    The parameter vector.
        @rtype:     numpy rank-1 array
        """

        # The rigid model initial parameter vector (the cone axis angles and the cone angle).
        if cdp.model == 'rigid':
            return array([cdp.alpha, cdp.beta, cdp.gamma], float64)

        # The isotropic cone model initial parameter vector (the cone axis angles and the cone angle).
        elif cdp.model == 'iso cone':
            return array([cdp.beta, cdp.gamma, cdp.theta_axis, cdp.phi_axis, cdp.s1], float64)

        # The pseudo-elliptic cone model initial parameter vector (the average position rotation, eigenframe and cone parameters).
        elif cdp.model == 'iso cone':
            return array([cdp.alpha, cdp.beta, cdp.gamma, cdp.eigen_alpha, cdp.eigen_beta, cdp.eigen_gamma, cdp.cone_theta_x, cdp.cone_theta_y, cdp.cone_sigma_max], float64)


    def _back_calc(self):
        """Back-calculation of the reduced alignment tensor.

        @return:    The reduced alignment tensors.
        @rtype:     numpy array
        """

        # Get the parameter vector.
        param_vector = self._assemble_param_vector()

        # Get the data structures for optimisation using the tensors as base data sets.
        full_tensors, red_tensors, red_tensor_err, full_in_ref_frame = self._minimise_setup_tensors()

        # Set up the optimisation function.
        target = frame_order.Frame_order(model=cdp.model, full_tensors=full_tensors, red_tensors=red_tensors, red_errors=red_tensor_err, full_in_ref_frame=full_in_ref_frame)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        target.func(param_vector)

        # Return the reduced tensors.
        return target.red_tensors_bc


    def _cone_pdb(self, size=30.0, file=None, dir=None, inc=40, force=False):
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

            # The isotropic cone object.
            cone = Iso_cone(cdp.theta_cone)

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
            cone_edge(mol=mol, res_name='CON', res_num=3+num_sim, apex=cdp.pivot, R=R, phi_max_fn=cone.phi_max, length=size, inc=inc)

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


    def _grid_row(self, incs, lower, upper, dist_type=None, end_point=True):
        """Set up a row of the grid search for a given parameter.

        @param incs:        The number of increments.
        @type incs:         int
        @param lower:       The lower bounds.
        @type lower:        float
        @param upper:       The upper bounds.
        @type upper:        float
        @keyword dist_type: The spacing or distribution type between grid nodes.  If None, then a linear grid row is returned.  If 'acos', then an inverse cos distribution of points is returned (e.g. for uniform sampling in angular space).
        @type dist_type:    None or str
        @keyword end_point: A flag which if False will cause the end point to be removed.
        @type end_point:    bool
        @return:            The row of the grid.
        @rtype:             list of float
        """

        # Init.
        row = []

        # Linear grid.
        if dist_type == None:
            # Loop over the increments.
            for i in range(incs):
                # The row.
                row.append(lower + i * (upper - lower) / (incs - 1.0))

        # Inverse cos distribution.
        elif dist_type == 'acos':
            # Generate the increment values of v from cos(upper) to cos(lower).
            v = zeros(incs, float64)
            val = (cos(lower) - cos(upper)) / (incs - 1.0)
            for i in range(incs):
                v[-i-1] = cos(upper) + float(i) * val

            # Generate the distribution.
            row = arccos(v)

        # Remove the last point.
        if not end_point:
            row = row[:-1]

        # Return the row (as a list).
        return list(row)


    def _minimise_setup_tensors(self, sim_index=None):
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
        for i, tensor in self._tensor_loop():
            if not hasattr(tensor, 'domain'):
                raise RelaxError("The domain that the '%s' tensor is attached to has not been set" % tensor.name)

        # Initialise.
        n = len(cdp.align_tensors.reduction)
        full_tensors = zeros(n*5, float64)
        red_tensors  = zeros(n*5, float64)
        red_err = ones(n*5, float64) * 1e-5
        full_in_ref_frame = zeros(n, float64)

        # Loop over the full tensors.
        for i, tensor in self._tensor_loop(red=False):
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
        for i, tensor in self._tensor_loop(red=True):
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


    def _pivot(self, pivot=None):
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


    def _ref_domain(self, ref=None):
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
        self._update_model()


    def _select_model(self, model=None):
        """Select the Frame Order model.

        @param model:   The Frame Order model.  This can be one of 'rigid', 'iso cone', or 'pseudo-ellipse'.
        @type model:    str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Test if the model is already setup.
        if hasattr(cdp, 'model'):
            raise RelaxModelError('Frame Order')

        # Test if the model name exists.
        if not model in ['rigid', 'iso cone', 'pseudo-ellipse']:
            raise RelaxError("The model name " + repr(model) + " is invalid.")

        # Set the model
        cdp.model = model

        # Initialise the list of model parameters.
        cdp.params = []

        # Update the model.
        self._update_model()


    def _tensor_loop(self, red=False):
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


    def _update_model(self):
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
            if cdp.model == 'iso cone':
                cdp.params.append('beta')
                cdp.params.append('gamma')
            else:
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
                cdp.params.append('s1')

            # Initialise the cone axis angles and order parameter values.
            if not hasattr(cdp, 'theta_axis'):
                cdp.theta_axis = 0.0
            if not hasattr(cdp, 'phi_axis'):
                cdp.phi_axis = 0.0
            if not hasattr(cdp, 's1'):
                cdp.s1 = 0.0

        # Pseudo-elliptic cone model.
        elif cdp.model == 'pseudo-ellipse':
            # Set up the parameter arrays.
            if init:
                cdp.params.append('eigen_alpha')
                cdp.params.append('eigen_beta')
                cdp.params.append('eigen_gamma')
                cdp.params.append('cone_theta_x')
                cdp.params.append('cone_theta_y')
                cdp.params.append('cone_sigma_max')

            # Initialise the cone axis angles and order parameter values.
            if not hasattr(cdp, 'eigen_alpha'):
                cdp.eigen_alpha = 0.0
            if not hasattr(cdp, 'eigen_beta'):
                cdp.eigen_beta = 0.0
            if not hasattr(cdp, 'eigen_gamma'):
                cdp.eigen_gamma = 0.0
            if not hasattr(cdp, 'cone_theta_x'):
                cdp.cone_theta_x = 0.0
            if not hasattr(cdp, 'cone_theta_y'):
                cdp.cone_theta_y = 0.0
            if not hasattr(cdp, 'cone_sigma_max'):
                cdp.cone_sigma_max = 0.0


    def _unpack_opt_results(self, results, sim_index=None):
        """Unpack and store the Frame Order optimisation results.

        @param results:     The results tuple returned by the minfx generic_minimise() function.
        @type results:      tuple
        @param sim_index:   The index of the simulation to optimise.  This should be None for normal
                            optimisation.
        @type sim_index:    None or int
         """

        # Disassemble the results.
        if len(results) == 4:    # Grid search.
            param_vector, func, iter_count, warning = results
            f_count = iter_count
            g_count = 0.0
            h_count = 0.0
        else:
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
            beta, gamma, theta_axis, phi_axis, s1 = param_vector

            # Alpha is zero in this model!
            alpha = 0.0

            # Calculate the cone angle.
            cdp.theta_cone = order_parameters.iso_cone_S_to_cos_theta(s1)

            # Monte Carlo simulation data structures.
            if sim_index != None:
                # Model parameters.
                cdp.theta_axis_sim[sim_index] = theta_axis
                cdp.phi_axis_sim[sim_index] = phi_axis
                cdp.s1_sim[sim_index] = s1

            # Normal data structures.
            else:
                # Model parameters.
                cdp.theta_axis = theta_axis
                cdp.phi_axis = phi_axis
                cdp.s1 = s1

        # Pseudo-ellipse cone model.
        elif cdp.model == 'pseudo-ellipse':
            # Disassemble the parameter vector.
            alpha, beta, gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = param_vector

            # Monte Carlo simulation data structures.
            if sim_index != None:
                # Model parameters.
                cdp.eigen_alpha[sim_index] = wrap_angles(eigen_alpha, 0.0, 2.0*pi)
                cdp.eigen_beta[sim_index] =  wrap_angles(eigen_beta,  0.0, 2.0*pi)
                cdp.eigen_gamma[sim_index] = wrap_angles(eigen_gamma, 0.0, 2.0*pi)
                cdp.cone_theta_x[sim_index] = cone_theta_x
                cdp.cone_theta_y[sim_index] = cone_theta_y
                cdp.cone_sigma_max[sim_index] = cone_sigma_max

            # Normal data structures.
            else:
                # Model parameters.
                cdp.eigen_alpha = wrap_angles(eigen_alpha, 0.0, 2.0*pi)
                cdp.eigen_beta =  wrap_angles(eigen_beta,  0.0, 2.0*pi)
                cdp.eigen_gamma = wrap_angles(eigen_gamma, 0.0, 2.0*pi)
                cdp.cone_theta_x = cone_theta_x
                cdp.cone_theta_y = cone_theta_y
                cdp.cone_sigma_max = cone_sigma_max

        # Wrap the Euler angles.
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


    def base_data_loop(self):
        """Generator method for looping nothing.

        The loop essentially consists of a single element.

        @return:    Nothing.
        @rtype:     None
        """

        yield None


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculate the chi-squared value for the current parameter values.

        @keyword spin_id:   The spin identification string (unused).
        @type spin_id:      None
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The optional MC simulation index (unused).
        @type sim_index:    None or int
        """

        # Assemble the parameter vector.
        param_vector = self._assemble_param_vector()

        # Get the data structures for optimisation using the tensors as base data sets.
        full_tensors, red_tensors, red_tensor_err, full_in_ref_frame = self._minimise_setup_tensors()

        # Set up the optimisation function.
        target = frame_order.Frame_order(model=cdp.model, full_tensors=full_tensors, red_tensors=red_tensors, red_errors=red_tensor_err, full_in_ref_frame=full_in_ref_frame)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        chi2 = target.func(param_vector)

        # Set the chi2.
        cdp.chi2 = chi2


    def create_mc_data(self, spin_id=None):
        """Create the Monte Carlo data by back calculating the reduced tensor data.

        @keyword spin_id:   The spin identification string (unused).
        @type spin_id:      None
        @return:            The Monte Carlo simulation data.
        @rtype:             list of floats
        """

        # Back calculate the tensors.
        red_tensors_bc = self._back_calc()

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
            - 's1', the isotropic cone order parameter.


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

        # The parameter suffix.
        if error_names:
            suffix = '_err'
        elif sim_names:
            suffix = '_sim'
        else:
            suffix = ''

        # Parameters.
        if set == 'all' or set == 'params':
            # The isotropic cone model.
            if hasattr(cdp, 'model') and cdp.model == 'iso cone':
                # Euler angles.
                names.append('beta%s' % suffix)
                names.append('gamma%s' % suffix)

                # Angular cone parameters.
                names.append('theta_axis%s' % suffix)
                names.append('phi_axis%s' % suffix)
                names.append('s1%s' % suffix)

            # All other models.
            else:
                names.append('alpha%s' % suffix)
                names.append('beta%s' % suffix)
                names.append('gamma%s' % suffix)

            # The pseudo-elliptic cone model.
            if hasattr(cdp, 'model') and cdp.model == 'pseudo-ellipse':
                # Eigenframe
                names.append('eigen_alpha%s' % suffix)
                names.append('eigen_beta%s' % suffix)
                names.append('eigen_gamma%s' % suffix)

                # Cone parameters.
                names.append('cone_theta_x%s' % suffix)
                names.append('cone_theta_y%s' % suffix)
                names.append('cone_sigma_max%s' % suffix)

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        # Return the names.
        return names


    def grid_search(self, lower=None, upper=None, inc=None, constraints=False, verbosity=0, sim_index=None):
        """Perform a grid search.

        @keyword lower:         The lower bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type lower:            list of float
        @keyword upper:         The upper bounds of the grid search which must be equal to the
                                number of parameters in the model.
        @type upper:            list of float
        @keyword inc:           The increments for each dimension of the space for the grid search.
                                The number of elements in the array must equal to the number of
                                parameters in the model.
        @type inc:              int or list of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating
                                parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher
                                the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The Monte Carlo simulation index.
        @type sim_index:        None or int
        """

        # Test if the Frame Order model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('Frame Order')

        # The number of parameters.
        n = len(cdp.params)

        # If inc is an int, convert it into an array of that value.
        if isinstance(inc, int):
            incs = [inc]*n
        else:
            incs = inc

        # Initialise the grid increments structures.
        lower_list = lower
        upper_list = upper
        grid = []
        """This structure is a list of lists.  The first dimension corresponds to the model
        parameter.  The second dimension are the grid node positions."""

        # Generate the grid.
        for i in range(n):
            # Reset.
            dist_type = None
            end_point = True

            # Alpha Euler angle.
            if cdp.params[i] == 'alpha':
                lower = 0.0
                upper = 2*pi * (1.0 - 1.0/incs[i])

            # Beta Euler angle.
            if cdp.params[i] == 'beta':
                # Change the default increment numbers.
                if not isinstance(inc, list):
                    incs[i] = incs[i] / 2 + 1

                # The distribution type and end point.
                dist_type = 'acos'
                end_point = False

                # Set the default bounds.
                lower = 0.0
                upper = pi

            # Gamma Euler angle.
            if cdp.params[i] == 'gamma':
                lower = 0.0
                upper = 2*pi * (1.0 - 1.0/incs[i])

            # The eigenframe alpha Euler angle.
            if cdp.params[i] == 'eigen_alpha':
                lower = 0.0
                upper = 2*pi * (1.0 - 1.0/incs[i])

            # The eigenframe beta Euler angle.
            if cdp.params[i] == 'eigen_beta':
                # Change the default increment numbers.
                if not isinstance(inc, list):
                    incs[i] = incs[i] / 2 + 1

                # The distribution type and end point.
                dist_type = 'acos'
                end_point = False

                # Set the default bounds.
                lower = 0.0
                upper = pi

            # The eigenframe gamma Euler angle.
            if cdp.params[i] == 'eigen_gamma':
                lower = 0.0
                upper = 2*pi * (1.0 - 1.0/incs[i])

            # The isotropic cone model.
            if cdp.model == 'iso cone':
                # Cone axis polar angle.
                if cdp.params[i] == 'theta_axis':
                    # Change the default increment numbers.
                    if not isinstance(inc, list):
                        incs[i] = incs[i] / 2 + 1

                    # The distribution type.
                    dist_type = 'acos'
                    end_point = False

                    # Set the default bounds.
                    lower = 0.0
                    upper = pi

                # Cone axis azimuthal angle.
                if cdp.params[i] == 'phi_axis':
                    lower = 0.0
                    upper = 2*pi * (1.0 - 1.0/incs[i])

                # The cone order parameter.
                if cdp.params[i] == 's1':
                    lower = -0.5
                    upper = 1.0

            # The pseudo-elliptic cone model parameters.
            if cdp.model == 'pseudo-ellipse':
                # Cone opening angles.
                if cdp.params[i] in ['cone_theta_x', 'cone_theta_y']:
                    lower = pi * (1.0/incs[i])
                    upper = pi * (1.0 - 1.0/incs[i])

                # Torsion angle restriction.
                if cdp.params[i] == 'cone_sigma_max':
                    lower = pi * (1.0/incs[i])
                    upper = pi * (1.0 - 1.0/incs[i])

            # Over-ride the bounds.
            if lower_list:
                lower = lower_list[i]
            if upper_list:
                upper = upper_list[i]

            # Append the grid row.
            row = self._grid_row(incs[i], lower, upper, dist_type=dist_type, end_point=end_point)
            grid.append(row)

        # Minimisation.
        self.minimise(min_algor='grid', min_options=grid, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def is_spin_param(self, name):
        """State that the parameter is not spin specific.

        @param name:    The name of the parameter.
        @type name:     str
        @return:        False.
        @rtype:         bool
        """

        # Not spin specific!
        return False


    def map_bounds(self, param, spin_id=None):
        """Create bounds for the OpenDX mapping function.

        @param param:       The name of the parameter to return the lower and upper bounds of.
        @type param:        str
        @param spin_id:     The spin identification string (unused).
        @type spin_id:      None
        @return:            The upper and lower bounds of the parameter.
        @rtype:             list of float
        """

        # Euler angles.
        if search('^alpha$', param) or search('^beta$', param) or search('^gamma$', param):
            return [0.0, 2*pi]

        # Axis spherical coordinate theta.
        if search('theta[ -_]axis', param):
            return [0.0, pi]

        # Axis spherical coordinate phi.
        if search('phi[ -_]axis', param):
            return [0.0, 2*pi]

        # Cone angle.
        if search('theta[ -_]cone', param):
            return [0.0, pi]


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
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
        @keyword lower:         The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:              array of int
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

        # Assemble the parameter vector.
        param_vector = self._assemble_param_vector()

        # Get the data structures for optimisation using the tensors as base data sets.
        full_tensors, red_tensors, red_tensor_err, full_in_ref_frame = self._minimise_setup_tensors(sim_index)

        # Set up the optimisation function.
        target = frame_order.Frame_order(model=cdp.model, full_tensors=full_tensors, red_tensors=red_tensors, red_errors=red_tensor_err, full_in_ref_frame=full_in_ref_frame)

        # Grid search.
        if search('^[Gg]rid', min_algor):
            results = grid(func=target.func, args=(), incs=min_options, verbosity=verbosity)

        # Minimisation.
        else:
            results = generic_minimise(func=target.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=True, print_flag=verbosity)

        # Unpack the results.
        self._unpack_opt_results(results, sim_index)


    def model_loop(self):
        """Dummy generator method.

        In this case only a single model per spin system is assumed.  Hence the yielded data is the
        spin container object.


        @return:    Information about the model which for this analysis is the spin container.
        @rtype:     SpinContainer instance
        """

        # Don't return anything, just loop once.
        yield None


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_info:    Unused.
        @type model_info:       None
        @keyword spin_id:       The spin identification string (unused).
        @type spin_id:          None
        @keyword global_stats:  Unused.
        @type global_stats:     None
        @return:                The optimisation statistics, in tuple format, of the number of
                                parameters (k), the number of data points (n), and the chi-squared
                                value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Count the number of parameters.
        param_vector = self._assemble_param_vector()
        k = len(param_vector)

        # The number of data points.
        n = len(cdp.align_tensors.reduction)

        # The chi2 value.
        if not hasattr(cdp, 'chi2'):
            raise RelaxError("Statistics are not available, most likely because the model has not been optimised.")
        chi2 = cdp.chi2

        # Return the data.
        return k, n, chi2


    def return_data_name(self, param):
        """Return a unique identifying string for the Frame order parameter.

        @param param:   The Frame order parameter.
        @type param:    str
        @return:        The unique parameter identifying string.
        @rtype:         str
        """

        # Euler angle alpha.
        if search('^alpha$', param):
            return 'alpha'

        # Euler angle beta.
        if search('^beta$', param):
            return 'beta'

        # Euler angle gamma.
        if search('^gamma$', param):
            return 'gamma'

        # Axis spherical coordinate theta.
        if search('theta[ -_]axis', param):
            return 'theta_axis'

        # Axis spherical coordinate phi.
        if search('phi[ -_]axis', param):
            return 'phi_axis'

        # Cone order parameter.
        if search('[Ss]1', param):
            return 's1'


    def return_error(self, spin_id):
        """Return the alignment tensor error structure.

        @param spin_id: The information yielded by the base_data_loop() generator method.
        @type spin_id:  None
        @return:        The array of tensor error values.
        @rtype:         list of float
        """

        # Get the tensor data structures.
        full_tensors, red_tensors, red_tensor_err, full_in_ref_frame = self._minimise_setup_tensors()

        # Return the errors.
        return red_tensor_err


    def return_units(self, param, spin=None, spin_id=None):
        """Return a string representing the parameters units.

        @param param:   The name of the parameter to return the units string for.
        @type param:    str
        @param spin:    The spin container (unused).
        @type spin:     None
        @param spin_id: The spin identification string (unused).
        @type spin_id:  None
        @return:        The parameter units string.
        @rtype:         str
        """

        # Euler angles.
        if search('^alpha$', param) or search('^beta$', param) or search('^gamma$', param):
            return 'rad'

        # Axis spherical coordinate theta.
        if search('theta[ -_]axis', param):
            return 'rad'

        # Axis spherical coordinate phi.
        if search('phi[ -_]axis', param):
            return 'rad'

        # Cone angle.
        if search('theta[ -_]cone', param):
            return 'rad'


    def set_error(self, model_info, index, error):
        """Set the parameter errors.

        @param model_info:  The model information originating from model_loop() (unused).
        @type model_info:   None
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
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


    def set_selected_sim(self, model_info, select_sim):
        """Set the simulation selection flag for the spin.

        @param model_info:  The model information originating from model_loop() (unused).
        @type model_info:   None
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


    def sim_pack_data(self, spin_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param spin_id:     The spin identification string, as yielded by the base_data_loop() generator method.
        @type spin_id:      None
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # Transpose the data.
        sim_data = transpose(sim_data)

        # Loop over the reduced tensors.
        for i, tensor in self._tensor_loop(red=True):
            # Set the reduced tensor simulation data.
            tensor.Axx_sim = sim_data[5*i + 0]
            tensor.Ayy_sim = sim_data[5*i + 1]
            tensor.Axy_sim = sim_data[5*i + 2]
            tensor.Axz_sim = sim_data[5*i + 3]
            tensor.Ayz_sim = sim_data[5*i + 4]


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The model information originating from model_loop() (unused).
        @type model_info:   None
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


    def sim_return_selected(self, model_info):
        """Return the array of selected simulation flags for the spin.

        @param model_info:  The model information originating from model_loop() (unused).
        @type model_info:   None
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Return the array.
        return cdp.select_sim
