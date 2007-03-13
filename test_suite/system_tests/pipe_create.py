###############################################################################
#                                                                             #
# Copyright (C) 2006-2007 Edward d'Auvergne                                   #
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


class Pipe_create:
    def __init__(self, relax):
        """Class for testing the creation of data pipes."""

        self.relax = relax

        # The name of the test.
        self.name = "The user function pipe.create()"


    def test(self, pipe):
        """The actual test."""

        # Create the data pipe.
        self.relax.interpreter._Pipe.create(pipe, 'mf')

        # Success.
        return 1
