from os import F_OK, access, mkdir


class Write:
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax


    def write_data(self, model=None, force=0):
        """Create the directories and files for output.

        The directory with the name of the model will be created.  The results will be placed in the
        file 'results' in the model directory.
        """

        # Directory creation.
        try:
            mkdir(model)
        except OSError:
            pass

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("print", model)
        if fns == None:
            return
        else:
            self.print_header, self.print_results = fns

        # The results file.
        file_name = model + "/results"
        if access(file_name, F_OK) and not force:
            print "The file '" + file_name + "' already exists.  Set the force flag to 1 to overwrite."
            return
        results_file = open(file_name, 'w')

        # Print the header.
        self.print_header(results_file, model)

        # Print the results.
        self.print_results(results_file, model)

        # Close the results file.
        results_file.close()
