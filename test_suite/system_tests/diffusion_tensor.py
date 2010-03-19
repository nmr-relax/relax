###############################################################################
#                                                                             #
# Copyright (C) 2006-2010 Edward d'Auvergne                                   #
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

# Python module imports.
import __main__
from math import pi
from numpy import array, float64, transpose, zeros
from os import sep
import sys

# relax module imports.
from base_classes import SystemTestCase
from data import Relax_data_store; ds = Relax_data_store()
from data.diff_tensor import DiffTensorSimList
from generic_fns.pipes import get_pipe
from maths_fns.rotation_matrix import euler_to_R_zyz
from relax_io import delete
from tempfile import mktemp


class Diffusion_tensor(SystemTestCase):
    """Class for testing various aspects specific to the diffusion tensor."""

    def setUp(self):
        """Function for initialising a spherical, spheroidal, and ellipsoidal diffusion tensor."""

        # Create three data pipes for spherical, spheroidal, and ellipsoidal diffusion.
        self.interpreter.pipe.create('sphere', 'mf')
        self.interpreter.pipe.create('spheroid', 'mf')
        self.interpreter.pipe.create('ellipsoid', 'mf')

        # Sphere tensor initialization.
        self.interpreter.pipe.switch('sphere')
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)
        self.interpreter.sequence.read(file='Ap4Aase.seq', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep, res_num_col=1, res_name_col=2)
        self.interpreter.diffusion_tensor.init(10e-9, fixed=True)
        self.tmpfile_sphere = mktemp()

        # Spheroid tensor initialization.
        self.interpreter.pipe.switch('spheroid')
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)
        self.interpreter.sequence.read(file='Ap4Aase.seq', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep, res_num_col=1, res_name_col=2)
        self.interpreter.diffusion_tensor.init((5e-09, -10000000., 1.6, 2.7), angle_units='rad', spheroid_type='oblate', fixed=True)
        self.tmpfile_spheroid = mktemp()

        # Ellipsoid tensor initialization.
        self.interpreter.pipe.switch('ellipsoid')
        self.interpreter.structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1)
        self.interpreter.sequence.read(file='Ap4Aase.seq', dir=__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep, res_num_col=1, res_name_col=2)
        self.interpreter.diffusion_tensor.init((9e-8, 5e6, 0.3, 60+360, 290, 100), fixed=False)
        self.tmpfile_ellipsoid = mktemp()


        # Some fake MC simulations (for the sphere).
        self.interpreter.pipe.switch('sphere')
        cdp.diff_tensor.tm_err = 10e-11
        cdp.diff_tensor.tm_sim = DiffTensorSimList('tm', cdp.diff_tensor, elements=5)
        tm_sim = [8.98e-8, 8.99e-8, 9.00e-7, 9.01e-8, 9.02e-8]
        for i in range(5):
            cdp.diff_tensor.tm_sim[i] = tm_sim[i]

        # Reset some values.
        cdp.diff_tensor.tm_sim[0] = 9.00e-8


        # Some fake MC simulations (for the spheroid).
        self.interpreter.pipe.switch('spheroid')

        # Initialise the data structures.
        cdp.diff_tensor.tm_sim = DiffTensorSimList('tm', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.Da_sim = DiffTensorSimList('Da', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.theta_sim = DiffTensorSimList('theta', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.phi_sim = DiffTensorSimList('phi', cdp.diff_tensor, elements=5)

        # Set some errors.
        cdp.diff_tensor.Da_err = 1000000
        cdp.diff_tensor.theta_err = 0.01
        cdp.diff_tensor.tm_err = 1e-11
        cdp.diff_tensor.phi_err = 0.01

        # The sim data.
        Da_sim = [-12000000., -11000000., -10000000., -9000000., -8000000.]
        theta_sim = [1.70, 1.65, 1.6, 1.55, 1.50]
        tm_sim = [5.4e-09, 4.8e-09, 5e-09, 5.4e-09, 5.8e-09]
        phi_sim = [2.5, 2.6, 2.7, 2.8, 100]
        for i in range(5):
            cdp.diff_tensor.Da_sim[i] = Da_sim[i]
            cdp.diff_tensor.theta_sim[i] = theta_sim[i]
            cdp.diff_tensor.tm_sim[i] = tm_sim[i]
            cdp.diff_tensor.phi_sim[i] = phi_sim[i]

        # Reset some values.
        cdp.diff_tensor.tm_sim[0] = 4.4e-9
        cdp.diff_tensor.phi_sim[4] = 2.9


        # Some fake MC simulations (for the ellipsoid).
        self.interpreter.pipe.switch('ellipsoid')

        # Initialise the data structures.
        cdp.diff_tensor.tm_sim = DiffTensorSimList('tm', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.Da_sim = DiffTensorSimList('Da', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.Dr_sim = DiffTensorSimList('Dr', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.alpha_sim = DiffTensorSimList('alpha', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.beta_sim = DiffTensorSimList('beta', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.gamma_sim = DiffTensorSimList('gamma', cdp.diff_tensor, elements=5)

        # The sim data.
        Dr_sim = [0.28, 0.29, 0.3, 0.31, 0.32]
        tm_sim = [8.97e-8, 8.99e-8, 9.00e-8, 9.01e-8, 9.02e-8]
        Da_sim = [5.02e6, 5.01e6, 5.00e6, 4.99e6, 4.98e6]
        alpha_sim = [80.0/360*2*pi, 70.0/360*2*pi, 60.0/360*2*pi, 50.0/360*2*pi, 40.0/360*2*pi]
        beta_sim = [295.0/360*2*pi, 292.5/360*2*pi, 290.0/360*2*pi, 289.5/360*2*pi, 288.0/360*2*pi]
        gamma_sim = [102.0/360*2*pi, 101.0/360*2*pi, 0, 99.0/360*2*pi, 98.0/360*2*pi]
        for i in range(5):
            cdp.diff_tensor.Dr_sim[i] = Dr_sim[i]
            cdp.diff_tensor.tm_sim[i] = tm_sim[i]
            cdp.diff_tensor.Da_sim[i] = Da_sim[i]
            cdp.diff_tensor.alpha_sim[i] = alpha_sim[i]
            cdp.diff_tensor.beta_sim[i] = beta_sim[i]
            cdp.diff_tensor.gamma_sim[i] = gamma_sim[i]

        # Reset some values.
        cdp.diff_tensor.tm_sim[0] = 8.98e-8
        cdp.diff_tensor.gamma_sim[2] = 100.0/360*2*pi


    def tearDown(self):
        """Reset the relax data storage object."""

        # Reset the relax data storage object.
        ds.__reset__()

        # Delete the temporary files.
        delete(self.tmpfile_sphere, fail=False)
        delete(self.tmpfile_spheroid, fail=False)
        delete(self.tmpfile_ellipsoid, fail=False)


    def check_ellipsoid(self, Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R):
        """Check if the ellipsoid in the cdp has the same values as given."""

        # Print outs.
        print("The relax data store diffusion tensor:\n\n%s\n\n" % cdp.diff_tensor)
        print("\nThe real tensor:\n%s" % D)
        print("\nThe tensor in relax:\n%s" % cdp.diff_tensor.tensor)
        print("\nThe real tensor (in eig frame):\n%s" % D_prime)
        print("\nThe tensor in relax (in eig frame):\n%s" % cdp.diff_tensor.tensor_diag)

        # Check the Euler angles.
        self.assertAlmostEqual(Dx, cdp.diff_tensor.Dx)
        self.assertAlmostEqual(Dy, cdp.diff_tensor.Dy)
        self.assertAlmostEqual(Dz, cdp.diff_tensor.Dz)
        self.assertAlmostEqual(Diso, cdp.diff_tensor.Diso)
        self.assertAlmostEqual(Da, cdp.diff_tensor.Da)
        self.assertAlmostEqual(Dr, cdp.diff_tensor.Dr)
        self.assertAlmostEqual(alpha, cdp.diff_tensor.alpha)
        self.assertAlmostEqual(beta, cdp.diff_tensor.beta)
        self.assertAlmostEqual(gamma, cdp.diff_tensor.gamma)

        # Check the elements.
        for i in range(3):
            for j in range(3):
                self.assertAlmostEqual(cdp.diff_tensor.tensor[i, j], D[i, j])
                self.assertAlmostEqual(cdp.diff_tensor.tensor_diag[i, j], D_prime[i, j])
                self.assertAlmostEqual(cdp.diff_tensor.rotation[i, j], R[i, j])


    def get_ellipsoid(self):
        """Return all the diffusion tensor info about the {Dx, Dy, Dz, alpha, beta, gamma} = {1e7, 2e7, 3e7, 1, 2, 0.5} ellipsoid tensor."""

        # The tensor info.
        Dx = 1e7
        Dy = 2e7
        Dz = 3e7
        Diso = 2e7
        Da = 1.5e7
        Dr = 1.0/3.0
        alpha = 1.0
        beta = 2.0
        gamma = 0.5

        # The actual tensor in the PDB frame.
        D = array([[ 22758858.4088357 ,  -7267400.1700938 ,   6272205.75829415],
                   [ -7267400.1700938 ,  17923072.3436445 ,   1284270.53726401],
                   [  6272205.75829415,   1284270.53726401,  19318069.2475198 ]], float64)

        # The tensor in the eigenframe.
        D_prime = zeros((3, 3), float64)
        D_prime[0, 0] = Dx
        D_prime[1, 1] = Dy
        D_prime[2, 2] = Dz

        # The rotation matrix.
        R = zeros((3, 3), float64)
        euler_to_R_zyz(gamma, beta, alpha, R)
        R = transpose(R)

        # Return the data.
        return Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R


    def test_copy(self):
        """The user function diffusion_tensor.copy()."""

        # Create three additional data pipes for copying the spherical, spheroidal, and ellipsoidal diffusion data.
        self.interpreter.pipe.create('sphere2', 'mf')
        self.interpreter.pipe.create('spheroid2', 'mf')
        self.interpreter.pipe.create('ellipsoid2', 'mf')

        # Copy the data.
        self.interpreter.diffusion_tensor.copy('sphere', 'sphere2')
        self.interpreter.diffusion_tensor.copy('spheroid', 'spheroid2')
        self.interpreter.diffusion_tensor.copy('ellipsoid', 'ellipsoid2')

        # Get the data pipes.
        sphere_pipe = get_pipe('sphere')
        sphere2_pipe = get_pipe('sphere2')

        # Check that this is indeed a copy.
        self.assertEqual(sphere2_pipe.diff_tensor.tm_sim[4], 9.02e-8)
        self.assertEqual(sphere2_pipe.diff_tensor.Diso_sim[4], 1/(6*9.02e-8))
        sphere_pipe.diff_tensor.tm_sim[4] = 8.88e-8
        self.assertEqual(sphere_pipe.diff_tensor.tm_sim[4], 8.88e-8)
        self.assertEqual(sphere_pipe.diff_tensor.Diso_sim[4], 1/(6*8.88e-8))
        self.assertEqual(sphere2_pipe.diff_tensor.tm_sim[4], 9.02e-8)
        self.assertEqual(sphere2_pipe.diff_tensor.Diso_sim[4], 1/(6*9.02e-8))


    def test_delete(self):
        """The user function diffusion_tensor.delete()."""

        # Delete the data.
        self.interpreter.pipe.switch('sphere')
        self.interpreter.diffusion_tensor.delete()
        self.interpreter.pipe.switch('spheroid')
        self.interpreter.diffusion_tensor.delete()
        self.interpreter.pipe.switch('ellipsoid')
        self.interpreter.diffusion_tensor.delete()


    def test_display(self):
        """The user function diffusion_tensor.display()."""

        # Display the data.
        self.interpreter.pipe.switch('sphere')
        self.interpreter.diffusion_tensor.display()
        self.interpreter.pipe.switch('spheroid')
        self.interpreter.diffusion_tensor.display()
        self.interpreter.pipe.switch('ellipsoid')
        self.interpreter.diffusion_tensor.display()


    def test_create_diff_tensor_pdb_sphere(self):
        """Test the user function structure.create_diff_tensor_pdb() for the sphere."""

        # First copy the data (a more vigorous copy test!).
        self.interpreter.pipe.copy('sphere', 'sphere2')
        self.interpreter.pipe.switch('sphere2')
        self.interpreter.diffusion_tensor.delete()
        self.interpreter.diffusion_tensor.copy('sphere', 'sphere2')

        # Create the diffusion tensor objects.
        self.interpreter.structure.create_diff_tensor_pdb(file=self.tmpfile_sphere)

        # Open the temp file.
        file = open(self.tmpfile_sphere)
        new_data = file.readlines()
        file.close()

        # Open the real file.
        file = open(__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'diff_tensors'+sep+'sphere.pdb')
        real_data = file.readlines()
        file.close()

        # Check the data.
        self.assertEqual(len(real_data), len(new_data))
        for i in range(len(real_data)):
            # Print the PDB line, for debugging.
            print((real_data[i][0:-1]))

            # Check the line.
            self.assertEqual(real_data[i], new_data[i])


    def test_create_diff_tensor_pdb_spheroid(self):
        """Test the user function structure.create_diff_tensor_pdb() for the spheroid."""

        # First copy the data (a more vigorous copy test!).
        self.interpreter.pipe.copy('spheroid', 'spheroid2')
        self.interpreter.pipe.switch('spheroid2')
        self.interpreter.diffusion_tensor.delete()
        self.interpreter.diffusion_tensor.copy('spheroid', 'spheroid2')

        # Create the diffusion tensor objects.
        self.interpreter.structure.create_diff_tensor_pdb(file=self.tmpfile_spheroid)

        # Open the temp file.
        file = open(self.tmpfile_spheroid)
        new_data = file.readlines()
        file.close()

        # Open the real file.
        file = open(__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'diff_tensors'+sep+'spheroid.pdb')
        real_data = file.readlines()
        file.close()

        # Check the data.
        self.assertEqual(len(real_data), len(new_data))
        for i in range(len(real_data)):
            # Print the PDB line, for debugging.
            print((real_data[i][0:-1]))

            # Check the line.
            self.assertEqual(real_data[i], new_data[i])


    def test_create_diff_tensor_pdb_ellipsoid(self):
        """Test the user function structure.create_diff_tensor_pdb() for the ellipsoid."""

        # First copy the data (a more vigorous copy test!).
        self.interpreter.pipe.copy('ellipsoid', 'ellipsoid2')
        self.interpreter.pipe.switch('ellipsoid2')
        self.interpreter.diffusion_tensor.delete()
        self.interpreter.diffusion_tensor.copy('ellipsoid', 'ellipsoid2')

        # Create the diffusion tensor objects.
        self.interpreter.structure.create_diff_tensor_pdb(file=self.tmpfile_ellipsoid, scale=1e-05)

        # Open the temp file.
        file = open(self.tmpfile_ellipsoid)
        new_data = file.readlines()
        file.close()

        # Open the real file.
        file = open(__main__.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'+sep+'diff_tensors'+sep+'ellipsoid.pdb')
        real_data = file.readlines()
        file.close()

        # Check the data.
        self.assertEqual(len(real_data), len(new_data))
        for i in range(len(real_data)):
            # Print the PDB line, for debugging.
            print((real_data[i][0:-1]))

            # Check the line.
            self.assertEqual(real_data[i], new_data[i])


    def test_init_ellipsoid_param_types_0(self):
        """Test the initialisation of the ellipsoid diffusion tensor using parameter set 0."""

        # Get the ellipsoid data.
        Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R = self.get_ellipsoid()

        # Create a new data pipe.
        self.interpreter.pipe.create('ellipsoid2', 'mf')

        # Tensor initialization.
        self.interpreter.diffusion_tensor.init((1/(6.0*Diso), Da, Dr, alpha, beta, gamma), param_types=0, angle_units='rad')

        # Check the ellipsoid.
        self.check_ellipsoid(Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R)


    def test_init_ellipsoid_param_types_1(self):
        """Test the initialisation of the ellipsoid diffusion tensor using parameter set 0."""

        # Get the ellipsoid data.
        Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R = self.get_ellipsoid()

        # Create a new data pipe.
        self.interpreter.pipe.create('ellipsoid2', 'mf')

        # Tensor initialization.
        self.interpreter.diffusion_tensor.init((Diso, Da, Dr, alpha, beta, gamma), param_types=1, angle_units='rad')

        # Check the ellipsoid.
        self.check_ellipsoid(Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R)


    def test_init_ellipsoid_param_types_2(self):
        """Test the initialisation of the ellipsoid diffusion tensor using parameter set 0."""

        # Get the ellipsoid data.
        Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R = self.get_ellipsoid()

        # Create a new data pipe.
        self.interpreter.pipe.create('ellipsoid2', 'mf')

        # Tensor initialization.
        self.interpreter.diffusion_tensor.init((Dx, Dy, Dz, alpha, beta, gamma), param_types=2, angle_units='rad')

        # Check the ellipsoid.
        self.check_ellipsoid(Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R)


    def test_init_ellipsoid_param_types_3(self):
        """Test the initialisation of the ellipsoid diffusion tensor using parameter set 0."""

        # Get the ellipsoid data.
        Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R = self.get_ellipsoid()

        # Create a new data pipe.
        self.interpreter.pipe.create('ellipsoid2', 'mf')

        # Tensor initialization.
        self.interpreter.diffusion_tensor.init((D[0, 0], D[1, 1], D[2, 2], D[0, 1], D[0, 2], D[1, 2]), param_types=3)

        # Check the ellipsoid.
        self.check_ellipsoid(Dx, Dy, Dz, Diso, Da, Dr, alpha, beta, gamma, D, D_prime, R)


    def test_opt_ellipsoid(self):
        """Check that the ellipsoid diffusion tensor optimisation functions correctly."""

        # Reset the relax data storage object.
        ds.__reset__()

        # The diffusion type (used by the script).
        ds.diff_type = 'ellipsoid'

        # Execute the script.
        self.interpreter.run(script_file=__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'diff_tensor'+sep+'tensor_opt.py')


    def test_opt_sphere(self):
        """Check that the sphere diffusion tensor optimisation functions correctly."""

        # Reset the relax data storage object.
        ds.__reset__()

        # The diffusion type (used by the script).
        ds.diff_type = 'sphere'

        # Execute the script.
        self.interpreter.run(script_file=__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'diff_tensor'+sep+'tensor_opt.py')


    def test_opt_spheroid(self):
        """Check that the spheroid diffusion tensor optimisation functions correctly."""

        # Reset the relax data storage object.
        ds.__reset__()

        # The diffusion type (used by the script).
        ds.diff_type = 'spheroid'

        # Execute the script.
        self.interpreter.run(script_file=__main__.install_path + sep+'test_suite'+sep+'system_tests'+sep+'scripts'+sep+'diff_tensor'+sep+'tensor_opt.py')
