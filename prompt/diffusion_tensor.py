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


class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the macro for setting up the diffusion tensor."""

        self.relax = relax


    def set(self, diff=None, params=None):
        """Macro for setting up the diffusion tensor."""

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = self.relax.interpreter.macro_prompt + "diffusion_tensor.set("
            text = text + "diff=" + `diff`
            text = text + ", params=" + `params` + ")\n"
            print text

        # Diffusion tensor argument.
        if diff == None:
            print "No diffusion tensor given."
            return
        elif type(diff) != str:
            print "The argument 'diff' must be a string."
            return

        # Isotropic diffusion tensor parameters.
        elif diff == 'iso' and type(params) != float:
            print "For isotropic diffusion the 'params' argument must be a floating point number."
            return

        # Axially symmetric diffusion tensor parameters.
        elif diff == 'axial':
            if type(params) != list:
                print "For axially symmetric diffusion the 'params' argument must be an array."
                return
            elif len(params) != 3:
                print "For axially symmetric diffusion the 'params' argument must be an array of three elements."
                return
            for i in range(len(params)):
                if type(params[i]) != float:
                    print "The elements of the 'params' array must be floating point numbers."
                    return

        # Anisotropic diffusion tensor parameters.
        elif diff == 'aniso':
            if type(params) != list:
                print "For anisotropic diffusion the 'params' argument must be an array."
                return
            elif len(params) != 6:
                print "For anisotropic diffusion the 'params' argument must be an array of six elements."
                return
            for i in range(len(params)):
                if type(params[i]) != float:
                    print "The elements of the 'params' array must be floating point numbers."
                    return

        # Execute the functional code.
        self.relax.diffusion_tensor.set(diff=diff, params=params)
