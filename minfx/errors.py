###############################################################################
#                                                                             #
# Copyright (C) 2009-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the minfx optimisation library,                        #
# https://gna.org/projects/minfx                                              #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing all of the MinfxError objects.

This file is part of the U{minfx optimisation library<https://gna.org/projects/minfx>}.
"""

# Base class for all errors.
############################

class BaseError(Exception):
    """The base class for all MinfxErrors."""

    def __str__(self):
        """Modify the behaviour of the error system."""

        return (self.text + "\n")



# Standard errors.
##################

class MinfxError(BaseError):
    def __init__(self, text):
        self.text = text
