###############################################################################
#                                                                             #
# Copyright (C) 2006 Edward d'Auvergne                                        #
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

import sys


class Diffusion_tensor:
    def __init__(self, relax, test_name):
        """Class for testing various aspects specific to the diffusion tensor."""

        self.relax = relax

        # Initialisation test.
        if test_name == 'init':
            self.name = "The user function diffusion_tensor.init()"
            self.test = self.init

        # Deletion test.
        if test_name == 'delete':
            self.name = "The user function diffusion_tensor.delete()"
            self.test = self.delete

        # Display test.
        if test_name == 'display':
            self.name = "The user function diffusion_tensor.display()"
            self.test = self.display

        # Copy test.
        if test_name == 'copy':
            self.name = "The user function diffusion_tensor.copy()"
            self.test = self.copy


    def copy(self, run):
        """The copy test."""

        # Initialise.
        self.initialise_tensors()

        # Create three additional runs for copying the spherical, spheroidal, and ellipsoidal diffusion data.
        self.relax.generic.runs.create('sphere2', 'mf')
        self.relax.generic.runs.create('spheroid2', 'mf')
        self.relax.generic.runs.create('ellipsoid2', 'mf')

        # Delete the data.
        self.relax.interpreter._Diffusion_tensor.copy('sphere', 'sphere2')
        self.relax.interpreter._Diffusion_tensor.copy('spheroid', 'spheroid2')
        self.relax.interpreter._Diffusion_tensor.copy('ellipsoid', 'ellipsoid2')

        # Success.
        return 1


    def delete(self, run):
        """The deletion test."""

        # Initialise.
        self.initialise_tensors()

        # Delete the data.
        self.relax.interpreter._Diffusion_tensor.delete('sphere')
        self.relax.interpreter._Diffusion_tensor.delete('spheroid')
        self.relax.interpreter._Diffusion_tensor.delete('ellipsoid')

        # Success.
        return 1


    def display(self, run):
        """The display test."""

        # Initialise some tensors.
        self.initialise_tensors()

        # Display the data.
        self.relax.interpreter._Diffusion_tensor.display('sphere')
        self.relax.interpreter._Diffusion_tensor.display('spheroid')
        self.relax.interpreter._Diffusion_tensor.display('ellipsoid')

        # Success.
        return 1


    def init(self, run):
        """The initialisation test."""

        # Initialise some tensors.
        self.initialise_tensors()

        # Success.
        return 1


    def initialise_tensors(self):
        """Fucntion for initialising a spherical, spheroidal, and ellipsoidal diffusion tensor."""

        # Create three runs for spherical, spheroidal, and ellipsoidal diffusion.
        self.relax.generic.runs.create('sphere', 'mf')
        self.relax.generic.runs.create('spheroid', 'mf')
        self.relax.generic.runs.create('ellipsoid', 'mf')

        # Initialise some data.
        self.relax.interpreter._Diffusion_tensor.init('sphere', 10e-9, fixed=1)
        self.relax.interpreter._Diffusion_tensor.init('spheroid', (2e-8, 1.3, 60-360, 290), param_types=2, spheroid_type='prolate', fixed=1)
        self.relax.interpreter._Diffusion_tensor.init('ellipsoid', (9e-8, 5e6, 0.3, 60+360, 290, 100), fixed=0)
