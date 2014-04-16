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
from numpy import array, cross, float32, float64, transpose, zeros
from numpy.linalg import norm
from os import F_OK, access, sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from lib.geometry.coord_transform import spherical_to_cartesian
from lib.geometry.lines import closest_point_ax
from lib.geometry.rotations import euler_to_R_zyz, reverse_euler_zyz
from lib.geometry.vectors import vector_angle
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
    NUM_INT_PTS = 50

    # The model parameters.
    AVE_POS_ALPHA, AVE_POS_BETA, AVE_POS_GAMMA = reverse_euler_zyz(4.3434999280669997, 0.43544332764249905, 3.8013235235956007)
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
    CONE_SIGMA_MAX2 = None

    # The pivot points.
    PIVOT = array([ 37.254, 0.5, 16.7465], float32)
    PIVOT2 = None

    # The CoM - for use in the rotor models.
    COM = array([44.737253525507697, -1.1684805963699558, 14.072436716990133], float32)


    def __init__(self, exec_fn):
        """Execute the frame order analysis."""

        # Parameter conversions.
        if self.MODEL in ['rotor', 'free rotor']:
            self.convert_rotor(theta=self.AXIS_THETA, phi=self.AXIS_PHI, pivot=self.PIVOT, com=self.COM)

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

        # Load the original structure.
        self.original_structure()

        # Domain transformation.
        self.transform()

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
        self.AXIS_ALPHA = vector_angle(perp_vect, axis, piv_com)


    def optimisation(self):
        """Optimise the frame order model."""

        # Set the number of numerical integration points.
        if self.NUM_INT_PTS != None:
            self._execute_uf(uf_name='frame_order.num_int_pts', num=self.NUM_INT_PTS)

        # Check the minimum.
        if self.MODEL not in ['free rotor', 'iso cone, free rotor']:
            if self.AVE_POS_ALPHA != None:
                self._execute_uf(uf_name='value.set', val=self.AVE_POS_ALPHA, param='ave_pos_alpha')
            if self.AVE_POS_BETA != None:
                self._execute_uf(uf_name='value.set', val=self.AVE_POS_BETA, param='ave_pos_beta')
            if self.AVE_POS_GAMMA != None:
                self._execute_uf(uf_name='value.set', val=self.AVE_POS_GAMMA, param='ave_pos_gamma')
        if self.EIGEN_ALPHA != None:
            self._execute_uf(uf_name='value.set', val=self.EIGEN_ALPHA, param='eigen_alpha')
        if self.EIGEN_BETA != None:
            self._execute_uf(uf_name='value.set', val=self.EIGEN_BETA, param='eigen_beta')
        if self.EIGEN_GAMMA != None:
            self._execute_uf(uf_name='value.set', val=self.EIGEN_GAMMA, param='eigen_gamma')
        if self.AXIS_THETA != None:
            self._execute_uf(uf_name='value.set', val=self.AXIS_THETA, param='axis_theta')
        if self.AXIS_PHI != None:
            self._execute_uf(uf_name='value.set', val=self.AXIS_PHI, param='axis_phi')
        if self.AXIS_ALPHA != None:
            self._execute_uf(uf_name='value.set', val=self.AXIS_ALPHA, param='axis_alpha')
        if self.CONE_THETA_X != None:
            self._execute_uf(uf_name='value.set', val=self.CONE_THETA_X, param='cone_theta_x')
        if self.CONE_THETA_Y != None:
            self._execute_uf(uf_name='value.set', val=self.CONE_THETA_Y, param='cone_theta_y')
        if self.CONE_THETA != None:
            self._execute_uf(uf_name='value.set', val=self.CONE_THETA, param='cone_theta')
        if self.CONE_S1 != None:
            self._execute_uf(uf_name='value.set', val=self.CONE_S1, param='cone_s1')
        if self.CONE_SIGMA_MAX != None:
            self._execute_uf(uf_name='value.set', val=self.CONE_SIGMA_MAX, param='cone_sigma_max')
        self._execute_uf(uf_name='calc')
        print("\nchi2: %s" % cdp.chi2)

        # Optimise.
        if hasattr(status, 'flag_opt') and status.flag_opt:
            #self._execute_uf(uf_name='grid_search', inc=11)
            self._execute_uf(uf_name='minimise', min_algor='simplex', constraints=False, max_iter=10)

            # Test Monte Carlo simulations.
            self._execute_uf(uf_name='monte_carlo.setup', number=3)
            self._execute_uf(uf_name='monte_carlo.create_data')
            self._execute_uf(uf_name='monte_carlo.initial_values')
            self._execute_uf(uf_name='minimise', min_algor='simplex', constraints=False, max_iter=10)
            self._execute_uf(uf_name='eliminate')
            self._execute_uf(uf_name='monte_carlo.error_analysis')

        # Write the results.
        self._execute_uf(uf_name='results.write', file='devnull', dir=None, force=True)


    def original_structure(self):
        """Load the original structure into a dedicated data pipe."""

        # Delete the data pipe (if a loaded state has been used).
        if self.LOAD_STATE:
            self._execute_uf(uf_name='pipe.delete', pipe_name='orig pos')

        # Create a special data pipe for the original rigid body position.
        self._execute_uf(uf_name='pipe.create', pipe_name='orig pos', pipe_type='frame order')

        # Load the structure.
        self._execute_uf(uf_name='structure.read_pdb', file='1J7P_1st_NH_rot.pdb', dir=BASE_PATH)


    def pymol_display(self):
        """Display the results in PyMOL."""

        # Switch back to the main data pipe.
        self._execute_uf(uf_name='pipe.switch', pipe_name='frame order')

        # Load the PDBs of the 2 domains.
        self._execute_uf(uf_name='structure.read_pdb', file='1J7O_1st_NH.pdb', dir=BASE_PATH)
        self._execute_uf(uf_name='structure.read_pdb', file='1J7P_1st_NH_rot.pdb', dir=BASE_PATH)

        # Create the cone PDB file.
        if self.CONE:
            self._execute_uf(uf_name='frame_order.pdb_model', ave_pos_file='devnull', rep_file='devnull', dist_file='devnull', force=True)


    def setup_full(self):
        """Set up the frame order model data from scratch."""

        # Create the data pipe.
        self._execute_uf(uf_name='pipe.create', pipe_name='frame order', pipe_type='frame order')

        # Read the structures.
        self._execute_uf(uf_name='structure.read_pdb', file='1J7O_1st_NH.pdb', dir=BASE_PATH, set_mol_name='N-dom')
        self._execute_uf(uf_name='structure.read_pdb', file='1J7P_1st_NH_rot.pdb', dir=BASE_PATH, set_mol_name='C-dom')

        # Solve the {a, b, g} -> {0, b', g'} angle conversion problem in the rotor models by pre-rotating the domain!
        if self.MODEL in ['free rotor', 'iso cone, free rotor']:
            # The rotation matrix.
            R = zeros((3, 3), float64)
            euler_to_R_zyz(self.AVE_POS_ALPHA, self.AVE_POS_BETA, self.AVE_POS_GAMMA, R)

            # Rotate.
            self._execute_uf(uf_name='structure.rotate', R=R, atom_id='#C-dom')

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
        self._execute_uf(uf_name='domain', id='N', spin_id=":1-78")
        self._execute_uf(uf_name='domain', id='C', spin_id=":80-148")

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

        # Set up the mechanics of the displacement to the average domain position.
        self._execute_uf(uf_name='frame_order.average_position', pivot='motional', translation=False)

        # Set the reference domain.
        self._execute_uf(uf_name='frame_order.ref_domain', ref='N')

        # Set the initial pivot point(s).
        self._execute_uf(uf_name='frame_order.pivot', pivot=self.PIVOT, fix=True)
        if self.PIVOT2 != None:
            self._execute_uf(uf_name='frame_order.pivot', pivot=self.PIVOT2, order=2, fix=True)

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


    def transform(self):
        """Transform the domain to the average position."""

        # Switch back to the main data pipe.
        self._execute_uf(uf_name='pipe.switch', pipe_name='frame order')

        # The rotation matrix.
        R = zeros((3, 3), float64)
        if hasattr(cdp, 'ave_pos_alpha'):
            euler_to_R_zyz(cdp.ave_pos_alpha, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        else:
            euler_to_R_zyz(0.0, cdp.ave_pos_beta, cdp.ave_pos_gamma, R)
        print("Rotation matrix:\n%s\n" % R)
        R = transpose(R)
        print("Inverted rotation:\n%s\n" % R)
        pivot = array([cdp.pivot_x, cdp.pivot_y, cdp.pivot_z])

        # Delete the data pipe (if a loaded state has been used).
        if self.LOAD_STATE:
            self._execute_uf(uf_name='pipe.delete', pipe_name='ave pos')

        # Create a special data pipe for the average rigid body position.
        self._execute_uf(uf_name='pipe.create', pipe_name='ave pos', pipe_type='frame order')

        # Load the structure.
        self._execute_uf(uf_name='structure.read_pdb', file='1J7P_1st_NH_rot.pdb', dir=BASE_PATH)

        # Rotate all atoms.
        self._execute_uf(uf_name='structure.rotate', R=R, origin=pivot)

        # Write out the new PDB.
        self._execute_uf(uf_name='structure.write_pdb', file='devnull')
