###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006-2007 Edward d'Auvergne                             #
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


# relax module imports.
from hybrid import Hybrid
from jw_mapping import Jw_mapping
from model_free import Model_free
from noe import Noe
from relax_fit import Relax_fit


# The available modules.
__all__ = [ 'base_class',
            'hybrid',
            'jw_mapping',
            'model_free',
            'noe',
            'relax_data']

# Set up all the classes.
hybrid = Hybrid()
jw_mapping = Jw_mapping()
model_free = Model_free()
noe = Noe()
relax_fit = Relax_fit()
