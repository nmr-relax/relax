from generic_functions import Generic_functions


class Print_all_data(Generic_functions):
    def __init__(self, relax):
        """Class containing the macros for manipulating the program state."""

        self.relax = relax


    def __repr__(self):
        """Macro for printing all the data in self.relax.data"""

        string = ""
        # Loop over the data structures in self.relax.data
        for name in dir(self.relax.data):
            if not self.filter_data_structure(name):
                string = string +  "self.relax.data." + name + ":\n" + `getattr(self.relax.data, name)` + "\n\n"
        return string
