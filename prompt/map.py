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


from Numeric import zeros
from re import match


class Map:
    def __init__(self, relax):
        """Space mapper."""

        self.relax = relax


    def map(self, model=None, map_type="Iso3D", inc=20, lower=None, upper=None, swap=None, file="map", dir="dx", point=None, point_file="point"):
        """Function for creating a map of the given space in OpenDX format.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

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


        Map type
        ~~~~~~~~

        The map type can be changed by supplying the 'map_type' keyword argument.  Here is a list of
        currently supported map types:
        _____________________________________________________________________________
        |                                           |                               |
        | Surface type                              | Pattern                       |
        |-------------------------------------------|-------------------------------|
        |                                           |                               |
        | 3D isosurface                             | '^[Ii]so3[Dd]'                |
        |-------------------------------------------|-------------------------------|

        Pattern syntax is simply regular expression syntax where square brackets [] means any
        character within the brackets, ^ means the start of the string, etc.


        Examples
        ~~~~~~~~

        The following commands will generate a map of the extended model-free space defined as model
        'm5' which consists of the parameters {S2f, S2s, ts}.  Files will be output into the
        directory 'dx' and will be prefixed by 'map'.

        relax> map('m5')
        relax> map('m5', 20, "map", "dx")
        relax> map('m5', file="map", dir="dx")
        relax> map(model='m5', inc=20, file="map", dir="dx")
        relax> map(model='m5', type="Iso3D", inc=20, swap=[0, 1, 2], file="map", dir="dx")


        The following commands will swap the S2s and ts axes of this map.

        relax> map('m5', swap=[0, 2, 1])
        relax> map(model='m5', type="Iso3D", inc=20, swap=[0, 2, 1], file="map", dir="dx")


        To map the model-free space 'm4' defined by the parameters {S2, te, Rex}, name the results
        'test', and not place the files in a subdirectory, use the following commands.

        relax> map('m4', file='test', dir=None)
        relax> map(model='m4', inc=100, file='test', dir=None)
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "map("
            text = text + "model=" + `model`
            text = text + ", map_type=" + `map_type`
            text = text + ", inc=" + `inc`
            text = text + ", lower=" + `lower`
            text = text + ", upper=" + `upper`
            text = text + ", swap=" + `swap`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", point=" + `point`
            text = text + ", point_file=" + `point_file` + ")\n"
            print text

        # The number of parameters.
        n = len(self.relax.data.param_types[model])

        # The model argument.
        if type(model) != str:
            print "The model argument " + `model` + " must be a string."
            return
        if not self.relax.data.equations.has_key(model):
            print "The model '" + model + "' has not been created yet."
            return

        # Increment.
        if type(inc) != int:
            print "The increment argument should be an integer."
            return
        elif inc <= 1:
            print "The increment value needs to be greater than 1."
            return

        # Lower bounds.
        if lower != None:
            if type(lower) != list:
                print "The lower bounds argument must be an array."
                return
            if len(lower) != n:
                print "The lower bounds array must be of length equal to the number of parameters."
                return
            for i in range(n):
                if type(lower[i]) != int and type(lower[i]) != float:
                    print "The elements of the lower bounds array must be numbers."
                    return

        # Upper bounds.
        if upper != None:
            if type(upper) != list:
                print "The upper bounds argument must be an array."
                return
            if len(upper) != n:
                print "The upper bounds array must be of length equal to the number of parameters."
                return
            for i in range(n):
                if type(upper[i]) != int and type(upper[i]) != float:
                    print "The elements of the upper bounds array must be numbers."
                    return

        # Axes swapping.
        if swap != None:
            if type(swap) != list:
                print "The swap argument must be an array."
                return
            if len(swap) != n:
                print "The swap array must be of length " + `n`
                return
            test = zeros(n)
            for i in range(n):
                if type(swap[i]) != int:
                    print "The elements of the swap array must be integers."
                    return
                if swap[i] >= n:
                    print "The integer " + `swap[i]` + " is greater than the final array element."
                    return
                elif swap[i] < 0:
                    print "All integers of the swap array must be positive."
                    return
                test[swap[i]] = 1
            for i in range(n):
                if test[i] != 1:
                    print "The swap array is invalid (possibly duplicated integer values)."
                    return

        # File and directory name.
        if type(file) != str:
            print "The file name must be a string."
            return
        elif type(dir) != str and dir != None:
            print "The directory name must be a string or 'None'."
            return

        # Point.
        if point != None:
            if type(point) != list:
                print "The point argument must be an array."
                return
            elif len(point) != n:
                print "The point array must be of length " + `n`
                return
            elif type(point_file) != str:
                print "The point file name must be a string."
                return
            for i in range(n):
                if type(point[i]) != int and type(point[i]) != float:
                    print "The elements of the point array must be numbers."
                    return

        # Space type.
        if type(map_type) != str:
            print "The map_type argument must be a string."
            return
        if match("^[Ii]so3[Dd]", map_type):
            if n != 3:
                print "The 3D isosurface map requires a strictly 3 parameter model."
                return
            self.relax.map.Iso3D.map_space(model=model, inc=inc, lower=lower, upper=upper, swap=swap, file=file, dir=dir, point=point, point_file=point_file)
        else:
            print "The map type '" + map_type + "' is not supported."
            return
