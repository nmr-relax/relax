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


    def diffusion_tensor(self, run=None, params=None, time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0):
        """Macro for setting up the diffusion tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run to assign the data to.

        params:  The parameters argument containing the diffusion tensor data.

        time_scale:  Value to scale the correlation time parameters values by.

        d_scale:  Value to scale the diffusion tensor eigenvalue parameters values by.

        angle_units:  The units for the angle parameters.

        param_types:  A flag to select different parameter combinations.


        Description
        ~~~~~~~~~~~

        To select isotropic diffusion, the parameters argument should be a single floating point
        number.  The number is the value of the isotropic global correlation time in seconds.  To
        specify the time in nanoseconds, set the 'time_scale' argmuent to 1e-9.  Alternative
        parameters can be used by changing the 'param_types' flag to the following integers:
            0 - tm   (Default)
            1 - Diso

        To select axially symmetric anisotropic diffusion, the parameters argument should be a tuple
        of floating point numbers of length four.  A tuple is a type of data structure enclosed in
        round brakets, the elements of which are separated by commas.  Alternative sets of
        parameters are:
            0 - (Dpar, Dper, theta, phi)   (Default)
            1 - (tm, Dratio, theta, phi)
        Dratio is defined as Dpar/Dper.

        To select fully anisotropic diffusion, the parameters argument should be a tuple of length
        six.  Alternative sets of parameters are:
            0 - (Dx, Dy, Dz, alpha, beta, gamma)   (Default)

        The 'time_scale' argument should be a floating point number.  Parameters affected by this
        value are:  tm.

        The 'd_scale' argument should also be a floating point number.  Parameters affected by this
        value are:  Diso; Dratio; Dpar; Dper; Dx; Dy; Dz.

        The 'angle_units' argument should either be the string 'deg' or 'rad'.  Parameters affected
        are:  theta, phi, alpha, beta, gamma.


        Examples
        ~~~~~~~~

        To set an isotropic diffusion tensor with a correlation time of 10ns, assigning it to the
        run 'm1', type:

        relax> diffusion_tensor('m1', 10e-9)
        relax> diffusion_tensor(run='m1', params=10e-9)
        relax> diffusion_tensor('m1', 10.0, 1e-9)
        relax> diffusion_tensor(run='m1', params=10.0, time_scale=1e-9)


        To select an axially symmetric diffusion tensor with a Dpar value of 1.698e7, Dper value of
        1.417e7, Theta value of 67.174°, and Phi value of -83.718°, and assign it to the run 'axial',
        type one of:

        relax> diffusion_tensor('axial', (1.698e7, 1.417e7, 67.174, -83.718))
        relax> diffusion_tensor(run='axial', params=(1.698e7, 1.417e7, 67.174, -83.718))
        relax> diffusion_tensor('axial', (1.698e-1, 1.417e-1, 67.174, -83.718), d_scale=1e8)
        relax> diffusion_tensor(run='axial', params=(1.698e-1, 1.417e-1, 67.174, -83.718),
                                d_scale=1e8)
        relax> diffusion_tensor('axial', (1.698e-1, 1.417e-1, 1.1724, -1.4612), d_scale=1e8,
                                angle_units='rad')
        relax> diffusion_tensor(run='axial', params=(1.698e-1, 1.417e-1, 1.1724, -1.4612),
                                d_scale=1e8, angle_units='rad')


        To select axially symmetric diffusion with a tm value of 8.5ns, Dratio of 1.1, Theta value
        of 20°, and Phi value of 20°, and assign it to the run '26', type:

        relax> diffusion_tensor('axial', (8.5e-9, 1.1, 20.0, 20.0), param_types=1)


        To select fully anisotropic diffusion, type:

        relax> diffusion_tensor('m5', (1.340e7, 1.516e7, 1.691e7, -82.027, -80.573, 65.568))
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "diffusion_tensor.set("
            text = text + "run=" + `run`
            text = text + ", params=" + `params`
            text = text + ", time_scale=" + `time_scale`
            text = text + ", d_scale=" + `d_scale`
            text = text + ", angle_units=" + `angle_units`
            text = text + ", param_types=" + `param_types` + ")"
            print text

        # The name of the run.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Parameter argument.
        if type(params) != float and type(params) != tuple:
            raise RelaxTupleFloatError, ('diffusion parameters', params)
        if type(params) == tuple:
            if len(params) != 4 and len(params) != 6:
                raise RelaxError, "The diffusion parameters argument should either be a floating point number or a tuple of length 4 or 6."
            for i in xrange(len(params)):
                if type(params[i]) != float:
                    raise RelaxTupleFloatError, ('diffusion parameters', params)

        # Time scale argument.
        if type(time_scale) != float:
            raise RelaxFloatError, ('time scale', time_scale)

        # D scale argument.
        if type(d_scale) != float:
            raise RelaxFloatError, ('D scale', d_scale)

        # Angle scale units argument.
        if type(angle_units) != str:
            raise RelaxStrError, ('angle units', angle_units)

        # Parameter types argument.
        if type(param_types) != int:
            raise RelaxIntError, ('parameter types', param_types)

        # Check the validity of the angle_units argument.
        valid_types = ['deg', 'rad']
        if not angle_units in valid_types:
            raise RelaxError, "The diffusion tensor 'angle_units' argument " + `angle_units` + " should be either 'deg' or 'rad'."

        # Execute the functional code.
        self.relax.diffusion_tensor.set(run=run, params=params, time_scale=time_scale, d_scale=d_scale, angle_units=angle_units, param_types=param_types)
