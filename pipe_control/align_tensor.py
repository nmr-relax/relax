###############################################################################
#                                                                             #
# Copyright (C) 2003-2015 Edward d'Auvergne                                   #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module containing functions for the handling of alignment tensors."""

# Python module imports.
from copy import deepcopy
from math import pi, sqrt
from numpy import arccos, complex128, dot, float64, inner, linalg, zeros
from numpy.linalg import norm
import sys
from warnings import warn

# relax module imports.
from data_store.align_tensor import AlignTensorList
from lib.alignment.alignment_tensor import calc_chi_tensor, kappa
from lib.errors import RelaxError, RelaxNoTensorError, RelaxTensorError, RelaxUnknownParamCombError, RelaxUnknownParamError
from lib.geometry.angles import wrap_angles
from lib.geometry.vectors import vector_angle_complex_conjugate
from lib.io import write_data
from lib.text.sectioning import section, subsection
from lib.warnings import RelaxWarning
import pipe_control
from pipe_control import pipes
from pipe_control.pipes import check_pipe


def align_data_exists(tensor=None, pipe=None):
    """Function for determining if alignment data exists in the current data pipe.

    @keyword tensor:    The alignment tensor ID string.  If not supplied, then any alignment data will result in the function returning True.
    @type tensor:       str or None
    @keyword pipe:      The data pipe to search for data in.  This defaults to the current data pipe if not supplied.
    @type pipe:         str or None
    @return:            The answer to the question.
    @rtype:             bool
    """

    # The data pipe to check.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    pipe = pipes.get_pipe(pipe)

    # Test if an alignment tensor corresponding to the arg 'tensor' exists.
    if hasattr(pipe, 'align_tensors'):
        if tensor == None:
            return True
        for data in pipe.align_tensors:
            if data.name == tensor:
                return True
    else:
        return False


def all_tensors_fixed():
    """Determine if all alignment tensors are fixed.

    @return:    True if all tensors are fixed, False otherwise.
    @rtype:     bool
    """

    # Loop over the tensors.
    for i in range(len(cdp.align_tensors)):
        # Not fixed, so return False.
        if not cdp.align_tensors[i].fixed:
            return False

    # All tensors are fixed.
    return True


def copy(tensor_from=None, pipe_from=None, tensor_to=None, pipe_to=None):
    """Function for copying alignment tensor data from one data pipe to another.

    @param tensor_from: The identification string of the alignment tensor to copy the data from.
    @type tensor_from:  str
    @param pipe_from:   The data pipe to copy the alignment tensor data from.  This defaults to the current data pipe.
    @type pipe_from:    str
    @param tensor_to:   The identification string of the alignment tensor to copy the data to.  If set to None, then the ID string will be set to the value of tensor_from.
    @type tensor_to:    str or None
    @param pipe_to:     The data pipe to copy the alignment tensor data to.  This defaults to the current data pipe.
    @type pipe_to:      str
    """

    # Defaults.
    if tensor_from == tensor_to and pipe_from == None and pipe_to == None:
        raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None when the tensor names are the same.")
    elif pipe_from == None:
        pipe_from = pipes.cdp_name()
    elif pipe_to == None:
        pipe_to = pipes.cdp_name()

    # The target tensor ID string.
    if tensor_to == None:
        tensor_to = tensor_from

    # Test if the pipe_from and pipe_to data pipes exist.
    check_pipe(pipe_from)
    check_pipe(pipe_to)

    # Get the data pipes.
    dp_from = pipes.get_pipe(pipe_from)
    dp_to = pipes.get_pipe(pipe_to)

    # Test if pipe_from contains alignment tensor data.
    if not align_data_exists(tensor_from, pipe_from):
        raise RelaxNoTensorError('alignment')

    # Test if pipe_to contains alignment tensor data.
    if align_data_exists(tensor_to, pipe_to):
        raise RelaxTensorError('alignment')

    # Create the align_tensors dictionary if it doesn't yet exist.
    if not hasattr(dp_to, 'align_tensors'):
        dp_to.align_tensors = AlignTensorList()

    # Add the tensor if it doesn't already exist.
    if tensor_to != None and tensor_to not in dp_to.align_tensors.names():
        dp_to.align_tensors.add_item(tensor_to)

    # Copy all data.
    if tensor_from == None:
        # Check.
        if tensor_to != tensor_from:
            raise RelaxError("The tensor_to argument '%s' should not be supplied when tensor_from is None." % tensor_to)

        # The align IDs.
        align_ids = []

        # Loop over and copy all tensors.
        for i in range(len(dp_from.align_tensors)):
            dp_to.align_tensors.append(deepcopy(dp_from.align_tensors[i]))
            align_ids.append(dp_from.align_tensors[i].align_id)

    # Copy a single tensor.
    else:
        # Find the tensor index.
        index_from = get_tensor_index(tensor=tensor_from, pipe=pipe_from)
        index_to = get_tensor_index(tensor=tensor_to, pipe=pipe_to)

        # Copy the tensor.
        tensor = deepcopy(dp_from.align_tensors[index_from])
        if index_to == None:
            dp_to.align_tensors.append(tensor)
            index_to = len(dp_to.align_tensors) - 1
        else:
            dp_to.align_tensors[index_to] = tensor

        # Update the tensor's name.
        dp_to.align_tensors[index_to].set('name', tensor_to)

        # The align IDs.
        align_ids = [dp_from.align_tensors[index_from].align_id]

    # Add the align IDs to the target data pipe if needed.
    if not hasattr(dp_to, 'align_ids'):
        dp_to.align_ids = []
    for align_id in align_ids:
        if align_id not in dp_to.align_ids:
            dp_to.align_ids.append(align_id)


