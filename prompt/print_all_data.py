###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from generic_functions import Generic_functions


class Print_all_data(Generic_functions):
    def __init__(self, relax):
        """Class containing the macros for manipulating the program state."""

        self.relax = relax


    def __repr__(self):
        """Macro for printing all the data in self.relax.data"""

        string = ""
        # Loop over the data structures in self.relax.data
        for name in dir(self.relax.data):
            if not self.filter_data_structure(name):
                string = string +  "self.relax.data." + name + ":\n" + `getattr(self.relax.data, name)` + "\n\n"
        return string
