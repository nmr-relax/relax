class Grid:
    def __init__(self, relax):
        """Class containing the fixed, grid_search, and minimise functions."""

        self.relax = relax


    def grid_search(self, model=None, lower=None, upper=None, inc=21, print_flag=1):
        """The grid search function.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

        lower:  An array of the lower bound parameter values for the grid search.  The length of the
        array should be equal to the number of parameters in the model.

        upper:  An array of the upper bound parameter values for the grid search.  The length of the
        array should be equal to the number of parameters in the model.

        inc:  The number of increments to search over.  If a single integer is given then the number
        of increments will be equal in all dimensions.  Different numbers of increments in each
        direction can be set if 'inc' is set to an array of integers of length equal to the number
        of parameters.

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.
        """

        # The model argument.
        if type(model) != str:
            print "The model argument " + `model` + " must be a string."
            return

        # Find the index of the model.
        if not self.relax.data.equations.has_key(model):
            print "The model '" + model + "' has not been created yet."
            return

        # The lower bounds.
        if lower:
            bad_arg = 0
            if len(lower) != len(self.relax.data.param_types[model]):
                bad_arg = 1
            for i in range(len(lower)):
                if type(lower[i]) != float and type(lower[i]) != int:
                    bad_arg = 1
            if bad_arg:
                print "The argument 'lower' must be an array of numbers of length equal to the number of parameters in the model."
                return
        else:
            lower = []
            for i in range(len(self.relax.data.param_types[model])):
                lower.append(None)

        # The upper bounds.
        if upper:
            bad_arg = 0
            if len(upper) != len(self.relax.data.param_types[model]):
                bad_arg = 1
            for i in range(len(upper)):
                if type(upper[i]) != float and type(upper[i]) != int:
                    bad_arg = 1
            if bad_arg:
                print "The argument 'upper' must be an array of numbers of length equal to the number of parameters in the model."
                return
        else:
            upper = []
            for i in range(len(self.relax.data.param_types[model])):
                upper.append(None)

        # The incrementation value.
        bad_arg = 0
        if type(inc) != int and type(inc) != list:
            bad_arg = 1
        if type(inc) == list:
            if len(inc) != len(self.relax.data.param_types[model]):
                bad_arg = 1
            for i in range(len(inc)):
                if type(inc[i]) != int:
                    bad_arg = 1
        if bad_arg:
            print "The argument 'inc' must be either an integer or an array of integers of length equal to the number of parameters in the model."
            return
        elif type(inc) == int:
            inc_vector = []
            for i in range(len(self.relax.data.param_types[model])):
                inc_vector.append(inc)

        # The debugging flag.
        if type(print_flag) != int:
            print "The print_flag argument must be an integer."
            return

        # Equation type specific function setup.
        fns = self.relax.specific_setup.setup("grid_search", model)
        if fns == None:
            return
        self.grid_setup, self.main_loop = fns

        # Setup the grid search options.
        min_options = self.grid_setup(model=model, inc_vector=inc_vector)

        # Set the lower and upper bounds if these are supplied.
        for i in range(len(self.relax.data.param_types[model])):
            if lower[i] != None:
                min_options[i][1] = lower[i]
            if upper[i] != None:
                min_options[i][2] = upper[i]

        # Diagonal scaling.
        if self.relax.data.scaling.has_key(model):
            for i in range(len(min_options)):
                min_options[i][1] = min_options[i][1] / self.relax.data.scaling[model][0][i]
                min_options[i][2] = min_options[i][2] / self.relax.data.scaling[model][0][i]

        # Main iterative loop.
        self.main_loop(model=model, min_algor='grid', min_options=min_options, print_flag=print_flag)
