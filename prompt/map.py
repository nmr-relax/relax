class Map:
    def __init__(self, relax):
        """Space mapper."""

        self.relax = relax


    def map(self, model=None, inc=20, file="map", dir="dx"):
        """Function for creating a map of the given space.
        
        OpenDX is the program used to view the output.  Currently only 3D and 4D mappings are
        implemented.


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

        inc:  The number of increments to map in each dimension.  This value controls the resolution
        of the map.

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


        To map the model-free space 'm4' defined by the parameters {S2, te, Rex}, name the results
        'test', and not place the files in a subdirectory, use the following commands.

        relax> map('m4', file='test', dir=None)
        relax> map(model='m4', inc=100, file='test', dir=None)
        """


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

        # File and directory name.
        if type(file) != str:
            print "The file name must be a string."
            return
        elif type(dir) != str and dir != None:
            print "The directory name must be a string or 'None'."
            return

        # Size of map.
        n = len(self.relax.data.param_types[model])
        if n != 3 and n != 4:
            print `n` + "D space mapping is not implemented."
            return
        
        self.relax.map.map_space(model=model, inc=inc, file=file, dir=dir)
