###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
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
from os import sep
import sys
from unittest import TestCase

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import pipes, results, structure
from relax_errors import RelaxError
from specific_fns.model_free import main
from status import Status; status = Status()


class Test_main(TestCase):
    """Unit tests for the class methods of specific_fns.model_free.main.Model_free_main."""

    # Instantiate the class.
    inst = main.Model_free_main()


    def setUp(self):
        """Setup some structures for the unit tests."""

        # Create a model-free data pipe.
        ds.add(pipe_name='orig', pipe_type='mf')


    def tearDown(self):
        """Reset the relax data storage object."""

        ds.__reset__()


    def test_duplicate_data1(self):
        """Test the model-free duplicate_data() method."""

        # Duplicate the data.
        self.inst.duplicate_data('orig', 'new', model_info=0)


    def test_duplicate_data2(self):
        """Test the model-free duplicate_data() method."""

        # Read a model-free results file.
        results.read(file='final_results_trunc_1.3', directory=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP')

        # Duplicate the data.
        self.inst.duplicate_data('orig', 'new', model_info=0)


    def test_duplicate_data3(self):
        """Test the model-free duplicate_data() method."""

        # Read a model-free results file.
        results.read(file='final_results_trunc_1.3', directory=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP')

        # Load a structure.
        structure.main.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='internal')

        # Duplicate the data.
        self.inst.duplicate_data('orig', 'new', model_info=0)

        # Check the original data.
        self.assert_(hasattr(pipes.get_pipe('orig'), 'structure'))

        # Check the duplication.
        self.assert_(hasattr(pipes.get_pipe('new'), 'structure'))


    def test_duplicate_data_single_mf_model(self):
        """Test the model-free duplicate_data() method."""

        # Read a model-free results file.
        results.read(file='final_results_trunc_1.3', directory=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP')

        # Load a structure.
        structure.main.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='internal')

        # Duplicate the data, model by model.
        self.inst.duplicate_data('orig', 'new', model_info=0)
        self.inst.duplicate_data('orig', 'new', model_info=1)
        self.inst.duplicate_data('orig', 'new', model_info=2)
        self.inst.duplicate_data('orig', 'new', model_info=3)


    def test_duplicate_data_fail1(self):
        """Test the failure of the model-free duplicate_data() method when the structures are not consistent."""

        # Read a model-free results file.
        results.read(file='final_results_trunc_1.3', directory=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'model_free'+sep+'OMP')

        # Load a structure.
        structure.main.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='internal')

        # Create a new model-free data pipe.
        ds.add(pipe_name='new', pipe_type='mf')

        # Load the structure for the second pipe.
        structure.main.read_pdb(file='Ap4Aase_res1-12.pdb', dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures', read_model=1, parser='internal')

        # Modify the structure.
        dp = pipes.get_pipe('new')
        dp.structure.structural_data[0].mol[0].file_name = 'test'

        # Duplicate the data and catch the error.
        self.assertRaises(RelaxError, self.inst.duplicate_data, 'orig', 'new', model_info=0)