def delete(tensor=None):
    """Function for deleting alignment tensor data.

    @param tensor:          The alignment tensor identification string.
    @type tensor:           str or None
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Test if alignment tensor data exists.
    if tensor and not align_data_exists(tensor):
        raise RelaxNoTensorError('alignment')

    # The tensor list.
    if tensor:
        tensors = [tensor]
    else:
        tensors = []
        for i in range(len(cdp.align_tensors)):
            tensors.append(cdp.align_tensors[i].name)

    # Loop over the tensors.
    for tensor in tensors:
        # Print out.
        print("Removing the '%s' tensor." % tensor)

        # Find the tensor index.
        index = get_tensor_index(tensor=tensor)

        # Delete the alignment data.
        cdp.align_tensors.pop(index)

        # Delete the alignment tensor list if empty.
        if not len(cdp.align_tensors):
            del(cdp.align_tensors)


def display(tensor=None):
    """Function for displaying the alignment tensor.

    @keyword tensor:        The alignment tensor identification string.
    @type tensor:           str or None
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Construct the tensor list.
    tensor_list = []
    if not tensor:
        for tensor_cont in cdp.align_tensors:
            tensor_list.append(tensor_cont.name)
    else:
        tensor_list.append(tensor)

    # Loop over the tensors.
    for tensor in tensor_list:
        # Test if alignment tensor data exists.
        if not align_data_exists(tensor):
            raise RelaxNoTensorError('alignment')

        # Pull out the tensor.
        data = get_tensor_object(tensor)

        # Header.
        section(file=sys.stdout, text="Tensor '%s'" % tensor, prespace=3, postspace=1)


        # The Saupe matrix.
        ###################

        subsection(file=sys.stdout, text="Saupe order matrix", prespace=0)

        # The parameter set {Sxx, Syy, Sxy, Sxz, Syz}.
        print("# 5D, rank-1 notation {Sxx, Syy, Sxy, Sxz, Syz}:")
        print("[%25.12e, %25.12e, %25.12e, %25.12e, %25.12e]\n" % (data.Sxx, data.Syy, data.Sxy, data.Sxz, data.Syz))

        # The parameter set {Szz, Sxx-yy, Sxy, Sxz, Syz}.
        print("# 5D, rank-1 notation {Szz, Sxx-yy, Sxy, Sxz, Syz} (the Pales default format).")
        print("[%25.12e, %25.12e, %25.12e, %25.12e, %25.12e]\n" % (data.Szz, data.Sxxyy, data.Sxy, data.Sxz, data.Syz))

        # 3D form.
        print("# 3D, rank-2 notation.")
        print("%s" % (data.S))


        # The alignment tensor.
        #######################

        subsection(file=sys.stdout, text="Alignment tensor", prespace=2)

        # The parameter set {Axx, Ayy, Axy, Axz, Ayz}.
        print("# 5D, rank-1 notation {Axx, Ayy, Axy, Axz, Ayz}:")
        print("[%25.12e, %25.12e, %25.12e, %25.12e, %25.12e]\n" % (data.Axx, data.Ayy, data.Axy, data.Axz, data.Ayz))

        # The parameter set {Azz, Axx-yy, Axy, Axz, Ayz}.
        print("# 5D, rank-1 notation {Azz, Axx-yy, Axy, Axz, Ayz} (the Pales default format).")
        print("[%25.12e, %25.12e, %25.12e, %25.12e, %25.12e]\n" % (data.Azz, data.Axxyy, data.Axy, data.Axz, data.Ayz))

        # 3D form.
        print("# 3D, rank-2 notation.")
        print("%s" % data.A)


        # The probability tensor.
        #########################

        subsection(file=sys.stdout, text="Probability tensor", prespace=2)

        # The parameter set {Pxx, Pyy, Pxy, Pxz, Pyz}.
        print("# 5D, rank-1 notation {Pxx, Pyy, Pxy, Pxz, Pyz}:")
        print("[%25.12e, %25.12e, %25.12e, %25.12e, %25.12e]\n" % (data.Pxx, data.Pyy, data.Pxy, data.Pxz, data.Pyz))

        # The parameter set {Pzz, Pxx-yy, Pxy, Pxz, Pyz}.
        print("# 5D, rank-1 notation {Pzz, Pxx-yy, Pxy, Pxz, Pyz}.")
        print("[%25.12e, %25.12e, %25.12e, %25.12e, %25.12e]\n" % (data.Pzz, data.Pxxyy, data.Pxy, data.Pxz, data.Pyz))

        # 3D form.
        print("# 3D, rank-2 notation.")
        print("%s" % data.P)


        # The magnetic susceptibility tensor.
        #####################################

        subsection(file=sys.stdout, text="Magnetic susceptibility tensor", prespace=2)
        chi_tensor = True

        # The field strength.
        print("# The magnetic field strength (MHz):")
        if hasattr(cdp, 'spectrometer_frq') and tensor in cdp.spectrometer_frq:
            print("%s\n" % (cdp.spectrometer_frq[tensor] / 1e6))
        else:
            print("Not set.\n")
            chi_tensor = False

        # The temperature.
        print("# The temperature (K):")
        if hasattr(cdp, 'temperature') and tensor in cdp.temperature:
            print("%s\n" % cdp.temperature[tensor])
        else:
            print("Not set.\n")
            chi_tensor = False

        # No chi tensor.
        if not chi_tensor:
            print("# The chi tensor:\nN/A.")

        # Calculate the chi tensor.
        else:
            # Conversions.
            chi_xx =    calc_chi_tensor(data.Axx, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
            chi_xy =    calc_chi_tensor(data.Axy, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
            chi_xz =    calc_chi_tensor(data.Axz, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
            chi_yy =    calc_chi_tensor(data.Ayy, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
            chi_yz =    calc_chi_tensor(data.Ayz, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
            chi_zz =    calc_chi_tensor(data.Azz, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
            chi_xxyy =  calc_chi_tensor(data.Axxyy, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
            chi =       calc_chi_tensor(data.A, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])

            # The parameter set {chi_xx, chi_yy, chi_xy, chi_xz, chi_yz}.
            print("# 5D, rank-1 notation {chi_xx, chi_yy, chi_xy, chi_xz, chi_yz}:")
            print("[%25.12e, %25.12e, %25.12e, %25.12e, %25.12e]\n" % (chi_xx, chi_yy, chi_xy, chi_xz, chi_yz))

            # The parameter set {chi_zz, chi_xx-yy, chi_xy, chi_xz, chi_yz}.
            print("# 5D, rank-1 notation {chi_zz, chi_xx-yy, chi_xy, chi_xz, chi_yz}.")
            print("[%25.12e, %25.12e, %25.12e, %25.12e, %25.12e]\n" % (chi_zz, chi_xxyy, chi_xy, chi_xz, chi_yz))

            # 3D form.
            print("# 3D, rank-2 notation.")
            print("%s" % chi)


        # The irreducible weights.
        ##########################

        subsection(file=sys.stdout, text="Irreducible spherical tensor coefficients", prespace=2)

        # The equations.
        print("# The spherical harmonic decomposition weights are:")
        print("#     A0 = (4pi/5)^(1/2) Szz,")
        print("#     A+/-1 = +/- (8pi/15)^(1/2)(Sxz +/- iSyz),")
        print("#     A+/-2 = (2pi/15)^(1/2)(Sxx - Syy +/- 2iSxy).")

        # The parameters.
        print("A-2 =  %25.12e %25.12ei" % (data.Am2.real, data.Am2.imag))
        print("A-1 =  %25.12e %25.12ei" % (data.Am1.real, data.Am1.imag))
        print("A0  =  %25.12e" % data.A0)
        print("A1  =  %25.12e %25.12ei" % (data.A1.real, data.A1.imag))
        print("A2  =  %25.12e %25.12ei" % (data.A2.real, data.A2.imag))


        # The Eigensystem.
        ##################

        subsection(file=sys.stdout, text="Eigensystem", prespace=2)

        # Eigenvalues.
        print("# Saupe order matrix eigenvalues {Sxx, Syy, Szz}.")
        print("[%25.12e, %25.12e, %25.12e]\n" % (data.S_diag[0, 0], data.S_diag[1, 1], data.S_diag[2, 2]))
        print("# Alignment tensor eigenvalues {Axx, Ayy, Azz}.")
        print("[%25.12e, %25.12e, %25.12e]\n" % (data.A_diag[0, 0], data.A_diag[1, 1], data.A_diag[2, 2]))
        print("# Probability tensor eigenvalues {Pxx, Pyy, Pzz}.")
        print("[%25.12e, %25.12e, %25.12e]\n" % (data.P_diag[0, 0], data.P_diag[1, 1], data.P_diag[2, 2]))
        if chi_tensor:
            chi_diag =       calc_chi_tensor(data.A_diag, cdp.spectrometer_frq[tensor], cdp.temperature[tensor])
            print("# Magnetic susceptibility eigenvalues {chi_xx, chi_yy, chi_zz}.")
            print("[%25.12e, %25.12e, %25.12e]\n" % (chi_diag[0, 0], chi_diag[1, 1], chi_diag[2, 2]))

        # Eigenvectors.
        print("# Eigenvector x.")
        print("[%25.12f, %25.12f, %25.12f]\n" % (data.unit_x[0], data.unit_x[1], data.unit_x[2]))
        print("# Eigenvector y.")
        print("[%25.12f, %25.12f, %25.12f]\n" % (data.unit_y[0], data.unit_y[1], data.unit_y[2]))
        print("# Eigenvector z.")
        print("[%25.12f, %25.12f, %25.12f]\n" % (data.unit_z[0], data.unit_z[1], data.unit_z[2]))

        # Rotation matrix.
        print("# Rotation matrix.")
        print("%s\n" % data.rotation)

        # zyz.
        print("# Euler angles in zyz notation {alpha, beta, gamma}.")
        print("[%25.12f, %25.12f, %25.12f]\n" % (data.euler[0], data.euler[1], data.euler[2]))


        # Geometric description.
        ########################

        subsection(file=sys.stdout, text="Geometric description", prespace=2)

        # The GDO.
        print("# Generalized degree of order (GDO).")
        print("GDO = %-25.12e\n" % gdo(data.A))

        # Anisotropy.
        print("# Alignment tensor axial component (Aa = 3/2 * Azz, where Aii are the eigenvalues).")
        print("Aa = %-25.12e\n" % data.Aa)

        # Rhombicity.
        print("# Rhombic component (Ar = Axx - Ayy, where Aii are the eigenvalues).")
        print("Ar = %-25.12e\n" % data.Ar)
        print("# Rhombicity (R = Ar / Aa).")
        print("R = %-25.12f\n" % data.R)
        print("# Asymmetry parameter (eta = (Axx - Ayy) / Azz, where Aii are the eigenvalues).")
        print("eta = %-25.12f\n" % data.eta)

        # Magnetic susceptibility tensor.
        if chi_tensor:
            # Chi tensor anisotropy.
            print("# Magnetic susceptibility axial parameter (chi_ax = chi_zz - (chi_xx + chi_yy)/2, where chi_ii are the eigenvalues).")
            print("chi_ax = %-25.12e\n" % (chi_diag[2, 2] - (chi_diag[0, 0] + chi_diag[1, 1])/2.0))

            # Chi tensor rhombicity.
            print("# Magnetic susceptibility rhombicity parameter (chi_rh = chi_xx - chi_yy, where chi_ii are the eigenvalues).")
            print("chi_rh = %-25.12e\n" % (chi_diag[0, 0] - chi_diag[1, 1]))


def fix(id=None, fixed=True):
    """Fix the alignment tensor during optimisation.

    @keyword id:    The alignment tensor ID string.  If set to None, then all alignment tensors will be fixed.
    @type id:       str or None
    @keyword fixed: If True, the alignment tensor will be fixed during optimisation.  If False, the alignment tensors will be optimised.
    @type fixed:    bool
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Loop over the tensors.
    for i in range(len(cdp.align_tensors)):
        # ID match.
        if id and cdp.align_tensors[i].name == id:
            cdp.align_tensors[i].set_fixed(fixed)

        # Set all tensor flags.
        if id == None:
            cdp.align_tensors[i].set_fixed(fixed)


def fold_angles(sim_index=None):
    """Wrap the Euler angles and remove the glide reflection and translational symmetries.

    Wrap the angles such that::

        0 <= alpha <= 2pi,
        0 <= beta <= pi,
        0 <= gamma <= 2pi.

    For the simulated values, the angles are wrapped as::

        alpha - pi <= alpha_sim <= alpha + pi
        beta - pi/2 <= beta_sim <= beta + pi/2
        gamma - pi <= gamma_sim <= gamma + pi


    @param sim_index:   The simulation index.  If set to None then the actual values will be folded
                        rather than the simulation values.
    @type sim_index:    int or None
    """


    # Wrap the angles.
    ##################

    # Get the current angles.
    alpha = cdp.align_tensors.alpha
    beta  = cdp.align_tensors.beta
    gamma = cdp.align_tensors.gamma

    # Simulated values.
    if sim_index != None:
        alpha_sim = cdp.align_tensors.alpha_sim[sim_index]
        beta_sim  = cdp.align_tensors.beta_sim[sim_index]
        gamma_sim = cdp.align_tensors.gamma_sim[sim_index]

    # Normal value.
    if sim_index == None:
        cdp.align_tensors.set(param='alpha', value=wrap_angles(alpha, 0.0, 2.0*pi))
        cdp.align_tensors.set(param='beta', value= wrap_angles(beta, 0.0, 2.0*pi))
        cdp.align_tensors.set(param='gamma', value=wrap_angles(gamma, 0.0, 2.0*pi))

    # Simulation values.
    else:
        cdp.align_tensors.set(param='alpha', value=wrap_angles(alpha_sim, alpha - pi, alpha + pi), category='sim', sim_index=sim_index)
        cdp.align_tensors.set(param='beta', value= wrap_angles(beta_sim, beta - pi, beta + pi), category='sim', sim_index=sim_index)
        cdp.align_tensors.set(param='gamma', value=wrap_angles(gamma_sim, gamma - pi, gamma + pi), category='sim', sim_index=sim_index)


    # Remove the glide reflection and translational symmetries.
    ###########################################################

    # Normal value.
    if sim_index == None:
        # Fold beta inside 0 and pi.
        if cdp.align_tensors.beta >= pi:
            cdp.align_tensors.set(param='alpha', value=pi - cdp.align_tensors.alpha)
            cdp.align_tensors.set(param='beta', value=cdp.align_tensors.beta - pi)

    # Simulation values.
    else:
        # Fold beta_sim inside beta-pi/2 and beta+pi/2.
        if cdp.align_tensors.beta_sim[sim_index] >= cdp.align_tensors.beta + pi/2.0:
            cdp.align_tensors.set(param='alpha', value=pi - cdp.align_tensors.alpha_sim[sim_index], category='sim', sim_index=sim_index)
            cdp.align_tensors.set(param='beta', value=cdp.align_tensors.beta_sim[sim_index] - pi, category='sim', sim_index=sim_index)
        elif cdp.align_tensors.beta_sim[sim_index] <= cdp.align_tensors.beta - pi/2.0:
            cdp.align_tensors.set(param='alpha', value=pi - cdp.align_tensors.alpha_sim[sim_index], category='sim', sim_index=sim_index)
            cdp.align_tensors.set(param='beta', value=cdp.align_tensors.beta_sim[sim_index] + pi, category='sim', sim_index=sim_index)


def gdo(A):
    """Calculate the generalized degree of order (GDO) for the given alignment tensor.

    @param A:   The alignment tensor.
    @type A:    rank-2, 3D numpy array
    @return:    The GDO value.
    @rtype:     float
    """

    # The matrix norm.
    gdo = sqrt(3.0/2.0) *  norm(A)

    # Return the GDO.
    return gdo


def get_align_ids():
    """Return the list of all alignment IDs.

    @return:        The list of all alignment IDs.
    @rtype:         list of str
    """

    # No pipe.
    if cdp == None:
        return []

    # No tensor data.
    if not hasattr(cdp, 'align_ids'):
        return []

    # The tensor IDs.
    return cdp.align_ids


def get_tensor_ids():
    """Return the list of all tensor IDs.

    @return:        The list of all tensor IDs.
    @rtype:         list of str
    """

    # Init.
    ids = []

    # No pipe.
    if cdp == None:
        return ids

    # No tensor data.
    if not hasattr(cdp, 'align_tensors'):
        return ids

    # Loop over the tensors.
    for i in range(len(cdp.align_tensors)):
        if cdp.align_tensors[i].name != None:
            ids.append(cdp.align_tensors[i].name)

    # Return the object.
    return ids


def get_tensor_index(tensor=None, align_id=None, pipe=None):
    """Function for returning the index corresponding to the 'tensor' argument.

    @keyword tensor:    The alignment tensor identification string.
    @type tensor:       str or None
    @keyword align_id:  Alternative to the tensor argument, used to return the tensor index for the tensors corresponding to the alignment ID string.  If more than one tensor exists, then this will fail.
    @type align_id:     str or None
    @keyword pipe:      The data pipe to search for data in.
    @type pipe:         str
    @return:            The index corresponding to the 'tensor' arg.
    @rtype:             int
    """

    # The data pipe to check.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Get the data pipe.
    dp = pipes.get_pipe(pipe)

    # Init.
    index = None
    count = 0

    # Loop over the tensors.
    for i in range(len(dp.align_tensors)):
        # Tensor name match.
        if tensor and dp.align_tensors[i].name == tensor:
            index = i
            count += 1

        # Alignment ID match.
        if align_id and hasattr(dp.align_tensors[i], 'align_id') and dp.align_tensors[i].align_id == align_id:
            index = i
            count += 1

    # No match.
    if count == 0:
        warn(RelaxWarning("No alignment tensors match the tensor name '%s' or alignment ID '%s' in the data pipe '%s'." % (tensor, align_id, pipe)))
        return None

    # More than one match.
    if count > 1:
        warn(RelaxWarning("More than one alignment tensors matches the tensor name '%s' or alignment ID '%s' in the data pipe '%s'." % (tensor, align_id, pipe)))
        return None

    # Return the index.
    return index


def get_tensor_object(tensor, pipe=None):
    """Return the AlignTensorData instance corresponding to the tensor ID.

    @param tensor:  The alignment tensor identification string.
    @type tensor:   str
    @param pipe:    The data pipe to search for data in.
    @type pipe:     str
    @return:        The alignment tensor object corresponding to the 'tensor' arg.
    @rtype:         AlignTensorData instance
    """

    # The data pipe to check.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Init.
    data = None

    # Loop over the tensors.
    for i in range(len(cdp.align_tensors)):
        if cdp.align_tensors[i].name == tensor:
            data = cdp.align_tensors[i]

    # Return the object.
    return data


def get_tensor_object_from_align(align_id, pipe=None):
    """Return the unique AlignTensorData instance corresponding to the alignment ID.

    @param align_id:    The alignment ID for the unique tensor.
    @type align_id:     str
    @return:            The alignment tensor object corresponding to the 'tensor' arg.
    @rtype:             AlignTensorData instance
    """

    # The data pipe to check.
    if pipe == None:
        pipe = pipes.cdp_name()

    # Init.
    data = None

    # Loop over the tensors.
    count = 0
    for i in range(len(cdp.align_tensors)):
        if hasattr(cdp.align_tensors[i], 'align_id') and cdp.align_tensors[i].align_id == align_id:
            data = cdp.align_tensors[i]
            count += 1

    # Multiple matches.
    if count > 1:
        raise RelaxError("Multiple alignment tensors match the alignment ID '%s'." % align_id)
    # Return the object.
    return data


def init(tensor=None, align_id=None, params=None, scale=1.0, angle_units='deg', param_types=0, domain=None, errors=False):
    """Function for initialising the alignment tensor.

    @keyword tensor:        The alignment tensor identification string.
    @type tensor:           str
    @keyword align_id:      The alignment ID string that the tensor corresponds to.
    @type align_id:         str or None
    @keyword params:        The alignment tensor parameters.
    @type params:           list of float or None
    @keyword scale:         The alignment tensor eigenvalue scaling value.
    @type scale:            float
    @keyword angle_units:   The units for the angle parameters (either 'deg' or 'rad').
    @type angle_units:      str
    @keyword param_types:   The type of parameters supplied.  The flag values correspond to, 0: {Axx, Ayy, Axy, Axz, Ayz}, and 1: {Azz, Axx-yy, Axy, Axz, Ayz}.
    @type param_types:      int
    @keyword domain:        The domain label.
    @type domain:           str or None
    @keyword errors:        A flag which determines if the alignment tensor data or its errors are being input.
    @type errors:           bool
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Parameter checks.
    if align_id == None:
        raise RelaxError("The alignment ID must be given.")

    # Check the validity of the angle_units argument.
    valid_types = ['deg', 'rad']
    if not angle_units in valid_types:
        raise RelaxError("The alignment tensor 'angle_units' argument " + repr(angle_units) + " should be either 'deg' or 'rad'.")

    # Test if alignment tensor data already exists.
    if errors and (not hasattr(cdp, 'align_ids') or not align_id in cdp.align_ids):
        raise RelaxNoTensorError('alignment')

    # Check that the domain is defined.
    if domain and (not hasattr(cdp, 'domain') or domain not in cdp.domain):
        raise RelaxError("The domain '%s' has not been defined.  Please use the domain user function." % domain)

    # Add the align ID to the current data pipe if needed.
    if not hasattr(cdp, 'align_ids'):
        cdp.align_ids = []
    if align_id not in cdp.align_ids:
        cdp.align_ids.append(align_id)

    # Add the align_tensors object to the data pipe.
    tensor_obj = None
    if not errors:
        # Initialise the super structure.
        if not hasattr(cdp, 'align_tensors'):
            cdp.align_tensors = AlignTensorList()

        # Add the tensor, if it doesn't already exist.
        if tensor == None or tensor not in cdp.align_tensors.names():
            tensor_obj = cdp.align_tensors.add_item(tensor)

    # Get the tensor.
    if not tensor_obj:
        if tensor:
            tensor_obj = get_tensor_object(tensor)
        else:
            tensor_obj = get_tensor_object_from_align(align_id)

    # Set the parameter values.
    if params:
        # {Sxx, Syy, Sxy, Sxz, Syz}.
        if param_types == 0:
            # Unpack the tuple.
            Sxx, Syy, Sxy, Sxz, Syz = params

            # Scaling.
            Sxx = Sxx * scale
            Syy = Syy * scale
            Sxy = Sxy * scale
            Sxz = Sxz * scale
            Syz = Syz * scale

            # Set the parameters.
            set(tensor=tensor_obj, value=[Sxx, Syy, Sxy, Sxz, Syz], param=['Sxx', 'Syy', 'Sxy', 'Sxz', 'Syz'], errors=errors)

        # {Szz, Sxx-yy, Sxy, Sxz, Syz}.
        elif param_types == 1:
            # Unpack the tuple.
            Szz, Sxxyy, Sxy, Sxz, Syz = params

            # Scaling.
            Szz = Szz * scale
            Sxxyy = Sxxyy * scale
            Sxy = Sxy * scale
            Sxz = Sxz * scale
            Syz = Syz * scale

            # Set the parameters.
            set(tensor=tensor_obj, value=[Szz, Sxxyy, Sxy, Sxz, Syz], param=['Szz', 'Sxxyy', 'Sxy', 'Sxz', 'Syz'], errors=errors)

        # {Axx, Ayy, Axy, Axz, Ayz}.
        elif param_types == 2:
            # Unpack the tuple.
            Axx, Ayy, Axy, Axz, Ayz = params

            # Scaling.
            Axx = Axx * scale
            Ayy = Ayy * scale
            Axy = Axy * scale
            Axz = Axz * scale
            Ayz = Ayz * scale

            # Set the parameters.
            set(tensor=tensor_obj, value=[Axx, Ayy, Axy, Axz, Ayz], param=['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'], errors=errors)

        # {Azz, Axx-yy, Axy, Axz, Ayz}.
        elif param_types == 3:
            # Unpack the tuple.
            Azz, Axxyy, Axy, Axz, Ayz = params

            # Scaling.
            Azz = Azz * scale
            Axxyy = Axxyy * scale
            Axy = Axy * scale
            Axz = Axz * scale
            Ayz = Ayz * scale

            # Set the parameters.
            set(tensor=tensor_obj, value=[Azz, Axxyy, Axy, Axz, Ayz], param=['Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz'], errors=errors)

        # {Axx, Ayy, Axy, Axz, Ayz}.
        elif param_types == 4:
            # Unpack the tuple.
            Axx, Ayy, Axy, Axz, Ayz = params

            # Get the bond length.
            r = None
            for spin in spin_loop():
                # First spin.
                if r == None:
                    r = spin.r

                # Different value.
                if r != spin.r:
                    raise RelaxError("Not all spins have the same bond length.")

            # Scaling.
            scale = scale / kappa() * r**3
            Axx = Axx * scale
            Ayy = Ayy * scale
            Axy = Axy * scale
            Axz = Axz * scale
            Ayz = Ayz * scale

            # Set the parameters.
            set(tensor=tensor_obj, value=[Axx, Ayy, Axy, Axz, Ayz], param=['Axx', 'Ayy', 'Axy', 'Axz', 'Ayz'], errors=errors)

        # {Azz, Axx-yy, Axy, Axz, Ayz}.
        elif param_types == 5:
            # Unpack the tuple.
            Azz, Axxyy, Axy, Axz, Ayz = params

            # Get the bond length.
            r = None
            for spin in spin_loop():
                # First spin.
                if r == None:
                    r = spin.r

                # Different value.
                if r != spin.r:
                    raise RelaxError("Not all spins have the same bond length.")

            # Scaling.
            scale = scale / kappa() * r**3
            Azz = Azz * scale
            Axxyy = Axxyy * scale
            Axy = Axy * scale
            Axz = Axz * scale
            Ayz = Ayz * scale

            # Set the parameters.
            set(tensor=tensor_obj, value=[Azz, Axxyy, Axy, Axz, Ayz], param=['Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz'], errors=errors)

        # {Pxx, Pyy, Pxy, Pxz, Pyz}.
        elif param_types == 6:
            # Unpack the tuple.
            Pxx, Pyy, Pxy, Pxz, Pyz = params

            # Scaling.
            Pxx = Pxx * scale
            Pyy = Pyy * scale
            Pxy = Pxy * scale
            Pxz = Pxz * scale
            Pyz = Pyz * scale

            # Set the parameters.
            set(tensor=tensor_obj, value=[Pxx, Pyy, Pxy, Pxz, Pyz], param=['Pxx', 'Pyy', 'Pxy', 'Pxz', 'Pyz'], errors=errors)

        # {Pzz, Pxx-yy, Pxy, Pxz, Pyz}.
        elif param_types == 7:
            # Unpack the tuple.
            Pzz, Pxxyy, Pxy, Pxz, Pyz = params

            # Scaling.
            Pzz = Pzz * scale
            Pxxyy = Pxxyy * scale
            Pxy = Pxy * scale
            Pxz = Pxz * scale
            Pyz = Pyz * scale

            # Set the parameters.
            set(tensor=tensor_obj, value=[Pzz, Pxxyy, Pxy, Pxz, Pyz], param=['Pzz', 'Pxxyy', 'Pxy', 'Pxz', 'Pyz'], errors=errors)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError('param_types', param_types)

    # Set the domain and alignment ID.
    if domain:
        set_domain(tensor=tensor, domain=domain)
    if align_id:
        tensor_obj.set(param='align_id', value=align_id)


def matrix_angles(basis_set='matrix', tensors=None, angle_units='deg', precision=1):
    """Function for calculating the inter-matrix angles between the alignment tensors.

    The basis set defines how the angles are calculated:

        - "matrix", the standard inter-matrix angle.  The angle is calculated via the Euclidean inner product of the alignment matrices in rank-2, 3D form divided by the Frobenius norm ||A||_F of the matrices.
        - "irreducible 5D", the irreducible 5D basis set {A-2, A-1, A0, A1, A2}.
        - "unitary 5D", the unitary 5D basis set {Sxx, Syy, Sxy, Sxz, Syz}.
        - "geometric 5D", the geometric 5D basis set {Szz, Sxxyy, Sxy, Sxz, Syz}.  This is also the Pales standard notation.


    @keyword basis_set:     The basis set to use for calculating the inter-matrix angles.  It can be one of "matrix", "irreducible 5D", "unitary 5D", or "geometric 5D".
    @type basis_set:        str
    @keyword tensors:       The list of alignment tensor IDs to calculate inter-matrix angles between.  If None, all tensors will be used.
    @type tensors:          None or list of str
    @keyword angle_units:   The units for the angle parameters, either 'deg' or 'rad'.
    @type angle_units:      str
    @keyword precision:     The precision of the printed out angles.  The number corresponds to the number of figures to print after the decimal point.
    @type precision:        int
    """

    # Argument check.
    allowed = ['matrix', 'unitary 9D', 'irreducible 5D', 'unitary 5D', 'geometric 5D']
    if basis_set not in allowed:
        raise RelaxError("The basis set of '%s' is not one of %s." % (basis_set, allowed))

    # Test that alignment tensor data exists.
    if not hasattr(cdp, 'align_tensors') or len(cdp.align_tensors) == 0:
        raise RelaxNoTensorError('alignment')

    # Count the number of tensors.
    tensor_num = 0
    for tensor in cdp.align_tensors:
        if tensors and tensor.name not in tensors:
            continue
        tensor_num = tensor_num + 1

    # Create the matrix which contains the 5D vectors.
    if basis_set == 'matrix':
        matrix = zeros((tensor_num, 3, 3), float64)
    elif basis_set == 'unitary 9D':
        matrix = zeros((tensor_num, 9), float64)
    elif basis_set in ['unitary 5D', 'geometric 5D']:
        matrix = zeros((tensor_num, 5), float64)
    elif basis_set in ['irreducible 5D']:
        matrix = zeros((tensor_num, 5), complex128)
        matrix_conj = zeros((tensor_num, 5), complex128)

    # Loop over the tensors.
    i = 0
    for tensor in cdp.align_tensors:
        # Skip tensors.
        if tensors and tensor.name not in tensors:
            continue

        # Full matrix.
        if basis_set == 'matrix':
            matrix[i] = tensor.A

        # 9D unitary basis set.
        elif basis_set == 'unitary 9D':
            matrix[i, 0] = tensor.Sxx
            matrix[i, 1] = tensor.Sxy
            matrix[i, 2] = tensor.Sxz
            matrix[i, 3] = tensor.Sxy
            matrix[i, 4] = tensor.Syy
            matrix[i, 5] = tensor.Syz
            matrix[i, 6] = tensor.Sxz
            matrix[i, 7] = tensor.Syz
            matrix[i, 8] = tensor.Szz

        # 5D unitary basis set.
        if basis_set == 'unitary 5D':
            matrix[i, 0] = tensor.Sxx
            matrix[i, 1] = tensor.Syy
            matrix[i, 2] = tensor.Sxy
            matrix[i, 3] = tensor.Sxz
            matrix[i, 4] = tensor.Syz

        # 5D irreducible basis set.
        if basis_set == 'irreducible 5D':
            matrix[i, 0] = tensor.Am2
            matrix[i, 1] = tensor.Am1
            matrix[i, 2] = tensor.A0
            matrix[i, 3] = tensor.A1
            matrix[i, 4] = tensor.A2

            # The (-1)^mS-m conjugate.
            matrix_conj[i, 0] = tensor.A2
            matrix_conj[i, 1] = -tensor.A1
            matrix_conj[i, 2] = tensor.A0
            matrix_conj[i, 3] = -tensor.Am1
            matrix_conj[i, 4] = tensor.Am2

        # 5D geometric basis set.
        elif basis_set == 'geometric 5D':
            matrix[i, 0] = tensor.Szz
            matrix[i, 1] = tensor.Sxxyy
            matrix[i, 2] = tensor.Sxy
            matrix[i, 3] = tensor.Sxz
            matrix[i, 4] = tensor.Syz

        # Normalisation.
        if basis_set in ['unitary 9D', 'unitary 5D', 'geometric 5D']:
            matrix[i] = matrix[i] / norm(matrix[i])

        # Increment the index.
        i = i + 1

    # Initialise the matrix of angles.
    cdp.align_tensors.angles = zeros((tensor_num, tensor_num), float64)

    # Header printout.
    if basis_set == 'matrix':
        sys.stdout.write("Standard inter-tensor matrix angles in degrees using the Euclidean inner product divided by the Frobenius norms (theta = arccos(<A1,A2>/(||A1||.||A2||)))")
    elif basis_set == 'irreducible 5D':
        sys.stdout.write("Inter-tensor vector angles in degrees for the irreducible 5D vectors {A-2, A-1, A0, A1, A2}")
    elif basis_set == 'unitary 9D':
        sys.stdout.write("Inter-tensor vector angles in degrees for the unitary 9D vectors {Sxx, Sxy, Sxz, Syx, Syy, Syz, Szx, Szy, Szz}")
    elif basis_set == 'unitary 5D':
        sys.stdout.write("Inter-tensor vector angles in degrees for the unitary 5D vectors {Sxx, Syy, Sxy, Sxz, Syz}")
    elif basis_set == 'geometric 5D':
        sys.stdout.write("Inter-tensor vector angles in degrees for the geometric 5D vectors {Szz, Sxx-yy, Sxy, Sxz, Syz}")
    sys.stdout.write(":\n\n")

    # Initialise the table of data.
    table = []

    # The table header.
    table.append([''])
    for i in range(tensor_num):
        # All tensors.
        if not tensors:
            if cdp.align_tensors[i].name == None:
                table[0].append(repr(i))
            else:
                table[0].append(cdp.align_tensors[i].name)

        # Subset.
        else:
            table[0].append(tensors[i])

    # First loop over the rows.
    for i in range(tensor_num):
        # Add the tensor name.
        if not tensors:
            if cdp.align_tensors[i].name == None:
                table.append([repr(i)])
            else:
                table.append([cdp.align_tensors[i].name])
        else:
            table.append([tensors[i]])

        # Second loop over the columns.
        for j in range(tensor_num):
            # The vector angles.
            if basis_set in ['unitary 9D', 'unitary 5D', 'geometric 5D']:
                # Dot product.
                delta = dot(matrix[i], matrix[j])

                # Check.
                if delta > 1:
                    delta = 1

                # The angle.
                theta = arccos(delta)

            # The irreducible complex conjugate angles.
            if basis_set in ['irreducible 5D']:
                theta = vector_angle_complex_conjugate(v1=matrix[i], v2=matrix[j], v1_conj=matrix_conj[i], v2_conj=matrix_conj[j])

            # The full matrix angle.
            elif basis_set in ['matrix']:
                # The Euclidean inner product.
                nom = inner(matrix[i].flatten(), matrix[j].flatten())

                # The Frobenius norms.
                denom = norm(matrix[i]) * norm(matrix[j])

                # The angle.
                ratio = nom / denom
                if ratio <= 1.0:
                    theta = arccos(nom / denom)
                else:
                    theta = 0.0

            # Store the angle (in rad).
            cdp.align_tensors.angles[i, j] = theta

            # Add to the table as degrees.
            angle = cdp.align_tensors.angles[i, j]
            if angle_units == 'deg':
                angle = angle * 180.0 / pi
            format = "%" + repr(7+precision) + "." + repr(precision) + "f"
            table[i+1].append(format % angle)

    # Write out the table.
    write_data(out=sys.stdout, data=table)


def num_tensors(skip_fixed=True):
    """Count the number of tensors.

    @keyword skip_fixed:    If set to True, then only the tensors without the fixed flag will be counted.  If set to False, then all tensors will be counted.
    @type skip_fixed:       bool
    @return:                The number of tensors (excluding fixed tensors by default).
    @rtype:                 int
    """

    # Init.
    count = 0

    # Loop over the tensors.
    for tensor_cont in cdp.align_tensors:
        # Skip fixed tensors.
        if skip_fixed and tensor_cont.fixed:
            continue

        # Increment.
        count += 1

    # Return the count.
    return count


def opt_uses_align_data(align_id=None):
    """Determine if the PCS or RDC data for the given alignment ID is needed for optimisation.

    @keyword align_id:  The optional alignment ID string.
    @type align_id:     str
    @return:            True if alignment data is to be used for optimisation, False otherwise.
    @rtype:             bool
    """

    # No alignment IDs.
    if not hasattr(cdp, 'align_ids'):
        return False

    # Convert the align IDs to an array, or take all IDs.
    if align_id:
        align_ids = [align_id]
    else:
        align_ids = cdp.align_ids

    # Check the PCS and RDC.
    for align_id in align_ids:
        if pipe_control.pcs.opt_uses_pcs(align_id) or pipe_control.rdc.opt_uses_rdc(align_id):
            return True

    # No alignment data is used for optimisation.
    return False


def opt_uses_tensor(tensor):
    """Determine if the given tensor is to be optimised.

    @param tensor:  The alignment tensor to check.
    @type tensor:   AlignmentTensor object.
    @return:        True if the tensor is to be optimised, False otherwise.
    @rtype:         bool
    """

    # Combine all RDC and PCS IDs.
    ids = []
    if hasattr(cdp, 'rdc_ids'):
        ids += cdp.rdc_ids
    if hasattr(cdp, 'pcs_ids'):
        ids += cdp.pcs_ids

    # No RDC or PCS data for the alignment, so skip the tensor as it will not be optimised.
    if tensor.align_id not in ids:
        return False

    # Fixed tensor.
    if tensor.fixed:
        return False

    # The tensor is to be optimised.
    return True


def reduction(full_tensor=None, red_tensor=None):
    """Specify which tensor is a reduction of which other tensor.

    @param full_tensor: The full alignment tensor.
    @type full_tensor:  str
    @param red_tensor:  The reduced alignment tensor.
    @type red_tensor:   str
    """

    # Tensor information.
    match_full = False
    match_red = False
    i = 0
    for tensor_cont in cdp.align_tensors:
        # Test the tensor names.
        if tensor_cont.name == full_tensor:
            match_full = True
            index_full = i
        if tensor_cont.name == red_tensor:
            match_red = True
            index_red = i

        # Increment.
        i = i + 1

    # No match.
    if not match_full:
        raise RelaxNoTensorError('alignment', full_tensor)
    if not match_red:
        raise RelaxNoTensorError('alignment', red_tensor)

    # Store.
    if not hasattr(cdp.align_tensors, 'reduction'):
        cdp.align_tensors.reduction = []
    cdp.align_tensors.reduction.append([index_full, index_red])


def return_tensor(index, skip_fixed=True):
    """Return the tensor container for the given index, skipping fixed tensors if required.

    @param index:           The index of the tensor (if skip_fixed is True, then fixed tensors are not included in the index count).
    @type index:            int
    @keyword skip_fixed:    A flag which if True will exclude fixed tensors from the indexation.
    @type skip_fixed:       bool
    @return:                The tensor corresponding to the index.
    @rtype:                 data.align_tensor.AlignTensorData instance
    """

    # Init.
    count = 0

    # Loop over the tensors.
    for tensor_cont in cdp.align_tensors:
        # Skip fixed tensors.
        if skip_fixed and tensor_cont.fixed:
            continue

        # Index match, so return the container.
        if index == count:
            return tensor_cont

        # Increment.
        count += 1

    # Return False if the container was not found.
    return False


def set(tensor=None, value=None, param=None, errors=False):
    """Set the tensor.

    @keyword tensor:    The alignment tensor object.
    @type tensor:       AlignTensorData instance
    @keyword value:     The list of values to set the parameters to.
    @type value:        list of float
    @keyword param:     The list of parameter names.
    @type param:        list of str
    @keyword errors:    A flag which determines if the alignment tensor data or its errors are being
                        input.
    @type errors:       bool
    """

    # Initialise.
    geo_params = []
    geo_values = []
    orient_params = []
    orient_values = []

    # Loop over the parameters.
    for i in range(len(param)):
        # Unknown parameter.
        if param[i] == None:
            raise RelaxUnknownParamError("alignment tensor", 'None')

        # Default value.
        if value[i] == None:
            value[i] = 0.0

        # Geometric parameter.
        if param[i] in ['Sxx', 'Syy', 'Szz', 'Sxxyy', 'Sxy', 'Sxz', 'Syz', 'Axx', 'Ayy', 'Azz', 'Axxyy', 'Axy', 'Axz', 'Ayz', 'Pxx', 'Pyy', 'Pzz', 'Pxxyy', 'Pxy', 'Pxz', 'Pyz']:
            geo_params.append(param[i])
            geo_values.append(value[i])

        # Orientational parameter.
        if param[i] in ['alpha', 'beta', 'gamma']:
            orient_params.append(param[i])
            orient_values.append(value[i])


    # Geometric parameters.
    #######################

    # A single geometric parameter.
    if len(geo_params) == 1:
        # Saupe order matrix.
        #####################

        # The single parameter Sxx.
        if geo_params[0] == 'Sxx':
            if errors:
                tensor.set(param='Sxx', value=geo_values[0], category='err')
            else:
                tensor.set(param='Sxx', value=geo_values[0])

        # The single parameter Syy.
        elif geo_params[0] == 'Syy':
            if errors:
                tensor.set(param='Syy', value=geo_values[0], category='err')
            else:
                tensor.set(param='Syy', value=geo_values[0])

        # The single parameter Sxy.
        elif geo_params[0] == 'Sxy':
            if errors:
                tensor.set(param='Sxy', value=geo_values[0], category='err')
            else:
                tensor.set(param='Sxy', value=geo_values[0])

        # The single parameter Sxz.
        elif geo_params[0] == 'Sxz':
            if errors:
                tensor.set(param='Sxz', value=geo_values[0], category='err')
            else:
                tensor.set(param='Sxz', value=geo_values[0])

        # The single parameter Syz.
        elif geo_params[0] == 'Syz':
            if errors:
                tensor.set(param='Syz', value=geo_values[0], category='err')
            else:
                tensor.set(param='Syz', value=geo_values[0])


        # Alignment tensor.
        ###################

        # The single parameter Axx.
        elif geo_params[0] == 'Axx':
            if errors:
                tensor.set(param='Sxx', value=3.0/2.0 * geo_values[0], category='err')
            else:
                tensor.set(param='Sxx', value=3.0/2.0 * geo_values[0])

        # The single parameter Ayy.
        elif geo_params[0] == 'Ayy':
            if errors:
                tensor.set(param='Syy', value=3.0/2.0 * geo_values[0], category='err')
            else:
                tensor.set(param='Syy', value=3.0/2.0 * geo_values[0])

        # The single parameter Axy.
        elif geo_params[0] == 'Axy':
            if errors:
                tensor.set(param='Sxy', value=3.0/2.0 * geo_values[0], category='err')
            else:
                tensor.set(param='Sxy', value=3.0/2.0 * geo_values[0])

        # The single parameter Axz.
        elif geo_params[0] == 'Axz':
            if errors:
                tensor.set(param='Sxz', value=3.0/2.0 * geo_values[0], category='err')
            else:
                tensor.set(param='Sxz', value=3.0/2.0 * geo_values[0])

        # The single parameter Ayz.
        elif geo_params[0] == 'Ayz':
            if errors:
                tensor.set(param='Syz', value=3.0/2.0 * geo_values[0], category='err')
            else:
                tensor.set(param='Syz', value=3.0/2.0 * geo_values[0])


        # Probability tensor.
        #####################

        # The single parameter Pxx.
        elif geo_params[0] == 'Pxx':
            if errors:
                tensor.set(param='Sxx', value=3.0/2.0 * (geo_values[0] - 1.0/3.0), category='err')
            else:
                tensor.set(param='Sxx', value=3.0/2.0 * (geo_values[0] - 1.0/3.0))

        # The single parameter Pyy.
        elif geo_params[0] == 'Pyy':
            if errors:
                tensor.set(param='Syy', value=3.0/2.0 * (geo_values[0] - 1.0/3.0), category='err')
            else:
                tensor.set(param='Syy', value=3.0/2.0 * (geo_values[0] - 1.0/3.0))

        # The single parameter Pxy.
        elif geo_params[0] == 'Pxy':
            if errors:
                tensor.set(param='Sxy', value=3.0/2.0 * geo_values[0], category='err')
            else:
                tensor.set(param='Sxy', value=3.0/2.0 * geo_values[0])

        # The single parameter Pxz.
        elif geo_params[0] == 'Pxz':
            if errors:
                tensor.set(param='Sxz', value=3.0/2.0 * geo_values[0], category='err')
            else:
                tensor.set(param='Sxz', value=3.0/2.0 * geo_values[0])

        # The single parameter Pyz.
        elif geo_params[0] == 'Pyz':
            if errors:
                tensor.set(param='Syz', value=3.0/2.0 * geo_values[0], category='err')
            else:
                tensor.set(param='Syz', value=3.0/2.0 * geo_values[0])

        # Cannot set the single parameter.
        else:
            raise RelaxError("The geometric alignment parameter " + repr(geo_params[0]) + " cannot be set.")

    # 5 geometric parameters.
    elif len(geo_params) == 5:
        # The geometric parameter set {Sxx, Syy, Sxy, Sxz, Syz}.
        if geo_params.count('Sxx') == 1 and geo_params.count('Syy') == 1 and geo_params.count('Sxy') == 1 and geo_params.count('Sxz') == 1 and geo_params.count('Syz') == 1:
            # The parameters.
            Sxx = geo_values[geo_params.index('Sxx')]
            Syy = geo_values[geo_params.index('Syy')]
            Sxy = geo_values[geo_params.index('Sxy')]
            Sxz = geo_values[geo_params.index('Sxz')]
            Syz = geo_values[geo_params.index('Syz')]

            # Set the internal parameter values.
            if errors:
                tensor.set(param='Axx', value=2.0/3.0 * Sxx, category='err')
                tensor.set(param='Ayy', value=2.0/3.0 * Syy, category='err')
                tensor.set(param='Axy', value=2.0/3.0 * Sxy, category='err')
                tensor.set(param='Axz', value=2.0/3.0 * Sxz, category='err')
                tensor.set(param='Ayz', value=2.0/3.0 * Syz, category='err')
            else:
                tensor.set(param='Axx', value=2.0/3.0 * Sxx)
                tensor.set(param='Ayy', value=2.0/3.0 * Syy)
                tensor.set(param='Axy', value=2.0/3.0 * Sxy)
                tensor.set(param='Axz', value=2.0/3.0 * Sxz)
                tensor.set(param='Ayz', value=2.0/3.0 * Syz)

        # The geometric parameter set {Szz, Sxxyy, Sxy, Sxz, Syz}.
        elif geo_params.count('Szz') == 1 and geo_params.count('Sxxyy') == 1 and geo_params.count('Sxy') == 1 and geo_params.count('Sxz') == 1 and geo_params.count('Syz') == 1:
            # The parameters.
            Szz = geo_values[geo_params.index('Szz')]
            Sxxyy = geo_values[geo_params.index('Sxxyy')]
            Sxy = geo_values[geo_params.index('Sxy')]
            Sxz = geo_values[geo_params.index('Sxz')]
            Syz = geo_values[geo_params.index('Syz')]

            # Set the internal parameter values.
            if errors:
                tensor.set(param='Axx', value=2.0/3.0 * -0.5*(Szz-Sxxyy), category='err')
                tensor.set(param='Ayy', value=2.0/3.0 * -0.5*(Szz+Sxxyy), category='err')
                tensor.set(param='Axy', value=2.0/3.0 * Sxy, category='err')
                tensor.set(param='Axz', value=2.0/3.0 * Sxz, category='err')
                tensor.set(param='Ayz', value=2.0/3.0 * Syz, category='err')
            else:
                tensor.set(param='Axx', value=2.0/3.0 * -0.5*(Szz-Sxxyy))
                tensor.set(param='Ayy', value=2.0/3.0 * -0.5*(Szz+Sxxyy))
                tensor.set(param='Axy', value=2.0/3.0 * Sxy)
                tensor.set(param='Axz', value=2.0/3.0 * Sxz)
                tensor.set(param='Ayz', value=2.0/3.0 * Syz)

        # The geometric parameter set {Axx, Ayy, Axy, Axz, Ayz}.
        elif geo_params.count('Axx') == 1 and geo_params.count('Ayy') == 1 and geo_params.count('Axy') == 1 and geo_params.count('Axz') == 1 and geo_params.count('Ayz') == 1:
            # The parameters.
            Axx = geo_values[geo_params.index('Axx')]
            Ayy = geo_values[geo_params.index('Ayy')]
            Axy = geo_values[geo_params.index('Axy')]
            Axz = geo_values[geo_params.index('Axz')]
            Ayz = geo_values[geo_params.index('Ayz')]

            # Set the internal parameter values.
            if errors:
                tensor.set(param='Axx', value=Axx, category='err')
                tensor.set(param='Ayy', value=Ayy, category='err')
                tensor.set(param='Axy', value=Axy, category='err')
                tensor.set(param='Axz', value=Axz, category='err')
                tensor.set(param='Ayz', value=Ayz, category='err')
            else:
                tensor.set(param='Axx', value=Axx)
                tensor.set(param='Ayy', value=Ayy)
                tensor.set(param='Axy', value=Axy)
                tensor.set(param='Axz', value=Axz)
                tensor.set(param='Ayz', value=Ayz)

        # The geometric parameter set {Azz, Axxyy, Axy, Axz, Ayz}.
        elif geo_params.count('Azz') == 1 and geo_params.count('Axxyy') == 1 and geo_params.count('Axy') == 1 and geo_params.count('Axz') == 1 and geo_params.count('Ayz') == 1:
            # The parameters.
            Azz = geo_values[geo_params.index('Azz')]
            Axxyy = geo_values[geo_params.index('Axxyy')]
            Axy = geo_values[geo_params.index('Axy')]
            Axz = geo_values[geo_params.index('Axz')]
            Ayz = geo_values[geo_params.index('Ayz')]

            # Set the internal parameter values.
            if errors:
                tensor.set(param='Axx', value=-0.5*(Azz-Axxyy), category='err')
                tensor.set(param='Ayy', value=-0.5*(Azz+Axxyy), category='err')
                tensor.set(param='Axy', value=Axy, category='err')
                tensor.set(param='Axz', value=Axz, category='err')
                tensor.set(param='Ayz', value=Ayz, category='err')
            else:
                tensor.set(param='Axx', value=-0.5*(Azz-Axxyy))
                tensor.set(param='Ayy', value=-0.5*(Azz+Axxyy))
                tensor.set(param='Axy', value=Axy)
                tensor.set(param='Axz', value=Axz)
                tensor.set(param='Ayz', value=Ayz)

        # The geometric parameter set {Pxx, Pyy, Pxy, Pxz, Pyz}.
        elif geo_params.count('Pxx') == 1 and geo_params.count('Pyy') == 1 and geo_params.count('Pxy') == 1 and geo_params.count('Pxz') == 1 and geo_params.count('Pyz') == 1:
            # The parameters.
            Pxx = geo_values[geo_params.index('Pxx')]
            Pyy = geo_values[geo_params.index('Pyy')]
            Pxy = geo_values[geo_params.index('Pxy')]
            Pxz = geo_values[geo_params.index('Pxz')]
            Pyz = geo_values[geo_params.index('Pyz')]

            # Set the internal parameter values.
            if errors:
                tensor.set(param='Axx', value=Pxx - 1.0/3.0, category='err')
                tensor.set(param='Ayy', value=Pyy - 1.0/3.0, category='err')
                tensor.set(param='Axy', value=Pxy, category='err')
                tensor.set(param='Axz', value=Pxz, category='err')
                tensor.set(param='Ayz', value=Pyz, category='err')
            else:
                tensor.set(param='Axx', value=Pxx - 1.0/3.0)
                tensor.set(param='Ayy', value=Pyy - 1.0/3.0)
                tensor.set(param='Axy', value=Pxy)
                tensor.set(param='Axz', value=Pxz)
                tensor.set(param='Ayz', value=Pyz)

        # The geometric parameter set {Pzz, Pxxyy, Pxy, Pxz, Pyz}.
        elif geo_params.count('Pzz') == 1 and geo_params.count('Pxxyy') == 1 and geo_params.count('Pxy') == 1 and geo_params.count('Pxz') == 1 and geo_params.count('Pyz') == 1:
            # The parameters.
            Pzz = geo_values[geo_params.index('Pzz')]
            Pxxyy = geo_values[geo_params.index('Pxxyy')]
            Pxy = geo_values[geo_params.index('Pxy')]
            Pxz = geo_values[geo_params.index('Pxz')]
            Pyz = geo_values[geo_params.index('Pyz')]

            # Set the internal parameter values.
            if errors:
                tensor.set(param='Axx', value=-0.5*(Pzz-Pxxyy) - 1.0/3.0, category='err')
                tensor.set(param='Ayy', value=-0.5*(Pzz+Pxxyy) - 1.0/3.0, category='err')
                tensor.set(param='Axy', value=Pxy, category='err')
                tensor.set(param='Axz', value=Pxz, category='err')
                tensor.set(param='Ayz', value=Pyz, category='err')
            else:
                tensor.set(param='Axx', value=-0.5*(Pzz-Pxxyy) - 1.0/3.0)
                tensor.set(param='Ayy', value=-0.5*(Pzz+Pxxyy) - 1.0/3.0)
                tensor.set(param='Axy', value=Pxy)
                tensor.set(param='Axz', value=Pxz)
                tensor.set(param='Ayz', value=Pyz)

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError('geometric parameter set', geo_params)


    # Unknown geometric parameters.
    else:
        raise RelaxUnknownParamCombError('geometric parameter set', geo_params)


    # Orientational parameters.
    ###########################

    # A single orientational parameter.
    if len(orient_params) == 1:
        # The single parameter alpha.
        if orient_params[0] == 'alpha':
            if errors:
                tensor.set(param='alpha', value=orient_values[orient_params.index('alpha')], category='err')
            else:
                tensor.set(param='alpha', value=orient_values[orient_params.index('alpha')])

        # The single parameter beta.
        elif orient_params[0] == 'beta':
            if errors:
                tensor.set(param='beta', value=orient_values[orient_params.index('beta')], category='err')
            else:
                tensor.set(param='beta', value=orient_values[orient_params.index('beta')])

        # The single parameter gamma.
        elif orient_params[0] == 'gamma':
            if errors:
                tensor.set(param='gamma', value=orient_values[orient_params.index('gamma')], category='err')
            else:
                tensor.set(param='gamma', value=orient_values[orient_params.index('gamma')])

    # Two orientational parameters.
    elif len(orient_params) == 2:
        # The orientational parameter set {alpha, beta}.
        if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
            if errors:
                tensor.set(param='alpha', value=orient_values[orient_params.index('alpha')], category='err')
                tensor.set(param='beta', value=orient_values[orient_params.index('beta')], category='err')
            else:
                tensor.set(param='alpha', value=orient_values[orient_params.index('alpha')])
                tensor.set(param='beta', value=orient_values[orient_params.index('beta')])

        # The orientational parameter set {alpha, gamma}.
        if orient_params.count('alpha') == 1 and orient_params.count('gamma') == 1:
            if errors:
                tensor.set(param='alpha', value=orient_values[orient_params.index('alpha')], category='err')
                tensor.set(param='gamma', value=orient_values[orient_params.index('gamma')], category='err')
            else:
                tensor.set(param='alpha', value=orient_values[orient_params.index('alpha')])
                tensor.set(param='gamma', value=orient_values[orient_params.index('gamma')])

        # The orientational parameter set {beta, gamma}.
        if orient_params.count('beta') == 1 and orient_params.count('gamma') == 1:
            if errors:
                tensor.set(param='beta', value=orient_values[orient_params.index('beta')], category='err')
                tensor.set(param='gamma', value=orient_values[orient_params.index('gamma')], category='err')
            else:
                tensor.set(param='beta', value=orient_values[orient_params.index('beta')])
                tensor.set(param='gamma', value=orient_values[orient_params.index('gamma')])

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError('orientational parameter set', orient_params)

    # Three orientational parameters.
    elif len(orient_params) == 3:
        # The orientational parameter set {alpha, beta, gamma}.
        if orient_params.count('alpha') == 1 and orient_params.count('beta') == 1:
            if errors:
                tensor.set(param='alpha', value=orient_values[orient_params.index('alpha')], category='err')
                tensor.set(param='beta', value=orient_values[orient_params.index('beta')], category='err')
                tensor.set(param='gamma', value=orient_values[orient_params.index('gamma')], category='err')
            else:
                tensor.set(param='alpha', value=orient_values[orient_params.index('alpha')])
                tensor.set(param='beta', value=orient_values[orient_params.index('beta')])
                tensor.set(param='gamma', value=orient_values[orient_params.index('gamma')])

        # Unknown parameter combination.
        else:
            raise RelaxUnknownParamCombError('orientational parameter set', orient_params)

    # More than three orientational parameters.
    elif len(orient_params) > 3:
        raise RelaxUnknownParamCombError('orientational parameter set', orient_params)


    # Fold the angles in.
    #####################

    if orient_params:
        fold_angles()


def set_align_id(tensor=None, align_id=None):
    """Set the align ID string for the given tensor.

    @keyword tensor:    The alignment tensor label.
    @type tensor:       str
    @keyword align_id:  The alignment ID string.
    @type align_id:     str
    """

    # Loop over the tensors.
    match = False
    for tensor_cont in cdp.align_tensors:
        # Find the matching tensor and then store the ID.
        if tensor_cont.name == tensor:
            tensor_cont.align_id = align_id
            match = True

    # The tensor label doesn't exist.
    if not match:
        raise RelaxNoTensorError('alignment', tensor)


def set_domain(tensor=None, domain=None):
    """Set the domain label for the given tensor.

    @param tensor:  The alignment tensor label.
    @type tensor:   str
    @param domain:  The domain label.
    @type domain:   str
    """

    # Check that the domain is defined.
    if not hasattr(cdp, 'domain') or domain not in cdp.domain:
        raise RelaxError("The domain '%s' has not been defined.  Please use the domain user function." % domain)

    # Loop over the tensors.
    match = False
    for tensor_cont in cdp.align_tensors:
        # Find the matching tensor and then store the domain label.
        if tensor_cont.name == tensor:
            tensor_cont.set(param='domain', value=domain)
            match = True

    # The tensor label doesn't exist.
    if not match:
        raise RelaxNoTensorError('alignment', tensor)


def svd(basis_set='irreducible 5D', tensors=None, precision=1):
    r"""Calculate the singular values of all the loaded tensors.

    The basis set can be set to one of:

        - 'irreducible 5D', the irreducible 5D basis set {A-2, A-1, A0, A1, A2}.  This is a linear map, hence angles are preserved.
        - 'unitary 9D', the unitary 9D basis set {Sxx, Sxy, Sxz, Syx, Syy, Syz, Szx, Szy, Szz}.  This is a linear map, hence angles are preserved.
        - 'unitary 5D', the unitary 5D basis set {Sxx, Syy, Sxy, Sxz, Syz}.  This is a non-linear map, hence angles are not preserved.
        - 'geometric 5D', the geometric 5D basis set {Szz, Sxxyy, Sxy, Sxz, Syz}.  This is a non-linear map, hence angles are not preserved.  This is also the Pales standard notation.

    If the selected basis set is the default of 'irreducible 5D', the matrix on which SVD will be performed will be::

        | A-2(1) A-1(1) A0(1)  A1(1)  A2(1) |
        | A-2(2) A-1(2) A0(2)  A1(2)  A2(2) |
        | A-2(3) A-1(3) A0(3)  A1(3)  A2(3) |
        |   .      .     .      .      .    |
        |   .      .     .      .      .    |
        |   .      .     .      .      .    |
        | A-2(N) A-1(N) A0(N)  A1(N)  A2(N) |

    If the selected basis set is 'unitary 9D', the matrix on which SVD will be performed will be::

        | Sxx1 Sxy1 Sxz1 Syx1 Syy1 Syz1 Szx1 Szy1 Szz1 |
        | Sxx2 Sxy2 Sxz2 Syx2 Syy2 Syz2 Szx2 Szy2 Szz2 |
        | Sxx3 Sxy3 Sxz3 Syx3 Syy3 Syz3 Szx3 Szy3 Szz3 |
        |  .    .    .    .    .    .    .    .    .   |
        |  .    .    .    .    .    .    .    .    .   |
        |  .    .    .    .    .    .    .    .    .   |
        | SxxN SxyN SxzN SyxN SyyN SyzN SzxN SzyN SzzN |

    Otherwise if the selected basis set is 'unitary 5D', the matrix for SVD is::

        | Sxx1 Syy1 Sxy1 Sxz1 Syz1 |
        | Sxx2 Syy2 Sxy2 Sxz2 Syz2 |
        | Sxx3 Syy3 Sxy3 Sxz3 Syz3 |
        |  .    .    .    .    .   |
        |  .    .    .    .    .   |
        |  .    .    .    .    .   |
        | SxxN SyyN SxyN SxzN SyzN |

    Or if the selected basis set is 'geometric 5D', the stretching and skewing parameters Szz and Sxx-yy will be used instead and the matrix is::

        | Szz1 Sxxyy1 Sxy1 Sxz1 Syz1 |
        | Szz2 Sxxyy2 Sxy2 Sxz2 Syz2 |
        | Szz3 Sxxyy3 Sxy3 Sxz3 Syz3 |
        |  .     .     .    .    .   |
        |  .     .     .    .    .   |
        |  .     .     .    .    .   |
        | SzzN SxxyyN SxyN SxzN SyzN |

    For the irreducible basis set, the Am components are defined as::

                / 4pi \ 1/2
           A0 = | --- |     Szz ,
                \  5  /

                    / 8pi \ 1/2
        A+/-1 = +/- | --- |     (Sxz +/- iSyz) ,
                    \ 15  /

                / 2pi \ 1/2
        A+/-2 = | --- |     (Sxx - Syy +/- 2iSxy) .
                \ 15  /

    The relationships between the geometric and unitary basis sets are::

        Szz = - Sxx - Syy,
        Sxxyy = Sxx - Syy,

    The SVD values and condition number are dependant upon the basis set chosen.


    @keyword basis_set: The basis set to use for the SVD.  This can be one of "irreducible 5D", "unitary 9D", "unitary 5D" or "geometric 5D".
    @type basis_set:    str
    @keyword tensors:   The list of alignment tensor IDs to calculate inter-matrix angles between.  If None, all tensors will be used.
    @type tensors:      None or list of str
    @keyword precision: The precision of the printed out angles.  The number corresponds to the number of figures to print after the decimal point.
    @type precision:    int
    """

    # Argument check.
    allowed = ['irreducible 5D', 'unitary 9D', 'unitary 5D', 'geometric 5D']
    if basis_set not in allowed:
        raise RelaxError("The basis set of '%s' is not one of %s." % (basis_set, allowed))

    # Test that alignment tensor data exists.
    if not hasattr(cdp, 'align_tensors') or len(cdp.align_tensors) == 0:
        raise RelaxNoTensorError('alignment')

    # Count the number of tensors used in the SVD.
    tensor_num = 0
    for tensor in cdp.align_tensors:
        if tensors and tensor.name not in tensors:
            continue
        tensor_num = tensor_num + 1

    # Create the matrix to apply SVD on.
    if basis_set in ['unitary 9D']:
        matrix = zeros((tensor_num, 9), float64)
    elif basis_set in ['irreducible 5D']:
        matrix = zeros((tensor_num, 5), complex128)
    else:
        matrix = zeros((tensor_num, 5), float64)

    # Pack the elements.
    i = 0
    for tensor in cdp.align_tensors:
        # Skip tensors.
        if tensors and tensor.name not in tensors:
            continue

        # 5D irreducible basis set.
        if basis_set == 'irreducible 5D':
            matrix[i, 0] = tensor.Am2
            matrix[i, 1] = tensor.Am1
            matrix[i, 2] = tensor.A0
            matrix[i, 3] = tensor.A1
            matrix[i, 4] = tensor.A2

        # 5D unitary basis set.
        elif basis_set == 'unitary 9D':
            matrix[i, 0] = tensor.Sxx
            matrix[i, 1] = tensor.Sxy
            matrix[i, 2] = tensor.Sxz
            matrix[i, 3] = tensor.Sxy
            matrix[i, 4] = tensor.Syy
            matrix[i, 5] = tensor.Syz
            matrix[i, 6] = tensor.Sxz
            matrix[i, 7] = tensor.Syz
            matrix[i, 8] = tensor.Szz

        # 5D unitary basis set.
        elif basis_set == 'unitary 5D':
            matrix[i, 0] = tensor.Sxx
            matrix[i, 1] = tensor.Syy
            matrix[i, 2] = tensor.Sxy
            matrix[i, 3] = tensor.Sxz
            matrix[i, 4] = tensor.Syz

        # 5D geometric basis set.
        elif basis_set == 'geometric 5D':
            matrix[i, 0] = tensor.Szz
            matrix[i, 1] = tensor.Sxxyy
            matrix[i, 2] = tensor.Sxy
            matrix[i, 3] = tensor.Sxz
            matrix[i, 4] = tensor.Syz

        # Increment the index.
        i = i + 1

    # SVD.
    u, s, vh = linalg.svd(matrix)

    # Store the singular values.
    cdp.align_tensors.singular_vals = s

    # Calculate and store the condition number.
    cdp.align_tensors.cond_num = s[0] / s[-1]

    # Print out.
    if basis_set == 'irreducible 5D':
        sys.stdout.write("SVD for the irreducible 5D vectors {A-2, A-1, A0, A1, A2}.\n")
    elif basis_set == 'unitary 9D':
        sys.stdout.write("SVD for the unitary 9D vectors {Sxx, Sxy, Sxz, Syx, Syy, Syz, Szx, Szy, Szz}.\n")
    elif basis_set == 'unitary 5D':
        sys.stdout.write("SVD for the unitary 5D vectors {Sxx, Syy, Sxy, Sxz, Syz}.\n")
    elif basis_set == 'geometric 5D':
        sys.stdout.write("SVD for the geometric 5D vectors {Szz, Sxx-yy, Sxy, Sxz, Syz}.\n")
    sys.stdout.write("\nSingular values:\n")
    for val in s:
        format = "    %." + repr(precision) + "e\n"
        sys.stdout.write(format % val)
    format = "\nCondition number: %." + repr(precision) + "f\n"
    sys.stdout.write(format % cdp.align_tensors.cond_num)
