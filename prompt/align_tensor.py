###############################################################################
#                                                                             #
# Copyright (C) 2007-2010 Edward d'Auvergne                                   #
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
"""Module containing the 'align_tensor' user function class."""
__docformat__ = 'plaintext'

# Python module imports.

# relax module imports.
from base_class import User_fn_class
import arg_check
from generic_fns import align_tensor


class Align_tensor(User_fn_class):
    """Class for manipulating the alignment tensor."""

    def copy(self, tensor_from=None, pipe_from=None, tensor_to=None, pipe_to=None):
        """Function for copying alignment tensor data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor_from:  The identification string of the alignment tensor to copy the data from.

        pipe_from:  The name of the data pipe to copy the alignment tensor data from.

        tensor_to:  The identification string of the alignment tensor to copy the data to.

        pipe_to:  The name of the data pipe to copy the alignment tensor data to.


        Description
        ~~~~~~~~~~~

        This function will copy the alignment tensor data to a new tensor or a new data pipe.  The
        destination data pipe must not contain any alignment tensor data corresponding to the
        tensor_to label.  If the pipe_from or pipe_to arguments are not supplied, then both will
        default to the current data pipe.  Both the tensor_from and tensor_to arguments must be
        supplied.


        Examples
        ~~~~~~~~

        To copy the alignment tensor data corresponding to 'Pf1' from the data pipe 'old' to the
        current data pipe, type one of:

        relax> align_tensor.copy('Pf1', 'old')
        relax> align_tensor.copy(tensor_from='Pf1', pipe_from='old')


        To copy the alignment tensor data corresponding to 'Otting' from the current data pipe to
        the data pipe new, type one of:

        relax> align_tensor.copy('Otting', pipe_to='new')
        relax> align_tensor.copy(tensor_from='Otting', pipe_to='new')


        To copy the alignment tensor data of 'Otting' to that of 'Otting new', type one of:

        relax> align_tensor.copy('Otting', tensor_to='Otting new')
        relax> align_tensor.copy(tensor_from='Pf1', tensor_to='Otting new')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.copy("
            text = text + "tensor_from=" + repr(tensor_from)
            text = text + ", pipe_from=" + repr(pipe_from)
            text = text + ", tensor_to=" + repr(tensor_to)
            text = text + ", pipe_to=" + repr(pipe_to) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(tensor_from, 'tensor from')
        arg_check.is_str(pipe_from, 'pipe from', can_be_none=True)
        arg_check.is_str(tensor_to, 'tensor to', can_be_none=True)
        arg_check.is_str(pipe_to, 'pipe to', can_be_none=True)

        # Execute the functional code.
        align_tensor.copy(tensor_from=tensor_from, pipe_from=pipe_from, tensor_to=tensor_to, pipe_to=pipe_to)


    def delete(self, tensor=None):
        """Function for deleting alignment tensor data.


        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor identification string.


        Description
        ~~~~~~~~~~~

        This function will delete the specified alignment tensor data from the current data pipe.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.delete("
            text = text + "tensor=" + repr(tensor) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(tensor, 'tensor', can_be_none=True)

        # Execute the functional code.
        align_tensor.delete(tensor=tensor)


    def display(self, tensor=None):
        """Function for displaying the alignment tensor information.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor identification string.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.display("
            text = text + "tensor=" + repr(tensor) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(tensor, 'tensor', can_be_none=True)

        # Execute the functional code.
        align_tensor.display(tensor=tensor)


    def fix(self, fixed=True):
        """Fix all alignment tensors so that they do not change during optimisation.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        fixed:  The flag specifying if the tensors should be fixed or variable.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.fix("
            text = text + "fixed=" + repr(fixed) + ")"
            print(text)

        # The argument checks.
        arg_check.is_bool(fixed, 'fixed')

        # Execute the functional code.
        align_tensor.fix(fixed=fixed)


    def init(self, tensor=None, params=None, scale=1.0, angle_units='deg', param_types=0, errors=False):
        """Function for initialising the alignment tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor identification string.

        params:  The alignment tensor data.

        scale:  The alignment tensor eigenvalue scaling value.

        angle_units:  The units for the angle parameters.

        param_types:  A flag to select different parameter combinations.

        errors:  A flag which determines if the alignment tensor data or its errors are being input.


        Description
        ~~~~~~~~~~~

        Using this function, the alignment tensor data can be set up.  The params argument should be
        a tuple of floating point numbers (a list surrounded by round brakets).  These correspond to
        the parameters of the tensor, which can be specified by the param_types argument, where the
        values correspond to

            0:  {Sxx, Syy, Sxy, Sxz, Syz}  (unitless),
            1:  {Szz, Sxx-yy, Sxy, Sxz, Syz}  (Pales default format),
            2:  {Axx, Ayy, Axy, Axz, Ayz}  (unitless),
            3:  {Azz, Axx-yy, Axy, Axz, Ayz}  (unitless),
            4:  {Axx, Ayy, Axy, Axz, Ayz}  (units of Hertz),
            5:  {Azz, Axx-yy, Axy, Axz, Ayz}  (units of Hertz),
            6:  {Pxx, Pyy, Pxy, Pxz, Pyz}  (unitless),
            7:  {Pzz, Pxx-yy, Pxy, Pxz, Pyz}  (unitless),

        Other formats may be added later.  The relationship between the Saupe order matrix S and the
        alignment tensor A is

            S = 3/2 A.

        The probability matrix P is related to the alignment tensor A by

            A = P - 1/3 I,

        where I is the identity matrix.  For the alignment tensor to be supplied in Hertz, the bond
        vectors must all be of equal length.


        Examples
        ~~~~~~~~

        To set a rhombic tensor to the run 'CaM', type one of:

        relax> align_tensor.init('super media', (-8.6322e-05, -5.5786e-04, -3.1732e-05, 2.2927e-05,
                                 2.8599e-04), param_types=1)
        relax> align_tensor.init(tensor='super media', params=(-8.6322e-05, -5.5786e-04,
                                 -3.1732e-05, 2.2927e-05, 2.8599e-04), param_types=1)
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.init("
            text = text + "tensor=" + repr(tensor)
            text = text + ", params=" + repr(params)
            text = text + ", scale=" + repr(scale)
            text = text + ", angle_units=" + repr(angle_units)
            text = text + ", param_types=" + repr(param_types)
            text = text + ", errors=" + repr(errors) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(tensor, 'tensor')
        arg_check.is_num_tuple(params, 'alignment tensor parameters', size=5)
        arg_check.is_float(scale, 'scale')
        arg_check.is_str(angle_units, 'angle units')
        arg_check.is_int(param_types, 'parameter types')
        arg_check.is_bool(errors, 'errors flag')

        # Execute the functional code.
        align_tensor.init(tensor=tensor, params=params, scale=scale, angle_units=angle_units, param_types=param_types, errors=errors)


    def matrix_angles(self, basis_set=0, tensors=None):
        """Function for calculating the 5D angles between all alignment tensors.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        basis_set:  The basis set to operate with.

        tensors:  A list of the tensors to apply the calculation to.  If None, all tensors are used.


        Description
        ~~~~~~~~~~~

        This function will calculate the angles between all loaded alignment tensors for the current
        data pipe.  The matrices are first converted to a 5D vector form and then then angles are
        calculated.  The angles are dependent on the basis set.  If the basis_set argument is set to
        the default of 0, the vectors {Sxx, Syy, Sxy, Sxz, Syz} are used.  If the basis_set argument
        is set to 1, the vectors {Szz, Sxxyy, Sxy, Sxz, Syz} are used instead.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.matrix_angles("
            text = text + "basis_set=" + repr(basis_set)
            text = text + ", tensors=" + repr(tensors) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(basis_set, 'basis set')
        arg_check.is_str_list(tensors, 'alignment tensors', can_be_none=True)

        # Execute the functional code.
        align_tensor.matrix_angles(basis_set, tensors)


    def reduction(self, full_tensor=None, red_tensor=None):
        """Specify that one tensor is a reduction of another.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        full_tensor:  The full alignment tensor.

        red_tensor:  The reduce alignment tensor.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the N-state model and Frame Order theories using alignment tensors,
        which tensor is a reduction of which other tensor must be specified through this user
        function.


        Examples
        ~~~~~~~~

        To state that the alignment tensor loaded as 'chi3 C-dom' is a reduction of 'chi3 N-dom', type:

        relax> align_tensor.reduction(full_tensor='chi3 N-dom', red_tensor='chi3 C-dom')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.reduction("
            text = text + "full_tensor=" + repr(full_tensor)
            text = text + ", red_tensor=" + repr(red_tensor) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(full_tensor, 'full tensor')
        arg_check.is_str(red_tensor, 'reduced tensor')

        # Execute the functional code.
        align_tensor.reduction(full_tensor=full_tensor, red_tensor=red_tensor)


    def set_domain(self, tensor=None, domain=None):
        """Set the domain label for the alignment tensor.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        tensor:  The alignment tensor to assign the domain label to.

        domain:  The domain label.


        Description
        ~~~~~~~~~~~

        Prior to optimisation of the N-state model or Frame Order theories, the domain to which each
        alignment tensor belongs must be specified.


        Examples
        ~~~~~~~~

        To link the alignment tensor loaded as 'chi3 C-dom' to the C-terminal domain 'C', type:

        relax> align_tensor.set_domain(tensor='chi3 C-dom', domain='C')
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.set_domain("
            text = text + "tensor=" + repr(tensor)
            text = text + ", domain=" + repr(domain) + ")"
            print(text)

        # The argument checks.
        arg_check.is_str(tensor, 'tensor')
        arg_check.is_str(domain, 'domain')

        # Execute the functional code.
        align_tensor.set_domain(tensor=tensor, domain=domain)


    def svd(self, basis_set=0, tensors=None):
        """Function for calculating the singular values for all tensors and the condition number.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        basis_set:  The basis set to operate with.

        tensors:  A list of the tensors to apply the calculation to.  If None, all tensors are used.


        Description
        ~~~~~~~~~~~

        This function will, using SVD, calculate the singular values of all tensors loaded for the
        current data pipe.  If the basis_set argument is set to the default of 0, the matrix on
        which SVD will be performed is composed of the unitary basis set {Sxx, Syy, Sxy, Sxz, Syz}
        layed out as:

        -----

            | Sxx1 Syy1 Sxy1 Sxz1 Syz1 |
            | Sxx2 Syy2 Sxy2 Sxz2 Syz2 |
            | Sxx3 Syy3 Sxy3 Sxz3 Syz3 |
            |  .    .    .    .    .   |
            |  .    .    .    .    .   |
            |  .    .    .    .    .   |
            | SxxN SyyN SxyN SxzN SyzN |

        -----

        If basis_set is set to 1, the geometric basis set consisting of the stretching and skewing
        parameters Szz and Sxx-yy respectively {Szz, Sxxyy, Sxy, Sxz, Syz} will be used instead.
        The matrix is:

        -----

            | Szz1 Sxxyy1 Sxy1 Sxz1 Syz1 |
            | Szz2 Sxxyy2 Sxy2 Sxz2 Syz2 |
            | Szz3 Sxxyy3 Sxy3 Sxz3 Syz3 |
            |  .     .     .    .    .   |
            |  .     .     .    .    .   |
            |  .     .     .    .    .   |
            | SzzN SxxyyN SxyN SxzN SyzN |

        -----

        The relationships between the geometric and unitary basis sets are:

        -----

            Szz = - Sxx - Syy,
            Sxxyy = Sxx - Syy,

        -----

        The SVD values and condition number are dependendent upon the basis set chosen.
        """

        # Function intro text.
        if self._exec_info.intro:
            text = self._exec_info.ps3 + "align_tensor.svd("
            text = text + "basis_set=" + repr(basis_set)
            text = text + ", tensors=" + repr(tensors) + ")"
            print(text)

        # The argument checks.
        arg_check.is_int(basis_set, 'basis set')
        arg_check.is_str_list(tensors, 'alignment tensors', can_be_none=True)

        # Execute the functional code.
        align_tensor.svd(basis_set, tensors)
