class Write:
    def __init__(self, relax):
        """Class containing functions for writing data."""

        self.relax = relax


    def write(self, model=None, file="results", force=0):
        """Function for writing results to a file.


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

        file:  The name of the file to output results to.  The default is 'results'.

        force:  A flag which if set to 1 will cause the results file to be overwitten if it already
        exists.
        """

        # The model argument.
        if type(model) != str:
            print "The model argument " + `model` + " must be a string."
            return
        if not self.relax.data.equations.has_key(model):
            print "The model '" + model + "' has not been created yet."
            return

        # File.
        if type(file) != str:
            print "The file name must be a string."
            return

        # The force flag.
        if type(force) != int and force != 0 and force != 1:
            print "The force flag should be the integer values of either 0 or 1."
            return

        self.relax.write.write_data(model=model, file=file, force=force)
