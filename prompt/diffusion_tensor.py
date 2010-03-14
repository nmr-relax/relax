###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007-2010 Edward d'Auvergne                        #
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
"""Module containing the 'diffusion_tensor' user function class."""
__docformat__ = 'plaintext'

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import diffusion_tensor
from relax_errors import RelaxError


class Diffusion_tensor(User_fn_class):
    """Class for manipulating the diffusion tensor."""

    def copy(self, pipe_from=None, pipe_to=None):
        """Function for copying diffusion tensor data from one data pipe to another.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the data pipe to copy the diffusion tensor data from.

        pipe_to:  The name of the data pipe to copy the diffusion tensor data to.


        Description
        ~~~~~~~~~~~

        This function will copy the diffusion tensor data between data pipes.  The destination data
        pipe must not contain any diffusion tensor data.  If the pipe_from or pipe_to arguments are
        not supplied, then both will default to the current data pipe (hence giving one argument is
        essential).


        Examples
        ~~~~~~~~

        To copy the diffusion tensor from the data pipe 'm1' to the current data pipe, type:

        relax> diffusion_tensor.copy('m1')
        relax> diffusion_tensor.copy(pipe_from='m1')


        To copy the diffusion tensor from the current data pipe to the data pipe 'm9', type:

        relax> diffusion_tensor.copy(pipe_to='m9')


        To copy the diffusion tensor from the data pipe 'm1' to 'm2', type:

        relax> diffusion_tensor.copy('m1', 'm2')
        relax> diffusion_tensor.copy(pipe_from='m1', pipe_to='m2')
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "diffusion_tensor.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        diffusion_tensor.copy(pipe_from=pipe_from, pipe_to=pipe_to)


    def delete(self):
        """Function for deleting diffusion tensor data.

        Description
        ~~~~~~~~~~~

        This function will delete all diffusion tensor data from the current data pipe.
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "diffusion_tensor.delete()"
            print(text)

        # Execute the functional code.
        diffusion_tensor.delete()


    def display(self):
        """Function for displaying the diffusion tensor information."""

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "diffusion_tensor.display()"
            print(text)

        # Execute the functional code.
        diffusion_tensor.display()


    def init(self, params=None, time_scale=1.0, d_scale=1.0, angle_units='deg', param_types=0, spheroid_type=None, fixed=True):
        """Function for initialising the diffusion tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        params:  The diffusion tensor data.

        time_scale:  The correlation time scaling value.

        d_scale:  The diffusion tensor eigenvalue scaling value.

        angle_units:  The units for the angle parameters.

        param_types:  A flag to select different parameter combinations.

        spheroid_type:  A string which, if supplied together with spheroid parameters, will restrict
        the tensor to either being 'oblate' or 'prolate'.

        fixed:  A flag specifying whether the diffusion tensor is fixed or can be optimised.


        The sphere (isotropic diffusion)
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        When the molecule diffuses as a sphere, all three eigenvalues of the diffusion tensor are
        equal, Dx = Dy = Dz.  In this case, the orientation of the XH bond vector within the
        diffusion frame is inconsequential to relaxation, hence, the spherical or Euler angles are
        undefined.  Therefore solely a single geometric parameter, either tm or Diso, can fully and
        sufficiently parameterise the diffusion tensor.  The correlation function for the global
        rotational diffusion is

        -----
                     1   - tau / tm
            C(tau) = - e            ,
                     5
        -----

        To select isotropic diffusion, the parameters argument should be a single floating point
        number.  The number is the value of the isotropic global correlation time, tm, in seconds.
        To specify the time in nanoseconds, set the 'time_scale' argument to 1e-9.  Alternative
        parameters can be used by changing the 'param_types' flag to the following integers

            0:  {tm}   (Default),
            1:  {Diso},

        where

            1 / tm = 6Diso.


        The spheroid (axially symmetric diffusion)
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        When two of the three eigenvalues of the diffusion tensor are equal, the molecule diffuses
        as a spheroid.  Four pieces of information are required to specify this tensor, the two
        geometric parameters, Diso and Da, and the two orientational parameters, the polar angle
        theta and the azimuthal angle phi describing the orientation of the axis of symmetry.  The
        correlation function of the global diffusion is

        -----
                       _1_
                     1 \          - tau / tau_i
            C(tau) = -  >  ci . e              ,
                     5 /__
                       i=-1
        -----

        where

            c-1 = 1/4 (3 dz^2 - 1)^2,
            c0  = 3 dz^2 (1 - dz^2),
            c1  = 3/4 (dz^2 - 1)^2,

        and

            1 / tau -1 = 6Diso - 2Da,
            1 / tau 0  = 6Diso - Da,
            1 / tau 1  = 6Diso + 2Da.

        The direction cosine dz is defined as the cosine of the angle alpha between the XH bond
        vector and the unique axis of the diffusion tensor.

        To select axially symmetric anisotropic diffusion, the parameters argument should be a tuple
        of floating point numbers of length four.  A tuple is a type of data structure enclosed in
        round brackets, the elements of which are separated by commas.  Alternative sets of
        parameters, 'param_types', are

            0:  {tm, Da, theta, phi}   (Default),
            1:  {Diso, Da, theta, phi},
            2:  {tm, Dratio, theta, phi},
            3:  {Dpar, Dper, theta, phi},
            4:  {Diso, Dratio, theta, phi},

        where

            tm = 1 / 6Diso,
            Diso = 1/3 (Dpar + 2Dper),
            Da = Dpar - Dper,
            Dratio = Dpar / Dper.

        The spherical angles {theta, phi} orienting the unique axis of the diffusion tensor within
        the PDB frame are defined between

            0 <= theta <= pi,
            0 <= phi <= 2pi,

        while the angle alpha which is the angle between this axis and the given XH bond vector is
        defined between

            0 <= alpha <= 2pi.

        The 'spheroid_type' argument should be 'oblate', 'prolate', or None.  The argument will be
        ignored if the diffusion tensor is not axially symmetric.  If 'oblate' is given, then the
        constraint Da <= 0 is used while if 'prolate' is given, then the constraint Da >= 0 is
        used.  If nothing is supplied, then Da will be allowed to have any values.  To prevent
        minimisation of diffusion tensor parameters in a space with two minima, it is recommended
        to specify which tensor is to be minimised, thereby partitioning the two minima into the two
        subspaces along the boundry Da = 0.


        The ellipsoid (rhombic diffusion)
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        When all three eigenvalues of the diffusion tensor are different, the molecule diffuses as
        an ellipsoid.  This diffusion is also known as fully anisotropic, asymmetric, or rhombic.
        The full tensor is specified by six pieces of information, the three geometric parameters
        Diso, Da, and Dr representing the isotropic, anisotropic, and rhombic components of the
        tensor, and the three Euler angles alpha, beta, and gamma orienting the tensor within the
        PDB frame.  The correlation function is


        -----
                       _2_
                     1 \          - tau / tau_i
            C(tau) = -  >  ci . e              ,
                     5 /__
                       i=-2
        -----

        where the weights on the exponentials are

            c-2 = 1/4 (d + e),
            c-1 = 3 dy^2 dz^2,
            c0  = 3 dx^2 dz^2,
            c1  = 3 dx^2 dy^2,
            c2  = 1/4 (d + e).

        Let

            R = sqrt(1 + 3Dr),

        then

            d = 3 (dx^4 + dy^4 + dz^4) - 1,
            e = - 1 / R ((1 + 3Dr)(dx^4 + 2dy^2 dz^2) + (1 - 3Dr)(dy^4 + 2dx^2 dz^2) - 2(dz^4 + 2dx^2 dy^2)).

        The correlation times are

            1 / tau -2 = 6Diso - 2Da . R,
            1 / tau -1 = 6Diso - Da (1 + 3Dr),
            1 / tau 0  = 6Diso - Da (1 - 3Dr),
            1 / tau 1  = 6Diso + 2Da,
            1 / tau 1  = 6Diso + 2Da . R.

        The three direction cosines dx, dy, and dz are the coordinates of a unit vector parallel to
        the XH bond vector.  Hence the unit vector is [dx, dy, dz].

        To select fully anisotropic diffusion, the parameters argument should be a tuple of length
        six.  A tuple is a type of data structure enclosed in round brackets, the elements of which
        are separated by commas.  Alternative sets of parameters, 'param_types', are

            0:  {tm, Da, Dr, alpha, beta, gamma}   (Default),
            1:  {Diso, Da, Dr, alpha, beta, gamma},
            2:  {Dx, Dy, Dz, alpha, beta, gamma},
            3:  {Dxx, Dyy, Dzz, Dxy, Dxz, Dyz},

        where

            tm = 1 / 6Diso,
            Diso = 1/3 (Dx + Dy + Dz),
            Da = Dz - (Dx + Dy)/2,
            Dr = (Dy - Dx)/2Da.

        The angles alpha, beta, and gamma are the Euler angles describing the diffusion tensor
        within the PDB frame.  These angles are defined using the z-y-z axis rotation notation where
        alpha is the initial rotation angle around the z-axis, beta is the rotation angle around the
        y-axis, and gamma is the final rotation around the z-axis again.  The angles are defined
        between

            0 <= alpha <= 2pi,
            0 <= beta <= pi,
            0 <= gamma <= 2pi.

        Within the PDB frame, the XH bond vector is described using the spherical angles theta and
        phi where theta is the polar angle and phi is the azimuthal angle defined between

            0 <= theta <= pi,
            0 <= phi <= 2pi.

        When param_types is set to 3, then the elements of the diffusion tensor matrix defined
        within the PDB frame can be supplied.


        Units
        ~~~~~

        The 'time_scale' argument should be a floating point number.  The only parameter affected by
        this value is tm.

        The 'd_scale' argument should also be a floating point number.  Parameters affected by this
        value are Diso, Dpar, Dper, Da, Dx, Dy, and Dz.  Significantly, Dr is not affected.

        The 'angle_units' argument should either be the string 'deg' or 'rad'.  Parameters affected
        are theta, phi, alpha, beta, and gamma.



        Examples
        ~~~~~~~~

        To set an isotropic diffusion tensor with a correlation time of 10 ns, type:

        relax> diffusion_tensor.init(10e-9)
        relax> diffusion_tensor.init(params=10e-9)
        relax> diffusion_tensor.init(10.0, 1e-9)
        relax> diffusion_tensor.init(params=10.0, time_scale=1e-9, fixed=True)


        To select axially symmetric diffusion with a tm value of 8.5 ns, Dratio of 1.1, theta value
        of 20 degrees, and phi value of 20 degrees, type:

        relax> diffusion_tensor.init((8.5e-9, 1.1, 20.0, 20.0), param_types=2)


        To select a spheroid diffusion tensor with a Dpar value of 1.698e7, Dper value of 1.417e7,
        theta value of 67.174 degrees, and phi value of -83.718 degrees, type one of:

        relax> diffusion_tensor.init((1.698e7, 1.417e7, 67.174, -83.718), param_types=3)
        relax> diffusion_tensor.init(params=(1.698e7, 1.417e7, 67.174, -83.718), param_types=3)
        relax> diffusion_tensor.init((1.698e-1, 1.417e-1, 67.174, -83.718), param_types=3,
                                     d_scale=1e8)
        relax> diffusion_tensor.init(params=(1.698e-1, 1.417e-1, 67.174, -83.718), param_types=3,
                                     d_scale=1e8)
        relax> diffusion_tensor.init((1.698e-1, 1.417e-1, 1.1724, -1.4612), param_types=3,
                                     d_scale=1e8, angle_units='rad')
        relax> diffusion_tensor.init(params=(1.698e-1, 1.417e-1, 1.1724, -1.4612), param_types=3,
                                     d_scale=1e8, angle_units='rad', fixed=True)


        To select ellipsoidal diffusion, type:

        relax> diffusion_tensor.init((1.340e7, 1.516e7, 1.691e7, -82.027, -80.573, 65.568),
                                param_types=2)
        """

        # Function intro text.
        if self.exec_info.intro:
            text = self.exec_info.ps3 + "diffusion_tensor.init("
            text = text + "params=" + repr(params)
            text = text + ", time_scale=" + repr(time_scale)
            text = text + ", d_scale=" + repr(d_scale)
            text = text + ", angle_units=" + repr(angle_units)
            text = text + ", param_types=" + repr(param_types)
            text = text + ", spheroid_type=" + repr(spheroid_type)
            text = text + ", fixed=" + repr(fixed) + ")"
            print(text)

        # The argument checks.
        arg_check.is_num_or_num_tuple(params, 'diffusion parameters', size=[4, 6])
        arg_check.is_num(time_scale, 'time scale')
        arg_check.is_num(d_scale, 'D scale')
        arg_check.is_str(angle_units, 'angle units')
        arg_check.is_int(param_types, 'parameter types')
        arg_check.is_str(spheroid_type, 'spheroid type', can_be_none=True)
        arg_check.is_bool(fixed, 'fixed flag')

        # Execute the functional code.
        diffusion_tensor.init(params=params, time_scale=time_scale, d_scale=d_scale, angle_units=angle_units, param_types=param_types, spheroid_type=spheroid_type, fixed=fixed)
