class select_res:
    def __init__(self):
        """Base class containing functions for the selection of residues."""


    def select_residues(self):
        """Function for the selection of residues.

        A list of the indecies of the selected residues is returned.
        """

        # Test if too many arguments are given.
        if len(self.sel) > 2:
            print "A maximum of two arguments for residue selection is allowed."
            return

        # Initialise the list of indecies.
        indecies = []

        # Both residue name and number are given.
        if len(self.sel) == 2:
            if type(self.sel[0]) == int and type(self.sel[1]) == str:
                num = self.sel[0]
                name = self.sel[1]
            elif type(self.sel[0]) == str and type(self.sel[1]) == int:
                name = self.sel[0]
                num = self.sel[1]
            else:
                print "If two arguments for residue selection are given, then they should be an integer and string."
                return

            for i in range(len(self.relax.data.seq)):
                if num == self.relax.data.seq[i][0] and name == self.relax.data.seq[i][1]:
                    indecies.append(i)

        # A single argument is given.
        elif len(self.sel) == 1:
            # Residue number.
            if type(self.sel[0]) == int:
                for i in range(len(self.relax.data.seq)):
                    if self.sel[0] == self.relax.data.seq[i][0]:
                        indecies.append(i)

            # Residue  name.
            elif type(self.sel[0]) == str:
                for i in range(len(self.relax.data.seq)):
                    if self.sel[0] == self.relax.data.seq[i][1]:
                        indecies.append(i)

            # Unknown argument.
            else:
                print "Unknown argument, should be either an integer or string."
                return

        # No arguments are given, therefore select all.
        else:
            for i in range(len(self.relax.data.seq)):
                indecies.append(i)

        # Return the list of indecies.
        return indecies
