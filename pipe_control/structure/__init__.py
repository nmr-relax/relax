###############################################################################
#                                                                             #
# Copyright (C) 2008-2013 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
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

# Package docstring.
"""This package consists of modules used reading, writing, creating, structural information.

In the future, numerous structure related operations will be present including:

    - Numerous PDB parsers.
    - A PDB writer.
    - CIF parsers.
    - Other structural data file parsers.
    - Functions for creating geometric objects in structural format.
    - Mass and inertia related functions.

This package has well defined API implemented as class methods for accessing structural data
independent of parser, writer, etc.
"""

__all__ = [
    'api_base',
    'geometric',
    'internal',
    'main',
    'mass'
]
