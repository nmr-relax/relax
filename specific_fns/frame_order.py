###############################################################################
#                                                                             #
# Copyright (C) 2009-2013 Edward d'Auvergne                                   #
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
"""Analysis specific code for the Frame Order theory of domain dynamics."""

# Python module imports.
from copy import deepcopy
from math import cos, pi
from minfx.generic import generic_minimise
from minfx.grid import grid_point_array
from numpy import arccos, array, dot, eye, float64, identity, ones, transpose, zeros
from numpy.linalg import inv, norm
from re import search
import sys
from warnings import warn

# relax module imports.
import arg_check
from float import isNaN, isInf
from generic_fns import pipes
from generic_fns.angles import wrap_angles
from generic_fns.interatomic import interatomic_loop, return_interatom
from generic_fns.mol_res_spin import return_spin, spin_loop
from generic_fns.structure import geometric
from generic_fns.structure.cones import Iso_cone, Pseudo_elliptic
from generic_fns.structure.mass import centre_of_mass
from generic_fns.structure.internal import Internal
from lib.text.sectioning import section
from maths_fns import frame_order, order_parameters
from maths_fns.coord_transform import spherical_to_cartesian
from maths_fns.rotation_matrix import euler_to_R_zyz, two_vect_to_R
from physical_constants import dipolar_constant, g1H, return_gyromagnetic_ratio
from relax_errors import RelaxError, RelaxInfError, RelaxNaNError, RelaxNoModelError, RelaxNoPCSError, RelaxNoRDCError, RelaxNoValueError, RelaxSpinTypeError
from relax_io import open_write_file
from relax_warnings import RelaxWarning
from specific_fns.api_base import API_base
from specific_fns.api_common import API_common
from specific_fns.api_base import API_base
from specific_fns.api_common import API_common


