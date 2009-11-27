###############################################################################
#                                                                             #
# Copyright (C) 2004, 2006 Edward d'Auvergne                                  #
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


from hybrid import Hybrid
from jw_mapping import Jw_mapping
from model_free import Model_free
from model_free_csa import Model_free_csa
from noe import Noe
from relax_data import Rx_data
from csa_data import CSAx_data
from relax_fit import Relax_fit


class Specific:
    def __init__(self, relax):
        """Class containing all the specific functions."""

        # Place the program class structure under self.relax
        self.relax = relax

        # Set up all the functions
        self.hybrid = Hybrid(self.relax)
        self.jw_mapping = Jw_mapping(self.relax)
        self.model_free = Model_free(self.relax)
        self.model_free_csa = Model_free_csa(self.relax)
        self.noe = Noe(self.relax)
        self.relax_data = Rx_data(self.relax)
        self.csa_data = CSAx_data(self.relax)
        self.relax_fit = Relax_fit(self.relax)
