###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
from re import search
from unittest import TestCase

# relax module imports.
from generic_fns.structure.api_base import Base_struct_API
from generic_fns.structure.internal import Internal
from generic_fns.structure.scientific import Scientific_data


class Test_api_base(TestCase):
    """Unit tests for the structural API base class."""

    def test_Internal_objects(self):
        """Are the initial public objects of the Internal structural object all within the API base class?"""

        # The base and internal objects.
        base = Base_struct_API()
        internal = Internal()

        # The objects in the base class.
        base_names = dir(base)

        # Loop over the objects in the internal object.
        for name in dir(internal):
            # Skip anything starting with '_'.
            if search('^_', name):
                continue

            # Not present.
            if name not in base_names:
                self.fail('The object ' + name + ' cannot be found in the structural API base class')


    def test_Scientific_objects(self):
        """Are the initial public objects of the Scientific structural object all within the API base class?"""

        # The base and Scientific objects.
        base = Base_struct_API()
        sci = Scientific_data()

        # The objects in the base class.
        base_names = dir(base)

        # Loop over the objects in the Scientific object.
        for name in dir(sci):
            # Skip anything starting with '_'.
            if search('^_', name):
                continue

            # Not present.
            if name not in base_names:
                self.fail('The object ' + name + ' cannot be found in the structural API base class')
