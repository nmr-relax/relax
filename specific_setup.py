from re import match


class Specific_setup:
    def __init__(self, relax):
        """Class for equation type specific function setup."""

        self.relax = relax


    def setup(self, type, model):
        """Setup function."""

        # Initialisation.
        eqi = self.relax.data.equations[model]

        # Model-free analysis.
        if match("mf", eqi):
            if match("fixed", type):
                return self.relax.model_free.fixed_setup, self.relax.model_free.main_loop
            elif match("grid_search", type):
                return self.relax.model_free.grid_setup, self.relax.model_free.main_loop
            elif match("map_space", type):
                return self.relax.model_free.map_bounds, self.relax.model_free.main_loop
            elif match("minimise", type):
                return self.relax.model_free.main_loop
            elif match("print", type):
                return self.relax.model_free.print_header, self.relax.model_free.print_results

        # Unknown equation type.
        else:
            print "The equation " + `self.relax.data.equations[model]` + " has not been coded into the grid search macro."
            return

