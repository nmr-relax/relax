###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


from Numeric import zeros
from re import match
import sys
from types import FunctionType


class Map:
    def __init__(self, relax):
        """Space mapper."""

        self.relax = relax


    def map(self, run=None, res_num=None, map_type="Iso3D", inc=20, lower=None, upper=None, swap=None, file="map", dir="dx", point=None, point_file="point", remap=None, labels=None):
        """Function for creating a map of the given space in OpenDX format.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        res_num:  The residue number.

        map_type:  The type of map to create.  For example the default, a 3D isosurface, the type is
        "Iso3D".  See below for more details.

        inc:  The number of increments to map in each dimension.  This value controls the resolution
        of the map.

        lower:  The lower bounds of the space.  If you wish to change the lower bounds of the map
        then supply an array of length equal to the number of parameters in the model.  A lower
        bound for each parameter must be supplied.  If nothing is supplied then the defaults will
        be used.

        upper:  The upper bounds of the space.  If you wish to change the upper bounds of the map
        then supply an array of length equal to the number of parameters in the model.  A upper
        bound for each parameter must be supplied.  If nothing is supplied then the defaults will
        be used.

        swap:  An array used to swap the position of the axes.  The length of the array should be
        the same as the number of parameters in the model.  The values should be integers specifying
        which elements to interchange.  For example if swap equals [0, 1, 2] for a three parameter
        model then the axes are not interchanged whereas if swap equals [1, 0, 2] then the first and
        second dimensions are interchanged.

        file:  The file name.  All the output files are prefixed with this name.  The main file
        containing the data points will be called the value of 'file'.  The OpenDX program will be
        called 'file.net' and the OpenDX import file will be called 'file.general'.

        dir:  The directory to output files to.  Set this to 'None' if you do not want the files to
        be placed in subdirectory.  If the directory does not exist, it will be created.

        point:  An array of parameter values where a point in the map, shown as a red sphere, will
        be placed.  The length must be equal to the number of parameters.

        point_file:  The name of that the point output files will be prefixed with.

        remap:  A user supplied remapping function.  This function will receive the parameter array
        and must return an array of equal length.

        labels:  The axis labels.  If supplied this argument should be an array of strings of length
        equal to the number of parameters.


        Map type
        ~~~~~~~~

        The map type can be changed by supplying the 'map_type' keyword argument.  Here is a list of
        currently supported map types:
        _____________________________________________________________________________
        |                                           |                               |
        | Surface type                              | Pattern                       |
        |___________________________________________|_______________________________|
        |                                           |                               |
        | 3D isosurface                             | '^[Ii]so3[Dd]'                |
        |___________________________________________|_______________________________|

        Pattern syntax is simply regular expression syntax where square brackets [] means any
        character within the brackets, ^ means the start of the string, etc.


        Examples
        ~~~~~~~~

        The following commands will generate a map of the extended model-free space defined as run
        'm5' which consists of the parameters {S2f, S2s, ts}.  Files will be output into the
        directory 'dx' and will be prefixed by 'map'.  The residue, in this case, is number 6.

        relax> map('m5', 6)
        relax> map('m5', 6, 20, "map", "dx")
        relax> map('m5', res_num=6, file="map", dir="dx")
        relax> map(run='m5', res_num=6, inc=20, file="map", dir="dx")
        relax> map(run='m5', res_num=6, type="Iso3D", inc=20, swap=[0, 1, 2], file="map", dir="dx")


        The following commands will swap the S2s and ts axes of this map.

        relax> map('m5', res_num=6, swap=[0, 2, 1])
        relax> map(run='m5', res_num=6, type="Iso3D", inc=20, swap=[0, 2, 1], file="map", dir="dx")


        To map the model-free space 'm4' defined by the parameters {S2, te, Rex}, name the results
        'test', and not place the files in a subdirectory, use the following commands (assuming
        residue 2).

        relax> map('m4', res_num=2, file='test', dir=None)
        relax> map(run='m4', res_num=2, inc=100, file='test', dir=None)
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "map("
            text = text + "run=" + `run`
            text = text + ", res_num=" + `res_num`
            text = text + ", map_type=" + `map_type`
            text = text + ", inc=" + `inc`
            text = text + ", lower=" + `lower`
            text = text + ", upper=" + `upper`
            text = text + ", swap=" + `swap`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", point=" + `point`
            text = text + ", point_file=" + `point_file`
            text = text + ", remap=" + `remap`
            text = text + ", labels=" + `labels` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The residue number.
        if type(res_num) != int:
            raise RelaxIntError, ('residue number', res_num)

        # Increment.
        if type(inc) != int:
            raise RelaxIntError, ('increment', inc)
        elif inc <= 1:
            raise RelaxError, "The increment value needs to be greater than 1."

        # Lower bounds.
        if lower != None:
            if type(lower) != list:
                raise RelaxListError, ('lower bounds', lower)
            for i in xrange(len(lower)):
                if type(lower[i]) != int and type(lower[i]) != float:
                    raise RelaxListNumError, ('lower bounds', lower)

        # Upper bounds.
        if upper != None:
            if type(upper) != list:
                raise RelaxListError, ('upper bounds', upper)
            for i in xrange(len(upper)):
                if type(upper[i]) != int and type(upper[i]) != float:
                    raise RelaxListNumError, ('upper bounds', upper)

        # Axes swapping.
        if swap != None:
            if type(swap) != list:
                raise RelaxListError, ('axes swapping', swap)
            for i in xrange(len(swap)):
                if type(swap[i]) != int:
                    raise RelaxListIntError, ('axes swapping', swap)

        # File name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory name.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # Point.
        if point != None:
            if type(point) != list:
                raise RelaxListError, ('point', point)
            if type(point_file) != str:
                raise RelaxStrError, ('point file name', point_file)
            for i in xrange(len(point)):
                if type(point[i]) != int and type(point[i]) != float:
                    raise RelaxListNumError, ('point', point)

        # Remap function.
        if remap != None and type(remap) is not FunctionType:
            raise RelaxFunctionError, ('remap function', remap)

        # Axis labels.
        if labels != None:
            if type(labels) != list:
                raise RelaxListError, ('axis labels', labels)
            for i in xrange(len(labels)):
                if type(labels[i]) != str:
                    raise RelaxListStrError, ('axis labels', labels)

        # Space type.
        if type(map_type) != str:
            raise RelaxStrError, ('map type', map_type)

        # Execute the functional code.
        self.relax.generic.map.map_space(run=run, res_num=res_num, map_type=map_type, inc=inc, lower=lower, upper=upper, swap=swap, file=file, dir=dir, point=point, point_file=point_file, remap=remap, labels=labels)
