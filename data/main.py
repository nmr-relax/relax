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


from math import pi


class Data:
    def __init__(self):
        """Class containing all the program data."""

        self.gh = 26.7522e7
        #self.gh = 26.7522212e7
        self.gx = -2.7126e7
        self.g_ratio = self.gh / self.gx
        self.h = 6.6260755e-34
        #self.h = 6.62606876e-34
        self.h_bar = self.h / ( 2.0*pi )
        self.mu0 = 4.0 * pi * 1e-7

        # The residue specific data
        self.res = []

        # The name of the runs.
        self.runs = []

        # The type of the runs.
        self.types = {}
