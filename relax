#! /usr/bin/python

###############################################################################
#                                                                             #
#                                    relax                                    #
#                                                                             #
#                   a program for relaxation data analysis                    #
#                                                                             #
#                             by Edward d'Auvergne                            #
#                                                                             #
###############################################################################
#                                                                             #
#                                   License                                   #
#                                                                             #
# relax, a program for relaxation data analysis.                              #
#                                                                             #
# Copyright (C) 2003, 2004  Edward d'Auvergne                                 #
#                                                                             #
# This program is free software; you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU Library General Public License for more details.                        #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program; if not, write to the Free Software                 #
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.  #
#                                                                             #
###############################################################################


import __builtin__
import profile
import pstats
from re import match
import sys

from angles import Angles
from create_run import Create_run
from data.main import Data
from delete import Delete
from diffusion_tensor import Diffusion_tensor
from dx.map import Map
from dx.opendx import OpenDX
from errors import RelaxErrors
from file_ops import File_ops
from fix import Fix
from min import Minimise
from model_free import Model_free
from model_selection import Model_selection
from nuclei import Nuclei
from palmer import Palmer
from pdb import PDB
from prompt.interpreter import Interpreter
from relax_data import Rx_data
from rw import RW
from selection import Selection
from sequence import Sequence
from specific_setup import Specific_setup
from state import State
from value import Value
from vectors import Vectors
from view import View

sys.path.append(sys.path[0])
sys.path[0] = '.'


class Relax:
    def __init__(self, argv):
        """The top level class."""

        self.argv = argv

        # Set up the user errors.
        RelaxErrors()

        # Test if all the dependencies are installed.
        self.test_deps()

        # Create a string to pass to the interpreter to print.
        self.set_intro_string()

        # Debugging option, 0 = off, 1 = on.
        self.debug = 0

        # The program data storage class.
        self.data = Data()

        # Various functions.
        self.angles = Angles(self)
        self.create_run = Create_run(self)
        self.delete = Delete(self)
        self.diffusion_tensor = Diffusion_tensor(self)
        self.file_ops = File_ops(self)
        self.fix = Fix(self)
        self.map = Map(self)
        self.min = Minimise(self)
        self.model_free = Model_free(self)
        self.model_selection = Model_selection(self)
        self.nuclei = Nuclei(self)
        self.opendx = OpenDX(self)
        self.palmer = Palmer(self)
        self.pdb = PDB(self)
        self.relax_data = Rx_data(self)
        self.rw = RW(self)
        self.selection = Selection(self)
        self.sequence = Sequence(self)
        self.specific_setup = Specific_setup(self)
        self.state = State(self)
        self.value = Value(self)
        self.vectors = Vectors(self)
        self.view = View(self)

        # Process the command line arguments.
        self.arguments()

        # Run the interpreter.
        self.interpreter = Interpreter(self)
        self.interpreter.run()


    def arguments(self):
        """Function for processing the command line arguments."""

        # Initialise.
        self.script_file = None

        # No arguments are given.
        if len(self.argv) == 1:
            return

        # Help.
        elif match('--help', self.argv[1]) or match('-h', self.argv[1]):
            self.print_help()
            sys.exit()

        # Script file.
        elif type(self.argv[1]) == str and len(self.argv) == 2:
            self.script_file = self.argv[1]

        # Unknown argument.
        else:
            print "Try \"relax --help\" for more information."
            sys.exit()


    def print_help(self):
        """Print the help message."""

        sys.stderr.write("\nUsage: relax [-h] [--help] [script]\n")
        sys.stderr.write("Options:\n")
        sys.stderr.write("   --help       Display this help and exit.\n\n")


    def set_intro_string(self):
        """Create the program introduction."""

        self.intro_string = """


                                            relax

                           a program for relaxation data analysis

                            Copyright (C) 2003 Edward d'Auvergne


This is free software which you are welcome to modify and redistribute under the conditions of the
GNU General Public License (GPL).  This program, including all modules, is licensed under the GPL
and comes with absolutely no warranty.  For details type GPL.
"""

    def test_deps(self):
        """Function for testing if all depenencies are installed."""

        # Initialisation.
        deps_ok = 1

        # Numeric.
        try:
            import Numeric
        except ImportError:
            error = RelaxDepError('Numeric')
            sys.stderr.write(error.__str__())
            deps_ok = 0

        # ScientificPython.
        try:
            import Scientific
        except ImportError:
            error = RelaxDepError('Scientific')
            sys.stderr.write(error.__str__())
            deps_ok = 0

        # Quit if the deps are not installed.
        if not deps_ok:
            sys.stderr.write('\n')
            sys.exit()


if __name__ == "__main__":
    # Change this flag to 1 for code profiling.
    profile_flag = 0

    if not profile_flag:
        Relax(sys.argv)
    else:
        def print_stats(stats):
            pstats.Stats(stats).sort_stats(-1).print_stats()

        profile.Profile.print_stats = print_stats
        profile.run('Relax(sys.argv)')
