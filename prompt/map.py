from Numeric import zeros


class Map:
    def __init__(self, relax):
        """Space mapper."""

        self.relax = relax


    def map(self, model=None, inc=20, lower=None, upper=None, swap=None, file="map", dir="dx"):
        """Function for creating a map of the given space.
        
        OpenDX is the program used to view the output.  Currently only 3D and 4D mappings are
        implemented.


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

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


        Examples
        ~~~~~~~~

        The following commands will generate a map of the extended model-free space defined as model
        'm5' which consists of the parameters {S2f, S2s, ts}.  Files will be output into the
        directory 'dx' and will be prefixed by 'map'.

        relax> map('m5')
        relax> map('m5', 20, "map", "dx")
        relax> map('m5', file="map", dir="dx")
        relax> map(model='m5', inc=20, file="map", dir="dx")
        relax> map(model='m5', inc=20, swap=[0, 1, 2], file="map", dir="dx")


        The following commands will swap the S2s and ts axes of this map.

        relax> map('m5', swap=[0, 2, 1])
        relax> map(model='m5', inc=20, swap=[0, 2, 1], file="map", dir="dx")


        To map the model-free space 'm4' defined by the parameters {S2, te, Rex}, name the results
        'test', and not place the files in a subdirectory, use the following commands.

        relax> map('m4', file='test', dir=None)
        relax> map(model='m4', inc=100, file='test', dir=None)
        """

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

        # Size of map.
        if n != 3 and n != 4:
            print `n` + "D space mapping is not implemented."
            return
        
        self.relax.map.map_space(model=model, inc=inc, lower=lower, upper=upper, swap=swap, file=file, dir=dir)
