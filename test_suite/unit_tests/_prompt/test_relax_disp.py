###############################################################################
#                                                                             #
# Copyright (C) 2008-2010 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
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

# relax module imports.
from prompt.relax_disp import Relax_disp
from relax_errors import RelaxNoneNumError, RelaxNumError, RelaxStrError

# Unit test imports.
from data_types import DATA_TYPES


class Test_relax_disp(TestCase):
    """Unit tests for the functions of the 'prompt.relax_disp' module."""

    # Instantiate the user function class.
    relax_disp_fns = Relax_disp()


    def test_relax_calc_r2eff_argfail_exp_type(self):
        """The exp_type arg test of the relax_disp.relax_calc_r2eff() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_disp_fns.calc_r2eff, exp_type=data[1])

    def test_relax_calc_r2eff_argfail_id(self):
        """The id arg test of the relax_disp.relax_calc_r2eff() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_disp_fns.calc_r2eff, id=data[1])


    def test_relax_calc_r2eff_argfail_delayT(self):
        """The delayT arg test of the relax_disp.relax_calc_r2eff() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, int and None arguments, and skip them.
            if data[0] == 'float' or data[0] == 'int' or data[0] == 'bin' or data[0] == 'None':
                continue

            # The argument test.
            self.assertRaises(RelaxNoneNumError, self.relax_disp_fns.calc_r2eff, id='test', delayT=data[1])


    def test_relax_calc_r2eff_argfail_int_cpmg(self):
        """The int_cpmg arg test of the relax_disp.relax_calc_r2eff() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, int and None arguments, and skip them.
            if data[0] == 'float' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.relax_disp_fns.calc_r2eff, id='test', int_cpmg=data[1])


    def test_relax_calc_r2eff_argfail_int_ref(self):
        """The int_ref arg test of the relax_disp.relax_calc_r2eff() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, int and None arguments, and skip them.
            if data[0] == 'float' or data[0] == 'int' or data[0] == 'bin':
                continue

            # The argument test.
            self.assertRaises(RelaxNumError, self.relax_disp_fns.calc_r2eff, id='test', int_ref=data[1])


    def test_relax_cpmg_delayT_argfail_id(self):
        """The id arg test of the relax_disp.relax_cpmg_delayT() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

            # The argument test.
            self.assertRaises(RelaxStrError, self.relax_disp_fns.cpmg_delayT, id=data[1])


    def test_relax_cpmg_delayT_argfail_delayT(self):
        """The delayT arg test of the relax_disp.cpmg_delayT() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, int and None arguments, and skip them.
            if data[0] == 'float' or data[0] == 'int' or data[0] == 'None':
                continue

        # The argument test.
        self.assertRaises(RelaxNoneNumError, self.relax_disp_fns.cpmg_delayT, delayT=data[1])


    def test_relax_cpmg_frq_argfail_cpmg_frq(self):
        """The cpmg_frq arg test of the relax_disp.cpmg_frq() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the float, int and None arguments, and skip them.
            if data[0] == 'float' or data[0] == 'int' or data[0] == 'None':
                continue

        # The argument test.
        self.assertRaises(RelaxNoneNumError, self.relax_disp_fns.cpmg_frq, cpmg_frq=data[1])


    def test_relax_cpmg_frq_argfail_spectrum_id(self):
        """The spectrum_id arg test of the relax_disp.cpmg_frq() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

        # The argument test.
        self.assertRaises(RelaxStrError, self.relax_disp_fns.cpmg_frq, spectrum_id=data[1])


    def test_relax_exp_type_argfail_exp_type(self):
        """The exp_type arg test of the relax_disp.exp_type() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

        # The argument test.
        self.assertRaises(RelaxStrError, self.relax_disp_fns.exp_type, exp_type=data[1])


    def test_relax_select_model_argfail_model(self):
        """The model arg test of the relax_disp.select_model() user function."""

        # Loop over the data types.
        for data in DATA_TYPES:
            # Catch the str arguments, and skip them.
            if data[0] == 'str':
                continue

        # The argument test.
        self.assertRaises(RelaxStrError, self.relax_disp_fns.select_model, model=data[1])
