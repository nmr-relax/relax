class Grid:
    def __init__(self, relax):
        """Class containing the grid_search macro."""

        self.relax = relax


    def grid_search(self, model=None, lower=None, upper=None, inc=21, constraints=1, print_flag=1):
        """The grid search macro.

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

        constraints:  A flag specifying whether the parameters should be constrained.  The default
        is to turn constraints on (constraints=1).

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "grid_search("
            text = text + "model=" + `model`
            text = text + ", lower=" + `lower`
            text = text + ", upper=" + `upper`
            text = text + ", inc=" + `inc`
            text = text + ", constraints=" + `constraints`
            text = text + ", print_flag=" + `print_flag` + ")\n"
            print text

        # The model argument.
        if type(model) != str:
            print "The model argument " + `model` + " must be a string."
            return

        # Find the index of the model.
        if not self.relax.data.equations.has_key(model):
            print "The model '" + model + "' has not been created yet."
            return

        # The lower bounds.
        if lower != None:
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
        if upper != None:
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
            inc = inc_vector

        # Constraint flag.
        if type(constraints) != int or (constraints != 0 and constraints != 1):
            print "The constraint arguments must be either the integers 0 or 1."
            return

        # The print flag.
        if type(print_flag) != int:
            print "The print_flag argument must be an integer."
            return

        # Execute the functional code.
        self.relax.min.grid_search(model=model, lower=lower, upper=upper, inc=inc, constraints=constraints, print_flag=print_flag)
