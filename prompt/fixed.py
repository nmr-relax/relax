from Numeric import Float64, array, zeros


class Fixed:
    def __init__(self, relax):
        """Class containing the fixed macro."""

        self.relax = relax


    def fixed(self, model=None, values=None, print_flag=1):
        """Macro for fixing the initial parameter values.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        model:  The name of the model.

        values:  An array of numbers of length equal to the number of parameters in the model.

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.


        Examples
        ~~~~~~~~

        This command will fix the parameter values of the model 'm2', which is the original
        model-free equation with parameters {S2, te}, before minimisation to the preselected values
        of this function.

        relax> fixed('m2')


        This command will do the same except the S2 and te values will be set to one and ten ps
        respectively.

        relax> fixed('m2', [1.0, 10 * 10e-12])
        relax> fixed('m2', values=[1.0, 10 * 10e-12])
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "fixed("
            text = text + "model=" + `model`
            text = text + ", values=" + `values`
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

        # User defined values.
        if values != None:
            if type(values) != list:
                print "The argument 'values' must be an array of numbers."
                return
            elif len(values) != len(self.relax.data.param_types[model]):
                print "The argument 'values' must be an array of length equal to the number of parameters in the model."
                return
            for i in range(len(values)):
                if type(values[i]) != float and type(values[i]) != int:
                    print "The argument 'values' must be an array of numbers."
                    return

        # The print flag.
        if type(print_flag) != int:
            print "The print_flag argument must be an integer."
            return

        # Execute the functional code.
        self.relax.min.fixed(model=model, values=values, print_flag=print_flag)
