###############################################################################
#                                                                             #
# Copyright (C) 2012 Edward d'Auvergne                                        #
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

# Package docstring.
"""Package containing all of the user function details.

This package contains all information and details about user functions, from documentation to icons to be used in the GUI.  This package contains a special data structure which will be used by the different UIs to automatically generate their interfaces to the user functions.
"""

# The __all__ package list (main modules).
__all__ = [
    'data',
    'functions',
    'objects'
]

# The __all__ package list (user function modules).
__all__ += [
    'bmrb',
    'pipe'
]

# Import all the modules to set up the data.
import user_functions.bmrb
import user_functions.pipe

# Import the data structure.
from user_functions.data import Uf_info; uf_info = Uf_info()

# Check the validity of the data.
uf_info.validate()
