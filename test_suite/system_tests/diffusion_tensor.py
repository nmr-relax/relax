###############################################################################
#                                                                             #
# Copyright (C) 2006-2008 Edward d'Auvergne                                   #
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
from unittest import TestCase
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()


class Diffusion_tensor(TestCase):
    """Class for testing various aspects specific to the diffusion tensor."""

    def setUp(self):
        """Function for initialising a spherical, spheroidal, and ellipsoidal diffusion tensor."""

        # Create three data pipes for spherical, spheroidal, and ellipsoidal diffusion.
        self.relax.interpreter._Pipe.create('sphere', 'mf')
        self.relax.interpreter._Pipe.create('spheroid', 'mf')
        self.relax.interpreter._Pipe.create('ellipsoid', 'mf')

        # Initialise some data.
        self.relax.interpreter._Pipe.switch('sphere')
        self.relax.interpreter._Diffusion_tensor.init(10e-9, fixed=True)
        self.relax.interpreter._Pipe.switch('spheroid')
        self.relax.interpreter._Diffusion_tensor.init((2e-8, 1.3, 60-360, 290), param_types=2, spheroid_type='prolate', fixed=True)
        self.relax.interpreter._Pipe.switch('ellipsoid')
        self.relax.interpreter._Diffusion_tensor.init((9e-8, 5e6, 0.3, 60+360, 290, 100), fixed=False)


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_copy(self):
        """The user function diffusion_tensor.copy()."""

        # Create three additional data pipes for copying the spherical, spheroidal, and ellipsoidal diffusion data.
        self.relax.interpreter._Pipe.create('sphere2', 'mf')
        self.relax.interpreter._Pipe.create('spheroid2', 'mf')
        self.relax.interpreter._Pipe.create('ellipsoid2', 'mf')

        # Delete the data.
        self.relax.interpreter._Diffusion_tensor.copy('sphere', 'sphere2')
        self.relax.interpreter._Diffusion_tensor.copy('spheroid', 'spheroid2')
        self.relax.interpreter._Diffusion_tensor.copy('ellipsoid', 'ellipsoid2')


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


    def test_createDiffTensor(self):
        """The user function structure.create_diff_tensor_pdb()."""

        # Create the diffusion tensor object
        self.relax.interpreter._Structure.read_pdb(file='Ap4Aase_res1-12.pdb', dir=sys.path[-1] + '/test_suite/shared_data/structures', model=1)
        self.relax.interpreter._Sequence.read(file='Ap4Aase.seq', dir=sys.path[-1] + '/test_suite/system_tests/data/')
        #self.relax.interpreter._Pipe.switch('sphere')
        #self.relax.interpreter._Structure.create_diff_tensor_pdb(file='tensor.pdb')
        #self.relax.interpreter._Pipe.switch('spheroid')
        #self.relax.interpreter._Structure.create_diff_tensor_pdb(file='tensor.pdb')
        self.relax.interpreter._Pipe.switch('ellipsoid')
        self.relax.interpreter._Structure.create_diff_tensor_pdb(file='tensor.pdb')
