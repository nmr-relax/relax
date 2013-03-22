#! /usr/bin/env python

"""Script for running the full relax test suite against different python versions."""

# Python module imports.
from os import F_OK, X_OK, access, sep, system
from sys import argv


# Variables.
COMPILER = 'gcc'
PATH_PREFIX = '/usr/local'


class Main:
    def __init__(self):
        """Setup, build and run."""

        # The command line arguments.
        self.get_args()

        # Check the python version.
        self.check_for_python()

        # Compile.
        self.compile()

        # Run the test suite.
        system("%s .%srelax --test-suite" % (self.path, sep))


    def compile(self):
        """Compile the C modules."""

        # Print out.

        print("\n"*2)
        print("#"*27)
        print("# Compiling the C modules #")
        print("#"*27)
        print("\n"*2)

        # Assume Linux (to be fixed later).
        include = PATH_PREFIX + sep + 'include' + sep + self.python
        numpy_core = PATH_PREFIX + sep + 'lib' + sep + self.python + sep + 'site-packages'+sep+'numpy'+sep+'core'+sep+'include'

        # The compilation commands.
        commands = []
        commands.append("%s -o target_functions/c_chi2.os -c -I%s -I%s -fPIC target_functions/c_chi2.c" % (COMPILER, include, numpy_core))
        commands.append("%s -o target_functions/exponential.os -c -I%s -I%s -fPIC target_functions/exponential.c" % (COMPILER, include, numpy_core))
        commands.append("%s -o target_functions/relax_fit.os -c -I%s -I%s -fPIC target_functions/relax_fit.c" % (COMPILER, include, numpy_core))
        commands.append("%s -o target_functions/relax_fit.so -shared target_functions/c_chi2.os target_functions/exponential.os target_functions/relax_fit.os" % COMPILER)

        # Execute.
        for command in commands:
            print(command)
            system(command)

        # End printout.
        print("\nDone")
        print("\n"*4)


    def check_for_python(self):
        """Check for the Python binary."""

        # The full path.
        self.python = 'python' + self.version
        self.path = PATH_PREFIX + sep + 'bin' + sep + self.python

        # Does it exist.
        if not access(self.path, F_OK):
            raise NameError("The Python binary '%s' cannot be found." % self.path)

        # Executable.
        if not access(self.path, X_OK):
            raise NameError("The Python binary '%s' is not executable." % self.path)


    def get_args(self):
        """Test and return the command line arguments."""

        # The Python version must be supplied.
        if len(argv) == 1:
            raise NameError("The Python version number must be supplied as the first argument.")

        # No other args are allowed.
        if len(argv) > 2:
            raise NameError("Only the Python version number is allowed as an argument.")

        # The python version.
        self.version = argv[1]


if __name__ == '__main__':
    Main()
