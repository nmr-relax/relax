###############################################################################
#                                                                             #
# Copyright (C) 2006-2011 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Module docstring.
"""Base classes for the GUI tests."""

# Python module imports.
import Queue
from traceback import print_exception
from unittest import TestCase

# relax module imports.
from prompt.interpreter import Interpreter
from status import Status; status = Status()


class GuiTestCase(TestCase):
    """The GUI specific test case."""

    def check_exceptions(self):
        """Check that no exception has occurred."""

        # Check.
        try:
            # Get the exception from the queue.
            index, exc = status.analyses.exception_queue.get(block=False)

            # Fail.
            self.fail()

        # No exception.
        except Queue.Empty:
            pass

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)
