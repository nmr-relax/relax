###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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
from numpy import array, float64, transpose, zeros
from os import sep

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from maths_fns.rotation_matrix import euler_to_R_zyz
from status import Status; status = Status()


# Some variables.
BASE_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'frame_order'+sep+'cam'+sep


class Base_script:
    # Class variables.
    cone = True
    load_state = False

    def __init__(self, exec_fn):
        """Execute the frame order analysis."""

        # Alias the user function executor method.
        self._execute_uf = exec_fn

        # The data path.
        self.data_path = BASE_PATH + self.directory

        # Pre-created set up.
        if self.load_state:
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


    def optimisation(self):
        """Optimise the frame order model."""

        # Set the number of numerical integration points.
        if hasattr(self, 'num_int_pts'):
            self._execute_uf(uf_name='frame_order.num_int_pts', num=self.num_int_pts)

        # Check the minimum.
        if hasattr(self, 'ave_pos_alpha'):
            self._execute_uf(uf_name='value.set', val=self.ave_pos_alpha, param='ave_pos_alpha')
        if hasattr(self, 'ave_pos_beta'):
            self._execute_uf(uf_name='value.set', val=self.ave_pos_beta, param='ave_pos_beta')
        if hasattr(self, 'ave_pos_gamma'):
            self._execute_uf(uf_name='value.set', val=self.ave_pos_gamma, param='ave_pos_gamma')
        if hasattr(self, 'eigen_alpha'):
            self._execute_uf(uf_name='value.set', val=self.eigen_alpha, param='eigen_alpha')
        if hasattr(self, 'eigen_beta'):
            self._execute_uf(uf_name='value.set', val=self.eigen_beta, param='eigen_beta')
        if hasattr(self, 'eigen_gamma'):
            self._execute_uf(uf_name='value.set', val=self.eigen_gamma, param='eigen_gamma')
        if hasattr(self, 'axis_theta'):
            self._execute_uf(uf_name='value.set', val=self.axis_theta, param='axis_theta')
        if hasattr(self, 'axis_phi'):
            self._execute_uf(uf_name='value.set', val=self.axis_phi, param='axis_phi')
        if hasattr(self, 'cone_theta_x'):
            self._execute_uf(uf_name='value.set', val=self.cone_theta_x, param='cone_theta_x')
        if hasattr(self, 'cone_theta_y'):
            self._execute_uf(uf_name='value.set', val=self.cone_theta_y, param='cone_theta_y')
        if hasattr(self, 'cone_theta'):
            self._execute_uf(uf_name='value.set', val=self.cone_theta, param='cone_theta')
        if hasattr(self, 'cone_s1'):
            self._execute_uf(uf_name='value.set', val=self.cone_s1, param='cone_s1')
        if hasattr(self, 'cone_sigma_max'):
            self._execute_uf(uf_name='value.set', val=self.cone_sigma_max, param='cone_sigma_max')
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
        if self.load_state:
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
        if self.cone:
            self._execute_uf(uf_name='frame_order.cone_pdb', file='devnull', force=True)

        # Set the domains.
        self._execute_uf(uf_name='frame_order.domain_to_pdb', domain='N', pdb='1J7O_1st_NH.pdb')
        self._execute_uf(uf_name='frame_order.domain_to_pdb', domain='C', pdb='1J7P_1st_NH_rot.pdb')


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
        self._execute_uf(uf_name='dipole_pair.define', spin_id1='@N', spin_id2='@H', direct_bond=True)
        self._execute_uf(uf_name='dipole_pair.set_dist', spin_id1='@N', spin_id2='@H', ave_dist=1.041 * 1e-10)
        self._execute_uf(uf_name='dipole_pair.unit_vectors')

        # Loop over the alignments.
        ln = ['dy', 'tb', 'tm', 'er']
        for i in range(len(ln)):
            # Load the RDCs.
            if not hasattr(status, 'flag_rdc') or status.flag_rdc:
                self._execute_uf(uf_name='rdc.read', align_id=ln[i], file='rdc_%s.txt'%ln[i], dir=self.data_path, spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4)

            # The PCS.
            if not hasattr(status, 'flag_pcs') or status.flag_pcs:
                self._execute_uf(uf_name='pcs.read', align_id=ln[i], file='pcs_%s.txt'%ln[i], dir=self.data_path, mol_name_col=1, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

            # The temperature and field strength.
            self._execute_uf(uf_name='temperature', id=ln[i], temp=303)
            self._execute_uf(uf_name='frq.set', id=ln[i], frq=900e6)

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
        self._execute_uf(uf_name='frame_order.select_model', model=self.model)

        # Set the reference domain.
        self._execute_uf(uf_name='frame_order.ref_domain', ref='N')

        # Set the initial pivot point.
        pivot = array([ 37.254, 0.5, 16.7465])
        self._execute_uf(uf_name='frame_order.pivot', pivot=pivot, fix=True)

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
        pivot = cdp.pivot

        # Delete the data pipe (if a loaded state has been used).
        if self.load_state:
            self._execute_uf(uf_name='pipe.delete', pipe_name='ave pos')

        # Create a special data pipe for the average rigid body position.
        self._execute_uf(uf_name='pipe.create', pipe_name='ave pos', pipe_type='frame order')

        # Load the structure.
        self._execute_uf(uf_name='structure.read_pdb', file='1J7P_1st_NH_rot.pdb', dir=BASE_PATH)

        # Rotate all atoms.
        self._execute_uf(uf_name='structure.rotate', R=R, origin=pivot)

        # Write out the new PDB.
        self._execute_uf(uf_name='structure.write_pdb', file='devnull')
