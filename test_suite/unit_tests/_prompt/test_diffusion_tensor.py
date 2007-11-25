###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from data import Data as relax_data_store
from generic_fns import residue
from prompt.diffusion_tensor import Diffusion_tensor
from relax_errors import RelaxError, RelaxIntError, RelaxNoPipeError, RelaxNoneStrError, RelaxStrError
from test_suite.unit_tests.diffusion_tensor_testing_base import Diffusion_tensor_base_class

# Unit test imports.
from data_types import DATA_TYPES
import fake_relax


class Test_diffusion_tensor(Diffusion_tensor_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.diffusion_tensor' module."""

    # Instantiate the user function class.
    diffusion_tensor_fns = Diffusion_tensor(fake_relax.fake_instance())
    residue_fns = residue
