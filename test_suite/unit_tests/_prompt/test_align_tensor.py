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
import sys

# relax module imports.
from prompt.align_tensor import Align_tensor
from test_suite.unit_tests.align_tensor_testing_base import Align_tensor_base_class

# Set the variable sys.ps3 (this is required by the user functions).
sys.ps3 = 'relax> '


# A class to act as a container.
class Container:
    pass

# Fake normal relax usage of the user function class.
relax = Container()
relax.interpreter = Container()
relax.interpreter.intro = True


class Test_align_tensor(Align_tensor_base_class, TestCase):
    """Unit tests for the functions of the 'prompt.align_tensor' module."""

    # Instantiate the user function class.
    align_tensor_fns = Align_tensor(relax)
 
