###############################################################################
#                                                                             #
# Copyright (C) 2012-2014 Edward d'Auvergne                                   #
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
"""Base script for the optimisation of the rigid frame order test models."""

# Python module imports.
from numpy import array, cross, float32, float64, zeros
from numpy.linalg import norm
from os import F_OK, access, sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.geometry.coord_transform import spherical_to_cartesian
from lib.geometry.lines import closest_point_ax
from lib.geometry.vectors import vector_angle_normal
from specific_analyses.frame_order.variables import MODEL_FREE_ROTOR, MODEL_ROTOR
from status import Status; status = Status()


# Some variables.
BASE_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep


class Base_script:
    # Flags for turning certain features on or off.
    CONE = True
    LOAD_STATE = False

    # The directory containing the data files.
    DIRECTORY = None

    # The frame order model.
    MODEL = None

    # The number of integration points.
    NUM_INT_PTS = 100

    # The model parameters.
    PIVOT_DISP = None
    AVE_POS_X, AVE_POS_Y, AVE_POS_Z = [ -21.269217407269576,   -3.122610661328414,   -2.400652421655998]
    AVE_POS_ALPHA, AVE_POS_BETA, AVE_POS_GAMMA = [5.623469076122531, 0.435439405668396, 5.081265529106499]
    AXIS_THETA = None
    AXIS_PHI = None
    AXIS_ALPHA = None
    EIGEN_ALPHA = None
    EIGEN_BETA = None
    EIGEN_GAMMA = None
    CONE_THETA = None
    CONE_S1 = None
    CONE_THETA_X = None
    CONE_THETA_Y = None
    CONE_SIGMA_MAX = None
    AXIS_THETA2 = None
    AXIS_PHI2 = None
    CONE_SIGMA_MAX_2 = None

    # The pivot points.
    PIVOT = array([ 37.254, 0.5, 16.7465], float32)

    # The CoM - for use in the rotor models.
    COM = array([44.737253525507697, -1.1684805963699558, 14.072436716990133], float32)


    def __init__(self, exec_fn):
        """Execute the frame order analysis."""

        # Parameter conversions.
        if self.MODEL in [MODEL_ROTOR, MODEL_FREE_ROTOR]:
            self.convert_rotor(theta=self.AXIS_THETA, phi=self.AXIS_PHI, pivot=self.PIVOT, com=self.COM)
            self.AXIS_THETA = None
            self.AXIS_PHI = None

        # Alias the user function executor method.
        self._execute_uf = exec_fn

        # The data path.
        self.data_path = BASE_PATH + self.DIRECTORY

        # Pre-created set up.
        if self.LOAD_STATE:
            self.setup_state()

        # New set up.
        else:
            self.setup_full()

        # Optimise.
        self.optimisation()

        # Display in pymol.
        self.pymol_display()

        # Save the state.
        self._execute_uf(uf_name='state.save', state='devnull', force=True)


    def convert_rotor(self, theta=None, phi=None, pivot=None, com=None):
        """Convert the rotor axis spherical angles to the axis alpha notation.

        The pivot will be shifted to the point on the axis closest to the CoM, and the alpha angle set.


        @keyword theta: The polar spherical angle.
        @type theta:    float
        @keyword phi:   The azimuthal spherical angle.
        @type phi:      float
        @keyword pivot: The pivot point on the rotation axis.
        @type pivot:    numpy rank-1 3D array
        @keyword com:   The pivot point on the rotation axis.
        @type com:      numpy rank-1 3D array
        """

        # The axis.
        axis = zeros(3, float64)
        spherical_to_cartesian([1.0, theta, phi], axis)

        # Reset the pivot to the closest point on the line to the CoM (shift the pivot).
        self.PIVOT = closest_point_ax(line_pt=pivot, axis=axis, point=com)

        # The CoM-pivot unit vector (for the shifted pivot).
        piv_com = com - self.PIVOT
        piv_com = piv_com / norm(piv_com)

        # The vector perpendicular to the CoM-pivot vector.
        z_axis = array([0, 0, 1], float64)
        perp_vect = cross(piv_com, z_axis)
        perp_vect = perp_vect / norm(perp_vect)

        # Set the alpha angle (the angle between the perpendicular vector and the axis).
        self.AXIS_ALPHA = vector_angle_normal(perp_vect, axis, piv_com)


    def optimisation(self):
        """Optimise the frame order model."""

        # Set up the Sobol' sequence.
        if self.NUM_INT_PTS != None:
            self._execute_uf(uf_name='frame_order.sobol_setup', max_num=self.NUM_INT_PTS, oversample=1)

        # Set the parameter values.
        params = [
            'pivot_disp',
            'ave_pos_x',
            'ave_pos_y',
            'ave_pos_z',
            'ave_pos_alpha',
            'ave_pos_beta',
            'ave_pos_gamma',
            'eigen_alpha',
            'eigen_beta',
            'eigen_gamma',
            'axis_theta',
            'axis_phi',
            'axis_alpha',
            'cone_theta_x',
            'cone_theta_y',
            'cone_theta',
            'cone_s1',
            'cone_sigma_max',
            'cone_sigma_max_2'
        ]
        for param in params:
            # Variable name.
            var_name = param.upper()

            # Not set.
            val = getattr(self, var_name)
            if val == None:
                continue

            # Set the value.
            self._execute_uf(uf_name='value.set', val=val, param=param)

        # Calculate and show the chi-squared value.
        self._execute_uf(uf_name='minimise.calculate')
        print("\nchi2: %s" % cdp.chi2)

        # Optimise.
        if hasattr(status, 'flag_opt') and status.flag_opt:
            self._execute_uf(uf_name='minimise.grid_search', inc=1)
            self._execute_uf(uf_name='minimise.execute', min_algor='simplex', constraints=True, max_iter=1)

            # Test Monte Carlo simulations.
            self._execute_uf(uf_name='monte_carlo.setup', number=3)
            self._execute_uf(uf_name='monte_carlo.create_data')
            self._execute_uf(uf_name='monte_carlo.initial_values')
            self._execute_uf(uf_name='minimise', min_algor='simplex', constraints=True, max_iter=1)
            self._execute_uf(uf_name='eliminate')
            self._execute_uf(uf_name='monte_carlo.error_analysis')

        # Write the results.
        self._execute_uf(uf_name='results.write', file='devnull', dir=None, force=True)


    def pymol_display(self):
        """Display the results in PyMOL."""

        # Create the PDB representation.
        self._execute_uf(uf_name='frame_order.pdb_model', ave_pos='devnull', rep='devnull', dist='devnull', force=True)


    def setup_full(self):
        """Set up the frame order model data from scratch."""

        # Create the data pipe.
        self._execute_uf(uf_name='pipe.create', pipe_name='frame order', pipe_type='frame order')

        # Read the structures.
        self._execute_uf(uf_name='structure.read_pdb', file='1J7O_1st_NH.pdb', dir=BASE_PATH, set_mol_name='N-dom')
        self._execute_uf(uf_name='structure.read_pdb', file='1J7P_1st_NH_rot.pdb', dir=BASE_PATH, set_mol_name='C-dom')

        # Set up the 15N and 1H spins.
        self._execute_uf(uf_name='structure.load_spins', spin_id='@N', ave_pos=False)
        self._execute_uf(uf_name='structure.load_spins', spin_id='@H', ave_pos=False)
        self._execute_uf(uf_name='spin.isotope', isotope='15N', spin_id='@N')
        self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H')

        # Define the magnetic dipole-dipole relaxation interaction.
        self._execute_uf(uf_name='interatom.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
        self._execute_uf(uf_name='interatom.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
        self._execute_uf(uf_name='interatom.unit_vectors')

        # Loop over the alignments.
        ln = ['dy', 'tb', 'tm', 'er']
        for i in range(len(ln)):
            # Load the RDCs (if present).
            if (not hasattr(status, 'flag_rdc') or status.flag_rdc) and access(self.data_path+sep+'rdc_%s.txt'%ln[i], F_OK):
                self._execute_uf(uf_name='rdc.read', align_id=ln[i], file='rdc_%s.txt'%ln[i], dir=self.data_path, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

            # The PCS (if present).
            if not hasattr(status, 'flag_pcs') or status.flag_pcs and access(self.data_path+sep+'pcs_%s.txt'%ln[i], F_OK):
                self._execute_uf(uf_name='pcs.read', align_id=ln[i], file='pcs_%s_subset.txt'%ln[i], dir=self.data_path, mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

            # The temperature and field strength.
            self._execute_uf(uf_name='spectrometer.temperature', id=ln[i], temp=303)
            self._execute_uf(uf_name='spectrometer.frequency', id=ln[i], frq=900e6)

        # Load the N-domain tensors (the full tensors).
        self._execute_uf(uf_name='script', file=BASE_PATH + 'tensors.py')

        # Define the domains.
        self._execute_uf(uf_name='domain', id='N', spin_id="#N-dom")
        self._execute_uf(uf_name='domain', id='C', spin_id="#C-dom")

        # The tensor domains and reductions.
        full = ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']
        red =  ['Dy C-dom', 'Tb C-dom', 'Tm C-dom', 'Er C-dom']
        ids =  ['dy', 'tb', 'tm', 'er']
        for i in range(len(full)):
            # Initialise the reduced tensor.
            self._execute_uf(uf_name='align_tensor.init', tensor=red[i], align_id=ids[i], params=(0, 0, 0, 0, 0))

            # Set the domain info.
            self._execute_uf(uf_name='align_tensor.set_domain', tensor=full[i], domain='N')
            self._execute_uf(uf_name='align_tensor.set_domain', tensor=red[i], domain='C')

            # Specify which tensor is reduced.
            self._execute_uf(uf_name='align_tensor.reduction', full_tensor=full[i], red_tensor=red[i])

        # Select the model.
        self._execute_uf(uf_name='frame_order.select_model', model=self.MODEL)

        # Set the reference domain.
        self._execute_uf(uf_name='frame_order.ref_domain', ref='N')

        # Set the initial pivot point - fixed when optimising, unfixed otherwise to check different code paths.
        fix = False
        if hasattr(status, 'flag_opt') and status.flag_opt:
            fix = True
        self._execute_uf(uf_name='frame_order.pivot', pivot=self.PIVOT, fix=fix)

        # Set the paramagnetic centre.
        self._execute_uf(uf_name='paramag.centre', pos=[35.934, 12.194, -4.206])


    def setup_state(self):
        """Set up the frame order model data from a saved state."""

        # Load the save file.
        self._execute_uf(uf_name='state.load', state='frame_order', dir=self.data_path)

        # Delete the RDC and PCS data as needed.
        if hasattr(status, 'flag_rdc') and not status.flag_rdc:
            self._execute_uf(uf_name='rdc.delete')
        if hasattr(status, 'flag_pcs') and not status.flag_pcs:
            self._execute_uf(uf_name='pcs.delete')
