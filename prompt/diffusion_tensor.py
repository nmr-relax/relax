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

import sys


class Diffusion_tensor:
    def __init__(self, relax):
        """Class containing the macro for setting up the diffusion tensor."""

        self.relax = relax


    def diffusion_tensor(self, run=None, diff=None, params=None):
        """Macro for setting up the diffusion tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        diff:  The type of diffusion tensor.

        params:  The diffusion tensor data.


        Description
        ~~~~~~~~~~~

        The argument 'diff' specifies the type of diffusion tensor and can be one of the following:
            iso - Isotropic diffusion.
            axial - Axially symmetric anisotropy.
            aniso - Anisotropic diffusion.

        The 'params' argument is dependent on the 'diff' argument.  If isotropic diffusion is
        selected then the params argument should be a single floating point number corresponding to
        the global correlation time.  If axially symmetric diffusion is selected then it should be a
        vector of numbers with a length of four.  If anisotropic diffusion is selected then it
        should be a vector of numbers with a length of six.
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "diffusion_tensor.set("
            text = text + "run=" + `run`
            text = text + ", diff=" + `diff`
            text = text + ", params=" + `params` + ")"
            print text

        # The name of the run.
        if type(run) != str:
            print "The run name must be a string."
            return

        # Isotropic diffusion tensor parameters.
        if diff == 'iso':
            if type(params) != float:
                print "For isotropic diffusion the 'params' argument must be a floating point number."
                return

        # Axially symmetric diffusion tensor parameters.
        elif diff == 'axial':
            if type(params) != list:
                print "For axially symmetric diffusion the 'params' argument must be an array."
                return
            elif len(params) != 4:
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

        # Diffusion tensor argument.
        elif diff == None:
            print "No diffusion tensor given."
            return
        else:
            print "The argument 'diff' must be one of 'iso', 'axial', or 'aniso'."
            return

        # Execute the functional code.
        self.relax.diffusion_tensor.set(run=run, diff=diff, params=params)
