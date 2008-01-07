###############################################################################
#                                                                             #
# Copyright (C) 2004-2005 Edward d'Auvergne                                   #
# Copyright (C) 2007 Sebastien Morin                                          #
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

import sys

import help


class Consistency_tests:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class containing functions specific to consistency tests for datasets from different fields."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def set_frq(self, run=None, frq=None):
        """Function for selecting which relaxation data to use in the consistency tests.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        frq:  The spectrometer frequency in Hz.


        Description
        ~~~~~~~~~~~

        This function will select the relaxation data to use in the consistency tests corresponding
        to the given frequencies.


        Examples
        ~~~~~~~~

        relax> consistency_tests.set_frq('test', 600.0 * 1e6)
        relax> consistency_tests.set_frq(run='test', frq=600.0 * 1e6)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "consistency_tests.set_frq("
            text = text + "run=" + `run`
            text = text + ", frq=" + `frq` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The frq arguments.
        if type(frq) != float:
            raise RelaxStrError, ('frq', frq)

        # Execute the functional code.
        self.__relax__.specific.consistency_tests.set_frq(run=run, frq=frq)
