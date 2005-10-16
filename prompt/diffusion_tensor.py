###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


class Diffusion_tensor:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for manipulating the diffusion tensor."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def copy(self, run1=None, run2=None):
        """Function for copying diffusion tensor data from run1 to run2.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run1:  The name of the run to copy the sequence from.

        run2:  The name of the run to copy the sequence to.


        Description
        ~~~~~~~~~~~

        This function will copy the diffusion tensor data from 'run1' to 'run2'.  'run2' must not
        contain any diffusion tensor data.


        Examples
        ~~~~~~~~

        To copy the diffusion tensor from run 'm1' to run 'm2', type:

        relax> diffusion_tensor.copy('m1', 'm2')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "diffusion_tensor.copy("
            text = text + "run1=" + `run1`
            text = text + ", run2=" + `run2` + ")"
            print text

        # The run1 argument.
        if type(run1) != str:
            raise RelaxStrError, ('run1', run1)

        # The run2 argument.
        if type(run2) != str:
            raise RelaxStrError, ('run2', run2)

        # Execute the functional code.
        self.__relax__.generic.diffusion_tensor.copy(run1=run1, run2=run2)


    def delete(self, run=None):
        """Function for deleting diffusion tensor data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.



        Description
        ~~~~~~~~~~~

        This function will delete all diffusion tensor data for the given run.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "diffusion_tensor.delete("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.diffusion_tensor.delete(run=run)


    def display(self, run=None):
        """Function for displaying the diffusion tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "diffusion_tensor.display("
            text = text + "run=" + `run` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Execute the functional code.
        self.__relax__.generic.diffusion_tensor.display(run=run)


    def set(self, run=None, params=None, time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, axial_type=None, fixed=1):
        """Function for setting up the diffusion tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run to assign the data to.

        params:  The diffusion tensor data.

        time_scale:  The correlation time scaling value.

        d_scale:  The diffusion tensor eigenvalue scaling value.

        angle_units:  The units for the angle parameters.

        param_types:  A flag to select different parameter combinations.

        axial_type:  A string, which if supplied with axially symmetric parameters, will restrict
        the tensor to either being 'oblate' or 'prolate'.

        fixed:  A flag specifying whether the diffusion tensor is fixed or can be optimised.


        Description
        ~~~~~~~~~~~

        Isotropic diffusion.

        To select isotropic diffusion, the parameters argument should be a single floating point
        number.  The number is the value of the isotropic global correlation time in seconds.  To
        specify the time in nanoseconds, set the 'time_scale' argument to 1e-9.  Alternative
        parameters can be used by changing the 'param_types' flag to the following integers

            0:  tm   (Default),
            1:  Diso,

        where

            tm = 1 / 6Diso.


        Axially symmetric diffusion.

        To select axially symmetric anisotropic diffusion, the parameters argument should be a tuple
        of floating point numbers of length four.  A tuple is a type of data structure enclosed in
        round brackets, the elements of which are separated by commas.  Alternative sets of
        parameters, 'param_types', are

            0:  (tm, Da, theta, phi)   (Default),
            1:  (tm, Dratio, theta, phi),
            2:  (Dpar, Dper, theta, phi),
            3:  (Diso, Da, theta, phi),
            4:  (Diso, Dratio, theta, phi),

        where

            tm = 1 / 6Diso,
            Diso = 1/3 (Dpar + 2Dper),
            Da = 1/3 (Dpar - Dper),
            Dratio = Dpar / Dper.

        The diffusion tensor is defined by the vector Dpar.  The angle alpha describes the bond
        vector with respect to the diffusion frame while the spherical angles {theta, phi} describe
        the diffusion tensor with respect to the PDB frame.  theta is the polar angle and phi is the
        azimuthal angle defined between

            0 <= theta <= pi,
            0 <= phi <= 2pi.

        The angle alpha is defined between

            0 <= alpha <= 2pi.

        The 'axial_type' argument should be 'oblate', 'prolate', or None.  The argument will be
        ignored if the diffusion tensor is not axially symmetric.  If 'oblate' is given, then the
        constraint Dper >= Dpar is used.  If 'prolate' is given, then the constraint Dper <= Dpar is
        used.  If nothing is supplied, then Dper and Dpar will be allowed to have any values.  To
        prevent minimisation of diffusion tensor parameters in a space with two minima, it is
        recommended to specify which tensor to be minimised, thereby partitioning the two minima
        into the two subspaces (the partition is where Da equals 0).


        Anisotropic diffusion.

        To select fully anisotropic diffusion, the parameters argument should be a tuple of length
        six.  A tuple is a type of data structure enclosed in round brackets, the elements of which
        are separated by commas.  Alternative sets of parameters, 'param_types', are

            0:  (tm, Da, Dr, alpha, beta, gamma)   (Default),
            1:  (Diso, Da, Dr, alpha, beta, gamma),
            2:  (Dx, Dy, Dz, alpha, beta, gamma),

        where

            tm = 1 / 6Diso,
            Diso = 1/3 (Dx + Dy + Dz),
            Da = 1/3 (Dz - (Dx + Dy)/2),
            Dr = (Dx - Dy)/2.

        The angles alpha, beta, and gamma are the Euler angles describing the diffusion tensor
        within the PDB frame.  These angles are defined using the z-y-z axis rotation notation where
        alpha is the initial rotation angle around the z-axis, beta is the rotation angle around the
        y-axis, and gamma is the final rotation around the z-axis again.  The angles are defined
        between

            0 <= alpha <= 2pi,
            0 <= beta <= pi,
            0 <= gamma <= 2pi.

        Within the PDB frame, the bond vector is described using the spherical angels theta and phi
        where theta is the polar angle and phi is the azimuthal angle defined between

            0 <= theta <= pi,
            0 <= phi <= 2pi.


        Units.

        The 'time_scale' argument should be a floating point number.  Parameters affected by this
        value are:  tm.

        The 'd_scale' argument should also be a floating point number.  Parameters affected by this
        value are:  Diso; Dpar; Dper; Da; Dr; Dx; Dy; Dz.

        The 'angle_units' argument should either be the string 'deg' or 'rad'.  Parameters affected
        are:  theta; phi; alpha; beta; gamma.



        Examples
        ~~~~~~~~

        To set an isotropic diffusion tensor with a correlation time of 10 ns, assigning it to the
        run 'm1', type:

        relax> diffusion_tensor('m1', 10e-9)
        relax> diffusion_tensor(run='m1', params=10e-9)
        relax> diffusion_tensor('m1', 10.0, 1e-9)
        relax> diffusion_tensor(run='m1', params=10.0, time_scale=1e-9, fixed=1)


        To select axially symmetric diffusion with a tm value of 8.5 ns, Dratio of 1.1, theta value
        of 20 degrees, and phi value of 20 degrees, and assign it to the run 'm8', type:

        relax> diffusion_tensor('m8', (8.5e-9, 1.1, 20.0, 20.0), param_types=1)


        To select an axially symmetric diffusion tensor with a Dpar value of 1.698e7, Dper value of
        1.417e7, theta value of 67.174 degrees, and phi value of -83.718 degrees, and assign it to
        the run 'axial', type one of:

        relax> diffusion_tensor('axial', (1.698e7, 1.417e7, 67.174, -83.718), param_types=1)
        relax> diffusion_tensor(run='axial', params=(1.698e7, 1.417e7, 67.174, -83.718),
                                param_types=1)
        relax> diffusion_tensor('axial', (1.698e-1, 1.417e-1, 67.174, -83.718), param_types=1,
                                d_scale=1e8)
        relax> diffusion_tensor(run='axial', params=(1.698e-1, 1.417e-1, 67.174, -83.718),
                                param_types=1, d_scale=1e8)
        relax> diffusion_tensor('axial', (1.698e-1, 1.417e-1, 1.1724, -1.4612), param_types=1,
                                d_scale=1e8, angle_units='rad')
        relax> diffusion_tensor(run='axial', params=(1.698e-1, 1.417e-1, 1.1724, -1.4612),
                                param_types=1, d_scale=1e8, angle_units='rad', fixed=1)


        To select fully anisotropic diffusion, type:

        relax> diffusion_tensor('m5', (1.340e7, 1.516e7, 1.691e7, -82.027, -80.573, 65.568),
                                param_types=2)


        To select and minimise an isotropic diffusion tensor, type (followed by a minimisation
        command):

        relax> diffusion_tensor('diff', 10e-9, fixed=0)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "diffusion_tensor.set("
            text = text + "run=" + `run`
            text = text + ", params=" + `params`
            text = text + ", time_scale=" + `time_scale`
            text = text + ", d_scale=" + `d_scale`
            text = text + ", angle_units=" + `angle_units`
            text = text + ", param_types=" + `param_types`
            text = text + ", axial_type=" + `axial_type`
            text = text + ", fixed=" + `fixed` + ")"
            print text

        # The name of the run.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Parameter argument.
        if type(params) != int and type(params) != float and type(params) != tuple:
            raise RelaxNumTupleError, ('diffusion parameters', params)
        if type(params) == tuple:
            if len(params) != 4 and len(params) != 6:
                raise RelaxError, "The diffusion parameters argument must either be a number or a tuple of numbers of length 4 or 6."
            for i in xrange(len(params)):
                if type(params[i]) != float and type(params[i]) != int:
                    raise RelaxNumTupleError, ('diffusion parameters', params)

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

        # Axial type argument.
        if axial_type != None and type(axial_type) != str:
            raise RelaxNoneStrError, ('axial type', axial_type)

        # The fixed flag.
        if type(fixed) != int or (fixed != 0 and fixed != 1):
            raise RelaxBinError, ('fixed flag', fixed)

        # Execute the functional code.
        self.__relax__.generic.diffusion_tensor.set(run=run, params=params, time_scale=time_scale, d_scale=d_scale, angle_units=angle_units, param_types=param_types, axial_type=axial_type, fixed=fixed)
