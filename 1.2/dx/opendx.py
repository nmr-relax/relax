###############################################################################
#                                                                             #
# Copyright (C) 2003-2005 Edward d'Auvergne                                   #
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

from os import system
from re import search

from isosurface_3D import Iso3D


class OpenDX:
    def __init__(self, relax):
        """Class containting the function for OpenDX."""

        # Place the program class structure under self.relax
        self.relax = relax

        # Set up all the classes.
        self.iso3d = Iso3D(relax)


    def map(self, run=None, params=None, map_type='Iso3D', res_num=None, inc=20, lower=None, upper=None, axis_incs=10, file="map", dir="dx", point=None, point_file="point", remap=None):
        """Function for mapping the given space and creating OpenDX files."""

        # Residue index.
        index = None
        if res_num:
            for i in xrange(len(self.relax.data.res[run])):
                if self.relax.data.res[run][i].num == res_num:
                    index = i
                    break
            if index == None:
                raise RelaxNoResError, res_num

        # Space type.
        if search("^[Ii]so3[Dd]", map_type):
            if len(params) != 3:
                raise RelaxError, "The 3D isosurface map requires a 3 parameter model."

            # Create the map.
            self.iso3d.map_space(run, params, res_num, index, inc, lower, upper, axis_incs, file, dir, point, point_file, remap)
        else:
            raise RelaxError, "The map type '" + map_type + "' is not supported."


    def run(self, file="map", dir="dx", dx_exe="dx", vp_exec=1):
        """Function for running OpenDX."""

        # Text for changing to the directory dir.
        dir_text = ""
        if dir != None:
            dir_text = " -directory " + dir

        # Text for executing OpenDX.
        execute_text = ""
        if vp_exec:
            execute_text = " -execute"

        # Test the binary file string corresponds to a valid executable.
        self.relax.IO.test_binary(dx_exe)

        # Run OpenDX.
        system(dx_exe + dir_text + " -program " + file + ".net" + execute_text + " &")
