###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################


from Numeric import Float64, array, zeros
import sys


class Fixed:
    def __init__(self, relax):
        """Class containing the fixed macro."""

        self.relax = relax


    def fixed(self, run=None, values=None, print_flag=1):
        """Macro for fixing the initial parameter values.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        values:  An array of numbers of length equal to the number of parameters in the model.

        print_flag:  The amount of information to print to screen.  Zero corresponds to minimal
        output while higher values increase the amount of output.  The default value is 1.


        Examples
        ~~~~~~~~

        This command will fix the parameter values of the run 'm2', which is the original
        model-free equation with parameters {S2, te}, before minimisation to the preselected values
        of this function.

        relax> fixed('m2')


        This command will do the same except the S2 and te values will be set to one and ten ps
        respectively.

        relax> fixed('m2', [1.0, 10 * 10e-12])
        relax> fixed(run='m2', values=[1.0, 10 * 10e-12])
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "fixed("
            text = text + "run=" + `run`
            text = text + ", values=" + `values`
            text = text + ", print_flag=" + `print_flag` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise UserArgStrError, ('run', run)

        # User defined values.
        if values != None:
            if type(values) != list:
                raise UserArgListError, ('values', values)
            for i in range(len(values)):
                if type(values[i]) != float and type(values[i]) != int:
                    raise UserArgListIntError, ('values', values)

        # The print flag.
        if type(print_flag) != int:
            raise UserArgIntError, ('print_flag', print_flag)

        # Execute the functional code.
        self.relax.min.fixed(run=run, values=values, print_flag=print_flag)