class Frame_order(API_base, API_common):
    """Class containing the specific methods of the Frame Order theories."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Execute the base class __init__ method.
        super(Frame_order, self).__init__()

        # Place methods into the API.
        self.overfit_deselect = self._overfit_deselect_dummy
        self.return_conversion_factor = self._return_no_conversion_factor
        self.set_param_values = self._set_param_values_global

        # Set up the global parameters.
        self.PARAMS.add('ave_pos_x', scope='global', units='rad', desc='The average position x translation', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('ave_pos_y', scope='global', units='rad', desc='The average position y translation', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('ave_pos_z', scope='global', units='rad', desc='The average position z translation', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('ave_pos_alpha', scope='global', units='rad', desc='The average position alpha Euler angle', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('ave_pos_beta', scope='global', units='rad', desc='The average position beta Euler angle', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('ave_pos_gamma', scope='global', units='rad', desc='The average position gamma Euler angle', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('eigen_alpha', scope='global', units='rad', desc='The Eigenframe alpha Euler angle', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('eigen_beta', scope='global', units='rad', desc='The Eigenframe beta Euler angle', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('eigen_gamma', scope='global', units='rad', desc='The Eigenframe gamma Euler angle', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('axis_theta', scope='global', units='rad', desc='The cone axis polar angle (for the isotropic cone model)', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('axis_phi', scope='global', units='rad', desc='The cone axis azimuthal angle (for the isotropic cone model)', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('cone_theta_x', scope='global', units='rad', desc='The pseudo-ellipse cone opening half-angle for the x-axis', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('cone_theta_y', scope='global', units='rad', desc='The pseudo-ellipse cone opening half-angle for the y-axis', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('cone_theta', scope='global', units='rad', desc='The isotropic cone opening half-angle', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('cone_s1', scope='global', units='', desc='The isotropic cone order parameter', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('cone_sigma_max', scope='global', units='rad', desc='The torsion angle', py_type=float, set='params', err=True, sim=True)
        self.PARAMS.add('params', scope='global', desc='The model parameters', py_type=list)

        # Add minimisation structures.
        self.PARAMS.add_min_data(min_stats_global=True)


    def _assemble_limit_arrays(self):
        """Assemble and return the limit vectors.

        @return:    The lower and upper limit vectors.
        @rtype:     numpy rank-1 array, numpy rank-1 array
        """

        # Init.
        lower = zeros(len(cdp.params), float64)
        upper = 2.0*pi * ones(len(cdp.params), float64)

        # Return the arrays.
        return lower, upper


    def _assemble_param_vector(self, sim_index=None):
        """Assemble and return the parameter vector.

        @return:            The parameter vector.
        @rtype:             numpy rank-1 array
        @keyword sim_index: The Monte Carlo simulation index.
        @type sim_index:    int
        """

        # Initialise.
        param_vect = []

        # Pivot point.
        if not self._pivot_fixed():
            for i in range(3):
                param_vect.append(cdp.pivot[i])

        # Normal values.
        if sim_index == None:
            # Average position translation.
            if not self._translation_fixed():
                param_vect.append(cdp.ave_pos_x)
                param_vect.append(cdp.ave_pos_y)
                param_vect.append(cdp.ave_pos_z)

            # Initialise the parameter array using the tensor rotation Euler angles (average domain position).
            if cdp.model in ['free rotor', 'iso cone, free rotor']:
                param_vect.append(cdp.ave_pos_beta)
                param_vect.append(cdp.ave_pos_gamma)
            else:
                param_vect.append(cdp.ave_pos_alpha)
                param_vect.append(cdp.ave_pos_beta)
                param_vect.append(cdp.ave_pos_gamma)

            # Frame order eigenframe - the full frame.
            if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
                param_vect.append(cdp.eigen_alpha)
                param_vect.append(cdp.eigen_beta)
                param_vect.append(cdp.eigen_gamma)

            # Frame order eigenframe - the isotropic cone axis.
            elif cdp.model in ['iso cone', 'free rotor', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor']:
                param_vect.append(cdp.axis_theta)
                param_vect.append(cdp.axis_phi)

            # Cone parameters - pseudo-elliptic cone parameters.
            if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
                param_vect.append(cdp.cone_theta_x)
                param_vect.append(cdp.cone_theta_y)

            # Cone parameters - single isotropic angle or order parameter.
            elif cdp.model in ['iso cone', 'iso cone, torsionless']:
                param_vect.append(cdp.cone_theta)
            elif cdp.model in ['iso cone, free rotor']:
                param_vect.append(cdp.cone_s1)

            # Cone parameters - torsion angle.
            if cdp.model in ['rotor', 'line', 'iso cone', 'pseudo-ellipse']:
                param_vect.append(cdp.cone_sigma_max)

        # Simulation values.
        else:
            # Average position translation.
            if not self._translation_fixed():
                param_vect.append(cdp.ave_pos_x_sim[sim_index])
                param_vect.append(cdp.ave_pos_y_sim[sim_index])
                param_vect.append(cdp.ave_pos_z_sim[sim_index])

            # Initialise the parameter array using the tensor rotation Euler angles (average domain position).
            if cdp.model in ['free rotor', 'iso cone, free rotor']:
                param_vect.append(cdp.ave_pos_beta_sim[sim_index])
                param_vect.append(cdp.ave_pos_gamma_sim[sim_index])
            else:
                param_vect.append(cdp.ave_pos_alpha_sim[sim_index])
                param_vect.append(cdp.ave_pos_beta_sim[sim_index])
                param_vect.append(cdp.ave_pos_gamma_sim[sim_index])

            # Frame order eigenframe - the full frame.
            if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
                param_vect.append(cdp.eigen_alpha_sim[sim_index])
                param_vect.append(cdp.eigen_beta_sim[sim_index])
                param_vect.append(cdp.eigen_gamma_sim[sim_index])

            # Frame order eigenframe - the isotropic cone axis.
            elif cdp.model in ['iso cone', 'free rotor', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor']:
                param_vect.append(cdp.axis_theta_sim[sim_index])
                param_vect.append(cdp.axis_phi_sim[sim_index])

            # Cone parameters - pseudo-elliptic cone parameters.
            if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
                param_vect.append(cdp.cone_theta_x_sim[sim_index])
                param_vect.append(cdp.cone_theta_y_sim[sim_index])

            # Cone parameters - single isotropic angle or order parameter.
            elif cdp.model in ['iso cone', 'iso cone, torsionless']:
                param_vect.append(cdp.cone_theta_sim[sim_index])
            elif cdp.model in ['iso cone, free rotor']:
                param_vect.append(cdp.cone_s1_sim[sim_index])

            # Cone parameters - torsion angle.
            if cdp.model in ['rotor', 'line', 'iso cone', 'pseudo-ellipse']:
                param_vect.append(cdp.cone_sigma_max_sim[sim_index])

        # Return as a numpy array.
        return array(param_vect, float64)


    def _assemble_scaling_matrix(self, data_types=None, scaling=True):
        """Create and return the scaling matrix.

        @keyword data_types:    The base data types used in the optimisation.  This list can contain the elements 'rdc', 'pcs' or 'tensor'.
        @type data_types:       list of str
        @keyword scaling:       If False, then the identity matrix will be returned.
        @type scaling:          bool
        @return:                The square and diagonal scaling matrix.
        @rtype:                 numpy rank-2 array
        """

        # Initialise.
        scaling_matrix = identity(self._param_num(), float64)

        # Return the identity matrix.
        if not scaling:
            return scaling_matrix

        # The pivot point.
        if not self._pivot_fixed():
            for i in range(3):
                scaling_matrix[i, i] = 1e2

        # Return the matrix.
        return scaling_matrix


    def _average_position(self, pivot='com', translation=True):
        """Set up the mechanics of the average domain position.

        @keyword pivot:         What to use as the motional pivot.  This can be 'com' for the centre of mass of the moving domain, or 'motional' to link the pivot of the motion to the rotation of the average domain position.
        @type pivot:            str
        @keyword translation:   If True, translation to the average domain position will be allowed.  If False, then translation will not occur.
        @type translation:      bool
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Check the pivot value.
        if pivot not in ['com', 'motional']:
            raise RelaxError("The pivot for the rotation to the average domain position must be either 'com' or 'motional'.")

        # Store the data.
        cdp.ave_pos_pivot = pivot
        cdp.ave_pos_translation = translation


    def _base_data_types(self):
        """Determine all the base data types.

        The base data types can include::
            - 'rdc', residual dipolar couplings.
            - 'pcs', pseudo-contact shifts.
            - 'noesy', NOE restraints.
            - 'tensor', alignment tensors.

        @return:    A list of all the base data types.
        @rtype:     list of str
        """

        # Array of data types.
        list = []

        # RDC search.
        for interatom in interatomic_loop(selection1=self._domain_moving()):
            if hasattr(interatom, 'rdc'):
                list.append('rdc')
                break

        # PCS search.
        for spin in spin_loop(selection=self._domain_moving()):
            if hasattr(spin, 'pcs'):
                list.append('pcs')
                break

        # Alignment tensor search.
        if not ('rdc' in list or 'pcs' in list) and hasattr(cdp, 'align_tensors'):
            list.append('tensor')

        # No data is present.
        if not list:
            raise RelaxError("Neither RDCs, PCSs nor alignment tensor data is present.")

        # Return the list.
        return list


    def _check_rdcs(self, interatom, spin1, spin2):
        """Check if the RDCs for the given interatomic data container should be used.

        @param interatom:   The interatomic data container.
        @type interatom:    InteratomContainer instance
        @param spin1:       The first spin container.
        @type spin1:        SpinContainer instance
        @param spin2:       The second spin container.
        @type spin2:        SpinContainer instance
        @return:            True if the RDCs should be used, False otherwise.
        """

        # Skip deselected spins.
        if not spin1.select or not spin2.select:
            return False

        # Only use interatomic data containers with RDC data.
        if not hasattr(interatom, 'rdc'):
            return False

        # RDC data exists but the interatomic vectors are missing?
        if not hasattr(interatom, 'vector'):
            # Throw a warning.
            warn(RelaxWarning("RDC data exists but the interatomic vectors are missing, skipping the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))

            # Jump to the next spin.
            return False

        # Skip non-Me pseudo-atoms for the first spin.
        if hasattr(spin1, 'members') and len(spin1.members) != 3:
            warn(RelaxWarning("Only methyl group pseudo atoms are supported due to their fast rotation, skipping the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))
            return False

        # Skip non-Me pseudo-atoms for the second spin.
        if hasattr(spin2, 'members') and len(spin2.members) != 3:
            warn(RelaxWarning("Only methyl group pseudo atoms are supported due to their fast rotation, skipping the spin pair '%s' and '%s'." % (interatom.spin_id1, interatom.spin_id2)))
            return False

        # Checks.
        if not hasattr(spin1, 'isotope'):
            raise RelaxSpinTypeError(interatom.spin_id1)
        if not hasattr(spin2, 'isotope'):
            raise RelaxSpinTypeError(interatom.spin_id2)
        if not hasattr(interatom, 'r'):
            raise RelaxNoValueError("averaged interatomic distance")

        # Everything is ok.
        return True


    def _domain_moving(self):
        """Return the spin ID string corresponding to the moving domain.

        @return:    The spin ID string defining the moving domain.
        @rtype:     str
        """

        # Check that the domain is defined.
        if not hasattr(cdp, 'domain'):
            raise RelaxError("No domains have been defined.  Please use the domain user function.")

        # Only support for 2 domains.
        if len(list(cdp.domain.keys())) > 2:
            raise RelaxError("Only two domains are supported in the frame order analysis.")

        # Reference domain not set yet, so return nothing.
        if not hasattr(cdp, 'ref_domain'):
            return None

        # Loop over the domains.
        for id in list(cdp.domain.keys()):
            # Reference domain.
            if id == cdp.ref_domain:
                continue

            # Return the ID.
            return cdp.domain[id]


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


    def _minimise_setup_atomic_pos(self, sim_index=None):
        """Set up the atomic position data structures for optimisation using PCSs and PREs as base data sets.

        @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:    None or int
        @return:            The atomic positions (the first index is the spins, the second is the structures, and the third is the atomic coordinates) and the paramagnetic centre.
        @rtype:             numpy rank-3 array, numpy rank-1 array.
        """

        # Initialise.
        atomic_pos = []

        # Store the atomic positions.
        for spin, spin_id in spin_loop(selection=self._domain_moving(), return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Only use spins with alignment/paramagnetic data.
            if not hasattr(spin, 'pcs') and not hasattr(spin, 'pre'):
                continue

            # A single atomic position.
            if spin.pos.shape == (3,):
                atomic_pos.append(spin.pos)

            # A single model (rank-2 array of a single position).
            elif spin.pos.shape == (1, 3):
                atomic_pos.append(spin.pos[0])

            # Average multiple atomic positions.
            else:
                # First throw a warning to tell the user what is happening.
                if sim_index == None:
                    warn(RelaxWarning("Averaging the %s atomic positions for the PCS for the spin '%s'." % (len(spin.pos), spin_id)))

                # The average position.
                ave_pos = zeros(3, float64)
                for i in range(len(spin.pos)):
                    ave_pos += spin.pos[i]
                ave_pos = ave_pos / len(spin.pos)

                # Store.
                atomic_pos.append(ave_pos)

        # Convert to numpy objects.
        atomic_pos = array(atomic_pos, float64)

        # The paramagnetic centre.
        if not hasattr(cdp, 'paramagnetic_centre'):
            paramag_centre = zeros(3, float64)
        else:
            paramag_centre = array(cdp.paramagnetic_centre)

        # Return the data structures.
        return atomic_pos, paramag_centre


    def _minimise_setup_pcs(self, sim_index=None):
        """Set up the data structures for optimisation using PCSs as base data sets.

        @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:    None or int
        @return:            The assembled data structures for using PCSs as the base data for optimisation.  These include:
                                - the PCS values.
                                - the unit vectors connecting the paramagnetic centre (the electron spin) to
                                - the PCS weight.
                                - the nuclear spin.
                                - the pseudocontact shift constants.
        @rtype:             tuple of (numpy rank-2 array, numpy rank-2 array, numpy rank-2 array, numpy rank-1 array, numpy rank-1 array)
        """

        # Data setup tests.
        if not hasattr(cdp, 'paramagnetic_centre'):
            raise RelaxError("The paramagnetic centre has not yet been specified.")
        if not hasattr(cdp, 'temperature'):
            raise RelaxError("The experimental temperatures have not been set.")
        if not hasattr(cdp, 'frq'):
            raise RelaxError("The spectrometer frequencies of the experiments have not been set.")

        # Initialise.
        pcs = []
        pcs_err = []
        pcs_weight = []
        temp = []
        frq = []

        # The PCS data.
        for i in range(len(cdp.align_ids)):
            # Alias the ID.
            align_id = cdp.align_ids[i]

            # Skip non-optimised data.
            if not self._opt_uses_align_data(align_id):
                continue

            # Append empty arrays to the PCS structures.
            pcs.append([])
            pcs_err.append([])
            pcs_weight.append([])

            # Get the temperature for the PCS constant.
            if align_id in cdp.temperature:
                temp.append(cdp.temperature[align_id])

            # The temperature must be given!
            else:
                raise RelaxError("The experimental temperature for the alignment ID '%s' has not been set." % align_id)

            # Get the spectrometer frequency in Tesla units for the PCS constant.
            if align_id in cdp.frq:
                frq.append(cdp.frq[align_id] * 2.0 * pi / g1H)

            # The frequency must be given!
            else:
                raise RelaxError("The spectrometer frequency for the alignment ID '%s' has not been set." % align_id)

            # Spin loop over the domain.
            j = 0
            for spin in spin_loop(selection=self._domain_moving()):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins without PCS data.
                if not hasattr(spin, 'pcs'):
                    continue

                # Append the PCSs to the list.
                if align_id in spin.pcs.keys():
                    if sim_index != None:
                        pcs[-1].append(spin.pcs_sim[align_id][sim_index])
                    else:
                        pcs[-1].append(spin.pcs[align_id])
                else:
                    pcs[-1].append(None)

                # Append the PCS errors.
                if hasattr(spin, 'pcs_err') and align_id in spin.pcs_err.keys():
                    pcs_err[-1].append(spin.pcs_err[align_id])
                else:
                    pcs_err[-1].append(None)

                # Append the weight.
                if hasattr(spin, 'pcs_weight') and align_id in spin.pcs_weight.keys():
                    pcs_weight[-1].append(spin.pcs_weight[align_id])
                else:
                    pcs_weight[-1].append(1.0)

                # Spin index.
                j = j + 1

        # Convert to numpy objects.
        pcs = array(pcs, float64)
        pcs_err = array(pcs_err, float64)
        pcs_weight = array(pcs_weight, float64)

        # Convert the PCS from ppm to no units.
        pcs = pcs * 1e-6
        pcs_err = pcs_err * 1e-6

        # Return the data structures.
        return pcs, pcs_err, pcs_weight, temp, frq


    def _minimise_setup_rdcs(self, sim_index=None):
        """Set up the data structures for optimisation using RDCs as base data sets.

        @keyword sim_index: The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:    None or int
        @return:            The assembled data structures for using RDCs as the base data for optimisation.  These include:
                                - rdc, the RDC values.
                                - rdc_err, the RDC errors.
                                - rdc_weight, the RDC weights.
                                - vectors, the interatomic vectors.
                                - rdc_const, the dipolar constants.
                                - absolute, the absolute value flags (as 1's and 0's).
        @rtype:             tuple of (numpy rank-2 array, numpy rank-2 array, numpy rank-2 array, numpy rank-3 array, numpy rank-2 array, numpy rank-2 array)
        """

        # Initialise.
        rdc = []
        rdc_err = []
        rdc_weight = []
        unit_vect = []
        rdc_const = []
        absolute = []

        # The unit vectors and RDC constants.
        for interatom in interatomic_loop(selection1=self._domain_moving()):
            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # RDC checks.
            if not self._check_rdcs(interatom, spin1, spin2):
                continue

            # A single unit vector.
            if interatom.vector.shape == (3,):
                unit_vect.append(interatom.vector)

            # Average multiple unit vectors.
            else:
                # First throw a warning to tell the user what is happening.
                if sim_index == None:
                    warn(RelaxWarning("Averaging the %s unit vectors for the RDC for the spin pair '%s' and '%s'." % (len(interatom.vector), interatom.spin_id1, interatom.spin_id2)))

                # The average position.
                ave_vector = zeros(3, float64)
                for i in range(len(interatom.vector)):
                    ave_vector += interatom.vector[i]

                # Store.
                unit_vect.append(ave_vector)

            # Normalise (to be sure).
            unit_vect[-1] = unit_vect[-1] / norm(unit_vect[-1])

            # Gyromagnetic ratios.
            g1 = return_gyromagnetic_ratio(spin1.isotope)
            g2 = return_gyromagnetic_ratio(spin2.isotope)

            # Calculate the RDC dipolar constant (in Hertz, and the 3 comes from the alignment tensor), and append it to the list.
            rdc_const.append(3.0/(2.0*pi) * dipolar_constant(g1, g2, interatom.r))

        # Fix the unit vector data structure.
        num = None
        for rdc_index in range(len(unit_vect)):
            # Number of vectors.
            if num == None:
                if unit_vect[rdc_index] != None:
                    num = len(unit_vect[rdc_index])
                continue

            # Check.
            if unit_vect[rdc_index] != None and len(unit_vect[rdc_index]) != num:
                raise RelaxError("The number of interatomic vectors for all no match:\n%s" % unit_vect)

        # Missing unit vectors.
        if num == None:
            raise RelaxError("No interatomic vectors could be found.")

        # Update None entries.
        for i in range(len(unit_vect)):
            if unit_vect[i] == None:
                unit_vect[i] = [[None, None, None]]*num

        # The RDC data.
        for i in range(len(cdp.align_ids)):
            # Alias the ID.
            align_id = cdp.align_ids[i]

            # Skip non-optimised data.
            if not self._opt_uses_align_data(align_id):
                continue

            # Append empty arrays to the RDC structures.
            rdc.append([])
            rdc_err.append([])
            rdc_weight.append([])
            absolute.append([])

            # Interatom loop over the domain.
            for interatom in interatomic_loop(self._domain_moving()):
                # Get the spins.
                spin1 = return_spin(interatom.spin_id1)
                spin2 = return_spin(interatom.spin_id2)

                # Skip deselected spins.
                if not spin1.select or not spin2.select:
                    continue

                # Only use interatomic data containers with RDC and vector data.
                if not hasattr(interatom, 'rdc') or not hasattr(interatom, 'vector'):
                    continue

                # Defaults of None.
                value = None
                error = None

                # Pseudo-atom set up.
                if (hasattr(spin1, 'members') or hasattr(spin2, 'members')) and align_id in interatom.rdc.keys():
                    raise RelaxError("Psuedo-atoms are currently not supported for the frame order analysis.")

                # Normal set up.
                elif align_id in interatom.rdc.keys():
                    # The RDC.
                    if sim_index != None:
                        value = interatom.rdc_sim[align_id][sim_index]
                    else:
                        value = interatom.rdc[align_id]

                    # The error.
                    if hasattr(interatom, 'rdc_err') and align_id in interatom.rdc_err.keys():
                        error = interatom.rdc_err[align_id]

                # Append the RDCs to the list.
                rdc[-1].append(value)

                # Append the RDC errors.
                rdc_err[-1].append(error)

                # Append the weight.
                if hasattr(interatom, 'rdc_weight') and align_id in interatom.rdc_weight.keys():
                    rdc_weight[-1].append(interatom.rdc_weight[align_id])
                else:
                    rdc_weight[-1].append(1.0)

                # Append the absolute value flag.
                if hasattr(interatom, 'absolute_rdc') and align_id in interatom.absolute_rdc.keys():
                    absolute[-1].append(interatom.absolute_rdc[align_id])
                else:
                    absolute[-1].append(False)

        # Convert to numpy objects.
        rdc = array(rdc, float64)
        rdc_err = array(rdc_err, float64)
        rdc_weight = array(rdc_weight, float64)
        unit_vect = array(unit_vect, float64)
        rdc_const = array(rdc_const, float64)
        absolute = array(absolute, float64)

        # Return the data structures.
        return rdc, rdc_err, rdc_weight, unit_vect, rdc_const, absolute


    def _minimise_setup_tensors(self, sim_index=None):
        """Set up the data structures for optimisation using alignment tensors as base data sets.

        @keyword sim_index: The simulation index.  This should be None if normal optimisation is desired.
        @type sim_index:    None or int
        @return:            The assembled data structures for using alignment tensors as the base data for optimisation.  These include:
                                - full_tensors, the full tensors as concatenated arrays.
                                - full_err, the full tensor errors as concatenated arrays.
                                - full_in_ref_frame, the flags specifying if the tensor is the full or reduced tensor in the non-moving reference domain.
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
        full_err = ones(n*5, float64) * 1e-5
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

            # The full tensor errors.
            if hasattr(tensor, 'Axx_err'):
                full_err[5*i + 0] = tensor.Axx_err
                full_err[5*i + 1] = tensor.Ayy_err
                full_err[5*i + 2] = tensor.Axy_err
                full_err[5*i + 3] = tensor.Axz_err
                full_err[5*i + 4] = tensor.Ayz_err

        # Return the data structures.
        return full_tensors, full_err, full_in_ref_frame


    def _num_int_pts(self, num=200000):
        """Set the number of integration points to use in the quasi-random Sobol' sequence.

        @keyword num:   The number of integration points.
        @type num:      int
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Store the value.
        cdp.num_int_pts = num


    def _opt_uses_align_data(self, align_id=None):
        """Determine if the PCS or RDC data for the given alignment ID is needed for optimisation.

        @keyword align_id:  The optional alignment ID string.
        @type align_id:     str
        @return:            True if alignment data is to be used for optimisation, False otherwise.
        @rtype:             bool
        """

        # No alignment IDs.
        if not hasattr(cdp, 'align_ids'):
            return False

        # Convert the align IDs to an array, or take all IDs.
        if align_id:
            align_ids = [align_id]
        else:
            align_ids = cdp.align_ids

        # Check the PCS and RDC.
        for align_id in align_ids:
            if self._opt_uses_pcs(align_id) or self._opt_uses_rdc(align_id):
                return True

        # No alignment data is used for optimisation.
        return False


    def _opt_uses_pcs(self, align_id):
        """Determine if the PCS data for the given alignment ID is needed for optimisation.

        @param align_id:    The alignment ID string.
        @type align_id:     str
        @return:            True if the PCS data is to be used for optimisation, False otherwise.
        @rtype:             bool
        """

        # No alignment IDs.
        if not hasattr(cdp, 'pcs_ids'):
            return False

        # No PCS data for the alignment.
        if align_id not in cdp.pcs_ids:
            return False

        # The PCS data is to be used for optimisation.
        return True


    def _opt_uses_rdc(self, align_id):
        """Determine if the RDC data for the given alignment ID is needed for optimisation.

        @param align_id:    The alignment ID string.
        @type align_id:     str
        @return:            True if the RDC data is to be used for optimisation, False otherwise.
        @rtype:             bool
        """

        # No alignment IDs.
        if not hasattr(cdp, 'rdc_ids'):
            return False

        # No RDC data for the alignment.
        if align_id not in cdp.rdc_ids:
            return False

        # The RDC data is to be used for optimisation.
        return True


    def _param_num(self):
        """Determine the number of parameters in the model.

        @return:    The number of model parameters.
        @rtype:     int
        """

        # Init.
        num = 0

        # Update the model if needed.
        self._update_model()

        # Determine the data type.
        data_types = self._base_data_types()

        # Average domain position translation.
        if not self._translation_fixed():
            num += 3

        # The pivot point.
        if not self._pivot_fixed():
            num += 3

        # Average domain position parameters.
        if cdp.model in ['free rotor', 'iso cone, free rotor']:
            num += 2
        else:
            num += 3

        # Frame order eigenframe - the full frame.
        if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
            num += 3

        # Frame order eigenframe - the isotropic cone axis.
        elif cdp.model in ['iso cone', 'free rotor', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor']:
            num += 2

        # Cone parameters - pseudo-elliptic cone parameters.
        if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
            num += 2

        # Cone parameters - single isotropic angle or order parameter.
        elif cdp.model in ['iso cone', 'iso cone, torsionless', 'iso cone, free rotor']:
            num += 1

        # Cone parameters - torsion angle.
        if cdp.model in ['rotor', 'line', 'iso cone', 'pseudo-ellipse']:
            num += 1

        # Return the number.
        return num


    def _pdb_ave_pos(self, file=None, dir=None, force=False):
        """Create a PDB file of the molecule with the moving domains shifted to the average position.

        @keyword file:  The name of the file for the average molecule structure.
        @type file:     str
        @keyword dir:   The name of the directory to place the PDB file into.
        @type dir:      str
        @keyword force: Flag which if set to True will cause any pre-existing file to be overwritten.
        @type force:    bool
        """

        # Printout.
        section(sys.stdout, "Creating a PDB file with the moving domains shifted to the average position.")

        # Make a copy of the structural object (so as to preserve the original structure).
        structure = deepcopy(cdp.structure)

        # First rotate the moving domain to the average position.
        R = zeros((3, 3), float64)
        if hasattr(cdp, 'ave_pos_alpha'):
            euler_to_R_zyz(cdp.ave_pos_alpha, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        else:
            euler_to_R_zyz(0.0, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        if cdp.ave_pos_pivot == 'com':
            origin = centre_of_mass(atom_id=self._domain_moving(), verbosity=0)
        else:
            origin = cdp.pivot
        structure.rotate(R=R, origin=origin, atom_id=self._domain_moving())

        # Then translate the moving domain.
        if not self._translation_fixed():
            structure.translate(T=[cdp.ave_pos_x, cdp.ave_pos_y, cdp.ave_pos_z], atom_id=self._domain_moving())

        # Write out the PDB file.
        file = open_write_file(file_name=file, dir=dir, force=force)
        structure.write_pdb(file=file)
        file.close()


    def _pdb_distribution(self, file=None, dir=None, force=False):
        """Create a PDB file of a distribution of positions coving the full dynamics of the moving domain.

        @keyword file:  The name of the file which will contain multiple models spanning the full dynamics distribution of the frame order model.
        @type file:     str
        @keyword dir:   The name of the directory to place the PDB file into.
        @type dir:      str
        @keyword force: Flag which if set to True will cause any pre-existing file to be overwritten.
        @type force:    bool
        """

        # Printout.
        section(sys.stdout, "Creating a PDB file of a distribution of positions coving the full dynamics of the moving domain.")



    def _pdb_geometric_rep(self, file=None, dir=None, size=30.0, inc=36, force=False, neg_cone=True):
        """Create a PDB file containing a geometric object representing the frame order dynamics.

        @keyword file:          The name of the file of the PDB representation of the frame order dynamics to create.
        @type file:             str
        @keyword dir:           The name of the directory to place the PDB file into.
        @type dir:              str
        @keyword size:          The size of the geometric object in Angstroms.
        @type size:             float
        @keyword inc:           The number of increments for the filling of the cone objects.
        @type inc:              int
        @keyword force:         Flag which if set to True will cause any pre-existing file to be overwritten.
        @type force:            bool
        @keyword neg_cone:      A flag which if True will cause the negative cone to be added to the representation.
        @type neg_cone:         bool
        """

        # Printout.
        section(sys.stdout, "Creating a PDB file containing a geometric object representing the frame order dynamics.")

        # Monte Carlo simulation flag.
        sim = False
        num_sim = 0
        if hasattr(cdp, 'sim_number'):
            sim = True
            num_sim = cdp.sim_number

        # The inversion matrix.
        inv_mat = -eye(3)

        # Create the structural object.
        structure = Internal()

        # Create model for the positive and negative images.
        model = structure.add_model(model=1)
        if neg_cone:
            model_neg = structure.add_model(model=2)

        # Create the molecule.
        structure.add_molecule(name=cdp.model)

        # Alias the molecules.
        mol = model.mol[0]
        if neg_cone:
            mol_neg = model_neg.mol[0]


        # The pivot point.
        ##################

        # Add the pivot point.
        structure.add_atom(mol_name=cdp.model, pdb_record='HETATM', atom_num=1, atom_name='R', res_name='PIV', res_num=1, pos=cdp.pivot, element='C')


        # The axes.
        ###########

        # The spherical angles.
        if cdp.model in ['iso cone', 'free rotor', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor']:
            # Print out.
            print("\nGenerating the z-axis system.")

            # The axis.
            axis = zeros(3, float64)
            spherical_to_cartesian([1.0, getattr(cdp, 'axis_theta'), getattr(cdp, 'axis_phi')], axis)
            print(("Central axis: %s." % axis))

            # Rotations and inversions.
            axis_pos = axis
            axis_neg = dot(inv_mat, axis)

            # Simulation central axis.
            axis_sim_pos = None
            axis_sim_neg = None
            if sim:
                # Init.
                axis_sim = zeros((cdp.sim_number, 3), float64)

                # Fill the structure.
                for i in range(cdp.sim_number):
                    spherical_to_cartesian([1.0, getattr(cdp, 'axis_theta_sim')[i], getattr(cdp, 'axis_phi_sim')[i]], axis_sim[i])

                # Inversion.
                axis_sim_pos = axis_sim
                axis_sim_neg = transpose(dot(inv_mat, transpose(axis_sim_pos)))

            # Generate the axis vectors.
            print("\nGenerating the axis vectors.")
            res_num = geometric.generate_vector_residues(mol=mol, vector=axis_pos, atom_name='z-ax', res_name_vect='AXE', sim_vectors=axis_sim_pos, res_num=2, origin=cdp.pivot, scale=size)

            # The negative.
            if neg_cone:
                res_num = geometric.generate_vector_residues(mol=mol_neg, vector=axis_neg, atom_name='z-ax', res_name_vect='AXE', sim_vectors=axis_sim_neg, res_num=2, origin=cdp.pivot, scale=size)

        # The full axis system.
        else:
            # Print out.
            print("\nGenerating the full axis system.")

            # The axis system.
            axes = zeros((3, 3), float64)
            euler_to_R_zyz(cdp.eigen_alpha, cdp.eigen_beta, cdp.eigen_gamma, axes)
            print(("Axis system:\n%s" % axes))

            # Rotations and inversions.
            axes_pos = axes
            axes_neg = dot(inv_mat, axes)

            # Simulations
            axes_sim_pos = None
            axes_sim_neg = None
            if sim:
                # Init.
                axes_sim_pos = zeros((cdp.sim_number, 3, 3), float64)
                axes_sim_neg = zeros((cdp.sim_number, 3, 3), float64)

                # Fill the structure.
                for i in range(cdp.sim_number):
                    # The positive system.
                    euler_to_R_zyz(cdp.eigen_alpha_sim[i], cdp.eigen_beta_sim[i], cdp.eigen_gamma_sim[i], axes_sim_pos[i])

                    # The negative system.
                    euler_to_R_zyz(cdp.eigen_alpha_sim[i], cdp.eigen_beta_sim[i], cdp.eigen_gamma_sim[i], axes_sim_neg[i])
                    axes_sim_neg[i] = dot(inv_mat, axes_sim_neg[i])

            # Generate the axis vectors.
            print("\nGenerating the axis vectors.")
            label = ['x', 'y', 'z']
            for j in range(len(label)):
                # The simulation data.
                axis_sim_pos = None
                axis_sim_neg = None
                if sim:
                    axis_sim_pos = axes_sim_pos[:,:, j]
                    axis_sim_neg = axes_sim_neg[:,:, j]

                # The vectors.
                res_num = geometric.generate_vector_residues(mol=mol, vector=axes_pos[:, j], atom_name='%s-ax'%label[j], res_name_vect='AXE', sim_vectors=axis_sim_pos, res_num=2, origin=cdp.pivot, scale=size)
                if neg_cone:
                    res_num = geometric.generate_vector_residues(mol=mol_neg, vector=axes_neg[:, j], atom_name='%s-ax'%label[j], res_name_vect='AXE', sim_vectors=axis_sim_neg, res_num=2, origin=cdp.pivot, scale=size)


        # The cone object.
        ##################

        # Skip models missing a cone.
        if cdp.model not in ['rotor', 'free rotor']:
            # The rotation matrix (rotation from the z-axis to the cone axis).
            if cdp.model not in ['iso cone', 'iso cone, torsionless', 'iso cone, free rotor']:
                R = axes
            else:
                R = zeros((3, 3), float64)
                two_vect_to_R(array([0, 0, 1], float64), axis, R)

            # Average position rotation.
            R_pos = R
            R_neg = dot(inv_mat, R)

            # The pseudo-ellipse cone object.
            if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
                cone = Pseudo_elliptic(cdp.cone_theta_x, cdp.cone_theta_y)

            # The isotropic cone object.
            else:
                # The angle.
                if hasattr(cdp, 'cone_theta'):
                    cone_theta = cdp.cone_theta
                elif hasattr(cdp, 'cone_s1'):
                    cone_theta = order_parameters.iso_cone_S_to_theta(cdp.cone_s1)

                # The object.
                cone = Iso_cone(cone_theta)

            # Create the positive and negative cones.
            geometric.create_cone_pdb(mol=mol, cone=cone, start_res=mol.res_num[-1]+1, apex=cdp.pivot, R=R_pos, inc=inc, distribution='regular', axis_flag=False)

            # The negative.
            if neg_cone:
                geometric.create_cone_pdb(mol=mol_neg, cone=cone, start_res=mol_neg.res_num[-1]+1, apex=cdp.pivot, R=R_neg, inc=inc, distribution='regular', axis_flag=False)


        # Create the PDB file.
        ######################

        # Print out.
        print("\nGenerating the PDB file.")

        # Write the file.
        pdb_file = open_write_file(file, dir, force=force)
        structure.write_pdb(pdb_file)
        pdb_file.close()


    def _pdb_model(self, ave_pos_file="ave_pos.pdb", rep_file="frame_order.pdb", dist_file="domain_distribution.pdb", dir=None, size=30.0, inc=36, force=False, neg_cone=True):
        """Create 3 different PDB files for representing the frame order dynamics of the system.

        @keyword ave_pos_file:  The name of the file for the average molecule structure.
        @type ave_pos_file:     str
        @keyword rep_file:      The name of the file of the PDB representation of the frame order dynamics to create.
        @type rep_file:         str
        @keyword dist_file:     The name of the file which will contain multiple models spanning the full dynamics distribution of the frame order model.
        @type dist_file:        str
        @keyword dir:           The name of the directory to place the PDB file into.
        @type dir:              str
        @keyword size:          The size of the geometric object in Angstroms.
        @type size:             float
        @keyword inc:           The number of increments for the filling of the cone objects.
        @type inc:              int
        @keyword force:         Flag which if set to True will cause any pre-existing file to be overwritten.
        @type force:            bool
        @keyword neg_cone:      A flag which if True will cause the negative cone to be added to the representation.
        @type neg_cone:         bool
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Create the average position structure.
        self._pdb_ave_pos(file=ave_pos_file, dir=dir, force=force)

        # Nothing more to do for the rigid model.
        if cdp.model == 'rigid':
            return

        # Create the geometric representation.
        self._pdb_geometric_rep(file=rep_file, dir=dir, size=size, inc=inc, force=force, neg_cone=neg_cone)

        # Create the distribution.
        self._pdb_distribution(file=dist_file, dir=dir, force=force)


    def _pivot(self, pivot=None, fix=None):
        """Set the pivot point for the 2 body motion.

        @keyword pivot: The pivot point of the two bodies (domains, etc.) in the structural coordinate system.
        @type pivot:    list of num
        @keyword fix:   A flag specifying if the pivot point should be fixed during optimisation.
        @type fix:      bool
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Set the pivot point and fixed flag.
        cdp.pivot = pivot
        cdp.pivot_fixed = fix

        # Convert to floats.
        for i in range(3):
            cdp.pivot[i] = float(cdp.pivot[i])


    def _pivot_fixed(self):
        """Determine if the pivot is fixed or not.

        @return:    The answer to the question.
        @rtype:     bool
        """

        # A pivot point is not supported by the model.
        if cdp.model in ['rigid']:
            return True

        # The PCS is loaded.
        if 'pcs' in self._base_data_types():
            # The fixed flag is not set.
            if hasattr(cdp, 'pivot_fixed') and not cdp.pivot_fixed:
                return False

        # The point is fixed.
        return True


    def _quad_int(self, flag=False):
        """Turn the high precision Scipy quadratic numerical integration on or off.

        @keyword flag:  The flag which if True will perform high precision numerical integration via the scipy.integrate quad(), dblquad() and tplquad() integration methods rather than the rough quasi-random numerical integration.
        @type flag:     bool
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Store the flag.
        cdp.quad_int = flag


    def _ref_domain(self, ref=None):
        """Set the reference domain for the frame order, multi-domain models.

        @param ref: The reference domain.
        @type ref:  str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Check that the domain is defined.
        if not hasattr(cdp, 'domain') or ref not in list(cdp.domain.keys()):
            raise RelaxError("The domain '%s' has not been defined.  Please use the domain user function." % ref)

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
        if hasattr(cdp, 'model'):
            self._update_model()


    def _select_model(self, model=None):
        """Select the Frame Order model.

        @param model:   The Frame Order model.  This can be one of 'pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor', 'iso cone', 'iso cone, torsionless', 'iso cone, free rotor', 'line', 'line, torsionless', 'line, free rotor', 'rotor', 'rigid', 'free rotor'.
        @type model:    str
        """

        # Test if the current data pipe exists.
        pipes.test()

        # Test if the model name exists.
        if not model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor', 'iso cone', 'iso cone, torsionless', 'iso cone, free rotor', 'line', 'line, torsionless', 'line, free rotor', 'rotor', 'rigid', 'free rotor']:
            raise RelaxError("The model name " + repr(model) + " is invalid.")

        # Set the model
        cdp.model = model

        # Initialise the list of model parameters.
        cdp.params = []

        # Set the integration method if needed.
        if not hasattr(cdp, 'quad_int'):
            # Scipy quadratic numerical integration.
            if cdp.model in []:
                cdp.quad_int = True

            # Quasi-random numerical integration.
            else:
                cdp.quad_int = False

        # Update the model.
        self._update_model()


    def _store_bc_data(self, target_fn):
        """Store the back-calculated data.

        @param target_fn:   The frame-order target function class.
        @type target_fn:    class instance
        """

        # Loop over the reduced tensors.
        for i, tensor in self._tensor_loop(red=True):
            # Store the values.
            tensor.set(param='Axx', value=target_fn.A_5D_bc[5*i + 0])
            tensor.set(param='Ayy', value=target_fn.A_5D_bc[5*i + 1])
            tensor.set(param='Axy', value=target_fn.A_5D_bc[5*i + 2])
            tensor.set(param='Axz', value=target_fn.A_5D_bc[5*i + 3])
            tensor.set(param='Ayz', value=target_fn.A_5D_bc[5*i + 4])

        # The RDC data.
        for i in range(len(cdp.align_ids)):
            # The alignment ID.
            align_id = cdp.align_ids[i]

            # Data flags
            rdc_flag = False
            if hasattr(cdp, 'rdc_ids') and align_id in cdp.rdc_ids:
                rdc_flag = True
            pcs_flag = False
            if hasattr(cdp, 'pcs_ids') and align_id in cdp.pcs_ids:
                pcs_flag = True

            # Spin loop over the domain.
            pcs_index = 0
            for spin in spin_loop(self._domain_moving()):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Spins with PCS data.
                if pcs_flag and hasattr(spin, 'pcs'):
                    # Initialise the data structure.
                    if not hasattr(spin, 'pcs_bc'):
                        spin.pcs_bc = {}

                    # Store the back-calculated value (in ppm).
                    spin.pcs_bc[align_id] = target_fn.pcs_theta[i, pcs_index] * 1e6

                    # Increment the index.
                    pcs_index += 1

            # Interatomic data container loop.
            rdc_index = 0
            for interatom in interatomic_loop(self._domain_moving()):
                # Get the spins.
                spin1 = return_spin(interatom.spin_id1)
                spin2 = return_spin(interatom.spin_id2)

                # RDC checks.
                if not self._check_rdcs(interatom, spin1, spin2):
                    continue

                # Initialise the data structure.
                if not hasattr(interatom, 'rdc_bc'):
                    interatom.rdc_bc = {}

                # Store the back-calculated value.
                interatom.rdc_bc[align_id] = target_fn.rdc_theta[i, rdc_index]

                # Increment the index.
                rdc_index += 1


    def _target_fn_setup(self, sim_index=None, scaling=True):
        """Initialise the target function for optimisation or direct calculation.

        @param sim_index:       The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:        None or int
        @param scaling:         If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
        @type scaling:          bool
        """

        # Check for the average domain displacement information.
        if not hasattr(cdp, 'ave_pos_pivot') or not hasattr(cdp, 'ave_pos_translation'):
            raise RelaxError("The mechanics of the displacement to the average domain position have not been set up.")

        # Assemble the parameter vector.
        param_vector = self._assemble_param_vector(sim_index=sim_index)

        # Determine if alignment tensors or RDCs are to be used.
        data_types = self._base_data_types()

        # Diagonal scaling.
        scaling_matrix = None
        if len(param_vector):
            scaling_matrix = self._assemble_scaling_matrix(data_types=data_types, scaling=scaling)
            param_vector = dot(inv(scaling_matrix), param_vector)

        # Get the data structures for optimisation using the tensors as base data sets.
        full_tensors, full_tensor_err, full_in_ref_frame = self._minimise_setup_tensors(sim_index)

        # Get the data structures for optimisation using PCSs as base data sets.
        pcs, pcs_err, pcs_weight, temp, frq = None, None, None, None, None
        if 'pcs' in data_types:
            pcs, pcs_err, pcs_weight, temp, frq = self._minimise_setup_pcs(sim_index=sim_index)

        # Get the data structures for optimisation using RDCs as base data sets.
        rdcs, rdc_err, rdc_weight, rdc_vect, rdc_const, absolute_rdc = None, None, None, None, None, None
        if 'rdc' in data_types:
            rdcs, rdc_err, rdc_weight, rdc_vect, rdc_const, absolute_rdc = self._minimise_setup_rdcs(sim_index=sim_index)

        # Data checks.
        if pcs != None and not len(pcs):
            raise RelaxNoPCSError
        if rdcs != None and not len(rdcs):
            raise RelaxNoRDCError

        # Get the atomic_positions.
        atomic_pos, paramag_centre = None, None
        if 'pcs' in data_types or 'pre' in data_types:
            atomic_pos, paramag_centre = self._minimise_setup_atomic_pos(sim_index=sim_index)

        # Average domain translation.
        translation_opt = False
        if not self._translation_fixed():
            translation_opt = True

        # The fixed pivot point.
        pivot = None
        if hasattr(cdp, 'pivot'):
            pivot = cdp.pivot

        # Pivot optimisation.
        pivot_opt = True
        if self._pivot_fixed():
            pivot_opt = False

        # The number of integration points.
        if not hasattr(cdp, 'num_int_pts'):
            cdp.num_int_pts = 200000

        # The centre of mass of the moving domain - to use as the centroid for the average domain position rotation.
        if cdp.ave_pos_pivot == 'com':
            com = centre_of_mass(atom_id=self._domain_moving(), verbosity=0)
            ave_pos_piv_sync = False

        # The centre of mass of the moving domain - to use as the centroid for the average domain position rotation.
        if cdp.ave_pos_pivot == 'motional':
            com = pivot
            ave_pos_piv_sync = True

        # Print outs.
        if sim_index == None:
            if cdp.model != 'rigid':
                if cdp.quad_int:
                    sys.stdout.write("Numerical integration via Scipy quadratic integration.\n")
                else:
                    sys.stdout.write("Numerical integration via the quasi-random Sobol' sequence.\n")
                    sys.stdout.write("Number of integration points: %s\n" % cdp.num_int_pts)
            base_data = []
            if rdcs != None and len(rdcs):
                base_data.append("RDCs")
            if pcs != None and len(pcs):
                base_data.append("PCSs")
            sys.stdout.write("Base data: %s\n" % repr(base_data))

        # Set up the optimisation function.
        target = frame_order.Frame_order(model=cdp.model, init_params=param_vector, full_tensors=full_tensors, full_in_ref_frame=full_in_ref_frame, rdcs=rdcs, rdc_errors=rdc_err, rdc_weights=rdc_weight, rdc_vect=rdc_vect, dip_const=rdc_const, pcs=pcs, pcs_errors=pcs_err, pcs_weights=pcs_weight, atomic_pos=atomic_pos, temp=temp, frq=frq, paramag_centre=paramag_centre, scaling_matrix=scaling_matrix, ave_pos_pivot=com, ave_pos_piv_sync=ave_pos_piv_sync, translation_opt=translation_opt, pivot=pivot, pivot_opt=pivot_opt, num_int_pts=cdp.num_int_pts, quad_int=cdp.quad_int)

        # Return the data.
        return target, param_vector, data_types, scaling_matrix


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


    def _translation_fixed(self):
        """Is the translation of the average domain position fixed?

        @return:    The answer to the question.
        @rtype:     bool
        """

        # PCS data must be present.
        if 'pcs' in self._base_data_types():
            # The fixed flag is not set.
            if hasattr(cdp, 'ave_pos_translation') and cdp.ave_pos_translation:
                return False

        # Default to being fixed.
        return True


    def _update_model(self):
        """Update the model parameters as necessary."""

        # Re-initialise the list of model parameters.
        cdp.params = []

        # The pivot parameters.
        if not self._pivot_fixed():
            cdp.params.append('pivot_x')
            cdp.params.append('pivot_y')
            cdp.params.append('pivot_z')

        # The average domain position translation parameters.
        if not self._translation_fixed():
            cdp.params.append('ave_pos_x')
            cdp.params.append('ave_pos_y')
            cdp.params.append('ave_pos_z')

        # The tensor rotation, or average domain position.
        if cdp.model not in ['free rotor', 'iso cone, free rotor']:
            cdp.params.append('ave_pos_alpha')
        cdp.params.append('ave_pos_beta')
        cdp.params.append('ave_pos_gamma')

        # Frame order eigenframe - the full frame.
        if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
            cdp.params.append('eigen_alpha')
            cdp.params.append('eigen_beta')
            cdp.params.append('eigen_gamma')

        # Frame order eigenframe - the isotropic cone axis.
        elif cdp.model in ['iso cone', 'free rotor', 'iso cone, torsionless', 'iso cone, free rotor', 'rotor']:
            cdp.params.append('axis_theta')
            cdp.params.append('axis_phi')

        # Cone parameters - pseudo-elliptic cone parameters.
        if cdp.model in ['pseudo-ellipse', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
            cdp.params.append('cone_theta_x')
            cdp.params.append('cone_theta_y')

        # Cone parameters - single isotropic angle or order parameter.
        elif cdp.model in ['iso cone', 'iso cone, torsionless']:
            cdp.params.append('cone_theta')
        elif cdp.model in ['iso cone, free rotor']:
            cdp.params.append('cone_s1')

        # Cone parameters - torsion angle.
        if cdp.model in ['rotor', 'line', 'iso cone', 'pseudo-ellipse']:
            cdp.params.append('cone_sigma_max')

        # Initialise the parameters in the current data pipe.
        for param in cdp.params:
            if not param in ['pivot_x', 'pivot_y', 'pivot_z'] and not hasattr(cdp, param):
                setattr(cdp, param, 0.0)


    def _unpack_opt_results(self, results, scaling=False, scaling_matrix=None, sim_index=None):
        """Unpack and store the Frame Order optimisation results.

        @param results:             The results tuple returned by the minfx generic_minimise() function.
        @type results:              tuple
        @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
        @type scaling:              bool
        @keyword scaling_matrix:    The scaling matrix.
        @type scaling_matrix:       numpy rank-2 array
        @keyword sim_index:         The index of the simulation to optimise.  This should be None for normal optimisation.
        @type sim_index:            None or int
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

        # Scaling.
        if scaling:
            param_vector = dot(scaling_matrix, param_vector)

        # Pivot point.
        if not self._pivot_fixed():
            # Store the pivot.
            cdp.pivot = param_vector[:3]

            # Then remove it from the params.
            param_vector = param_vector[3:]

        # Average domain position translation.
        ave_pos_x, ave_pos_y, ave_pos_z = None, None, None
        if not self._translation_fixed():
            ave_pos_x = param_vector[0]
            ave_pos_y = param_vector[1]
            ave_pos_z = param_vector[2]

            # Remove the parameters from the array.
            param_vector = param_vector[3:]

        # Unpack the parameters.
        ave_pos_alpha, ave_pos_beta, ave_pos_gamma = None, None, None
        eigen_alpha, eigen_beta, eigen_gamma = None, None, None
        axis_theta, axis_phi = None, None
        cone_theta_x, cone_theta_y = None, None
        cone_theta = None
        cone_s1 = None
        cone_sigma_max = None
        if cdp.model == 'pseudo-ellipse':
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y, cone_sigma_max = param_vector
        elif cdp.model in ['pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor']:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_theta_y = param_vector
        elif cdp.model == 'iso cone':
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta, cone_sigma_max = param_vector
        elif cdp.model in ['iso cone, torsionless']:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_theta = param_vector
        elif cdp.model in ['iso cone, free rotor']:
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_s1 = param_vector
            ave_pos_alpha = None
        elif cdp.model == 'line':
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_sigma_max = param_vector
        elif cdp.model in ['line, torsionless', 'line, free rotor']:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, eigen_alpha, eigen_beta, eigen_gamma, cone_theta_x, cone_sigma_max = param_vector
        elif cdp.model in ['rotor']:
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi, cone_sigma_max = param_vector
        elif cdp.model in ['free rotor']:
            ave_pos_beta, ave_pos_gamma, axis_theta, axis_phi = param_vector
            ave_pos_alpha = None
        elif cdp.model == 'rigid':
            ave_pos_alpha, ave_pos_beta, ave_pos_gamma = param_vector

        # Monte Carlo simulation data structures.
        if sim_index != None:
            # Average position parameters.
            if ave_pos_x != None:
                cdp.ave_pos_x_sim[sim_index] = ave_pos_x
            if ave_pos_y != None:
                cdp.ave_pos_y_sim[sim_index] = ave_pos_y
            if ave_pos_z != None:
                cdp.ave_pos_z_sim[sim_index] = ave_pos_z
            if ave_pos_alpha != None:
                cdp.ave_pos_alpha_sim[sim_index] = wrap_angles(ave_pos_alpha, cdp.ave_pos_alpha-pi, cdp.ave_pos_alpha+pi)
            if ave_pos_beta != None:
                cdp.ave_pos_beta_sim[sim_index] = wrap_angles(ave_pos_beta, cdp.ave_pos_beta-pi, cdp.ave_pos_beta+pi)
            if ave_pos_gamma != None:
                cdp.ave_pos_gamma_sim[sim_index] = wrap_angles(ave_pos_gamma, cdp.ave_pos_gamma-pi, cdp.ave_pos_gamma+pi)

            # Eigenframe parameters.
            if eigen_alpha != None:
                cdp.eigen_alpha_sim[sim_index] = wrap_angles(eigen_alpha, cdp.eigen_alpha-pi, cdp.eigen_alpha+pi)
            if eigen_beta != None:
                cdp.eigen_beta_sim[sim_index] =  wrap_angles(eigen_beta, cdp.eigen_beta-pi, cdp.eigen_beta+pi)
            if eigen_gamma != None:
                cdp.eigen_gamma_sim[sim_index] = wrap_angles(eigen_gamma, cdp.eigen_gamma-pi, cdp.eigen_gamma+pi)
            if axis_theta != None:
                cdp.axis_theta_sim[sim_index] = wrap_angles(axis_theta, cdp.axis_theta-pi, cdp.axis_theta+pi)
            if axis_phi != None:
                cdp.axis_phi_sim[sim_index] = wrap_angles(axis_phi, cdp.axis_phi-pi, cdp.axis_phi+pi)

            # Cone parameters.
            if cone_theta != None:
                cdp.cone_theta_sim[sim_index] = cone_theta
            if cone_s1 != None:
                cdp.cone_s1_sim[sim_index] = cone_s1
                cdp.cone_theta_sim[sim_index] = order_parameters.iso_cone_S_to_theta(cone_s1)
            if cone_theta_x != None:
                cdp.cone_theta_x_sim[sim_index] = cone_theta_x
            if cone_theta_y != None:
                cdp.cone_theta_y_sim[sim_index] = cone_theta_y
            if cone_sigma_max != None:
                cdp.cone_sigma_max_sim[sim_index] = abs(cone_sigma_max)

            # Optimisation stats.
            cdp.chi2_sim[sim_index] = func
            cdp.iter_sim[sim_index] = iter_count
            cdp.f_count_sim[sim_index] = f_count
            cdp.g_count_sim[sim_index] = g_count
            cdp.h_count_sim[sim_index] = h_count
            cdp.warning_sim[sim_index] = warning

        # Normal data structures.
        else:
            # Average position parameters.
            if ave_pos_x != None:
                cdp.ave_pos_x = ave_pos_x
            if ave_pos_y != None:
                cdp.ave_pos_y = ave_pos_y
            if ave_pos_z != None:
                cdp.ave_pos_z = ave_pos_z
            if ave_pos_alpha != None:
                cdp.ave_pos_alpha = wrap_angles(ave_pos_alpha, 0.0, 2.0*pi)
            if ave_pos_beta != None:
                cdp.ave_pos_beta = wrap_angles(ave_pos_beta, 0.0, 2.0*pi)
            if ave_pos_gamma != None:
                cdp.ave_pos_gamma = wrap_angles(ave_pos_gamma, 0.0, 2.0*pi)

            # Eigenframe parameters.
            if eigen_alpha != None:
                cdp.eigen_alpha = wrap_angles(eigen_alpha, 0.0, 2.0*pi)
            if eigen_beta != None:
                cdp.eigen_beta =  wrap_angles(eigen_beta,  0.0, 2.0*pi)
            if eigen_gamma != None:
                cdp.eigen_gamma = wrap_angles(eigen_gamma, 0.0, 2.0*pi)
            if axis_theta != None:
                cdp.axis_theta = wrap_angles(axis_theta, 0.0, 2.0*pi)
            if axis_phi != None:
                cdp.axis_phi = wrap_angles(axis_phi, 0.0, 2.0*pi)

            # Cone parameters.
            if cone_theta != None:
                cdp.cone_theta = cone_theta
            if cone_s1 != None:
                cdp.cone_s1 = cone_s1
                cdp.cone_theta = order_parameters.iso_cone_S_to_theta(cone_s1)
            if cone_theta_x != None:
                cdp.cone_theta_x = cone_theta_x
            if cone_theta_y != None:
                cdp.cone_theta_y = cone_theta_y
            if cone_sigma_max != None:
                cdp.cone_sigma_max = abs(cone_sigma_max)

            # Optimisation stats.
            cdp.chi2 = func
            cdp.iter = iter_count
            cdp.f_count = f_count
            cdp.g_count = g_count
            cdp.h_count = h_count
            cdp.warning = warning


    def base_data_loop(self):
        """Generator method for looping over the base data - alignment tensors, RDCs, PCSs.

        This loop yields the following:

            - The RDC identification data for the interatomic data container and alignment.
            - The PCS identification data for the spin data container and alignment.

        @return:    The base data type ('rdc' or 'pcs'), the spin or interatomic data container information (either one or two spin IDs), and the alignment ID string.
        @rtype:     list of str
        """

        # Loop over the interatomic data containers for the moving domain (for the RDC data).
        for interatom in interatomic_loop(selection1=self._domain_moving()):
            # Get the spins.
            spin1 = return_spin(interatom.spin_id1)
            spin2 = return_spin(interatom.spin_id2)

            # RDC checks.
            if not self._check_rdcs(interatom, spin1, spin2):
                continue

            # Loop over the alignment IDs.
            for align_id in cdp.rdc_ids:
                # Yield the info set.
                yield ['rdc', interatom.spin_id1, interatom.spin_id2, align_id]

        # Loop over the spin containers for the moving domain (for the PCS data).
        for spin, spin_id in spin_loop(selection=self._domain_moving(), return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # No PCS, so skip.
            if not hasattr(spin, 'pcs'):
                continue

            # Loop over the alignment IDs.
            for align_id in cdp.pcs_ids:
                # Yield the info set.
                yield ['pcs', spin_id, align_id]


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculate the chi-squared value for the current parameter values.

        @keyword spin_id:   The spin identification string (unused).
        @type spin_id:      None
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The optional MC simulation index (unused).
        @type sim_index:    None or int
        """

        # Set up the target function for direct calculation.
        model, param_vector, data_types, scaling_matrix = self._target_fn_setup(sim_index=sim_index)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        chi2 = model.func(param_vector)

        # Set the chi2.
        cdp.chi2 = chi2

        # Store the back-calculated data.
        self._store_bc_data(model)

        # Printout.
        print("Chi2:  %s" % chi2)


    def create_mc_data(self, data_id=None):
        """Create the Monte Carlo data by back calculating the reduced tensor data.

        @keyword data_id:   The data set as yielded by the base_data_loop() generator method.
        @type data_id:      list of str
        @return:            The Monte Carlo simulation data.
        @rtype:             list of floats
        """

        # Initialise the MC data structure.
        mc_data = []

        # The RDC data.
        if data_id[0] == 'rdc':
            # Unpack the set.
            data_type, spin_id1, spin_id2, align_id = data_id

            # Get the interatomic data container.
            interatom = return_interatom(spin_id1, spin_id2)

            # Does back-calculated data exist?
            if not hasattr(interatom, 'rdc_bc'):
                self.calculate()

            # The data.
            if not hasattr(interatom, 'rdc_bc') or align_id not in interatom.rdc_bc:
                data = None
            else:
                data = interatom.rdc_bc[align_id]

            # Append the data.
            mc_data.append(data)

        # The PCS data.
        elif data_id[0] == 'pcs':
            # Unpack the set.
            data_type, spin_id, align_id = data_id

            # Get the spin container.
            spin = return_spin(spin_id)

            # Does back-calculated data exist?
            if not hasattr(spin, 'pcs_bc'):
                self.calculate()

            # The data.
            if not hasattr(spin, 'pcs_bc') or align_id not in spin.pcs_bc:
                data = None
            else:
                data = spin.pcs_bc[align_id]

            # Append the data.
            mc_data.append(data)

        # Return the data.
        return mc_data


    def deselect(self, model_info, sim_index=None):
        """Deselect models or simulations.

        @param model_info:      The model index from model_loop().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword sim_index:     The optional Monte Carlo simulation index.  If None, then models will be deselected, otherwise the given simulation will.
        @type sim_index:        None or int
        """

        # Set the deselection flag.
        cdp.select = False


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_info=None, global_stats=False, verbose=True):
        """Duplicate the data specific to a single frame order data pipe.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @param model_info:      The model index from model_loop().
        @type model_info:       int
        @keyword global_stats:  The global statistics flag.
        @type global_stats:     bool
        @keyword verbose:       Unused.
        @type verbose:          bool
        """

        # Check that the data pipe does not exist.
        if pipes.has_pipe(pipe_to):
            raise RelaxError("The data pipe '%s' already exists." % pipe_to)

        # Create the pipe_to data pipe by copying.
        pipes.copy(pipe_from=pipe_from, pipe_to=pipe_to)


    def eliminate(self, name, value, model_info, args, sim=None):
        """Model elimination method.

        @param name:        The parameter name.
        @type name:         str
        @param value:       The parameter value.
        @type value:        float
        @param model_info:  The model index from model_info().
        @type model_info:   int
        @param args:        The elimination constant overrides.
        @type args:         None or tuple of float
        @keyword sim:       The Monte Carlo simulation index.
        @type sim:          int
        @return:            True if the model is to be eliminated, False otherwise.
        @rtype:             bool
        """

        # Text to print out if a model failure occurs.
        text = "The %s parameter of %.5g is %s than %.5g, eliminating "
        if sim == None:
            text += "the model."
        else:
            text += "simulation %i." % sim

        # Isotropic order parameter out of range.
        if name == 'cone_s1' and hasattr(cdp, 'cone_s1'):
            if cdp.cone_s1 > 1.0:
                print(text % ("cone S1 order", cdp.cone_s1, "greater", 1.0))
                return True
            if cdp.cone_s1 < -0.125:
                print(text % ("cone S1 order", cdp.cone_s1, "less", -0.125))
                return True

        # Isotropic cone angle out of range.
        if name == 'cone_theta' and hasattr(cdp, 'cone_theta'):
            if cdp.cone_theta >= pi:
                print(text % ("cone opening angle theta", cdp.cone_theta, "greater", pi))
                return True
            if cdp.cone_theta < 0.0:
                print(text % ("cone opening angle theta", cdp.cone_theta, "less", 0))
                return True

        # Pseudo-ellipse cone angles out of range (0.001 instead of 0.0 because of truncation in the numerical integration).
        if name == 'cone_theta_x' and hasattr(cdp, 'cone_theta_x'):
            if cdp.cone_theta_x >= pi:
                print(text % ("cone opening angle theta x", cdp.cone_theta_x, "greater", pi))
                return True
            if cdp.cone_theta_x < 0.001:
                print(text % ("cone opening angle theta x", cdp.cone_theta_x, "less", 0.001))
                return True
        if name == 'cone_theta_y' and hasattr(cdp, 'cone_theta_y'):
            if cdp.cone_theta_y >= pi:
                print(text % ("cone opening angle theta y", cdp.cone_theta_y, "greater", pi))
                return True
            if cdp.cone_theta_y < 0.001:
                print(text % ("cone opening angle theta y", cdp.cone_theta_y, "less", 0.001))
                return True

        # Torsion angle out of range.
        if name == 'cone_sigma_max' and hasattr(cdp, 'cone_sigma_max'):
            if cdp.cone_sigma_max >= pi:
                print(text % ("torsion angle sigma_max", cdp.cone_sigma_max, "greater", pi))
                return True
            if cdp.cone_sigma_max < 0.0:
                print(text % ("torsion angle sigma_max", cdp.cone_sigma_max, "less", 0.0))
                return True

        # No failure.
        return False


    def get_param_names(self, model_info=None):
        """Return a vector of parameter names.

        @keyword model_info:    The model index from model_info().
        @type model_info:       int
        @return:                The vector of parameter names.
        @rtype:                 list of str
        """

        # First update the model, if needed.
        self._update_model()

        # Return the parameter list object.
        return cdp.params


    def get_param_values(self, model_info=None, sim_index=None):
        """Return a vector of parameter values.

        @keyword model_info:    The model index from model_info().  This is zero for the global models or equal to the global spin index (which covers the molecule, residue, and spin indices).
        @type model_info:       int
        @keyword sim_index:     The Monte Carlo simulation index.
        @type sim_index:        int
        @return:                The vector of parameter values.
        @rtype:                 list of str
        """

        # Assemble the values and return it.
        return self._assemble_param_vector(sim_index=sim_index)


    def grid_search(self, lower=None, upper=None, inc=None, constraints=False, verbosity=0, sim_index=None):
        """Perform a grid search.

        @keyword lower:         The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:            list of float
        @keyword upper:         The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:            list of float
        @keyword inc:           The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.
        @type inc:              int or list of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The Monte Carlo simulation index.
        @type sim_index:        None or int
        """

        # Test if the Frame Order model has been set up.
        if not hasattr(cdp, 'model'):
            raise RelaxNoModelError('Frame Order')

        # Parameter scaling.
        scaling_matrix = self._assemble_scaling_matrix(data_types=self._base_data_types(), scaling=True)

        # The number of parameters.
        n = self._param_num()

        # If inc is an int, convert it into an array of that value.
        if isinstance(inc, int):
            incs = [inc]*n
        else:
            incs = inc

        # Sanity check.
        if len(incs) != n:
            raise RelaxError("The size of the increment list %s does not match the number of parameters in %s." % (incs, cdp.params))

        # Initialise the grid increments structures.
        lower_list = lower
        upper_list = upper
        grid = []
        """This structure is a list of lists.  The first dimension corresponds to the model
        parameter.  The second dimension are the grid node positions."""

        # Generate the grid.
        for i in range(n):
            # Fixed parameter.
            if incs[i] == None:
                grid.append(None)
                continue

            # Reset.
            dist_type = None
            end_point = True

            # The pivot point.
            if cdp.params[i] == 'pivot_x':
                lower = cdp.pivot[0] - 10.0
                upper = cdp.pivot[0] + 10.0
            elif cdp.params[i] == 'pivot_y':
                lower = cdp.pivot[1] - 10.0
                upper = cdp.pivot[1] + 10.0
            elif cdp.params[i] == 'pivot_z':
                lower = cdp.pivot[2] - 10.0
                upper = cdp.pivot[2] + 10.0

            # Average domain position translation (in a +/- 5 Angstrom box).
            if cdp.params[i] in ['ave_pos_x', 'ave_pos_y', 'ave_pos_z']:
                lower = -5
                upper = 5

            # Linear angle grid from 0 to one inc before 2pi.
            if cdp.params[i] in ['ave_pos_alpha', 'ave_pos_gamma', 'eigen_alpha', 'eigen_gamma', 'axis_phi']:
                lower = 0.0
                upper = 2*pi * (1.0 - 1.0/incs[i])

            # Arccos grid from 0 to pi.
            if cdp.params[i] in ['ave_pos_beta', 'eigen_beta', 'axis_theta']:
                # Change the default increment numbers.
                if not isinstance(inc, list):
                    incs[i] = int(incs[i] / 2) + 1

                # The distribution type and end point.
                dist_type = 'acos'
                end_point = False

                # Set the default bounds.
                lower = 0.0
                upper = pi

            # The isotropic cone order parameter.
            if cdp.params[i] == 'cone_s1':
                lower = -0.125
                upper = 1.0

            # Linear angle grid from 0 to pi excluding the outer points.
            if cdp.params[i] in ['cone_theta', 'cone_theta_x', 'cone_theta_y', 'cone_sigma_max']:
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

            # Remove an inc if the end point has been removed.
            if not end_point:
                incs[i] -= 1

        # Total number of points.
        total_pts = 1
        for i in range(n):
            # Fixed parameter.
            if grid[i] == None:
                continue

            total_pts = total_pts * len(grid[i])

        # Check the number.
        max_pts = 50e6
        if total_pts > max_pts:
            raise RelaxError("The total number of grid points '%s' exceeds the maximum of '%s'." % (total_pts, int(max_pts)))

        # Build the points array.
        pts = zeros((total_pts, n), float64)
        indices = zeros(n, int)
        for i in range(total_pts):
            # Loop over the dimensions.
            for j in range(n):
                # Fixed parameter.
                if grid[j] == None:
                    # Get the current parameter value (pivot, assuming the pivot point is always at the start of the parameter array).
                    if cdp.params[j] in ['pivot_x', 'pivot_y', 'pivot_z']:
                        pts[i, j] = cdp.pivot[j] / scaling_matrix[j, j]

                    # Get the current parameter value (normal parameter).
                    else:
                        pts[i, j] = getattr(cdp, cdp.params[j]) / scaling_matrix[j, j]

                # Add the point coordinate.
                else:
                    pts[i, j] = grid[j][indices[j]] / scaling_matrix[j, j]

            # Increment the step positions.
            for j in range(n):
                if incs[j] != None and indices[j] < incs[j]-1:
                    indices[j] += 1
                    break    # Exit so that the other step numbers are not incremented.
                else:
                    indices[j] = 0

        # Minimisation.
        self.minimise(min_algor='grid', min_options=pts, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


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

        # Average domain position.
        if param in ['ave_pos_x', 'ave_pos_y', 'ave_pos_z']:
            return [-100.0, 100]
        if param in ['ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma']:
            return [0.0, 2*pi]

        # Axis spherical coordinate theta.
        if param == 'axis_theta':
            return [0.0, pi]

        # Axis spherical coordinate phi.
        if param == 'axis_phi':
            return [0.0, 2*pi]

        # Cone angle.
        if param == 'cone_theta':
            return [0.0, pi]


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Minimisation function.

        @param min_algor:       The minimisation algorithm to use.
        @type min_algor:        str
        @param min_options:     An array of options to be used by the minimisation algorithm.
        @type min_options:      array of str
        @param func_tol:        The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:         None or float
        @param grad_tol:        The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:         None or float
        @param max_iterations:  The maximum number of iterations for the algorithm.
        @type max_iterations:   int
        @param constraints:     If True, constraints are used during optimisation.
        @type constraints:      bool
        @param scaling:         If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
        @type scaling:          bool
        @param verbosity:       A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:        int
        @param sim_index:       The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:        None or int
        @keyword lower:         The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:              array of int
        """

        # Set up the target function for direct calculation.
        model, param_vector, data_types, scaling_matrix = self._target_fn_setup(sim_index=sim_index, scaling=scaling)

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

        # Grid search.
        if search('^[Gg]rid', min_algor):
            results = grid_point_array(func=model.func, args=(), points=min_options, verbosity=verbosity)

        # Minimisation.
        else:
            results = generic_minimise(func=model.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=True, print_flag=verbosity)

        # Unpack the results.
        self._unpack_opt_results(results, scaling, scaling_matrix, sim_index)

        # Store the back-calculated data.
        self._store_bc_data(model)


    def model_desc(self, model_info):
        """Return a description of the model.

        @param model_info:  The model index from model_loop().
        @type model_info:   int
        @return:            The model description.
        @rtype:             str
        """

        return ""


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


    def model_type(self):
        """Return the type of the model, either being 'local' or 'global'.

        @return:            The model type, one of 'local' or 'global'.
        @rtype:             str
        """

        return 'global'


    def return_error(self, data_id):
        """Return the alignment tensor error structure.

        @param data_id:     The data set as yielded by the base_data_loop() generator method.
        @type data_id:      list of str
        @return:            The array of tensor error values.
        @rtype:             list of float
        """

        # Initialise the MC data structure.
        mc_errors = []

        # The RDC data.
        if data_id[0] == 'rdc':
            # Unpack the set.
            data_type, spin_id1, spin_id2, align_id = data_id

            # Get the interatomic data container.
            interatom = return_interatom(spin_id1, spin_id2)

            # Do errors exist?
            if not hasattr(interatom, 'rdc_err'):
                raise RelaxError("The RDC errors are missing for interatomic data container between spins '%s' and '%s'." % (spin_id1, spin_id2))

            # Handle missing data.
            if align_id not in interatom.rdc_err:
                mc_errors.append(None)

            # Append the data.
            else:
                mc_errors.append(interatom.rdc_err[align_id])

        # The PCS data.
        elif data_id[0] == 'pcs':
            # Unpack the set.
            data_type, spin_id, align_id = data_id

            # Get the spin container.
            spin = return_spin(spin_id)

            # Do errors exist?
            if not hasattr(spin, 'pcs_err'):
                raise RelaxError("The PCS errors are missing for spin '%s'." % spin_id)

            # Handle missing data.
            if align_id not in spin.pcs_err:
                mc_errors.append(None)

            # Append the data.
            else:
                mc_errors.append(spin.pcs_err[align_id])

        # Return the errors.
        return mc_errors


    def return_units(self, param):
        """Return a string representing the parameters units.

        @param param:   The name of the parameter to return the units string for.
        @type param:    str
        @return:        The parameter units string.
        @rtype:         str
        """

        # Average domain position.
        if param in ['ave_pos_x', 'ave_pos_y', 'ave_pos_z']:
            return 'Angstrom'
        if param in ['ave_pos_alpha', 'ave_pos_beta', 'ave_pos_gamma']:
            return 'rad'

        # Eigenframe angles.
        if param in ['eigen_alpha', 'eigen_beta', 'eigen_gamma', 'axis_theta', 'axis_phi']:
            return 'rad'

        # Cone angles.
        if param in ['cone_theta_x', 'cone_theta_y', 'cone_sigma_max', 'cone_theta']:
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
            # Not a parameter of the model.
            if param not in cdp.params:
                continue

            # Return the parameter array.
            if index == inc:
                setattr(cdp, param + "_err", error)

            # Increment.
            inc = inc + 1

        # Add some additional parameters.
        if cdp.model == 'iso cone, free rotor' and inc == index:
            setattr(cdp, 'cone_theta_err', error)



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

        # The model parameters.
        model_params = deepcopy(cdp.params)

        # Add some additional parameters.
        if cdp.model == 'iso cone, free rotor':
            param_names.append('cone_theta')
            model_params.append('cone_theta')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Loop over all the parameter names.
        for object_name in param_names:
            # Not a parameter of the model.
            if object_name not in model_params:
                continue

            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Test if the simulation object already exists.
            if hasattr(cdp, sim_object_name):
                raise RelaxError("Monte Carlo parameter values have already been set.")


        # Set the Monte Carlo parameter values.
        #######################################

        # Loop over all the data names.
        for object_name in param_names:
            # Not a parameter of the model.
            if object_name not in model_params:
                continue

            # Name for the simulation object.
            sim_object_name = object_name + '_sim'

            # Create the simulation object.
            setattr(cdp, sim_object_name, [])

            # Get the simulation object.
            sim_object = getattr(cdp, sim_object_name)

            # Loop over the simulations.
            for j in range(cdp.sim_number):
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
            for j in range(cdp.sim_number):
                # Copy and append the data.
                sim_object.append(deepcopy(getattr(cdp, object_name)))


    def sim_pack_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param data_id:     The data set as yielded by the base_data_loop() generator method.
        @type data_id:      list of str
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # The RDC data.
        if data_id[0] == 'rdc':
            # Unpack the set.
            data_type, spin_id1, spin_id2, align_id = data_id

            # Get the interatomic data container.
            interatom = return_interatom(spin_id1, spin_id2)

            # Initialise.
            if not hasattr(interatom, 'rdc_sim'):
                interatom.rdc_sim = {}
                    
            # Store the data structure.
            interatom.rdc_sim[align_id] = []
            for i in range(cdp.sim_number):
                interatom.rdc_sim[align_id].append(sim_data[i][0])

        # The PCS data.
        elif data_id[0] == 'pcs':
            # Unpack the set.
            data_type, spin_id, align_id = data_id

            # Get the spin container.
            spin = return_spin(spin_id)

            # Initialise.
            if not hasattr(spin, 'pcs_sim'):
                spin.pcs_sim = {}
                
            # Store the data structure.
            spin.pcs_sim[data_id[2]] = []
            for i in range(cdp.sim_number):
                spin.pcs_sim[data_id[2]].append(sim_data[i][0])


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        """

        # Parameter increment counter.
        inc = 0

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Loop over the parameters.
        for param in param_names:
            # Not a parameter of the model.
            if param not in cdp.params:
                continue

            # Return the parameter array.
            if index == inc:
                return getattr(cdp, param + "_sim")

            # Increment.
            inc = inc + 1

        # Add some additional parameters.
        if cdp.model == 'iso cone, free rotor' and inc == index:
            return getattr(cdp, 'cone_theta_sim')


    def sim_return_selected(self, model_info):
        """Return the array of selected simulation flags for the spin.

        @param model_info:  The model information originating from model_loop() (unused).
        @type model_info:   None
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Return the array.
        return cdp.select_sim
