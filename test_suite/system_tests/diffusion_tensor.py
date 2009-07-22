###############################################################################
#                                                                             #
# Copyright (C) 2006-2009 Edward d'Auvergne                                   #
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
from math import pi
from os import remove
from unittest import TestCase
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.diff_tensor import DiffTensorSimList
from generic_fns.pipes import get_pipe
from tempfile import mktemp


class Diffusion_tensor(TestCase):
    """Class for testing various aspects specific to the diffusion tensor."""

    def setUp(self):
        """Function for initialising a spherical, spheroidal, and ellipsoidal diffusion tensor."""

        # Create three data pipes for spherical, spheroidal, and ellipsoidal diffusion.
        self.relax.interpreter._Pipe.create('sphere', 'mf')
        self.relax.interpreter._Pipe.create('spheroid', 'mf')
        self.relax.interpreter._Pipe.create('ellipsoid', 'mf')

        # Sphere tensor initialization.
        self.relax.interpreter._Pipe.switch('sphere')
        self.relax.interpreter._Structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + '/test_suite/shared_data/structures', read_model=1)
        self.relax.interpreter._Sequence.read(file='Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/shared_data/')
        self.relax.interpreter._Diffusion_tensor.init(10e-9, fixed=True)
        self.tmpfile_sphere = mktemp()

        # Spheroid tensor initialization.
        self.relax.interpreter._Pipe.switch('spheroid')
        self.relax.interpreter._Structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + '/test_suite/shared_data/structures', read_model=1)
        self.relax.interpreter._Sequence.read(file='Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/shared_data/')
        self.relax.interpreter._Diffusion_tensor.init((3.5457744201817697e-09, -10027622.7828162, 1.6721590102675075, 2.7163466955672457), angle_units='rad', spheroid_type='oblate', fixed=True)
        self.tmpfile_spheroid = mktemp()

        # Ellipsoid tensor initialization.
        self.relax.interpreter._Pipe.switch('ellipsoid')
        self.relax.interpreter._Structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + '/test_suite/shared_data/structures', read_model=1)
        self.relax.interpreter._Sequence.read(file='Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/shared_data/')
        self.relax.interpreter._Diffusion_tensor.init((9e-8, 5e6, 0.3, 60+360, 290, 100), fixed=False)
        self.tmpfile_ellipsoid = mktemp()

        # Some fake MC simulations (for the sphere).
        self.relax.interpreter._Pipe.switch('sphere')
        cdp = get_pipe()
        cdp.diff_tensor.tm_err = 10e-11
        cdp.diff_tensor.tm_sim = DiffTensorSimList('tm', cdp.diff_tensor, elements=5)
        tm_sim = [8.98e-8, 8.99e-8, 9.00e-8, 9.01e-8, 9.02e-8]
        for i in range(5):
            cdp.diff_tensor.tm_sim[i] = tm_sim[i]


        # Some fake MC simulations (for the spheroid).
        self.relax.interpreter._Pipe.switch('spheroid')
        cdp = get_pipe()

        # Initialise the data structures.
        cdp.diff_tensor.tm_sim = DiffTensorSimList('tm', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.Da_sim = DiffTensorSimList('Da', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.theta_sim = DiffTensorSimList('theta', cdp.diff_tensor, elements=5)
        cdp.diff_tensor.phi_sim = DiffTensorSimList('phi', cdp.diff_tensor, elements=5)

        # Set some errors.
        cdp.diff_tensor.Da_err = 765986.42128728074
        cdp.diff_tensor.theta_err = 0.00068021155978203692
        cdp.diff_tensor.tm_err = 1.7695846045376088e-11
        cdp.diff_tensor.phi_err = 0.00078453847526795194

        # The sim data.
        Da_sim = [-10090112.175, -9922709.9518, -10118143.631, -10016815.789, -10009684.028]
        theta_sim = [1.67256128318, 1.67099947873, 1.67255937685, 1.67210656881, 1.6715284024]
        tm_sim = [3.5314969337e-09, 3.56919594167e-09, 3.52348845053e-09, 3.54505145128e-09, 3.5502948504e-09]
        phi_sim = [2.71811219172, 2.7177223339, 2.71817620501, 2.71783544462, 2.71625856632]
        for i in range(5):
            cdp.diff_tensor.Da_sim[i] = Da_sim[i]
            cdp.diff_tensor.theta_sim[i] = theta_sim[i]
            cdp.diff_tensor.tm_sim[i] = tm_sim[i]
            cdp.diff_tensor.phi_sim[i] = phi_sim[i]


        # Some fake MC simulations (for the ellipsoid).
        self.relax.interpreter._Pipe.switch('ellipsoid')
        cdp = get_pipe()

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
        try:
            remove(self.tmpfile_sphere)
            remove(self.tmpfile_spheroid)
            remove(self.tmpfile_ellipsoid)
        except OSError:
            pass


    def test_copy(self):
        """The user function diffusion_tensor.copy()."""

        # Create three additional data pipes for copying the spherical, spheroidal, and ellipsoidal diffusion data.
        self.relax.interpreter._Pipe.create('sphere2', 'mf')
        self.relax.interpreter._Pipe.create('spheroid2', 'mf')
        self.relax.interpreter._Pipe.create('ellipsoid2', 'mf')

        # Copy the data.
        self.relax.interpreter._Diffusion_tensor.copy('sphere', 'sphere2')
        self.relax.interpreter._Diffusion_tensor.copy('spheroid', 'spheroid2')
        self.relax.interpreter._Diffusion_tensor.copy('ellipsoid', 'ellipsoid2')

        # Get the data pipes.
        sphere_pipe = get_pipe('sphere')
        sphere2_pipe = get_pipe('sphere2')

        # Check that this is indeed a copy.
        self.assertEqual(sphere2_pipe.diff_tensor.tm_sim[4], 9.02e-8)
        sphere_pipe.diff_tensor.tm_sim[4] = 8.88e-8
        self.assertEqual(sphere2_pipe.diff_tensor.tm_sim[4], 9.02e-8)


    def test_delete(self):
        """The user function diffusion_tensor.delete()."""

        # Delete the data.
        self.relax.interpreter._Pipe.switch('sphere')
        self.relax.interpreter._Diffusion_tensor.delete()
        self.relax.interpreter._Pipe.switch('spheroid')
        self.relax.interpreter._Diffusion_tensor.delete()
        self.relax.interpreter._Pipe.switch('ellipsoid')
        self.relax.interpreter._Diffusion_tensor.delete()


    def test_display(self):
        """The user function diffusion_tensor.display()."""

        # Display the data.
        self.relax.interpreter._Pipe.switch('sphere')
        self.relax.interpreter._Diffusion_tensor.display()
        self.relax.interpreter._Pipe.switch('spheroid')
        self.relax.interpreter._Diffusion_tensor.display()
        self.relax.interpreter._Pipe.switch('ellipsoid')
        self.relax.interpreter._Diffusion_tensor.display()


    def test_create_diff_tensor_pdb_sphere(self):
        """Test the user function structure.create_diff_tensor_pdb() for the sphere."""

        # Create the diffusion tensor objects.
        self.relax.interpreter._Pipe.switch('sphere')
        self.relax.interpreter._Structure.create_diff_tensor_pdb(file=self.tmpfile_sphere)

        # Open the temp files.
        file_sphere = open(self.tmpfile_sphere)


    def test_create_diff_tensor_pdb_spheroid(self):
        """Test the user function structure.create_diff_tensor_pdb() for the spheroid."""

        # Create the diffusion tensor objects.
        self.relax.interpreter._Pipe.switch('spheroid')
        self.relax.interpreter._Structure.create_diff_tensor_pdb(file=self.tmpfile_spheroid)

        # Open the temp files.
        file_spheroid = open(self.tmpfile_spheroid)


    def test_create_diff_tensor_pdb_ellipsoid(self):
        """Test the user function structure.create_diff_tensor_pdb() for the ellipsoid."""

        # First copy the data (a more vigorous copy test!).
        self.relax.interpreter._Pipe.copy('ellipsoid', 'ellipsoid2')
        self.relax.interpreter._Pipe.switch('ellipsoid2')
        self.relax.interpreter._Diffusion_tensor.delete()
        self.relax.interpreter._Diffusion_tensor.copy('ellipsoid', 'ellipsoid2')

        # Create the diffusion tensor objects.
        self.relax.interpreter._Structure.create_diff_tensor_pdb(file=self.tmpfile_ellipsoid, scale=1e-05)

        # Open the temp file.
        file = open(self.tmpfile_ellipsoid)
        new_data = file.readlines()
        file.close()

        # Open the real file.
        file = open(sys.path[-1] + '/test_suite/shared_data/structures/diff_tensors/ellipsoid.pdb')
        real_data = file.readlines()
        file.close()

        # Check the data.
        self.assertEqual(len(real_data), len(new_data))
        for i in range(len(real_data)):
            # Print the PDB line, for debugging.
            print real_data[i][0:-1]

            # Check the line.
            self.assertEqual(real_data[i], new_data[i])

