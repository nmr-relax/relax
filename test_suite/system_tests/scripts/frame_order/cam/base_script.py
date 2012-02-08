###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

    def __init__(self, interpreter):
        """Execute the frame order analysis."""

        # Store the interpreter.
        self.interpreter = interpreter
        self.interpreter.populate_self()

        # The data path.
        self.data_path = BASE_PATH + self.directory

        # Pre-created set up.
        if self.load_state:
            # Reset the data store.
            self.interpreter.reset()

            # Load the save file.
            self.interpreter.state.load('frame_order', dir=self.data_path)

        # New set up.
        else:
            self.setup()

        # Optimise.
        self.optimisation()

        # Load the original structure.
        self.original_structure()

        # Domain transformation.
        self.transform()

        # Display in pymol.
        self.pymol_display()

        # Save the state.
        self.interpreter.state.save('devnull', force=True)


    def optimisation(self):
        """Optimise the frame order model."""

        # Set the number of numerical integration points.
        if hasattr(self, 'num_int_pts'):
            cdp.num_int_pts = self.num_int_pts

        # Check the minimum.
        if hasattr(self, 'ave_pos_alpha'):
            self.interpreter.value.set(val=self.ave_pos_alpha, param='ave_pos_alpha')
        if hasattr(self, 'ave_pos_beta'):
            self.interpreter.value.set(val=self.ave_pos_beta, param='ave_pos_beta')
        if hasattr(self, 'ave_pos_gamma'):
            self.interpreter.value.set(val=self.ave_pos_gamma, param='ave_pos_gamma')
        if hasattr(self, 'eigen_alpha'):
            self.interpreter.value.set(val=self.eigen_alpha, param='eigen_alpha')
        if hasattr(self, 'eigen_beta'):
            self.interpreter.value.set(val=self.eigen_beta, param='eigen_beta')
        if hasattr(self, 'eigen_gamma'):
            self.interpreter.value.set(val=self.eigen_gamma, param='eigen_gamma')
        if hasattr(self, 'axis_theta'):
            self.interpreter.value.set(val=self.axis_theta, param='axis_theta')
        if hasattr(self, 'axis_phi'):
            self.interpreter.value.set(val=self.axis_phi, param='axis_phi')
        if hasattr(self, 'cone_theta_x'):
            self.interpreter.value.set(val=self.cone_theta_x, param='cone_theta_x')
        if hasattr(self, 'cone_theta_y'):
            self.interpreter.value.set(val=self.cone_theta_y, param='cone_theta_y')
        if hasattr(self, 'cone_theta'):
            self.interpreter.value.set(val=self.cone_theta, param='cone_theta')
        if hasattr(self, 'cone_s1'):
            self.interpreter.value.set(val=self.cone_s1, param='cone_s1')
        if hasattr(self, 'cone_sigma_max'):
            self.interpreter.value.set(val=self.cone_sigma_max, param='cone_sigma_max')
        self.interpreter.calc()
        print("\nchi2: %s" % cdp.chi2)

        # Optimise.
        if hasattr(ds, 'flag_opt') and ds.flag_opt:
            self.interpreter.grid_search(inc=11)
            self.interpreter.minimise('simplex', constraints=False)

            # Test Monte Carlo simulations.
            self.interpreter.monte_carlo.setup(number=3)
            self.interpreter.monte_carlo.create_data()
            self.interpreter.monte_carlo.initial_values()
            self.interpreter.minimise('simplex', constraints=False)
            self.interpreter.eliminate()
            self.interpreter.monte_carlo.error_analysis()

        # Write the results.
        self.interpreter.results.write('devnull', dir=None, force=True)


    def original_structure(self):
        """Load the original structure into a dedicated data pipe."""

        # Create a special data pipe for the original rigid body position.
        self.interpreter.pipe.create(pipe_name='orig pos', pipe_type='frame order')

        # Load the structure.
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=BASE_PATH)


    def pymol_display(self):
        """Display the results in PyMOL."""

        # Switch back to the main data pipe.
        self.interpreter.pipe.switch('frame order')

        # Load the PDBs of the 2 domains.
        self.interpreter.structure.read_pdb('1J7O_1st_NH.pdb', dir=BASE_PATH)
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=BASE_PATH)

        # Create the cone PDB file.
        if self.cone:
            self.interpreter.frame_order.cone_pdb(file='devnull', force=True)

        # Set the domains.
        self.interpreter.frame_order.domain_to_pdb(domain='N', pdb='1J7O_1st_NH.pdb')
        self.interpreter.frame_order.domain_to_pdb(domain='C', pdb='1J7P_1st_NH_rot.pdb')


    def setup(self):
        """Optimise the frame order model."""

        # Create the data pipe.
        self.interpreter.pipe.create(pipe_name='frame order', pipe_type='frame order')

        # Read the structures.
        self.interpreter.structure.read_pdb('1J7O_1st_NH.pdb', dir=BASE_PATH, set_mol_name='N-dom')
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=BASE_PATH, set_mol_name='C-dom')

        # Load the spins.
        self.interpreter.structure.load_spins('@N')
        self.interpreter.structure.load_spins('@H')

        # Load the NH vectors.
        self.interpreter.structure.vectors(spin_id='@N', attached='H', ave=False)

        # Set the values needed to calculate the dipolar constant.
        self.interpreter.value.set(1.041 * 1e-10, 'r', spin_id="@N")
        self.interpreter.value.set('15N', 'heteronuc_type', spin_id="@N")
        self.interpreter.value.set('1H', 'proton_type', spin_id="@N")

        # Loop over the alignments.
        ln = ['dy', 'tb', 'tm', 'er']
        for i in range(len(ln)):
            # Load the RDCs.
            if not hasattr(ds, 'flag_rdc') or ds.flag_rdc:
                self.interpreter.rdc.read(align_id=ln[i], file='rdc_%s.txt'%ln[i], dir=self.data_path, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

            # The PCS.
            if not hasattr(ds, 'flag_pcs') or ds.flag_pcs:
                self.interpreter.pcs.read(align_id=ln[i], file='pcs_%s.txt'%ln[i], dir=self.data_path, res_num_col=2, spin_name_col=5, data_col=6, error_col=7)

            # The temperature and field strength.
            self.interpreter.temperature(id=ln[i], temp=303)
            self.interpreter.frq.set(id=ln[i], frq=900e6)

        # Load the N-domain tensors (the full tensors).
        self.interpreter.script(BASE_PATH + 'tensors.py')

        # Define the domains.
        self.interpreter.domain(id='N', spin_id=":1-78")
        self.interpreter.domain(id='C', spin_id=":80-148")

        # The tensor domains and reductions.
        full = ['Dy N-dom', 'Tb N-dom', 'Tm N-dom', 'Er N-dom']
        red =  ['Dy C-dom', 'Tb C-dom', 'Tm C-dom', 'Er C-dom']
        for i in range(len(full)):
            # Initialise the reduced tensor.
            self.interpreter.align_tensor.init(tensor=red[i], params=(0,0,0,0,0))

            # Set the domain info.
            self.interpreter.align_tensor.set_domain(tensor=full[i], domain='N')
            self.interpreter.align_tensor.set_domain(tensor=red[i], domain='C')

            # Specify which tensor is reduced.
            self.interpreter.align_tensor.reduction(full_tensor=full[i], red_tensor=red[i])

        # Select the model.
        self.interpreter.frame_order.select_model(self.model)

        # Set the reference domain.
        self.interpreter.frame_order.ref_domain('N')

        # Set the initial pivot point.
        pivot = array([ 37.254, 0.5, 16.7465])
        self.interpreter.frame_order.pivot(pivot, fix=True)

        # Set the paramagnetic centre.
        self.interpreter.paramag.centre(pos=[35.934, 12.194, -4.206])


    def transform(self):
        """Transform the domain to the average position."""

        # Switch back to the main data pipe.
        self.interpreter.pipe.switch('frame order')

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

        # Create a special data pipe for the average rigid body position.
        self.interpreter.pipe.create(pipe_name='ave pos', pipe_type='frame order')

        # Load the structure.
        self.interpreter.structure.read_pdb('1J7P_1st_NH_rot.pdb', dir=BASE_PATH)

        # Rotate all atoms.
        self.interpreter.structure.rotate(R=R, origin=pivot)

        # Write out the new PDB.
        self.interpreter.structure.write_pdb('devnull')
