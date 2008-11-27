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


class Modsel:
    def __init__(self, relax, test_name):
        """Class for testing model selection."""

        self.relax = relax

        # Diffusion tensor selection.
        if test_name == 'diff tensor':
            # The name of the test.
            self.name = "AIC model selection between two diffusion tensors"

            # The test.
            self.test = self.diff


    def diff(self, run):
        """The test of selecting between diffusion tensors using AIC."""

        # Create the three runs.
        self.relax.generic.runs.create('sphere', 'mf')
        self.relax.generic.runs.create('spheroid', 'mf')
        self.relax.generic.runs.create('aic', 'mf')

        # Path of the files.
        path = sys.path[-1] + '/test_suite/data/model_free/S2_0.970_te_2048_Rex_0.149'

        # Read the sequence.
        self.relax.interpreter._Sequence.read('sphere', file='r1.600.out', dir=path)
        self.relax.interpreter._Sequence.read('spheroid', file='r1.600.out', dir=path)

        # Select the model.
        self.relax.interpreter._Model_free.select_model('sphere', model='m4')
        self.relax.interpreter._Model_free.select_model('spheroid', model='m4')

        # Read the relaxation data.
        self.relax.interpreter._Relax_data.read('sphere', 'R1', '600', 600.0 * 1e6, 'r1.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('sphere', 'R2', '600', 600.0 * 1e6, 'r2.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('sphere', 'NOE', '600', 600.0 * 1e6, 'noe.600.out', dir=path)
        self.relax.interpreter._Relax_data.read('sphere', 'R1', '500', 500.0 * 1e6, 'r1.500.out', dir=path)
        self.relax.interpreter._Relax_data.read('sphere', 'R2', '500', 500.0 * 1e6, 'r2.500.out', dir=path)
        self.relax.interpreter._Relax_data.read('sphere', 'NOE', '500', 500.0 * 1e6, 'noe.500.out', dir=path)
        self.relax.interpreter._Relax_data.copy('sphere', 'spheroid')

        # Set the diffusion tensors.
        self.relax.interpreter._Diffusion_tensor.init('sphere', 1e-9, fixed=0)
        self.relax.interpreter._Diffusion_tensor.init('spheroid', (1e-9, 0, 0, 0), fixed=0)

        # Set some global stats.
        self.relax.data.chi2['sphere'] = 200
        self.relax.data.chi2['spheroid'] = 0

        # Model selection.
        self.relax.interpreter._Modsel.model_selection(method='AIC', modsel_run='aic')

        # Test if the spheroid has been selected.
        if not self.relax.data.diff.has_key('aic') or not self.relax.data.diff['aic'].type == 'spheroid':
            print "\nThe spheroid diffusion tensor has not been selected."
            return

        # Success.
        return 1
