from re import match


class Tab:
    def __init__(self, readline):
        """The interpreter class."""

        self.readline = readline


    def run(self, switch):
        """Run the python interpreter.

        The namespace of this function is the namespace seen inside the interpreter.  All macros
        should be defined in this namespace.
        """

        if match("[Oo][Ff][Ff]", switch):
            self.readline.parse_and_bind()
        elif match("[Oo][Nn]", switch):
            self.readline.parse_and_bind("tab: complete")
        else:
            print "Invalid tab option."
